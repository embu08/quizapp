from django.test import TestCase
from django.test.client import Client
from users.forms import RegisterUserForm, LoginUserForm, UpdateUserForm, PasswordResetFormCustom, SetPasswordFormCustom
from users.models import CustomUser


class RegisterUserFormTestCase(TestCase):

    def test_valid_user_registration_form(self):
        form = RegisterUserForm(
            data={
                'username': 'test_user',
                'email': 'test@test.com',
                'password1': 'testPassword1!',
                'password2': 'testPassword1!'
            }
        )
        self.assertTrue(form.is_valid())

    def test_lower_than_3_lengths_cause_errors(self):
        form = RegisterUserForm(
            data={
                'username': 't',
                'email': 't',
                'password1': 'testPassword1!',
                'password2': 'testPassword1!'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        with self.assertRaises(ValueError):
            form.save()
        self.assertFormError(form, 'username', 'Ensure this value has at least 3 characters (it has 1).')
        self.assertFormError(form, 'email',
                             ['Enter a valid email address.',
                              'Ensure this value has at least 3 characters (it has 1).'])

    def test_higher_than_150_lengths_cause_errors(self):
        form = RegisterUserForm(
            data={
                'username': '*' * 151,
                'email': 'a@test.com' * 20,
                'first_name': '*' * 151,
                'last_name': '*' * 151,
                'password1': 'testPassword1!',
                'password2': 'testPassword1!'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)
        with self.assertRaises(ValueError):
            form.save()
        self.assertFormError(form, 'username', 'Ensure this value has at most 150 characters (it has 151).')
        self.assertFormError(form, 'email',
                             ['Enter a valid email address.',
                              'Ensure this value has at most 150 characters (it has 200).'])
        self.assertFormError(form, 'first_name', 'Ensure this value has at most 150 characters (it has 151).')
        self.assertFormError(form, 'last_name', 'Ensure this value has at most 150 characters (it has 151).')

    def test_wrong_password2_cause_error(self):
        form = RegisterUserForm(
            data={
                'username': 'test_user',
                'email': 'aas@test.com',
                'password1': 'testPassword1!',
                'password2': 'testPassword1!aaa'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        with self.assertRaises(ValueError):
            form.save()
        self.assertFormError(form, 'password2', 'The two password fields didn’t match.')

    def test_to_easy_passwords_cause_error(self):
        form = RegisterUserForm(
            data={
                'username': 'test_user',
                'email': 'aas@test.com',
                'password1': 'aa',
                'password2': 'aa'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        with self.assertRaises(ValueError):
            form.save()
        self.assertFormError(form, 'password2', ['The password is too similar to the email.',
                                                 'This password is too short. It must contain at least 8 characters.',
                                                 'This password is too common.'])

    def test_form_has_correct_labels(self):
        form = RegisterUserForm(
            data={
                'username': 'test_user',
                'email': 'aas@test.com',
                'first_name': 'User',
                'last_name': 'Test',
                'password1': 'testPassword1!',
                'password2': 'testPassword1!'
            }
        )
        self.assertEqual(form['username'].label, 'Username')
        self.assertEqual(form['email'].label, 'Email')
        self.assertEqual(form['first_name'].label, 'First name')
        self.assertEqual(form['last_name'].label, 'Last name')
        self.assertEqual(form['password1'].label, 'Password')
        self.assertEqual(form['password2'].label, 'Confirm password')


class LoginUserFormTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='test_user',
            first_name='User',
            last_name='Test',
            email='test@test.com',
            password='testPassword1!'
        )

    def test_valid_user_data_can_login(self):
        form = LoginUserForm(
            data={
                'username': 'test_user',
                'password': 'testPassword1!',
                'remember_me': True
            }
        )
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.get_user(), CustomUser)
        self.assertEqual(form.get_user().username, 'test_user')

    def test_invalid_user_data_cause_error(self):
        form = LoginUserForm(
            data={
                'username': 'test_user',
                'password': 'testPassword1!_sss',
                'remember_me': True
            }
        )
        form1 = LoginUserForm(
            data={
                'username': 'test_user_sss',
                'password': 'testPassword1!',
                'remember_me': True
            }
        )
        self.assertFalse(form.is_valid())
        self.assertFalse(form1.is_valid())
        self.assertFormError(form, field=None,
                             errors='Please enter a correct username and password. Note that both fields may be case-sensitive.')
        self.assertFormError(form1, field=None,
                             errors='Please enter a correct username and password. Note that both fields may be case-sensitive.')

    def test_invalid_form_cause_error(self):
        form = LoginUserForm(
            data={
                'username': '*' * 151,
                'password': 'testPassword1!',
                'remember_me': 'cat'
            }
        )
        self.assertFormError(form, 'username', 'Ensure this value has at most 150 characters (it has 151).')
        self.assertFalse(form.is_valid())

    def test_form_has_correct_labels(self):
        form = LoginUserForm(
            data={
                'username': 'test_user',
                'password': 'testPassword1!',
                'remember_me': True
            }
        )
        self.assertEqual(form['username'].label, 'Username')
        self.assertEqual(form['password'].label, 'Password')
        self.assertEqual(form['remember_me'].label, 'Remember me')


class UpdateUserFormTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='test_user',
            first_name='User',
            last_name='Test',
            email='test@test.com',
            password='testPassword1!'
        )

    def test_valid_data_change_form(self):
        form = UpdateUserForm(
            data={
                'first_name': 'fn',
                'last_name': 'ln',
            },
            instance=self.user
        )
        form.save()
        self.assertEqual('fn', self.user.first_name)
        self.assertEqual('ln', self.user.last_name)

    def test_invalid_data_cause_error(self):
        form = UpdateUserForm(
            data={
                'first_name': '*' * 151,
                'last_name': 'a' * 151,
            },
            instance=self.user
        )
        with self.assertRaises(ValueError):
            form.save()
        self.assertEqual(2, len(form.errors))
        self.assertFormError(form, 'first_name', 'Ensure this value has at most 150 characters (it has 151).')
        self.assertFormError(form, 'last_name', 'Ensure this value has at most 150 characters (it has 151).')

    def test_form_has_correct_labels(self):
        form = UpdateUserForm(
            data={
                'first_name': 'fasdn',
                'last_name': 'lnasd',
            },
            instance=self.user
        )
        self.assertEqual(form['first_name'].label, 'First name')
        self.assertEqual(form['last_name'].label, 'Last name')


class PasswordResetFormCustomTestCase(TestCase):

    def test_valid_data_works(self):
        form = PasswordResetFormCustom(
            data={
                'email': 'test@test.com'
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_email_cause_errors(self):
        form = PasswordResetFormCustom(
            data={
                'email': 'testtest.com'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))

    def test_too_long_email_cause_error(self):
        form = PasswordResetFormCustom(
            data={
                'email': 'a' * 150 + 'tes@ttest.com'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertFormError(form, 'email', 'Ensure this value has at most 150 characters (it has 163).')

    def test_form_has_correct_labels(self):
        form = PasswordResetFormCustom(
            data={
                'email': 'test@test.com'
            }
        )
        self.assertEqual(form['email'].label, 'Email')


class SetPasswordFormCustomTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='test_user',
            first_name='User',
            last_name='Test',
            email='test@test.com',
            password='testPassword1!'
        )

    def test_valid_data_is_valid(self):
        form = SetPasswordFormCustom(
            data={
                'new_password1': 'testPassword2!',
                'new_password2': 'testPassword2!'
            },
            user=self.user
        )
        self.assertTrue(form.is_valid())

    def test_invalid_data_cause_error(self):
        form = SetPasswordFormCustom(
            data={
                'new_password1': 'testPassword2!',
                'new_password2': 'testPassword2!...'
            },
            user=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertFormError(form, 'new_password2', 'The two password fields didn’t match.')

    def test_form_has_correct_labels(self):
        form = SetPasswordFormCustom(
            data={
                'new_password1': 'testPassword1!',
                'new_password2': 'testPassword1!'
            },
            user=self.user
        )
        self.assertEqual(form['new_password1'].label, 'New password')
        self.assertEqual(form['new_password2'].label, 'Confirm the new password')
