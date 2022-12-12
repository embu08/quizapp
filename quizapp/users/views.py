from .tokens import account_activation_token
from django.contrib import messages, auth
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, UpdateView, TemplateView
from main_app.models import Test, PassedTests
from users.forms import LoginUserForm, RegisterUserForm, UpdateUserForm, PasswordResetFormCustom, SetPasswordFormCustom
from users.models import CustomUser


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        activate_email(self.request, self.request.user, form.cleaned_data.get('email'))
        return redirect('tests:home')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            msg = mark_safe(
                f'You are already sign up. If you want to register a new account, please <a class="text-dark" href="/users/logout/">log out</a> first.')
            messages.add_message(
                self.request,
                messages.ERROR,
                msg
            )
            return redirect('tests:home')
        return super().get(request, *args, **kwargs)


def activate_email(request, user, to_email):
    return_in_the_end = False
    if type(user) == str:
        # it can be called from template, that passes user as string, not as CustomUser object
        user = CustomUser.objects.get(pk=request.user.pk)
        return_in_the_end = True
    mail_subject = 'Activate your user account.'
    message = render_to_string('users/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.add_message(request, messages.SUCCESS,
                             mark_safe(f'Dear <b>{user}</b>, we sent activation link to your '
                                       f'email <b>{email}</b>, please click on it to confirm and complete registration.'))
    else:
        messages.add_message(request, messages.ERROR,
                             f'Problem sending email to {to_email}, check if you type it correctly!')
    if return_in_the_end:
        return redirect('tests:home')


def login_user(request):
    if request.user.is_authenticated:
        msg = mark_safe(
            f'You are already logged in. If you want to log in to another account, please <a class="text-dark" href="/users/logout/">log out</a> first.')
        messages.add_message(
            request,
            messages.ERROR,
            msg
        )
        return redirect('tests:home')

    form = LoginUserForm
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = auth.authenticate(username=CustomUser.objects.get(email=username), password=password)
        except:
            user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            if request.POST.get('remember_me') == 'False' or not request.POST.get('remember_me'):
                request.session.set_expiry(0)
                request.session.modified = True
            messages.add_message(request, messages.SUCCESS,
                                 f'You have successfully logged in.')
            return redirect('tests:home')
        else:
            messages.add_message(request, messages.ERROR,
                                 f'Please enter a correct username and password. '
                                 f'Note that both fields may be case-sensitive.')
    context = {'form': form}
    return render(request, 'users/login.html', context=context)


def logout_user(request):
    logout(request)
    return redirect('users:login')


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/user_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_data'] = CustomUser.objects.get(pk=self.request.user.pk)
        context['created_tests'] = Test.objects.filter(owner=self.request.user.pk).order_by('-time_update')[
                                   :6].select_related('category')
        context['passed_tests'] = PassedTests.objects.prefetch_related(
            Prefetch('test', queryset=Test.objects.all().select_related('owner'))).filter(
            user=self.request.user.pk).order_by('-data_passed')[:6]
        return context


class UpdateUserView(LoginRequiredMixin, UpdateView):
    template_name = 'users/update_user.html'
    form_class = UpdateUserForm

    def get_success_url(self):
        return reverse_lazy('users:my_profile')

    def get_object(self, queryset=None):
        return self.request.user


class ChangePasswordView(PasswordChangeView):
    template_name = 'users/password_change.html'

    def get_success_url(self):
        return reverse_lazy('users:my_profile')

    def form_valid(self, form):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Password has been successfully changed!'
        )
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.email_confirmed = True
        user.save()
        messages.add_message(request, messages.SUCCESS,
                             f'Your email was successfully confirmed!')
    else:
        messages.add_message(request, messages.ERROR,
                             f'Activation link is invalid!')

    return redirect('tests:home')


class PasswordResetViewCustom(PasswordResetView):
    email_template_name = 'users/password_reset_email.html'
    template_name = 'users/password_reset.html'
    form_class = PasswordResetFormCustom

    def get_success_url(self):
        return reverse_lazy('users:password_reset_done')


class PasswordResetConfirmViewCustom(PasswordResetConfirmView):
    form_class = SetPasswordFormCustom
    template_name = 'users/password_reset_confirm.html'

    def form_valid(self, form):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Your password has been set. You may go ahead and log in now.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('users:login')
