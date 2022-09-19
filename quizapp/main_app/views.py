from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, DetailView, FormView, UpdateView
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin

from .forms import *
from .models import *


class HomeView(TemplateView):
    template_name = 'home.html'


class ShowAllTestsListVIew(ListView):
    model = Test
    template_name = 'show_tests_list.html'
    context_object_name = 'tests'
    paginate_by = 12
    ordering = ['-time_create', ]


class ShowMyTestsListVIew(ListView):
    model = Test
    template_name = 'show_my_tests_list.html'
    context_object_name = 'tests'
    paginate_by = 12
    ordering = ['-time_create', ]

    def get_queryset(self):
        return Test.objects.filter(owner=self.request.user).all().order_by('-time_create')


class AddTestView(LoginRequiredMixin, CreateView):
    model = Test
    template_name = 'add_test.html'
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


class UpdateTestView(UpdateView):
    model = Test
    form_class = UpdateTestForm
    template_name = 'test_edit.html'
    context_object_name = 'update_fields'

    def form_valid(self, form):
        form.save()
        print('cat', '*' * 100)
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Changes were saved.'
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('tests:test_detail', kwargs={'pk': self.object.pk})


class TestDetailView(DetailView):
    model = Test
    template_name = 'test_detail.html'
    context_object_name = 'details'


class TestQuestionsEditView(SingleObjectMixin, FormView):
    model = Questions
    template_name = 'test_questions_edit.html'
    context_object_name = 'test_questions'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Test.objects.all())
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

    def get_success_url(self):
        return reverse('tests:test_detail', kwargs={'pk': self.object.pk})


def pass_test(request, pk):
    return HttpResponse(f'passing tess {pk}')
