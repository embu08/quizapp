from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.generic import CreateView, ListView

from .forms import *
from .models import *


def home(request):
    return HttpResponse('Hello world')


class ShowAllTests(ListView):
    model = Test
    template_name = 'show_tests.html'
    context_object_name = 'tests'
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Available tests'
        return context

    def get_queryset(self):
        return Test.objects.all()


#
@login_required
def create_test_view(request):
    queryset = Questions.objects.all()
    QuestionsFormSet = modelformset_factory(Questions,
                                            form=CreateQuestionForm, extra=1)
    if request.method == 'POST':
        question_form = QuestionsFormSet(request.POST, queryset=queryset)
        test_form = CreateTestForm(request.POST)
        if test_form.is_valid() and question_form.is_valid():
            print('прошло')
            # print(test_form.cleaned_data)
            # print(question_form.cleaned_data)
            test = test_form.save(commit=False)
            questions = question_form.save(commit=False)
            test.owner = request.user
            if not test.category:
                test.category = Categories.objects.get(name='No category')
            questions[0].test = test
            print('test: ', test)
            print('questions.test: ', questions[0].test)
            print('questions: ', questions)
            test.save()
            questions[0].save()
        else:
            print('не прошло')

    test_form = CreateTestForm()
    question_form = QuestionsFormSet(queryset=queryset)
    context = {'test_form': test_form, 'question_form': question_form}
    return render(request, "create_test.html", context)
