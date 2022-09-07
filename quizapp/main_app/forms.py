from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms


class RegisterUserForm(UserCreationForm):
    pass


class LoginUserForm(AuthenticationForm):
    pass


class ContactForm(forms.Form):
    pass


class CreateTestForm(forms.Form):
    pass


class PassTestForm(forms.Form):
    pass
