from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse
from .models import Customer, UserPasswordHistory
from .utils import hash_password, check_password

class UserRegistrationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_view_post_valid(self):
        response = self.client.post(self.register_url, {
            'email': 'testuser@example.com',
            'password': 'Test@12345',
            'confirm_password': 'Test@12345'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.first().email, 'testuser@example.com')
        self.assertEqual(UserPasswordHistory.objects.count(), 1)
        self.assertEqual(UserPasswordHistory.objects.first().email, 'testuser@example.com')

    def test_register_view_post_invalid(self):
        response = self.client.post(self.register_url, {
            'email': 'testuser@example.com',
            'password': 'Test@12345',
            'confirm_password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.count(), 0)
        self.assertContains(response, 'Passwords do not match.')


def test_change_password_view_post_reused_password(self):
    # Change password to 'NewPass@12345'
    self.client.post(self.change_password_url, {
        'current_password': 'OldPass@12345',
        'new_password': 'NewPass@12345',
        'confirm_password': 'NewPass@12345'
    })
    # Try to change password to 'OldPass@12345' again
    response = self.client.post(self.change_password_url, {
        'current_password': 'NewPass@12345',
        'new_password': 'OldPass@12345',
        'confirm_password': 'OldPass@12345'
    })
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'New password cannot be one of the last 3 passwords used.')

def test_change_password_view_post_reused_among_last_three_passwords(self):
    # Change password to 'Password2@12345'
    self.client.post(self.change_password_url, {
        'current_password': 'OldPass@12345',
        'new_password': 'Password2@12345',
        'confirm_password': 'Password2@12345'
    })
    # Change password to 'Password3@12345'
    self.client.post(self.change_password_url, {
        'current_password': 'Password2@12345',
        'new_password': 'Password3@12345',
        'confirm_password': 'Password3@12345'
    })
    # Change password to 'Password4@12345'
    self.client.post(self.change_password_url, {
        'current_password': 'Password3@12345',
        'new_password': 'Password4@12345',
        'confirm_password': 'Password4@12345'
    })
    # Try to change password to 'Password2@12345' again
    response = self.client.post(self.change_password_url, {
        'current_password': 'Password4@12345',
        'new_password': 'Password2@12345',
        'confirm_password': 'Password2@12345'
    })
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'New password cannot be one of the last 3 passwords used.')


class ResetPasswordTest(TestCase):

    def setUp(self):
        self.client = Client()
        hashed_password = hash_password('OldPass@12345')
        self.customer = Customer.objects.create(
            email='testuser@example.com',
            password=hashed_password
        )
        UserPasswordHistory.objects.create(email='testuser@example.com', password=hashed_password)
        self.reset_password_url = reverse('reset_password')

    def test_reset_password_view_get(self):
        token = 'resettoken'
        self.customer.reset_token = token
        self.customer.save()
        response = self.client.get(self.reset_password_url, {'token': token})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reset_password.html')

    def test_reset_password_view_post_valid(self):
        token = 'resettoken'
        self.customer.reset_token = token
        self.customer.save()
        response = self.client.post(self.reset_password_url, {
            'token': token,
            'new_password': 'NewPass@12345',
            'confirm_password': 'NewPass@12345'
        })
        self.assertEqual(response.status_code, 302)
        self.customer.refresh_from_db()
        self.assertTrue(check_password(self.customer.password, 'NewPass@12345'))
        self.assertEqual(UserPasswordHistory.objects.filter(email='testuser@example.com').count(), 2)

    def test_reset_password_view_post_invalid_token(self):
        response = self.client.post(self.reset_password_url, {
            'token': 'invalidtoken',
            'new_password': 'NewPass@12345',
            'confirm_password': 'NewPass@12345'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid or expired token.')

    def test_reset_password_view_post_invalid_confirm_password(self):
        token = 'resettoken'
        self.customer.reset_token = token
        self.customer.save()
        response = self.client.post(self.reset_password_url, {
            'token': token,
            'new_password': 'NewPass@12345',
            'confirm_password': 'WrongPass@12345'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match.')

class ForgotPasswordTest(TestCase):

    def setUp(self):
        self.client = Client()
        hashed_password = hash_password('Test@12345')
        self.customer = Customer.objects.create(
            email='testuser@example.com',
            password=hashed_password
        )
        self.forgot_password_url = reverse('forgot_password')

    def test_forgot_password_view_get(self):
        response = self.client.get(self.forgot_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forgot_password.html')

    def test_forgot_password_view_post_valid(self):
        response = self.client.post(self.forgot_password_url, {
            'email': 'testuser@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset for Communication_LTD', mail.outbox[0].subject)
        self.assertIn('Your new password is:', mail.outbox[0].body)

    def test_forgot_password_view_post_invalid(self):
        response = self.client.post(self.forgot_password_url, {
            'email': 'nonexistent@example.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email does not exist.')
        self.assertEqual(len(mail.outbox), 0)
