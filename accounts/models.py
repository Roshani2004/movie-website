# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets
import hashlib


class User(AbstractUser):
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class OTPToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_tokens')
    otp_hash = models.CharField(max_length=64)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @staticmethod
    def generate_otp():
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

    @staticmethod
    def hash_otp(code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def verify(self, code: str) -> bool:
        if not self.is_valid() or self.attempts >= self.max_attempts:
            return False
        if self.hash_otp(code) == self.otp_hash:
            self.is_used = True
            self.save(update_fields=['is_used'])
            return True
        self.attempts += 1
        self.save(update_fields=['attempts'])
        return False

    @classmethod
    def create_for_user(cls, user, expiry_minutes=10):
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        code = cls.generate_otp()
        token = cls.objects.create(
            user=user,
            otp_hash=cls.hash_otp(code),
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
        )
        return code, token
class PasswordResetOTP(models.Model):
    """OTP for password reset — expires after 10 minutes, single use."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_otps')
    otp_hash = models.CharField(max_length=64)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @staticmethod
    def generate_otp():
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

    @staticmethod
    def hash_otp(code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def verify(self, code: str) -> bool:
        if not self.is_valid() or self.attempts >= self.max_attempts:
            return False
        if self.hash_otp(code) == self.otp_hash:
            self.is_used = True
            self.save(update_fields=['is_used'])
            return True
        self.attempts += 1
        self.save(update_fields=['attempts'])
        return False

    @classmethod
    def create_for_user(cls, user, expiry_minutes=10):
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        code = cls.generate_otp()
        token = cls.objects.create(
            user=user,
            otp_hash=cls.hash_otp(code),
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
        )
        return code, token