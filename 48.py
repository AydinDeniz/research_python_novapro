import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import logging

# Configure logging to avoid printing sensitive information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def decrypt_config(encrypted_data, key):
    try:
        # Base64 decode the encrypted data
        encrypted_data = base64.b64decode(encrypted_data)
        
        # Extract the IV from the encrypted data
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Create a Cipher object
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Decrypt the ciphertext
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad the decrypted data
        decrypted_data = unpad(decrypted_data)
        
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logging.error("Decryption failed: %s", type(e).__name__)
        return None

def unpad(s):
    return s[:-ord(s[len(s)-1:])]

def read_config(file_path, key):
    try:
        with open(file_path, 'r') as file:
            encrypted_config = file.read()
            decrypted_config = decrypt_config(encrypted_config, key)
            if decrypted_config:
                logging.info("Configuration file decrypted successfully")
                return decrypted_config
            else:
                logging.error("Failed to decrypt configuration file")
                return None
    except FileNotFoundError:
        logging.error("Configuration file not found")
        return None
    except Exception as e:
        logging.error("An error occurred: %s", type(e).__name__)
        return None

if __name__ == '__main__':
    # Example usage
    key = b'your-32-byte-long-key-here'  # Replace with your actual 32-byte key
    file_path = 'config.enc'  # Replace with your actual file path
    
    config = read_config(file_path, key)
    if config:
        print("Decrypted Config:", config)
    else:
        print("Failed to read config")