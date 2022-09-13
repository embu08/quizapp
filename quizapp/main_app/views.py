from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.forms import modelformset_factory
from django.views.generic import CreateView, ListView, TemplateView

from .forms import *
from .models import *


class HomeView(TemplateView):
    template_name = 'home.html'
    extra_context = {'title': 'Homepage'}


class ShowAllTestsListVIew(ListView):
    model = Test
    template_name = 'show_tests_list.html'
    context_object_name = 'tests'
    extra_context = {'title': 'Available tests'}
    paginate_by = 12


def edit_test(request, pk):
    return HttpResponse(f'updating post {pk}')


def pass_test(request, pk):
    return HttpResponse(f'passing tess {pk}')


@login_required
def create_test(request):
    pass
