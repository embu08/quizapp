from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DetailView

from users.forms import LoginUserForm, RegisterUserForm, UpdateUserForm
from users.models import CustomUser

from main_app.models import Test, PassedTests


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
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tests:home')

    def form_valid(self, form):
        print(self.request.session.get_session_cookie_age())
        if not form.cleaned_data['remember_me']:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super(LoginUser, self).form_valid(form)


class UpdateUserView(LoginRequiredMixin, UpdateView):
    template_name = 'users/update_user.html'
    form_class = UpdateUserForm
    model = CustomUser

    def get_success_url(self):
        return reverse_lazy('users:my_profile', kwargs={'pk': self.request.user.pk})


class MyProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/user_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['created_tests'] = Test.objects.filter(owner=self.request.user.pk).order_by('-time_update')[:6]
        context['passed_tests'] = PassedTests.objects.filter(user=self.request.user.pk).order_by('-data_passed')[:6]
        return context


def logout_user(request):
    logout(request)
    return redirect('users:login')


class ChangePasswordView(PasswordChangeView):
    template_name = 'users/password_change.html'

    def get_success_url(self):
        return reverse_lazy('users:my_profile', kwargs={'pk': self.request.user.pk})

    def form_valid(self, form):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Password has been successfully changed'
        )
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)
