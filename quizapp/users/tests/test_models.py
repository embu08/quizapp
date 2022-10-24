from users.models import CustomUser
from django.test import TestCase


class CustomUserTestCase(TestCase):

    def test_user_creation(self):
        u = CustomUser.objects.create_user(username='user',
                                           first_name='asdasd',
                                           last_name='asdasd',
                                           email='test@test.com',
                                           email_confirmed=True)
        self.assertIsInstance(u, CustomUser)
        self.assertFalse(u.is_staff)
        self.assertFalse(u.is_superuser)
        self.assertEqual(u.email, 'test@test.com')

    def test_superuser_creation(self):
        u = CustomUser.objects.create_superuser(username='user',
                                                first_name='asdasd',
                                                last_name='asdasd',
                                                email='test@test.com',
                                                email_confirmed=True)
        self.assertIsInstance(u, CustomUser)
        self.assertTrue(u.is_staff)
        self.assertTrue(u.is_superuser)
        self.assertEqual(u.email, 'test@test.com')
