from django.http import HttpResponse
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.generic import CreateView

from .forms import *
from .models import *


def home(request):
    return HttpResponse('Hello world')


# def create_test_view(request):
#     question_formset = modelformset_factory(CreateQuestionForm, fields=('question', 'correct_answer'))
#     answer_formset = modelformset_factory(CreateAnswerForm, fields=('answer_1', 'answer_2', 'answer_3'))
#     if request.method == 'POST':
#         question_form = question_formset(request.POST)
#         answer_form = answer_formset(request.POST)
#         test_form = CreateTestForm(request.POST)
#         if test_form.is_valid() and question_form.is_valid() and answer_form.is_valid():
#             print(test_form.cleaned_data)
#         print(question_form.cleaned_data)
#         print(answer_form.cleaned_data)
#
#     test_form = CreateTestForm()
#     question_form = question_formset()
#     answer_form = answer_formset()
#     context = {'test_form': test_form, 'question_form': question_form, 'answer_form': answer_form, }
#     return render(request, "create_test.html", context)

#
def create_test_view(request):
    question_formset = modelformset_factory(Questions,
                                            fields=('question', 'correct_answer', 'answer_1', 'answer_2', 'answer_3'))
    if request.method == 'POST':
        # question_form = question_formset(request.POST)
        test_form = CreateTestForm(request.POST)
        if test_form.is_valid():
            print(test_form.cleaned_data)
            test = test_form.save(commit=False)
            test.owner = request.user
            test.category = Categories.objects.first()

            # print(question_form.cleaned_data)
        else:
            print('не прошло')

    test_form = CreateTestForm()
    question_form = question_formset()
    context = {'test_form': test_form, 'question_form': question_form}
    return render(request, "create_test.html", context)
