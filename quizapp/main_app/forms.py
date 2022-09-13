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
    name = forms.CharField(label='',
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'Title...'}))
    description = forms.CharField(label='',
                                  widget=forms.Textarea(attrs={'rows': '1', 'class': 'form-control',
                                                               'placeholder': 'Description...'}))
    category = forms.SelectMultiple()

    class Meta:
        model = Test
        fields = ['name', 'owner', 'category', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = 'form-select'


class CreateQuestionForm(forms.ModelForm):
    question = forms.CharField(label='Question',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    correct_answer = forms.CharField(label='Correct answer',
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_1 = forms.CharField(label='Wrong answer 1',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_2 = forms.CharField(label='Wrong answer 2',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_3 = forms.CharField(label='Wrong answer 3',
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Questions
        fields = ['question', 'correct_answer', 'answer_1', 'answer_2', 'answer_3', 'test']
