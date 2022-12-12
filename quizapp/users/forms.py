from .models import CustomUser
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, \
    SetPasswordForm


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Username',
                               widget=forms.TextInput(attrs={'class': 'form-control'}),
                               min_length=3, max_length=150)
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'class': 'form-control'}),
                             min_length=3, max_length=150)
    first_name = forms.CharField(label='First name', widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 required=False, max_length=150)
    last_name = forms.CharField(label='Last name', widget=forms.TextInput(attrs={'class': 'form-control'}),
                                required=False, max_length=150)
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm password',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Username',
                               widget=forms.TextInput(attrs={'class': 'form-control'}),
                               min_length=3, max_length=150)
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    remember_me = forms.BooleanField(required=False,
                                     widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class UpdateUserForm(UserChangeForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput({'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput({'class': 'form-control'}))

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('first_name', 'last_name')


class PasswordResetFormCustom(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=150,
        widget=forms.EmailInput(attrs={"autocomplete": "email", 'class': 'form-control'}),
    )


class SetPasswordFormCustom(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'class': 'form-control'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="Confirm the new password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'class': 'form-control'}),
    )
