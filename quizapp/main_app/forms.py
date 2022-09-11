from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import *


class ContactForm(forms.Form):
    name = forms.CharField(label='Username',
                           widget=forms.TextInput(attrs={'class': ''}))
    email = forms.EmailField(label='Email',
                             widget=forms.TextInput(attrs={'class': ''}))
    content = forms.CharField(label='Content',
                              widget=forms.TextInput(attrs={'class': ''}))
    # captcha


class CreateTestForm(forms.ModelForm):
    name = forms.CharField(label='Test title',
                           widget=forms.TextInput(attrs={'class': ''}))

    class Meta:
        model = Test
        fields = ['name', 'owner', 'category']

#
# class CreateQuestionForm(forms.Form):
#     question = forms.CharField(label='Question',
#                                widget=forms.TextInput(attrs={'class': ''}))
#     correct_answer = forms.CharField(label='Correct answer',
#                                      widget=forms.TextInput(attrs={'class': ''}))
#
#     # class Meta:
#     #     model = Questions
#     #     fields = ['question', 'correct_answer']
