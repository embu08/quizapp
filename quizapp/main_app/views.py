from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, ListView, TemplateView, DetailView, FormView, UpdateView
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin
from random import shuffle
from quizapp.local_settings import EMAIL_FROM

from django.core.mail import EmailMessage

from .forms import *
from .models import *
from users.models import CustomUser
from django.db.models import Q


class HomeView(TemplateView):
    template_name = 'main_app/home.html'


class ContactsView(FormView):
    template_name = 'main_app/contacts.html'
    form_class = ContactForm
    success_url = reverse_lazy('tests:home')

    def form_valid(self, form):
        print(form.cleaned_data)
        mail_subject = f'Message from Quizapp Contact Us. Sender: {form.cleaned_data["name"]}, {form.cleaned_data["email"]}'
        message = form.cleaned_data["message"]
        email = EmailMessage(mail_subject, message, to=[EMAIL_FROM])
        if email.send():
            messages.add_message(
                self.request,
                messages.SUCCESS,
                'Your message was successfully sent. Thank you!'
            )
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                "Message wasn't sent :("
            )
        return redirect('tests:home')


class ShowAllTestsListVIew(ListView):
    model = Test
    template_name = 'main_app/show_tests_list.html'
    context_object_name = 'tests'
    paginate_by = 12
    ordering_title = {
        'time_update': 'Updated first',
        '-time_update': 'Updated last',
        'category': 'Category',
        '-category': 'Category reversed',
        'name': 'Title',
        '-name': 'Title reversed',
        'owner': 'Author',
        '-owner': 'Author reversed',
        None: 'Updated last'
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = {}
        for t in context['object_list']:
            questions[t.pk] = Questions.objects.filter(test=t.pk).count()
        context['questions'] = questions
        context['ordering'] = self.get_ordering()
        context['title_ordering'] = self.ordering_title[context['ordering']]
        context['search'] = self.request.GET.get('search', '')
        return context

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        # take all tests, that have questions, then take zero index, because previous return in tuple
        tests_with_questions = [b[0] for b in [q for q in Questions.objects.values_list('test').distinct()]]
        if search_query:
            q = Test.objects.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) | Q(owner__username__icontains=search_query),
                pk__in=tests_with_questions, is_public=True)
        else:
            q = Test.objects.filter(pk__in=tests_with_questions, is_public=True)
        ordering = self.get_ordering()
        if ordering:
            q = q.order_by(ordering)
        else:
            q = q.order_by('-time_update')
        return q

    def get_ordering(self):
        ordering = self.request.GET.get('ordering')
        return ordering


class ShowMyTestsListVIew(LoginRequiredMixin, ListView):
    model = Test
    template_name = 'main_app/show_my_tests_list.html'
    context_object_name = 'tests'
    paginate_by = 12
    ordering_title = {
        'time_update': 'Updated first',
        '-time_update': 'Updated last',
        'category': 'Category',
        '-category': 'Category reversed',
        'name': 'Title',
        '-name': 'Title reversed',
        None: 'Updated last'
    }

    def get_queryset(self):
        q = Test.objects.filter(owner=self.request.user)
        ordering = self.get_ordering()
        if ordering:
            q = q.order_by(ordering)
        else:
            q = q.order_by('-time_update')
        return q

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = {}
        for t in context['object_list']:
            questions[t.pk] = Questions.objects.filter(test=t.pk).count()
        context['questions'] = questions
        context['ordering'] = self.get_ordering()
        context['title_ordering'] = self.ordering_title[context['ordering']]
        return context

    def get_ordering(self):
        ordering = self.request.GET.get('ordering')
        return ordering


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

    def get(self, request, *args, **kwargs):
        if not request.user.email_confirmed:
            messages.add_message(
                self.request,
                messages.ERROR,
                'Please verify your email address. You cannot add tests and reset your password'
            )
            return redirect('tests:home')
        return super().get(request, *args, **kwargs)


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
    if not test.access_by_link and not test.is_public and request.user != test.owner and not request.user.is_staff:
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
        ans = []
        for q in questions:
            ans.append(request.POST.get(q.question))
            max_result += q.value
            if q.correct_answer == request.POST.get(q.question):
                correct += 1
                result += q.value
        try:
            PassedTests.objects.create(test=Test.objects.get(pk=pk), user=CustomUser.objects.get(pk=request.user.pk),
                                       grade=round(result / max_result * 100, 2), score=int(result),
                                       max_score=int(max_result))
        except Exception as e:
            pass
            print(f'adding PassedTest to BD error: {e}')
        show_results = Test.objects.get(id=pk).show_results
        if show_results:
            context = {
                'grade': round(result / max_result * 100, 2),
                'result': result,
                'max_result': max_result,
                'time': request.POST.get('timer'),
                'correct': correct,
                'total': total_questions,
                'ans': ans,
                'questions': questions,
                'show_results': show_results
            }
        else:
            context = {
                'grade': round(result / max_result * 100, 2),
                'result': result,
                'max_result': max_result,
                'time': request.POST.get('timer'),
                'correct': correct,
                'total': total_questions,
                'show_results': show_results
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
               'show_results': Test.objects.get(id=pk).show_results, 'description': Test.objects.get(id=pk).description}
    return render(request, 'main_app/pass_test.html', context)


class PassedTestView(LoginRequiredMixin, ListView):
    model = PassedTests
    template_name = 'main_app/passed_tests.html'
    context_object_name = 'passed_tests'
    paginate_by = 20
    ordering_title = {
        'data_passed': 'Passed first',
        '-data_passed': 'Passed last',
        'test': 'Test',
        '-test': 'Test reversed',
        'grade': 'Grade min to max',
        '-grade': 'Grade max to min',
        None: 'Passed last'
    }

    def get_queryset(self):
        q = PassedTests.objects.filter(user=self.request.user)
        ordering = self.get_ordering()
        if ordering:
            q = q.order_by(ordering)
        else:
            q = q.order_by('-data_passed')
        return q

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordering'] = self.get_ordering()
        context['title_ordering'] = self.ordering_title[context['ordering']]
        return context

    def get_ordering(self):
        ordering = self.request.GET.get('ordering')
        return ordering
