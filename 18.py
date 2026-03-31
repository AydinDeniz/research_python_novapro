# Prompt 18

import hashlib
import itertools
import string
import time

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def brute_force_attack(hashed_password, max_length=4):
    """Attempt to crack a hashed password using a brute force attack."""
    characters = string.ascii_letters + string.digits
    for length in range(1, max_length + 1):
        for attempt in itertools.product(characters, repeat=length):
            attempt - The generated text has been blocked by our content filters.