from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView

from users.forms import LoginUserForm, RegisterUserForm, UpdateUserForm


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('tests:home')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('tests:home')


class UpdateUserView(UpdateView):
    form_class = UpdateUserForm
    template_name = 'users/update_user.html'

    def get_success_url(self):
        return reverse_lazy('tests:home')


class MyProfileView(DetailView):
    model = User
    template_name = 'users/user_detail.html'


def logout_user(request):
    logout(request)
    return redirect('users:login')
