import json
from django.core.exceptions import ValidationError

with open('configuration.json') as config_file:
        config = json.load(config_file)
        
def validate_password(password):   
    if len(password) < config['min_length']:
        raise ValidationError(f"Password must be at least {config['min_length']} characters long.")
    if not any(c.isupper() for c in password) and 'uppercase' in config['complexity']:
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in password) and 'lowercase' in config['complexity']:
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in password) and 'numbers' in config['complexity']:
        raise ValidationError("Password must contain at least one number.")
    if not any(c in config['special_characters_list'] for c in password) and 'special' in config['complexity']:
        raise ValidationError(f"Password must contain at least one special character from {config['special_characters_list']}.")
    if password in config['common_weak_passwords']:
        raise ValidationError("Password is too common and easy to guess. Please choose a more secure password.")
