import hashlib
import random
import string
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def check_password(stored_password, provided_password):
    try:
        return bcrypt.checkpw(provided_password.encode(), stored_password.encode())
    except ValueError:
        # Handle legacy passwords
        return False

def generate_token():
    return hashlib.sha1(''.join(random.choices(string.ascii_uppercase + string.digits, k=20)).encode()).hexdigest()
