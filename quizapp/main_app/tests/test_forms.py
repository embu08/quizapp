from main_app.forms import *
from django.test import TestCase


class CreateTestTestCase(TestCase):

    def tests_CreateTestForm_form_is_valid(self):
        category = Categories.objects.create(name='category')
        form = CreateTestForm(
            data={
                'name': 'cat',
                'category': category,
                'description': 'cats',
                'is_public': False,
                'show_results': False,
                'access_by_link': False,
            }
        )
        if form.errors:
            for e in form.errors:
                print('*' * 20, e)
        self.assertTrue(form.is_valid())

    def tests_CreateTestForm_form_is_not_valid(self):
        form = CreateTestForm(
            data={
                'name': 'ca',
                'description': '*' * 1001
            }
        )
        form2 = UpdateTestForm(
            data={
                'name': '*' * 256,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)

        self.assertFalse(form2.is_valid())
        self.assertEqual(len(form2.errors), 1)


class UpdateTestTestCase(TestCase):
    def tests_UpdateTestForm_form_is_valid(self):
        category = Categories.objects.create(name='category')
        form = UpdateTestForm(
            data={
                'name': 'cat',
                'category': category,
                'description': 'cats',
                'is_public': False,
                'show_results': False,
                'access_by_link': False,
            }
        )
        if form.errors:
            for e in form.errors:
                print('*' * 20, e)
        self.assertTrue(form.is_valid())

    def tests_UpdateTestForm_form_is_not_valid(self):
        form = UpdateTestForm(
            data={
                'name': 'ca',
                'description': '*' * 1001
            }
        )
        form2 = UpdateTestForm(
            data={
                'name': '*' * 256,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)

        self.assertFalse(form2.is_valid())
        self.assertEqual(len(form2.errors), 1)
