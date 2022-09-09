from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import validate_email


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username', 'email')
