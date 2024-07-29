from django import forms
from django.core.exceptions import ValidationError
from .models import Customer
from .validators import validate_password

# RegisterForm
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
        
        validate_password(password)

# ChangePasswordForm
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
        
        validate_password(new_password)

# ForgotPasswordForm
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

# ResetPasswordForm
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
        
        validate_password(new_password)

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class CustomerNameForm(forms.ModelForm):
    new_customer_name = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 1,
        'cols': 50,
    }), label='Enter Customer name:')

    class Meta:
        model = Customer
        fields = []