import hashlib
import random
import string
from django.contrib.auth.hashers import make_password, check_password

def hash_password(password):
    # Django's make_password which defaults to PBKDF2 hasher
    #PBKDF2 = hash-based message authentication code (HMAC), to the input password or passphrase along with a salt value
    return make_password(password)

def verify_password(stored_password, provided_password):
    try:
        is_correct = check_password(provided_password, stored_password)
        return is_correct
    except ValueError:
        return False


def generate_token():
    return hashlib.sha1(''.join(random.choices(string.ascii_uppercase + string.digits, k=20)).encode()).hexdigest()
