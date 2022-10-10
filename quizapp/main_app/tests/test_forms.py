from main_app.forms import *
from django.test import TestCase


class CreateTestTestCase(TestCase):

    def tests_form_is_valid(self):
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

    def tests_form_is_not_valid(self):
        form = CreateTestForm(
            data={
                'name': 'ca',
                'description': '*' * 1001
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
