import os
import hashlib
import boto3
import argparse

CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB

def calculate_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def upload_file_to_s3(file_path, bucket_name, object_name, s3_client):
    if os.path.exists(file_path):
        file_hash = calculate_file_hash(file_path)
        existing_object = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=object_name)
        if "Contents" in existing_object:
            for obj in existing_object["Contents"]:
                if obj["Key"] == object_name:
                    existing_metadata = s3_client.head_object(Bucket=bucket_name, Key=object_name)
                    if "Metadata" in existing_metadata and existing_metadata["Metadata"].get("file_hash") == file_hash:
                        print(f"File {object_name} is already up to date.")
                        return

        print(f"Uploading {file_path} to {bucket_name}/{object_name}")
        with open(file_path, "rb") as data:
            s3_client.upload_fileobj(data, bucket_name, object_name, ExtraArgs={"Metadata": {"file_hash": file_hash}})
    else:
        print(f"File {file_path} does not exist.")

def download_file_from_s3(file_path, bucket_name, object_name, s3_client):
    if os.path.exists(file_path):
        local_hash = calculate_file_hash(file_path)
        existing_object = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=object_name)
        if "Contents" in existing_object:
            for obj in existing_object["Contents"]:
                if obj["Key"] == object_name:
                    existing_metadata = s3_client.head_object(Bucket=bucket_name, Key=object_name)
                    if "Metadata" in existing_metadata and existing_metadata["Metadata"].get("file_hash") == local_hash:
                        print(f"File {object_name} is already up to date.")
                        return

    print(f"Downloading {bucket_name}/{object_name} to {file_path}")
    s3_client.download_file(bucket_name, object_name, file_path)

def sync_files(local_path, bucket_name, s3_client, direction="upload"):
    for root, _, files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            object_name = os.path.relpath(local_file_path, local_path)

            if direction == "upload":
                upload_file_to_s3(local_file_path, bucket_name, object_name, s3_client)
            elif direction == "download":
                download_file_from_s3(local_file_path, bucket_name, object_name, s3_client)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync files between local and S3")
    parser.add_argument("local_path", help="Local path to sync")
    parser.add_argument("bucket_name", help="S3 bucket name")
    parser.add_argument("direction", choices=["upload", "download"], help="Direction of sync")
    args = parser.parse_args()

    s3_client = boto3.client("s3")
    sync_files(args.local_path, args.bucket_name, s3_client, args.direction)