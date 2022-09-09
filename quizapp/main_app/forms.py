from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator


class RegisterUserForm():
    pass



class LoginUserForm(AuthenticationForm):
    pass


class ContactForm(forms.Form):
    pass


class CreateTestForm(forms.Form):
    pass


class PassTestForm(forms.Form):
    pass
