from django.test import TestCase, SimpleTestCase
from django.urls import reverse
import random
from main_app.models import *
from users.models import CustomUser
from django.test.client import Client


class HomeViewTestCase(SimpleTestCase):
    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('tests:home'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('tests:home'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'main_app/home.html')


class ShowAllTestsListVIewTestCase(TestCase):
    # create 13 tests, with questions and users
    @classmethod
    def setUpTestData(cls):
        number_of_tests, questions = 15, 5
        Categories.objects.create(name='cat')
        u = CustomUser.objects.create(
            username='user0',
            email='user0@test.com',
            email_confirmed=True
        )

        for test in range(number_of_tests):
            # first test is private, so it doesn't in queryset
            if test == 0:
                Test.objects.create(
                    name='test' + str(test),
                    owner=u,
                    description='cat',
                    category=Categories.objects.first(),
                    is_public=False
                )
            else:
                Test.objects.create(
                    name='test' + str(test),
                    owner=random.choice(CustomUser.objects.all()),
                    description='cat',
                    category=Categories.objects.first()
                )

        for t in Test.objects.all():
            # there are no questions for 4 test, so it doesn't in queryset
            if t.name != 'test4':
                for i in range(5):
                    Questions.objects.create(
                        question='what' + str(i),
                        correct_answer='3',
                        answer_1='4',
                        answer_2='5',
                        answer_3='6',
                        value=1,
                        test=t
                    )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/tests/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('tests:tests'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('tests:tests'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'main_app/show_tests_list.html')

    def test_pagination_is_twelve(self):
        resp = self.client.get(reverse('tests:tests'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'])
        self.assertEqual(12, len(resp.context['tests']))

    def test_one_test_in_second_page_of_pagination(self):
        resp = self.client.get(reverse('tests:tests') + '?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(1, len(resp.context['tests']))

    def test_test0_not_in_queryset_cause_its_private(self):
        resp = self.client.get(reverse('tests:tests'))
        resp_2 = self.client.get(reverse('tests:tests') + '?page=2')
        t0 = Test.objects.get(name='test0')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(t0 in resp.context['tests'])
        self.assertFalse(t0 in resp_2.context['tests'])

    def test_test4_not_in_queryset_cause_it_doesnt_have_any_questions(self):
        resp = self.client.get(reverse('tests:tests'))
        resp_2 = self.client.get(reverse('tests:tests') + '?page=2')
        t4 = Test.objects.get(name='test4')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(t4 in resp.context['tests'])
        self.assertFalse(t4 in resp_2.context['tests'])

    def test_ordering_last_updated_is_first(self):
        resp = self.client.get(reverse('tests:tests'))
        last_test = Test.objects.last()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(last_test, resp.context['tests'][0])


class ShowMyTestsListVIewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_tests, questions = 30, 5
        c = Categories.objects.create(name='cat')
        for test in range(number_of_tests):
            Test.objects.create(
                name='test' + str(test),
                description='cat',
                category=c,
                is_public=True)

        for t in Test.objects.all():
            # there are no questions for 4 test, so it doesn't in queryset
            if t.name != 'test4':
                for i in range(5):
                    Questions.objects.create(
                        question='what' + str(i),
                        correct_answer='3',
                        answer_1='4',
                        answer_2='5',
                        answer_3='6',
                        value=1,
                        test=t
                    )

    def setUp(self):
        self.client = Client()
        self.u1 = CustomUser.objects.create_user(
            username='user1',
            email='u1@test.com',
            email_confirmed=True,
            password='server10pass'
        )
        self.u2 = CustomUser.objects.create_user(
            username='user2',
            email='u2@test.com',
            email_confirmed=True,
            password='server10pass'
        )
        for t in Test.objects.all():
            if int(t.name[-1]) % 2 == 0:
                Test.objects.filter(pk=t.pk).update(owner=self.u1)
            else:
                Test.objects.filter(pk=t.pk).update(owner=self.u2)

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user1', password='server10pass')
        resp = self.client.get('/tests/my/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user1', password='server10pass')
        resp = self.client.get(reverse('tests:my_tests'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='server10pass')
        resp = self.client.get(reverse('tests:my_tests'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'main_app/show_my_tests_list.html')

    def test_pagination_is_twelve(self):
        self.client.login(username='user1', password='server10pass')
        resp = self.client.get(reverse('tests:my_tests'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'])
        self.assertEqual(12, len(resp.context['tests']))

    def test_three_tests_in_second_page_of_pagination(self):
        self.client.login(username='user1', password='server10pass')
        resp = self.client.get(reverse('tests:my_tests') + '?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(3, len(resp.context['tests']))

    def test_ordering_last_updated_is_first(self):
        self.client.login(username='user1', password='server10pass')
        resp = self.client.get(reverse('tests:my_tests'))
        last_test = Test.objects.filter(owner=self.u1).last()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(last_test, resp.context['tests'][0])

    def test_u1_have_only_even_tests_and_dont_see_foreign_tests(self):
        self.client.login(username='user1', password='server10pass')
        resp = self.client.get(reverse('tests:my_tests'))
        even_t = Test.objects.get(name='test28')
        odd_t = Test.objects.get(name='test29')
        self.assertTrue(even_t in resp.context['tests'])
        self.assertFalse(odd_t in resp.context['tests'])
        for i in resp.context['tests']:
            self.assertEqual(self.u1, i.owner)

    def test_u2_have_only_idd_tests_and_dont_see_foreign_tests(self):
        self.client.login(username='user2', password='server10pass')
        resp = self.client.get(reverse('tests:my_tests'))
        even_t = Test.objects.get(name='test28')
        odd_t = Test.objects.get(name='test29')
        self.assertFalse(even_t in resp.context['tests'])
        self.assertTrue(odd_t in resp.context['tests'])
        for i in resp.context['tests']:
            self.assertEqual(self.u2, i.owner)

    def test_anonymous_user_doesnt_have_my_tests_page(self):
        resp = self.client.get(reverse('tests:my_tests'))
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
