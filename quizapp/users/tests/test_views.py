from main_app.models import Categories
from quizapp import settings
from users.models import CustomUser
from django.test import TestCase
from users.views import *
from django.test.client import Client
from django.contrib import auth
from django.core import mail
from django.contrib.messages import get_messages

password = 'testpassword1!'


class RegisterUserTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.u = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password=password
        )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/users/register/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('users:sign_up'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.logout()
        resp = self.client.get(reverse('users:sign_up'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'users/register.html')

    def test_login_user_redirected_to_home(self):
        self.client.login(username='user', password=password)
        resp = self.client.get('/users/register/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('tests:home'))

    def test_valid_form_logs_user_in_and_redirects_to_home(self):
        data = {
            'username': 'user1',
            'email': 'user1@test.com',
            'first_name': 'User',
            'last_name': 'One',
            'password1': password,
            'password2': password
        }
        resp = self.client.post(reverse('users:sign_up'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('tests:home'))
        u = auth.get_user(self.client)
        self.assertTrue(u.is_authenticated)
        self.assertEqual(u.username, 'user1')
        self.assertFalse(u.email_confirmed)

    def test_activate_email_sends_email_and_verification_link_is_correct(self):
        '''
        this also tests users.views.activate function
        '''
        data = {
            'username': 'user1',
            'email': 'user1@test.com',
            'first_name': 'User',
            'last_name': 'One',
            'password1': password,
            'password2': password
        }
        self.client.post(reverse('users:sign_up'), data)
        self.assertEqual(len(mail.outbox), 1)
        activation_link = ''
        for line in mail.outbox[0].body.splitlines():
            if 'http' in line:
                activation_link = line
        resp2 = self.client.post(activation_link)
        self.assertEqual(resp2.status_code, 302)
        self.assertRedirects(resp2, reverse('tests:home'))
        u = auth.get_user(self.client)
        self.assertTrue(u.is_authenticated)

    def test_wrong_activate_link_cause_error(self):
        data = {
            'username': 'user1',
            'email': 'user1@test.com',
            'first_name': 'User',
            'last_name': 'One',
            'password1': password,
            'password2': password
        }
        self.client.post(reverse('users:sign_up'), data)
        self.assertEqual(len(mail.outbox), 1)
        activation_link = ''
        for line in mail.outbox[0].body.splitlines():
            if 'http' in line:
                activation_link = line
        resp = self.client.post(activation_link + 'aaaaa')
        msg = list(get_messages(resp.wsgi_request))
        self.assertEqual(str(msg[1]), 'Activation link is invalid!')


class LoginUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password=password
        )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/users/login/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('users:login'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.logout()
        resp = self.client.get(reverse('users:login'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'users/login.html')

    def test_logged_in_user_redirected_to_home(self):
        self.client.login(username='user', password=password)
        resp = self.client.get(reverse('users:login'))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('tests:home'))

    def test_valid_data_can_login_and_redirects_to_home(self):
        data = {
            'username': 'user',
            'password': password,
            'remember_me': True
        }
        resp = self.client.post(reverse('users:login'), data)
        u = auth.get_user(self.client)
        self.assertTrue(u.is_authenticated)
        self.assertEqual('user', u.username)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('tests:home'))

    def test_user_can_login_by_email(self):
        data = {
            'username': 'user@test.com',
            'password': password,
            'remember_me': True
        }
        resp = self.client.post(reverse('users:login'), data)
        u = auth.get_user(self.client)
        self.assertTrue(u.is_authenticated)
        self.assertEqual('user', u.username)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('tests:home'))

    def test_invalid_data_cannot_login(self):
        data = {
            'username': 'user1',
            'password': password,
            'remember_me': True
        }
        resp = self.client.post(reverse('users:login'), data)
        u = auth.get_user(self.client)
        self.assertTrue(u.is_anonymous)
        self.assertEqual(resp.status_code, 200)

    def test_remember_me_button_not_checked(self):
        data = {
            'username': 'user',
            'password': password,
        }
        self.client.post(reverse('users:login'), data)
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_remember_me_button_checked(self):
        data = {
            'username': 'user',
            'password': password,
            'remember_me': True
        }
        self.client.post(reverse('users:login'), data)
        self.assertFalse(self.client.session.get_expire_at_browser_close())


class LogOutTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password=password
        )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/users/logout/')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('users:login'))

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('users:logout'))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('users:login'))

    def test_logout_works(self):
        self.client.login(username='user', password=password)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        resp = self.client.post(reverse('users:logout'))

        user = auth.get_user(self.client)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('users:login'))
        self.assertFalse(user.is_authenticated)
        self.assertTrue(user.is_anonymous)


class MyProfileViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        Categories.objects.create(name='cat')
        CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        for t in range(10):
            Test.objects.create(
                name='test' + str(t),
                owner=CustomUser.objects.first(),
                description='cat',
                category=Categories.objects.first())
        for t in range(10):
            PassedTests.objects.create(test=Test.objects.get(name='test0'),
                                       user=CustomUser.objects.first(),
                                       grade=51.42,
                                       score=4,
                                       max_score=10)

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.get(username='user')

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get('/users/my_profile/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get(reverse('users:my_profile'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get(reverse('users:my_profile'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'users/user_detail.html')

    def test_anonymous_user_doesnt_have_access_to_my_profile_page(self):
        resp = self.client.get(reverse('users:my_profile'))
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/users/login/?next=' + reverse('users:my_profile'))

    def test_template_gets_only_last_6_created_and_passed_tests(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get(reverse('users:my_profile'))
        self.assertTrue(len(resp.context['created_tests']) <= 6)
        self.assertTrue(len(resp.context['passed_tests']) <= 6)
        self.assertEqual(Test.objects.filter(owner=self.user).last(), resp.context['created_tests'][0])
        self.assertEqual(PassedTests.objects.filter(user=self.user).last(), resp.context['passed_tests'][0])


class UpdateUserViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get('/users/my_profile/update/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get(reverse('users:my_profile_update'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get(reverse('users:my_profile_update'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'users/update_user.html')

    def test_anonymous_user_doesnt_have_access_to_my_profile_update_page(self):
        resp = self.client.get(reverse('users:my_profile_update'))
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/users/login/?next=' + reverse('users:my_profile_update'))

    def test_updated_user_data_saves_correctly(self):
        self.client.login(username='user', password='testpassword1!')
        self.assertEqual(None, CustomUser.objects.get(username='user').first_name)
        self.assertEqual(None, CustomUser.objects.get(username='user').last_name)
        data = {
            'first_name': 'User',
            'last_name': 'Test',
        }
        resp = self.client.post(reverse('users:my_profile_update'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('users:my_profile'))
        self.assertEqual('User', CustomUser.objects.get(username='user').first_name)
        self.assertEqual('Test', CustomUser.objects.get(username='user').last_name)


class ChangePasswordViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get('/users/my_profile/password_change/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get(reverse('users:password_change'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get(reverse('users:password_change'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'users/password_change.html')

    def test_anonymous_user_doesnt_have_access_to_my_profile_password_change(self):
        resp = self.client.get(reverse('users:password_change'))
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/users/login/?next=' + reverse('users:password_change'))

    def test_after_changing_password_user_can_login_with_new_password(self):
        self.client.login(username='user', password='testpassword1!')
        data = {
            'old_password': 'testpassword1!',
            'new_password1': 'passwordtest1!',
            'new_password2': 'passwordtest1!'
        }
        resp = self.client.post(reverse('users:password_change'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('users:my_profile'))

        self.client.logout()
        self.client.login(username='user', password='passwordtest1!')
        u = auth.get_user(self.client)
        self.assertTrue(u.is_authenticated)
        self.assertEqual('user', u.username)

    def test_after_changing_password_user_cannot_login_with_old_password(self):
        self.client.login(username='user', password='testpassword1!')
        data = {
            'old_password': 'testpassword1!',
            'new_password1': 'passwordtest1!',
            'new_password2': 'passwordtest1!'
        }
        resp = self.client.post(reverse('users:password_change'), data)
        self.client.logout()
        self.client.login(username='user', password='testpassword1!')
        self.assertFalse(auth.get_user(self.client).is_authenticated)
        self.assertTrue(auth.get_user(self.client).is_anonymous)


class PasswordResetViewCustomTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get('/users/password_reset/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get(reverse('users:password_reset'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user', password='testpassword1!')
        resp = self.client.get(reverse('users:password_reset'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'users/password_reset.html')

    def test_anonymous_user_has_access_to_password_reset(self):
        resp = self.client.get(reverse('users:password_reset'))
        self.assertEqual(resp.status_code, 200)

    def test_reset_password_sends_email_if_any_user_has_it_and_reset_link_works(self):
        data = {
            'email': 'user@test.com',
        }
        resp = self.client.post(reverse('users:password_reset'), data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertRedirects(resp, reverse('users:password_reset_done'))

        reset_link = ''
        for line in mail.outbox[0].body.splitlines():
            if line.startswith('http'):
                reset_link = line
        data2 = {
            'new_password1': 'passwordtest1!',
            'new_password2': 'passwordtest1!'
        }
        resp2 = self.client.post(reset_link)
        reset_url = resp2.url
        resp3 = self.client.post(reset_url, data2)
        self.assertEqual(resp3.status_code, 302)
        self.assertRedirects(resp3, reverse('users:login'))

    def test_reset_password_doesnt_sends_email_if_nobody_has_it(self):
        data = {
            'email': 'aaaaa@test.com',
        }
        resp = self.client.post(reverse('users:password_reset'), data)
        self.assertEqual(len(mail.outbox), 0)
        self.assertRedirects(resp, reverse('users:password_reset_done'))


class PasswordResetConfirmViewCustomTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.data = {
            'email': 'user@test.com',
        }

    def test_user_can_login_with_new_password(self):
        self.client.post(reverse('users:password_reset'), self.data)
        reset_link = ''
        for line in mail.outbox[0].body.splitlines():
            if line.startswith('http'):
                reset_link = line
        data2 = {
            'new_password1': 'randomPassword1',
            'new_password2': 'randomPassword1'
        }
        resp2 = self.client.post(reset_link)
        reset_url = resp2.url
        self.client.post(reset_url, data2)

        u = auth.get_user(self.client)
        self.assertFalse(u.is_authenticated)

        self.client.login(username='user', password='randomPassword1')
        u1 = auth.get_user(self.client)
        self.assertTrue(u1.is_authenticated)
        self.assertEqual('user', u1.username)

    def test_user_cannot_login_with_old_password(self):
        self.client.post(reverse('users:password_reset'), self.data)
        reset_link = ''
        for line in mail.outbox[0].body.splitlines():
            if line.startswith('http'):
                reset_link = line
        data2 = {
            'new_password1': 'randomPassword1',
            'new_password2': 'randomPassword1'
        }
        resp2 = self.client.post(reset_link)
        reset_url = resp2.url
        self.client.post(reset_url, data2)

        u = auth.get_user(self.client)
        self.assertFalse(u.is_authenticated)

        self.client.login(username='user', password='testpassword1!')
        u1 = auth.get_user(self.client)
        self.assertFalse(u1.is_authenticated)
