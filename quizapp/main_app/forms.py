from django import forms
from .models import *
from django.forms.models import inlineformset_factory
from . import InlineFormSet


class ContactForm(forms.Form):
    name = forms.CharField(label='Username',
                           widget=forms.TextInput(attrs={'class': ''}), min_length=1, max_length=255)
    email = forms.EmailField(label='Email',
                             widget=forms.TextInput(attrs={'class': ''}), min_length=1, max_length=255)
    content = forms.CharField(label='Content',
                              widget=forms.TextInput(attrs={'class': ''}), min_length=1, max_length=1000)
    # captcha


class CreateTestForm(forms.ModelForm):
    name = forms.CharField(label='Test name',
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'enter the test name here...'}),
                           min_length=3, max_length=255)
    description = forms.CharField(label='Description',
                                  widget=forms.Textarea(attrs={'rows': '3', 'class': 'form-control',
                                                               'placeholder': 'enter the test description...', }),
                                  max_length=1000,
                                  required=False)

    class Meta:
        model = Test
        fields = ['name', 'category', 'description', 'is_public', 'show_results', 'access_by_link']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-select'
        self.fields['category'].empty_label = 'Not selected'
        self.fields['is_public'].widget.attrs['class'] = 'form-check-input'
        self.fields['show_results'].widget.attrs['class'] = 'form-check-input'
        self.fields['access_by_link'].widget.attrs['class'] = 'form-check-input'


class UpdateTestForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput({'class': 'form-control'}), min_length=3, max_length=255)
    description = forms.CharField(widget=forms.Textarea({'class': 'form-control', 'rows': '3'}),
                                  required=False, max_length=1000)

    class Meta:
        model = Test
        fields = ('name', 'description', 'category', 'is_public', 'show_results', 'access_by_link')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_public'].widget.attrs['class'] = 'form-check-input'
        self.fields['show_results'].widget.attrs['class'] = 'form-check-input'
        self.fields['access_by_link'].widget.attrs['class'] = 'form-check-input'
        self.fields['category'].widget.attrs['class'] = 'form-select'


TestQuestionsFormset = inlineformset_factory(Test,
                                             Questions,
                                             fields=('question', 'correct_answer', 'answer_1',
                                                     'answer_2', 'answer_3', 'value'),
                                             extra=10,
                                             max_num=50,
                                             can_delete_extra=False,
                                             formset=InlineFormSet)
