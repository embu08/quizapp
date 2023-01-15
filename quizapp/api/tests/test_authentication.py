from django.test import TestCase
from django.test.client import Client
from django.contrib import auth
from django.urls import reverse

from users.models import CustomUser


class SessionAuthenticationAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )

    def test_login_works(self):
        resp = self.client.get('/api/v1/session_auth/login/')
        cookies = resp.cookies['csrftoken']
        csrftoken = cookies.coded_value

        u = auth.get_user(self.client)
        self.assertFalse(u.is_authenticated)
        data_for_resp2 = {
            'X-CSRFToken': csrftoken,
            'username': 'user',
            'password': 'testpassword1!'
        }
        resp2 = self.client.post('/api/v1/session_auth/login/', data=data_for_resp2)
        self.assertEqual(302, resp2.status_code)
        u = auth.get_user(self.client)
        self.assertTrue(u.is_authenticated)

    def test_login_with_wrong_data_doesnt_work(self):
        resp = self.client.get('/api/v1/session_auth/login/')
        cookies = resp.cookies['csrftoken']
        csrftoken = cookies.coded_value

        u = auth.get_user(self.client)
        self.assertFalse(u.is_authenticated)
        data_for_resp2 = {
            'X-CSRFToken': csrftoken,
            'username': 'user',
            'password': 'wrong_password'
        }
        resp2 = self.client.post('/api/v1/session_auth/login/', data=data_for_resp2)
        self.assertEqual(200, resp2.status_code)
        error_message = resp2.context_data['form'].error_messages['invalid_login']
        self.assertTrue(
            'Please enter a correct %(username)s and password. Note that both fields may be case-sensitive.' == error_message)
        u = auth.get_user(self.client)
        self.assertFalse(u.is_authenticated)


class TokenAuthorizationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )

    def test_token_auth_works(self):
        user_data = {
            'username': 'user',
            'password': 'testpassword1!'
        }
        resp = self.client.post('/api/v1/auth/token/login/', data=user_data)
        self.assertEqual(200, resp.status_code)
        auth_token = f'Token {resp.data["auth_token"]}'

        resp2 = self.client.get(reverse('api:passed'))
        self.assertEqual(401, resp2.status_code)

        headers = {
            'HTTP_AUTHORIZATION': auth_token
        }

        resp3 = self.client.get(reverse('api:passed'), **headers)
        self.assertEqual(200, resp3.status_code)

    def test_token_auth_with_wrong_token_doesnt_work(self):
        user_data = {
            'username': 'user',
            'password': 'testpassword1!'
        }
        resp = self.client.post('/api/v1/auth/token/login/', data=user_data)
        self.assertEqual(200, resp.status_code)
        auth_token = f'Token {resp.data["auth_token"]}'

        resp2 = self.client.get(reverse('api:passed'))
        self.assertEqual(401, resp2.status_code)

        headers = {
            'HTTP_AUTHORIZATION': auth_token + 'aaa'
        }

        resp3 = self.client.get(reverse('api:passed'), **headers)
        self.assertEqual(401, resp3.status_code)
        self.assertEqual('Invalid token.', resp3.data['detail'])

    def test_token_auth_with_wrong_user_data_doesnt_work(self):
        user_data = {
            'username': 'user',
            'password': 'testpassword1!' + 'aaa'
        }
        resp = self.client.post('/api/v1/auth/token/login/', data=user_data)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('Unable to log in with provided credentials.', resp.data['non_field_errors'][0])
        self.assertEqual(1, len(resp.data['non_field_errors']))
