from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import Customer
from .forms import RegisterForm, ChangePasswordForm, ForgotPasswordForm, ResetPasswordForm, LoginForm,CustomerNameForm
from .models import Customer, UserPasswordHistory
from .hashers import hash_password, verify_password, generate_token
from .login_attempts_handler import handle_failed_login, reset_failed_attempts, is_account_locked

def home(request):
    return render(request, 'home.html')

def save_password_history(email, password):
    UserPasswordHistory.objects.create(email=email, password=password)
    # Keep only the last 3 passwords
    passwords = UserPasswordHistory.objects.filter(email=email).order_by('-timestamp')
    if passwords.count() > 3:
        for password in passwords[3:]:
            password.delete()

# register
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
                return redirect('login')
            except IntegrityError:
                form.add_error('email', 'Email already exists.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

#login
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            try:
                customer = Customer.objects.get(email=email)
            except Customer.DoesNotExist:
                messages.error(request, 'Invalid email or password')
                return render(request, 'login.html', {'form': form})

            if is_account_locked(customer):
                messages.error(request, 'Account locked due to too many failed login attempts.')
                return render(request, 'login.html', {'form': form})

            user = authenticate(request, username=email, password=password)
            if user is not None:
                reset_failed_attempts(customer)
                auth_login(request, user)
                return redirect('profile')
            else:
                handle_failed_login(request, customer)
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = LoginForm()
        # Clear any residual messages
        storage = messages.get_messages(request)
        list(storage)  # Access the messages to clear them
        
    return render(request, 'login.html', {'form': form})

# -------------------- loged in user--------------------------------
@login_required
def profile(request):
    try:
        customer = Customer.objects.get(email=request.user.email)
    except Customer.DoesNotExist:
        messages.error(request, "Customer does not exist.")
        return redirect('profile')

    if request.method == 'POST':
        new_customer_name = request.POST.get('new_customer_name')
        if new_customer_name:
            customer.new_customer_name.append(new_customer_name) 
            customer.save()  
        return redirect('profile')
    else:
        form = CustomerNameForm(instance=customer)

    context = {
        'form': form,
        'new_customer_names': customer.new_customer_name 
    }
    return render(request, 'profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            customer = Customer.objects.get(email=request.user.email)

            if verify_password(customer.password, current_password):
                hashed_new_password = hash_password(new_password)

                recent_passwords = UserPasswordHistory.objects.filter(email=request.user.email).order_by('-timestamp')[:3]
                for password_entry in recent_passwords:
                    if verify_password(password_entry.password, new_password):
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

@login_required
def user_logout(request):
    auth_logout(request)
    return redirect('login')
#------------------------------------------------------------------

# user login -> forgot_password process
# forgot_password process: ( forgot_password -> enter_passcode -> reset_password )
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                customer = Customer.objects.get(email=email)
                # Generate reset token
                reset_token = generate_token()
                customer.reset_token = reset_token
                customer.token_created_at = timezone.now()
                customer.save()

                # Construct the email content
                plain_text_content = f"""
                Dear {customer.email},

                A password reset request has been initiated for your account. Please use the following passcode to proceed with resetting your password:

                Passcode: {customer.reset_token}

                If you did not initiate this request, please ignore this email.

                Best regards,
                Communication_LTD Support Team
                """

                html_content = f"""
                <p>Dear {customer.email},</p>
                <p>A password reset request has been initiated for your account. Please use the following passcode to proceed with resetting your password:</p>
                <p><strong>Passcode: {customer.reset_token}</strong></p>
                <p>If you did not initiate this request, please ignore this email.</p>
                <p>Best regards,<br>Communication_LTD Support Team</p>
                """

                # Send the passcode to the user's email
                subject = 'Password Reset for Communication_LTD'
                from_email = 'from@example.com'
                to = [email]

                msg = EmailMultiAlternatives(subject, plain_text_content, from_email, to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                messages.success(request, 'A passcode has been sent to your email.')
                return redirect('enter_passcode')
            except Customer.DoesNotExist:
                form.add_error('email', 'Email does not exist.')
            except Exception as e:
                messages.error(request, 'An error occurred while sending the email. Please try again later.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

# enter_passcode 
def enter_passcode(request):
    if request.method == 'POST':
        reset_token = request.POST.get('reset_token')
        try:
            customer = Customer.objects.get(reset_token=reset_token)
            if reset_token == customer.reset_token:
                return redirect(f'/reset-password/?token={customer.reset_token}')
            else:
                messages.error(request, 'Invalid passcode.')
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid passcode.')
    return render(request, 'passcode_entry.html')

# reset_password
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
                
                # Check if token is expired
                if timezone.now() - customer.token_created_at > timezone.timedelta(hours=1):
                    form.add_error(None, 'The token is invalid or expired.')
                    return render(request, 'reset_password.html', {'form': form})

                # Check password history
                recent_passwords = UserPasswordHistory.objects.filter(email=customer.email).order_by('-timestamp')[:3]
                for password_entry in recent_passwords:
                    if verify_password(password_entry.password, new_password):
                        form.add_error('new_password', 'New password cannot be one of the last 3 passwords used.')
                        return render(request, 'reset_password.html', {'form': form})

                # Update password and clear token
                hashed_new_password = hash_password(new_password)
                customer.set_password(new_password) 
                customer.reset_token = ''
                customer.token_created_at = None
                customer.save()
                save_password_history(customer.email, hashed_new_password)
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
            except Customer.DoesNotExist:
                form.add_error(None, 'The token is invalid or expired.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        token = request.GET.get('token')
        if not token:
            return redirect('forgot_password')
        form = ResetPasswordForm(initial={'token': token})
    return render(request, 'reset_password.html', {'form': form})