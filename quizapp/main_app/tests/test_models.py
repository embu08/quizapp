from django.template.backends import django
from django.test import TestCase
from ..models import *
from django.contrib.auth import get_user_model


class CategoriesModelTest(TestCase):

    def test_create_category(self):
        cat = Categories.objects.create(name='Test')
        self.assertEqual(cat.name, 'Test')
        self.assertEqual(len(Categories.objects.all()), 1)

    def test_delete_category(self):
        Categories.objects.create(name='Test')
        Categories.objects.filter(name='Test').delete()
        self.assertEqual(len(Categories.objects.all()), 0)


class TestTest(TestCase):
    def test_create_test(self):
        cat = Categories.objects.create(name='Test')
        User = get_user_model()
        user = User.objects.create_user(username='user123', password='foo')
        test_1 = Test.objects.create(name='My test', owner=user, category=cat)
        self.assertEqual(test_1.name, 'My test')
        self.assertEqual(test_1.owner.username, 'user123')
        self.assertEqual(test_1.category.name, 'Test')
        test_2 = Test.objects.create(name='My test2', category=cat)
        self.assertEqual(test_2.owner, None)
