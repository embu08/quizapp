from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import *
from django.forms.models import inlineformset_factory
from . import InlineFormSet


class ContactForm(forms.Form):
    name = forms.CharField(label='Username',
                           widget=forms.TextInput(attrs={'class': ''}))
    email = forms.EmailField(label='Email',
                             widget=forms.TextInput(attrs={'class': ''}))
    content = forms.CharField(label='Content',
                              widget=forms.TextInput(attrs={'class': ''}))
    # captcha


class CreateTestForm(forms.ModelForm):
    name = forms.CharField(label='Test name',
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'enter the test name here...'}))
    description = forms.CharField(label='Description',
                                  widget=forms.Textarea(attrs={'rows': '3', 'class': 'form-control',
                                                               'placeholder': 'enter the test description...'}))

    class Meta:
        model = Test
        fields = ['name', 'category', 'description', 'is_public']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-select'
        self.fields['category'].empty_label = 'Not selected'
        self.fields['is_public'].widget.attrs['class'] = 'form-check-input'


TestQuestionsFormset = inlineformset_factory(Test,
                                             Questions,
                                             fields=('question', 'correct_answer', 'answer_1',
                                                     'answer_2', 'answer_3'),
                                             extra=5,
                                             max_num=5,
                                             can_delete_extra=False,
                                             formset=InlineFormSet)
