import os
import hashlib
import paramiko
from paramiko.sftp_attr import SFTPAttributes

def calculate_hash(file_path):
    """Calculate the SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            hash_sha256.update(byte_block)
    return hash_sha256.hexdigest()

def get_remote_file_hash(sftp, remote_path):
    """Get the SHA-256 hash of a remote file."""
    try:
        with sftp.open(remote_path, 'rb') as f:
            hash_sha256 = hashlib.sha256()
            for byte_block in iter(lambda: f.read(4096), b""):
                hash_sha256.update(byte_block)
            return hash_sha256.hexdigest()
    except FileNotFoundError:
        return None

def sync_files(local_folder, remote_folder, hostname, username, password):
    transport = paramiko.Transport((hostname, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    for root, _, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            remote_path = os.path.join(remote_folder, os.path.relpath(local_path, local_folder))
            
            local_hash = calculate_hash(local_path)
            remote_hash = get_remote_file_hash(sftp, remote_path)
            
            if remote_hash and local_hash == remote_hash:
                print(f"Skipping {local_path} (no changes)")
                continue
            
            try:
                remote_stat = sftp.stat(remote_path)
                if remote_stat.st_mtime > os.path.getmtime(local_path):
                    print(f"Skipping {local_path} (remote is newer)")
                    continue
            except FileNotFoundError:
                pass
            
            print(f"Uploading {local_path} to {remote_path}")
            sftp.put(local_path, remote_path)
    
    transport.close()

if __name__ == '__main__':
    local_folder = '/path/to/local/folder'  # Replace with your local folder path
    remote_folder = '/path/to/remote/folder'  # Replace with your remote folder path
    hostname = 'your.remote.server'  # Replace with your remote server hostname
    username = 'your_username'  # Replace with your username
    password = 'your_password'  # Replace with your password
    
    sync_files(local_folder, remote_folder, hostname, username, password)