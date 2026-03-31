import getpass
import sys
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_note(note: str, password: str) -> bytes:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(note.encode())
    return salt + encrypted

def decrypt_note(encrypted_note: bytes, password: str) -> str:
    salt = encrypted_note[:16]
    encrypted = encrypted_note[16:]
    key = derive_key(password, salt)
    f = Fernet(key)
    try:
        decrypted = f.decrypt(encrypted).decode()
    except InvalidToken:
        raise ValueError("Incorrect password")
    return decrypted

def save_note(encrypted_note: bytes, filename: str):
    with open(filename, 'wb') as f:
        f.write(encrypted_note)

def load_note(filename: str) -> bytes:
    with open(filename, 'rb') as f:
        return f.read()

def main():
    if len(sys.argv) != 2:
        print("Usage: python encrypted_notes.py <note_file>")
        sys.exit(1)

    note_file = sys.argv[1]
    password = getpass.getpass("Enter password: ")

    if os.path.exists(note_file):
        encrypted_note = load_note(note_file)
        try:
            note = decrypt_note(encrypted_note, password)
            print("Decrypted note:", note)
        except ValueError as e:
            print("Error:", e)
            return
    else:
        note = input("Enter your note: ")
        encrypted_note = encrypt_note(note, password)
        save_note(encrypted_note, note_file)
        print("Note saved securely.")

if __name__ == "__main__":
    main()