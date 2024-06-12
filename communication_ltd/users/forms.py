
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import json

#RegisterForm
class RegisterForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        
        # Validate password complexity
        with open('configuration.json') as config_file:
            config = json.load(config_file)
            
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

#ChangePasswordForm
class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise ValidationError("Passwords do not match.")

#ForgotPasswordForm
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

#ResetPasswordForm
class ResetPasswordForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)