from django.test import TestCase, SimpleTestCase
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
    @classmethod
    def setUpTestData(cls):
        number_of_tests, questions = 15, 5
        Categories.objects.create(name='category')
        u = CustomUser.objects.create_user(
            username='user0',
            email='user0@test.com',
            email_confirmed=True,
            password='password!@#'
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
                    owner=u,
                    description='cat',
                    category=Categories.objects.first(),
                    is_public=True
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

    def test_default_ordering_last_updated_is_first(self):
        resp = self.client.get(reverse('tests:tests'))
        last_test = Test.objects.last()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(last_test, resp.context['tests'][0])

    def test_ordering_by_time_update_returns_correct_order(self):
        resp = self.client.get(reverse('tests:tests'), {'ordering': 'time_update'})
        # test1 because test0 is private
        first_test = Test.objects.get(name='test1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(first_test, resp.context['tests'][0])

    def test_ordering_by_name_returns_correct_order(self):
        resp = self.client.get(reverse('tests:tests'), {'ordering': 'name'})
        # test1 because test0 is private
        first_test = Test.objects.get(name='test1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(first_test, resp.context['tests'][0])

    def test_ordering_by_name_reversed_returns_correct_order(self):
        resp = self.client.get(reverse('tests:tests'), {'ordering': '-name'})
        # test1 because test0 is private
        first_test = Test.objects.get(name='test9')
        self.assertTrue('9' > '14')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(first_test, resp.context['tests'][0])

    def test_search_returns_correct_tests(self):
        # test1, 10, 11, 12, 13, 14
        resp = self.client.get(reverse('tests:tests'), {'search': 'test1'})
        tests = resp.context['tests']
        test1 = Test.objects.get(name='test1')
        test10 = Test.objects.get(name='test10')
        test11 = Test.objects.get(name='test11')
        test12 = Test.objects.get(name='test12')
        test13 = Test.objects.get(name='test13')
        test14 = Test.objects.get(name='test14')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(6, len(tests))
        self.assertTrue(test1 in tests)
        self.assertTrue(test10 in tests)
        self.assertTrue(test11 in tests)
        self.assertTrue(test12 in tests)
        self.assertTrue(test13 in tests)
        self.assertTrue(test14 in tests)

    def test_search_works_by_description_as_well(self):
        resp = self.client.get(reverse('tests:tests'), {'search': 'cat'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(12, len(resp.context['tests']))
        resp2 = self.client.get(reverse('tests:tests'), {'page': '2', 'search': 'cat'})
        self.assertEqual(resp2.status_code, 200)
        # 15 - 1 (private) - 1 (without questions) - 12 (in 1 page) = 1
        self.assertEqual(1, len(resp2.context['tests']))

    def test_search_works_by_category_as_well(self):
        resp = self.client.get(reverse('tests:tests'), {'search': 'category'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(12, len(resp.context['tests']))
        resp2 = self.client.get(reverse('tests:tests'), {'page': '2', 'search': 'category'})
        self.assertEqual(resp2.status_code, 200)
        # 15 - 1 (private) - 1 (without questions) - 12 (in 1 page) = 1
        self.assertEqual(1, len(resp2.context['tests']))

    def test_search_works_by_owner_as_well(self):
        resp = self.client.get(reverse('tests:tests'), {'search': 'user0'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(12, len(resp.context['tests']))
        resp2 = self.client.get(reverse('tests:tests'), {'page': '2', 'search': 'user0'})
        self.assertEqual(resp2.status_code, 200)
        # 15 - 1 (private) - 1 (without questions) - 12 (in 1 page) = 1
        self.assertEqual(1, len(resp2.context['tests']))


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
            password='testpassword1!'
        )
        self.u2 = CustomUser.objects.create_user(
            username='user2',
            email='u2@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        for t in Test.objects.all():
            if int(t.name[-1]) % 2 == 0:
                Test.objects.filter(pk=t.pk).update(owner=self.u1)
            else:
                Test.objects.filter(pk=t.pk).update(owner=self.u2)

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get('/tests/my/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'main_app/show_my_tests_list.html')

    def test_pagination_is_twelve(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'])
        self.assertEqual(12, len(resp.context['tests']))

    def test_three_tests_in_second_page_of_pagination(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests') + '?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(3, len(resp.context['tests']))

    def test_ordering_last_updated_is_first(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests'))
        last_test = Test.objects.filter(owner=self.u1).last()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(last_test, resp.context['tests'][0])

    def test_u1_have_only_even_tests_and_dont_see_foreign_tests(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests'))
        even_t = Test.objects.get(name='test28')
        odd_t = Test.objects.get(name='test29')
        self.assertTrue(even_t in resp.context['tests'])
        self.assertFalse(odd_t in resp.context['tests'])
        for i in resp.context['tests']:
            self.assertEqual(self.u1, i.owner)

    def test_u2_have_only_idd_tests_and_dont_see_foreign_tests(self):
        self.client.login(username='user2', password='testpassword1!')
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

    def test_ordering_by_time_update_returns_correct_order(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests'), {'ordering': 'time_update'})
        first_test = Test.objects.get(name='test0')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(first_test, resp.context['tests'][0])

    def test_ordering_by_time_update_reversed_returns_correct_order(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests'), {'ordering': '-time_update'})
        first_test = Test.objects.get(name='test28')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(first_test, resp.context['tests'][0])

    def test_ordering_by_name_returns_correct_order(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests'), {'ordering': 'name'})
        first_test = Test.objects.get(name='test0')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(first_test, resp.context['tests'][0])

    def test_ordering_by_name_reversed_returns_correct_order(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:my_tests'), {'ordering': '-name'})
        first_test = Test.objects.get(name='test8')
        self.assertTrue('8' > '28')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(first_test, resp.context['tests'][0])


class AddTestViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.u1 = CustomUser.objects.create_user(
            username='user1',
            email='u1@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.u2 = CustomUser.objects.create_user(
            username='user2',
            email='u2@test.com',
            email_confirmed=False,
            password='testpassword1!'
        )
        self.c = Categories.objects.create(name='cat')
        self.data = {
            'name': 'cat',
            'category': self.c,
            'description': 'cats',
        }

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get('/tests/add/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:add'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:add'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'main_app/add_test.html')

    def test_anonymous_user_doesnt_have_add_test_page(self):
        resp = self.client.get(reverse('tests:add'))
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/users/login/?next=' + reverse('tests:add'))

    def test_not_verified_email_user_doesnt_have_add_test_page(self):
        self.client.login(username='user2', password='testpassword1!')
        resp = self.client.get('/tests/add/')
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/')

    def test_blank_form_cause_error(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.post(reverse('tests:add'), {})
        self.assertFormError(resp, 'form', 'name', 'This field is required.')

    def test_invalid_form_cause_error(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.post(reverse('tests:add'), {'name': '*' * 256})
        self.assertFormError(resp, 'form', 'name', 'Ensure this value has at most 255 characters (it has 256).')

    def test_valid_form_assigns_current_user_to_test_owner(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.post(reverse('tests:add'), {'name': 'asdasdas2'})
        self.assertEqual(self.u1, Test.objects.get(name='asdasdas2').owner)

    def test_valid_form_cause_redirect_to_tests_detail(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.post(reverse('tests:add'), {'name': 'asdasdas'})
        test_pk = Test.objects.get(name='asdasdas').pk
        self.assertRedirects(resp, reverse('tests:test_detail', kwargs={'pk': test_pk}))


class UpdateTestViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.u1 = CustomUser.objects.create_user(
            username='user1',
            email='u1@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.u2 = CustomUser.objects.create_user(
            username='user2',
            email='u2@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.c = Categories.objects.create(name='cat')
        self.test = Test.objects.create(name='test1', owner=self.u1)
        self.data = {
            'name': 'cat',
            'category': self.c,
            'description': 'cats',
        }
        self.url_of_first_test = f'/tests/{self.test.pk}/edit/'

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(self.url_of_first_test)
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:test_edit', kwargs={'pk': self.test.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(self.url_of_first_test)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'main_app/test_edit.html')

    def test_anonymous_user_doesnt_have_access_to_test_edit_page(self):
        resp = self.client.get(self.url_of_first_test)
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/users/login/?next=' + self.url_of_first_test)

    def test_not_owner_of_the_test_doesnt_have_access_to_test_edit_page(self):
        self.client.login(username='user2', password='testpassword1!')
        resp = self.client.get(self.url_of_first_test)
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/')

    def test_blank_form_cause_error(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.post(self.url_of_first_test, {})
        self.assertFormError(resp, 'form', 'name', 'This field is required.')

    def test_invalid_form_cause_error(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.post(self.url_of_first_test, {'name': '*' * 256})
        self.assertFormError(resp, 'form', 'name', 'Ensure this value has at most 255 characters (it has 256).')

    def test_valid_form_cause_redirect_to_tests_detail(self):
        self.client.login(username='user1', password='testpassword1!')
        test_pk = Test.objects.get(name='test1').pk
        resp = self.client.post(self.url_of_first_test, {'name': 'test123', 'description': 'asasd'})
        self.assertRedirects(resp, reverse('tests:test_detail', kwargs={'pk': test_pk}))
        self.assertEqual('test123', Test.objects.get(pk=test_pk).name)
        self.assertEqual('asasd', Test.objects.get(pk=test_pk).description)


class TestDetailViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.u1 = CustomUser.objects.create_user(
            username='user1',
            email='u1@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.u2 = CustomUser.objects.create_user(
            username='user2',
            email='u2@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.c = Categories.objects.create(name='cat')
        self.test = Test.objects.create(name='test1', owner=self.u1)
        self.data = {
            'name': 'cat',
            'category': self.c,
            'description': 'cats',
        }
        self.url_of_first_test = f'/tests/{self.test.pk}/'

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(self.url_of_first_test)
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:test_detail', kwargs={'pk': self.test.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(self.url_of_first_test)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'main_app/test_detail.html')

    def test_anonymous_user_doesnt_have_access_to_test_edit_page(self):
        resp = self.client.get(self.url_of_first_test)
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/users/login/?next=' + self.url_of_first_test)

    def test_not_owner_of_the_test_doesnt_have_access_to_test_edit_page(self):
        self.client.login(username='user2', password='testpassword1!')
        resp = self.client.get(self.url_of_first_test)
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/')


class TestQuestionsEditViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.u1 = CustomUser.objects.create_user(
            username='user1',
            email='u1@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.u2 = CustomUser.objects.create_user(
            username='user2',
            email='u2@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.c = Categories.objects.create(name='cat')
        self.test = Test.objects.create(name='test1', owner=self.u1)
        self.question = Questions.objects.create(
            question='why',
            correct_answer='because',
            answer_1='idk1',
            answer_2='idk2',
            answer_3='idk3',
            test=self.test)
        self.url_of_first_question = f'/tests/{self.test.pk}/questions/edit/'

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(self.url_of_first_question)
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:test_questions_edit', kwargs={'pk': self.test.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(self.url_of_first_question)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'main_app/test_questions_edit.html')

    def test_anonymous_user_doesnt_have_access_to_test_edit_page(self):
        resp = self.client.get(self.url_of_first_question)
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/users/login/?next=' + self.url_of_first_question)

    def test_not_owner_of_the_test_doesnt_have_access_to_test_edit_page(self):
        self.client.login(username='user2', password='testpassword1!')
        resp = self.client.get(self.url_of_first_question)
        # 302 - cause LoginRequiredMixin redirects to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/')

    def test_valid_form_redirects_to_test_detail(self):
        self.client.login(username='user1', password='testpassword1!')
        data = {
            'question_test-TOTAL_FORMS': '1',
            'question_test-INITIAL_FORMS': '1',
            'question_test-MIN_NUM_FORMS': '0',
            'question_test-MAX_NUM_FORMS': '50',
            'question_test-0-question': ['2 + 6'],
            'question_test-0-correct_answer': ['8'],
            'question_test-0-answer_1': ['10'],
            'question_test-0-answer_2': ['23'],
            'question_test-0-answer_3': [''],
            'question_test-0-value': 4,
            'question_test-0-id': str(self.question.pk),
            'question_test-0-test': str(self.test.pk)
        }
        resp = self.client.post(self.url_of_first_question, data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/tests/' + str(self.test.pk) + '/')

    def test_creation_question_with_same_name_cause_error(self):
        self.client.login(username='user1', password='testpassword1!')
        data = {
            'question_test-TOTAL_FORMS': '2',
            'question_test-INITIAL_FORMS': '2',
            'question_test-MIN_NUM_FORMS': '0',
            'question_test-MAX_NUM_FORMS': '50',
            'question_test-0-question': ['why'],
            'question_test-0-correct_answer': ['8'],
            'question_test-0-answer_1': ['10'],
            'question_test-0-answer_2': ['23'],
            'question_test-0-answer_3': [''],
            'question_test-0-value': 4,
            'question_test-0-id': str(self.question.pk),
            'question_test-0-test': str(self.test.pk),
            'question_test-1-question': ['why'],
            'question_test-1-correct_answer': ['8'],
            'question_test-1-answer_1': ['10'],
            'question_test-1-answer_2': ['23'],
            'question_test-1-answer_3': [''],
            'question_test-1-value': 4,
            'question_test-1-id': str(self.question.pk),
            'question_test-1-test': str(self.test.pk)
        }
        resp = self.client.post(self.url_of_first_question, data)
        er_msg = '<ul class="errorlist nonfield"><li>This question is already in this test.</li></ul>'
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(er_msg, resp.context_data['form'].errors)


class TestPassTestTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        u = CustomUser.objects.create_user(
            username='user1',
            email='u1@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        Test.objects.create(name='test1', owner=u)
        Test.objects.create(name='test2', owner=u, is_public=False)
        Test.objects.create(name='test3', owner=u, is_public=False, access_by_link=False)
        Test.objects.create(name='test4', owner=u, show_results=False)
        for t in Test.objects.all():
            for q in range(2):
                Questions.objects.create(
                    question='why' + str(q),
                    correct_answer='correct_answer',
                    answer_1='wrong_answer1',
                    answer_2='wrong_answer1',
                    answer_3='wrong_answer1',
                    value=1,
                    test=t)

    def setUp(self):
        self.u1 = CustomUser.objects.get(username='user1')
        self.u2 = CustomUser.objects.create_user(
            username='user2',
            email='u2@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.client = Client()
        self.t1 = Test.objects.get(name='test1')
        self.t2 = Test.objects.get(name='test2')
        self.t3 = Test.objects.get(name='test3')
        self.t4 = Test.objects.get(name='test4')
        self.t1_url = '/tests/' + str(self.t1.pk) + '/pass/'
        self.t2_url = '/tests/' + str(self.t2.pk) + '/pass/'
        self.t3_url = '/tests/' + str(self.t3.pk) + '/pass/'
        self.t4_url = '/tests/' + str(self.t4.pk) + '/pass/'

    def test_view_url_exists_at_desired_location_and_anonymous_user_get_access_to_public_test(self):
        resp = self.client.get(self.t1_url)
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('tests:pass_test', kwargs={'pk': self.t1.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.t1_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'main_app/pass_test.html')

    def test_non_owner_user_get_access_to_public_test(self):
        self.client.login(username='user2', password='testpassword1!')
        resp = self.client.get(self.t1_url)
        self.assertEqual(resp.status_code, 200)

    def test_private_test_accessible_by_link(self):
        resp = self.client.get(self.t2_url)
        self.assertEqual(resp.status_code, 200)

    def test_private_and_not_accessible_by_link_not_accessible(self):
        resp = self.client.get(self.t3_url)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/')

    def test_pass_test_redirects_to_results(self):
        self.client.login(username='user1', password='testpassword1!')
        data = {'why0': 'correct_answer', 'why1': 'wrong_answer1', 'timer': '123'}
        resp = self.client.post(self.t1_url, data=data)
        self.assertTemplateUsed(resp, 'main_app/result.html')

    def test_correct_answers_increase_score_and_time_is_saved_correctly(self):
        self.client.login(username='user1', password='testpassword1!')
        data = {'why0': 'correct_answer', 'why1': 'correct_answer', 'timer': '1'}
        resp = self.client.post(self.t1_url, data=data)
        for i in resp.context[0]:
            if 'result' in i:
                self.assertEqual(2, i['result'])
            if 'time' in i:
                self.assertEqual('1', i['time'])
        data = {'why0': 'correct_answer', 'why1': 'wrong_answer', 'timer': '12'}
        resp = self.client.post(self.t1_url, data=data)
        for i in resp.context[0]:
            if 'result' in i:
                self.assertEqual(1, i['result'])
            if 'time' in i:
                self.assertEqual('12', i['time'])
        data = {'why0': 'wrong_answer', 'why1': 'wrong_answer', 'timer': '123'}
        resp = self.client.post(self.t1_url, data=data)
        for i in resp.context[0]:
            if 'result' in i:
                self.assertEqual(0, i['result'])
            if 'time' in i:
                self.assertEqual('123', i['time'])

    def test_context_is_reduced_if_not_show_results(self):
        self.client.login(username='user1', password='testpassword1!')
        data = {'why0': 'correct_answer', 'why1': 'correct_answer', 'timer': '1'}
        resp = self.client.post(self.t4_url, data=data)
        self.assertEqual(None, resp.context.get('ans', None))
        self.assertEqual(None, resp.context.get('questions', None))


class PassedTestViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        number_of_tests, questions = 21, 5
        Categories.objects.create(name='cat')
        u = CustomUser.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpassword1!',
            email_confirmed=True
        )
        Test.objects.create(
            name='test',
            owner=u,
            description='cat',
            category=Categories.objects.first(), )
        for t in range(number_of_tests):
            PassedTests.objects.create(test=Test.objects.get(name='test'),
                                       user=u,
                                       grade=50.23,
                                       score=5,
                                       max_score=1)

    def setUp(self):
        self.client = Client()
        self.client.login(username='user1', password='testpassword1!')

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/tests/passed_tests/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('tests:passed_tests'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('tests:passed_tests'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'main_app/passed_tests.html')

    def test_pagination_is_twenty(self):
        resp = self.client.get(reverse('tests:passed_tests'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'])
        self.assertEqual(20, len(resp.context['passed_tests']))

    def test_one_test_in_second_page_of_pagination(self):
        resp = self.client.get(reverse('tests:passed_tests') + '?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(1, len(resp.context['passed_tests']))

    def test_ordering_last_passed_is_first(self):
        resp = self.client.get(reverse('tests:passed_tests'))
        last_test = PassedTests.objects.last()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(last_test, resp.context['passed_tests'][0])

    def test_ordering_by_data_passed_returns_correct_order(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:passed_tests'), {'ordering': 'data_passed'})
        first_test = PassedTests.objects.first()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(first_test, resp.context['passed_tests'][0])

    def test_ordering_by_data_passed_reversed_returns_correct_order(self):
        self.client.login(username='user1', password='testpassword1!')
        resp = self.client.get(reverse('tests:passed_tests'), {'ordering': '-data_passed'})
        first_test = PassedTests.objects.last()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(first_test, resp.context['passed_tests'][0])
