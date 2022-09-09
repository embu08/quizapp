from django.contrib.auth import get_user_model
from django.test import TestCase


class UserManagerTest(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username='user123', password='foo')
        self.assertEqual(user.username, 'user123')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(username='')
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', password='foo')

    def test_create_superuser(self):
        User = get_user_model()
        user = User.objects.create_superuser(username='user321', password='foo')
        self.assertEqual(user.username, 'user321')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username='user321', password='foo', is_superuser=False)
