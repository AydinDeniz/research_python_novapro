# Prompt 53

import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.exceptions import InvalidSignature

def load_public_key(pem_file):
    with open(pem_file, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read()
        )
    return public_key

def verify_signature(public_key, signature, document):
    try:
        public_key.verify(
            signature,
            document,
            padding.PKCS1v15(),
            utils.Prehashed(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False

def main():
    public_key_file = "public_key.pem"
    document_file = "document.txt"
    signature_file = "signature.txt"

    if not os.path.exists(public_key_file) or not os.path.exists(document_file) or not os.path.exists(signature_file):
        print("Missing required files.")
        return

    public_key = load_public_key(public_key_file)

    with open(document_file, "rb") as doc_file:
        document = doc_file.read()

    with open(signature_file, "rb") as sig_file:
        signature = base64.b64decode(sig_file.read())

    if verify_signature(public_key, signature, document):
        print("Signature is valid.")
    else:
        print("Signature is invalid or malformed.")

if __name__ == "__main__":
    main()