import json
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from users.models import UserPasswordHistory
from communication_ltd.users.hashers import hash_password, check_password

User = get_user_model()

class UserTests(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.change_password_url = reverse('change_password')
        self.password = "TestPassword123!"
        self.email = "testuser@example.com"
        self.user = User.objects.create_user(email=self.email, password=self.password)

        self.config = {
            "min_length": 10,
            "max_attempts": 3,
            "complexity": "uppercase,lowercase,numbers,special",
            "history": 3,
            "dictionary_check": True,
            "digits": True,
            "salt": "sgnankaklfndah",
            "special_characters": True,
            "special_characters_list": "!@#$%^&*()_+=-{}[]:;\"'<>,.?/|\\",
            "cool_down_period": 1  # In minutes
        }

    @patch('builtins.open', create=True)
    @patch('json.load', return_value={
        "min_length": 10,
        "max_attempts": 3,
        "complexity": "uppercase,lowercase,numbers,special",
        "history": 3,
        "dictionary_check": True,
        "digits": True,
        "salt": "sgnankaklfndah",
        "special_characters": True,
        "special_characters_list": "!@#$%^&*()_+=-{}[]:;\"'<>,.?/|\\",
        "cool_down_period": 1
    })
    def test_user_registration(self, mock_json_load, mock_open):
        response = self.client.post(self.register_url, {
            'email': 'newuser@example.com',
            'password': 'NewUserPassword123!',
            'confirm_password': 'NewUserPassword123!'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration
        new_user = User.objects.get(email='newuser@example.com')
        self.assertTrue(new_user.check_password('NewUserPassword123!'))

    @patch('builtins.open', create=True)
    @patch('json.load', return_value={
        "min_length": 10,
        "max_attempts": 3,
        "complexity": "uppercase,lowercase,numbers,special",
        "history": 3,
        "dictionary_check": True,
        "digits": True,
        "salt": "sgnankaklfndah",
        "special_characters": True,
        "special_characters_list": "!@#$%^&*()_+=-{}[]:;\"'<>,.?/|\\",
        "cool_down_period": 1
    })
    def test_user_login(self, mock_json_load, mock_open):
        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login
        self.assertTrue(response.url.startswith(self.profile_url))  # Should redirect to profile

    @patch('builtins.open', create=True)
    @patch('json.load', return_value={
        "min_length": 10,
        "max_attempts": 3,
        "complexity": "uppercase,lowercase,numbers,special",
        "history": 3,
        "dictionary_check": True,
        "digits": True,
        "salt": "sgnankaklfndah",
        "special_characters": True,
        "special_characters_list": "!@#$%^&*()_+=-{}[]:;\"'<>,.?/|\\",
        "cool_down_period": 1
    })
    def test_invalid_user_login(self, mock_json_load, mock_open):
        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 200)  # Should return to login page
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid email or password" in str(message) for message in messages))

    @patch('builtins.open', create=True)
    @patch('json.load', return_value={
        "min_length": 10,
        "max_attempts": 3,
        "complexity": "uppercase,lowercase,numbers,special",
        "history": 3,
        "dictionary_check": True,
        "digits": True,
        "salt": "sgnankaklfndah",
        "special_characters": True,
        "special_characters_list": "!@#$%^&*()_+=-{}[]:;\"'<>,.?/|\\",
        "cool_down_period": 1
    })
    def test_account_lockout_after_max_attempts(self, mock_json_load, mock_open):
        for _ in range(self.config['max_attempts']):
            response = self.client.post(self.login_url, {
                'email': self.email,
                'password': 'WrongPassword'
            })
            self.assertEqual(response.status_code, 200)
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("Invalid email or password" in str(message) for message in messages))

        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Your account is locked due to too many failed login attempts. Please try again later." in str(message) for message in messages))

    @patch('builtins.open', create=True)
    @patch('json.load', return_value={
        "min_length": 10,
        "max_attempts": 3,
        "complexity": "uppercase,lowercase,numbers,special",
        "history": 3,
        "dictionary_check": True,
        "digits": True,
        "salt": "sgnankaklfndah",
        "special_characters": True,
        "special_characters_list": "!@#$%^&*()_+=-{}[]:;\"'<>,.?/|\\",
        "cool_down_period": 1
    })
    def test_password_history(self, mock_json_load, mock_open):
        old_passwords = [
            hash_password('OldPassword1!'),
            hash_password('OldPassword2@'),
            hash_password('OldPassword3#')
        ]
        
        for pw in old_passwords:
            UserPasswordHistory.objects.create(email=self.email, password=pw)
        
        new_password = 'NewSecurePassword4$'
        
        response = self.client.post(self.change_password_url, {
            'current_password': self.password,
            'new_password': new_password,
            'confirm_password': new_password
        })
        self.assertEqual(response.status_code, 302)
        
        self.assertEqual(UserPasswordHistory.objects.filter(email=self.email).count(), 3)
        self.assertTrue(UserPasswordHistory.objects.filter(email=self.email, password=old_passwords[2]).exists())
        self.assertFalse(UserPasswordHistory.objects.filter(email=self.email, password=old_passwords[0]).exists())
