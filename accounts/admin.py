# accounts/admin.py
from django.contrib import admin
from .models import User, OTPToken

admin.site.register(User)
admin.site.register(OTPToken)