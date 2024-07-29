import json
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages

# Load configuration from file
with open('configuration.json') as config_file:
    config = json.load(config_file)

MAX_FAILED_ATTEMPTS = config.get('max_failed_attempts', 3)
LOCKOUT_PERIOD = timedelta(minutes=config.get('lockout_period_minutes', 2))

def handle_failed_login(request, customer):
    customer.failed_login_attempts += 1
    customer.last_failed_login = timezone.now()
    customer.save()

    attempts_left = MAX_FAILED_ATTEMPTS - customer.failed_login_attempts
    if attempts_left > 0:
        messages.error(request, f'{customer.failed_login_attempts}/{MAX_FAILED_ATTEMPTS} tries... \n Strike 3 and you\'re out!')
    else:
        messages.error(request, 'Account locked due to too many failed login attempts.')

def reset_failed_attempts(customer):
    customer.failed_login_attempts = 0
    customer.save()

def is_account_locked(customer):
    if customer.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        lockout_expired = customer.last_failed_login + LOCKOUT_PERIOD < timezone.now()
        if lockout_expired:
            reset_failed_attempts(customer)
            return False
        return True
    return False
