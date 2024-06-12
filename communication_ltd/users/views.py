from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.urls import reverse
from .forms import RegisterForm, ChangePasswordForm, ForgotPasswordForm, ResetPasswordForm, LoginForm
from .models import Customer, UserPasswordHistory
from .utils import hash_password, check_password, generate_token

def save_password_history(email, password):
    UserPasswordHistory.objects.create(email=email, password=password)
    # Keep only the last 3 passwords
    passwords = UserPasswordHistory.objects.filter(email=email).order_by('-timestamp')
    if passwords.count() > 3:
        for password in passwords[3:]:
            password.delete()

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            hashed_password = hash_password(password)
            
            try:
                customer = Customer.objects.create(email=email, password=hashed_password)
                save_password_history(email, hashed_password)
                send_mail(
                    'Welcome to Communication_LTD',
                    'Thanks for registering!',
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )
                return redirect('login')
            except IntegrityError:
                form.add_error('email', 'Email already exists.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            customer = Customer.objects.get(email=request.user.email)
            if check_password(customer.password, current_password):
                # Check if new password is not one of the last 3 passwords
                hashed_new_password = hash_password(new_password)
                recent_passwords = UserPasswordHistory.objects.filter(email=request.user.email).order_by('-timestamp')[:3]
                for password_entry in recent_passwords:
                    if check_password(password_entry.password, new_password):
                        form.add_error('new_password', 'New password cannot be one of the last 3 passwords used.')
                        return render(request, 'change_password.html', {'form': form})
                
                customer.password = hashed_new_password
                customer.save()
                save_password_history(customer.email, hashed_new_password)
                return redirect('profile')
            else:
                form.add_error('current_password', 'Current password is incorrect.')
    else:
        form = ChangePasswordForm()
    return render(request, 'change_password.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                customer = Customer.objects.get(email=email)
                new_password = generate_token()
                hashed_password = hash_password(new_password)
                customer.password = hashed_password
                customer.reset_token = ''
                customer.token_created_at = None
                customer.save()
                email_content = f'Your new password is: {new_password}'
                send_mail(
                    'Password Reset for Communication_LTD',
                    email_content,
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )
                return redirect('password_reset_done')
            except Customer.DoesNotExist:
                form.add_error('email', 'Email does not exist.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data.get('token')
            new_password = form.cleaned_data.get('new_password')
            confirm_password = form.cleaned_data.get('confirm_password')
            if new_password != confirm_password:
                form.add_error('confirm_password', 'Passwords do not match.')
                return render(request, 'reset_password.html', {'form': form})
            try:
                customer = Customer.objects.get(reset_token=token)
                if timezone.now() - customer.token_created_at > timezone.timedelta(hours=1):
                    form.add_error(None, 'The token is invalid or expired.')
                    return render(request, 'reset_password.html', {'form': form})
                customer.password = hash_password(new_password)
                customer.reset_token = ''
                customer.token_created_at = None
                customer.save()
                return redirect('login')
            except Customer.DoesNotExist:
                form.add_error(None, 'The token is invalid or expired.')
    else:
        token = request.GET.get('token')
        if not token:
            return redirect('forgot_password')
        form = ResetPasswordForm(initial={'token': token})
    return render(request, 'reset_password.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)  # Use auth_login to avoid conflict
                return redirect('profile')  # Adjust this as needed
            form.add_error(None, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    return render(request, 'home.html')

def password_reset_done(request):
    return render(request, 'password_reset_done.html')
