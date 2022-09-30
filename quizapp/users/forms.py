from django import forms
from .models import CustomUser

from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Username',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='First name', widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 required=False)
    last_name = forms.CharField(label='Last name', widget=forms.TextInput(attrs={'class': 'form-control'}),
                                required=False)
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm password ',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Username',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    remember_me = forms.BooleanField(required=False,
                                     widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class UpdateUserForm(UserChangeForm):
    first_name = forms.CharField(max_length=255, widget=forms.TextInput({'class': 'form-control'}))
    last_name = forms.CharField(max_length=255, widget=forms.TextInput({'class': 'form-control'}))

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('first_name', 'last_name')
