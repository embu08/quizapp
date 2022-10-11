from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, ListView, TemplateView, DetailView, FormView, UpdateView
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin
from random import shuffle

from .forms import *
from .models import *
from users.models import CustomUser


class HomeView(TemplateView):
    template_name = 'main_app/home.html'


class ShowAllTestsListVIew(ListView):
    model = Test
    template_name = 'main_app/show_tests_list.html'
    context_object_name = 'tests'
    paginate_by = 12

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = {}
        for t in context['object_list']:
            questions[t.pk] = Questions.objects.filter(test=t.pk).count()
        context['questions'] = questions
        return context

    def get_queryset(self):
        tests_with_questions = []
        for q in Questions.objects.values_list('test').distinct():
            tests_with_questions.append(*q)
        return Test.objects.filter(pk__in=tests_with_questions, is_public=True).order_by('-time_update')


class ShowMyTestsListVIew(LoginRequiredMixin, ListView):
    model = Test
    template_name = 'main_app/show_my_tests_list.html'
    context_object_name = 'tests'
    paginate_by = 12
    ordering = ['-time_create', ]

    def get_queryset(self):
        return Test.objects.filter(owner=self.request.user).order_by('-time_update')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = {}
        for t in context['object_list']:
            questions[t.pk] = Questions.objects.filter(test=t.pk).count()
        context['questions'] = questions
        return context


class AddTestView(LoginRequiredMixin, CreateView):
    model = Test
    template_name = 'main_app/add_test.html'
    form_class = CreateTestForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'The test has been added.'
        )
        return super().form_valid(form)


class UpdateTestView(LoginRequiredMixin, UpdateView):
    model = Test
    form_class = UpdateTestForm
    template_name = 'main_app/test_edit.html'
    context_object_name = 'update_fields'

    def form_valid(self, form):
        form.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Changes were saved.'
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('tests:test_detail', kwargs={'pk': self.object.pk})

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != self.request.user:
            messages.add_message(
                self.request,
                messages.ERROR,
                'You are not owner of the test.'
            )
            return redirect('tests:home')
        return super().get(request, *args, **kwargs)


class TestDetailView(LoginRequiredMixin, DetailView):
    model = Test
    template_name = 'main_app/test_detail.html'
    context_object_name = 'details'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != self.request.user:
            messages.add_message(
                self.request,
                messages.ERROR,
                'You are not owner of the test.'
            )
            return redirect('tests:home')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class TestQuestionsEditView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Questions
    template_name = 'main_app/test_questions_edit.html'
    context_object_name = 'test_questions'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Test.objects.all())
        if self.object.owner != self.request.user:
            messages.add_message(
                self.request,
                messages.ERROR,
                'You are not owner of the test.'
            )
            return redirect('tests:home')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Test.objects.all())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return TestQuestionsFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Changes were saved.'
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.ERROR,
            'Something wrong with questions.'
        )
        for n, v in enumerate(form.errors):
            msg = '<ul class="errorlist nonfield"><li>This question is already in this test.</li></ul>'
            if v:
                if v.get('__all__', None):
                    form.errors[n]['__all__'] = mark_safe(msg)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('tests:test_detail', kwargs={'pk': self.object.pk})


def pass_test(request, pk=None):
    test = Test.objects.get(pk=pk)
    if not test.is_public and not test.access_by_link and request.user != test.owner and not request.user.is_staff:
        messages.add_message(
            request,
            messages.ERROR,
            'The test does not exist or it is not accessible.'
        )
        return redirect('tests:home')
    questions = Questions.objects.filter(test=pk)

    # for result
    if request.method == 'POST':
        correct, total_questions = 0, len(questions)
        result, max_result = 0, 0
        cor_ans, ans = [], []
        for q in questions:
            cor_ans.append(q.correct_answer)
            ans.append(request.POST.get(q.question))
            max_result += q.value
            if q.correct_answer == request.POST.get(q.question):
                correct += 1
                result += q.value
        try:
            PassedTests.objects.create(test=Test.objects.get(pk=pk), user=CustomUser.objects.get(pk=request.user.pk),
                                       grade=int(result), max_grade=int(max_result))
        except Exception as e:
            print(f'adding PassedTest to BD error: {e}')
        context = {
            'result': result,
            'max_result': max_result,
            'time': request.POST.get('timer'),
            'correct': correct,
            'total': total_questions,
            'cor_ans': cor_ans,
            'ans': ans,
            'questions': questions,
            'show_results': Test.objects.get(id=pk).show_results
        }
        return render(request, 'main_app/result.html', context)

    # for test
    answers = {}
    len_a = []
    for q in questions:
        a = []
        for i in [q.correct_answer, q.answer_1, q.answer_2, q.answer_3]:
            if i:
                a.append(i)
        shuffle(a)
        len_a.append(len(a))
        answers[q.question] = a

    context = {'questions': questions, 'answers': answers, 'len_a': len_a,
               'show_results': Test.objects.get(id=pk).show_results}
    return render(request, 'main_app/pass_test.html', context)


class PassedTestView(LoginRequiredMixin, ListView):
    model = PassedTests
    template_name = 'main_app/passed_tests.html'
    context_object_name = 'passed_tests'
    paginate_by = 20

    def get_queryset(self):
        return PassedTests.objects.filter(user=self.request.user).order_by('-data_passed')
