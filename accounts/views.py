# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import User, PasswordResetOTP


# ---------- Registration ----------
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        # Validation
        if not username or not email or not mobile or not password:
            messages.error(request, 'All fields are required')
            return render(request, 'accounts/register.html')

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/register.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'accounts/register.html')

        if not mobile.isdigit() or len(mobile) < 10:
            messages.error(request, 'Please enter a valid mobile number')
            return render(request, 'accounts/register.html')

        # Check existing
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered. Please log in.')
            return redirect('login')

        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, 'This mobile number is already registered. Please log in.')
            return redirect('login')

        # Create user (Django hashes the password automatically)
        user = User.objects.create_user(
            username=username,
            email=email,
            mobile=mobile,
            password=password,   # gets hashed by create_user
        )
        user.is_active = True
        user.email_verified = True
        user.save()

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'accounts/register.html')


# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import User # keep other imports as they are

def login_view(request):
    if request.method == 'POST':
        # We use Django's built-in form to handle the password checking
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            # This prints the exact failure reason to your terminal
            print("LOGIN FAILED:", form.errors)
            messages.error(request, 'Invalid email or password')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


# ---------- Forgot Password ----------
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal whether the email exists
            messages.success(request, 'If this email is registered, you will receive a reset code.')
            return redirect('login')

        code, token = PasswordResetOTP.create_for_user(user)

        send_mail(
            subject='Password Reset Code',
            message=f'Your password reset code is: {code}\n\nThis code expires in 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        request.session['reset_user_id'] = user.id
        messages.success(request, 'A reset code has been sent to your email.')
        return redirect('reset_password')

    return render(request, 'accounts/forgot_password.html')


# ---------- Reset Password ----------
def reset_password_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Session expired, please try again')
        return redirect('forgot_password')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('forgot_password')

    if request.method == 'POST':
        code = request.POST.get('otp', '').strip()
        new_password = request.POST.get('password', '')
        new_password2 = request.POST.get('password2', '')

        if new_password != new_password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/reset_password.html')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'accounts/reset_password.html')

        token = PasswordResetOTP.objects.filter(
            user=user, is_used=False
        ).order_by('-created_at').first()

        if not token or not token.is_valid():
            messages.error(request, 'Code expired or invalid. Please request a new one.')
            return redirect('forgot_password')

        if token.verify(code):
            user.set_password(new_password)
            user.save()
            del request.session['reset_user_id']
            messages.success(request, 'Password reset successful. Please log in.')
            return redirect('login')
        else:
            remaining = token.max_attempts - token.attempts
            messages.error(request, f'Incorrect code. {remaining} attempts remaining.')

    return render(request, 'accounts/reset_password.html')