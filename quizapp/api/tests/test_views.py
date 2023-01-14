import random

from django.contrib import auth
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.core import mail
from main_app.models import Categories, Test, Questions, PassedTests
from users.models import CustomUser
from django.urls import reverse
from django.test.client import Client


class TestAPIViewTestCase(TestCase):
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
        resp = self.client.get('/api/v1/tests/')
        self.assertEqual(200, resp.status_code)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('api:tests'))
        self.assertEqual(200, resp.status_code)

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('api:tests'))
        self.assertEqual(200, resp.status_code)
        self.assertTrue('next' in resp.data and 'previous' in resp.data)
        self.assertEqual(10, len(resp.data['results']))

    def test_three_tests_in_second_page_of_pagination(self):
        resp = self.client.get(reverse('api:tests') + '?page=2')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(3, len(resp.data['results']))

    def test_test0_not_in_queryset_cause_its_private(self):
        resp = self.client.get(reverse('api:tests'))
        resp_2 = self.client.get(reverse('api:tests') + '?page=2')
        t0 = Test.objects.get(name='test0')
        self.assertEqual(200, resp.status_code)
        self.assertFalse(t0 in resp.data['results'])
        self.assertFalse(t0 in resp_2.data['results'])

    def test_test4_not_in_queryset_cause_it_doesnt_have_any_questions(self):
        resp = self.client.get(reverse('api:tests'))
        resp_2 = self.client.get(reverse('api:tests') + '?page=2')
        t4 = Test.objects.get(name='test4')
        self.assertEqual(200, resp.status_code)
        self.assertFalse(t4 in resp.data['results'])
        self.assertFalse(t4 in resp_2.data['results'])

    def test_default_ordering_last_updated_is_first(self):
        resp = self.client.get(reverse('api:tests'))
        last_test = Test.objects.all().order_by('-time_update')[0]
        self.assertEqual(200, resp.status_code)
        self.assertEqual(last_test.id, resp.data['results'][0]['id'])

    def test_ordering_by_time_update_returns_correct_order(self):
        resp = self.client.get(reverse('api:tests'), {'ordering': 'time_update'})
        # test1 because test0 is private
        first_test = Test.objects.get(name='test1')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(first_test.id, resp.data['results'][0]['id'])

    def test_ordering_by_name_returns_correct_order(self):
        resp = self.client.get(reverse('api:tests'), {'ordering': 'name'})
        # test1 because test0 is private
        first_test = Test.objects.get(name='test1')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(first_test.id, resp.data['results'][0]['id'])

    def test_ordering_by_name_reversed_returns_correct_order(self):
        resp = self.client.get(reverse('api:tests'), {'ordering': '-name'})
        # test1 because test0 is private
        first_test = Test.objects.get(name='test9')
        self.assertTrue('9' > '14')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(first_test.id, resp.data['results'][0]['id'])

    def test_search_returns_correct_tests(self):
        # test1, 10, 11, 12, 13, 14
        resp = self.client.get(reverse('api:tests'), {'search': 'test1'})
        tests = resp.data['results']
        test1 = Test.objects.get(name='test1')
        test10 = Test.objects.get(name='test10')
        test11 = Test.objects.get(name='test11')
        test12 = Test.objects.get(name='test12')
        test13 = Test.objects.get(name='test13')
        test14 = Test.objects.get(name='test14')
        all_expected_tests = [i.id for i in (test1, test10, test11, test12, test13, test14)]
        all_got_tests = [i['id'] for i in tests]
        self.assertEqual(200, resp.status_code)
        self.assertEqual(6, len(tests))
        self.assertEqual(sorted(all_expected_tests), sorted(all_got_tests))


class ContactViewTestCase(TestCase):
    def test_valid_form_sends_an_email(self):
        valid_data = {
            'name': 'test_name',
            'email': 'test@test.com',
            'message': 'hello world',
            'captcha_0': 'actually anything',
            'captcha_1': 'PASSED'
        }
        resp = self.client.post(reverse('api:contacts'), data=valid_data)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual("Sender's name: test_name, sender's email: test@test.com\nMessage:\nhello world",
                         mail.outbox[0].body)
        self.assertEqual('A Message from Quizapp Contact Us Form', mail.outbox[0].subject)

    def test_invalid_data_doesnt_send_an_email(self):
        invalid_data = {
            'name': '',
            'email': 'test@test.com',
            'message': 'hello world',
        }
        resp = self.client.post(reverse('api:contacts'), data=invalid_data)
        self.assertEqual(400, resp.status_code)
        self.assertEqual(0, len(mail.outbox))
        invalid_data2 = {
            'name': 'cat',
            'email': '',
            'message': 'hello world',
        }
        resp2 = self.client.post(reverse('api:contacts'), data=invalid_data2)
        self.assertEqual(400, resp2.status_code)
        self.assertEqual(0, len(mail.outbox))
        invalid_data3 = {
            'name': 'cat',
            'email': 'test@test.com',
            'message': '',
        }
        resp3 = self.client.post(reverse('api:contacts'), data=invalid_data3)
        self.assertEqual(400, resp3.status_code)
        self.assertEqual(0, len(mail.outbox))

    def test_valid_data_sends_an_email(self):
        invalid_data = {
            'name': 'cat',
            'email': 'test@test.com',
            'message': 'hello world',
        }
        resp = self.client.post(reverse('api:contacts'), data=invalid_data)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(mail.outbox))


class MyTestsAPIViewTestCase(TestCase):
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
            # there are no questions for 4 test, so but it still in queryset
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
        self.client.force_login(user=self.u1)
        resp = self.client.get('/api/v1/tests/my/')
        self.assertEqual(200, resp.status_code)

    def test_view_url_accessible_by_name(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my'))
        self.assertEqual(200, resp.status_code)

    def test_pagination_is_ten(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my'))
        self.assertEqual(200, resp.status_code)
        self.assertTrue('next' in resp.data and 'previous' in resp.data)
        self.assertEqual(10, len(resp.data['results']))

    def test_5_tests_in_second_page_of_pagination(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my') + '?page=2')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(5, len(resp.data['results']))
        self.client.logout()
        self.client.force_login(user=self.u2)
        resp2 = self.client.get(reverse('api:tests_my') + '?page=2')
        self.assertEqual(200, resp2.status_code)
        # 5 cause test without questions are showed in "my_tests" too
        self.assertEqual(5, len(resp2.data['results']))

    def test_ordering_last_updated_is_first(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my'))
        # idk why sometimes it == 26 and sometimes == 28
        last_test_name = ['test28', 'test26']
        self.assertEqual(200, resp.status_code)
        self.assertTrue(resp.data['results'][0]['name'] in last_test_name)

    def test_u1_have_only_even_tests_and_doesnt_see_foreign_tests(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my'))
        even_t = Test.objects.get(name='test28')
        odd_t = Test.objects.get(name='test29')
        all_got_tests = [i['id'] for i in resp.data['results']]
        self.assertTrue(even_t.id in all_got_tests)
        self.assertFalse(odd_t.id in all_got_tests)
        for i in resp.data['results']:
            self.assertEqual(self.u1.id, i['owner'])

    def test_u2_have_only_odd_tests_and_doesnt_see_foreign_tests(self):
        self.client.force_login(user=self.u2)
        resp = self.client.get(reverse('api:tests_my'))
        even_t = Test.objects.get(name='test28')
        odd_t = Test.objects.get(name='test29')
        all_got_tests = [i['id'] for i in resp.data['results']]
        self.assertFalse(even_t.id in all_got_tests)
        self.assertTrue(odd_t.id in all_got_tests)
        for i in resp.data['results']:
            self.assertEqual(self.u2.id, i['owner'])

    def test_anonymous_user_doesnt_have_my_tests_page(self):
        resp = self.client.get(reverse('api:tests_my'))
        # 401 Unauthorized
        self.assertEqual(resp.status_code, 401)

    def test_ordering_by_time_update_returns_correct_order(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my'), {'ordering': 'time_update'})
        first_test = Test.objects.get(name='test0')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(first_test.id, resp.data['results'][0]['id'])

    def test_ordering_by_time_update_reversed_returns_correct_order(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my'), {'ordering': '-time_update'})
        first_test = Test.objects.get(name='test28')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(first_test.id, resp.data['results'][0]['id'])

    def test_ordering_by_name_returns_correct_order(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my'), {'ordering': 'name'})
        first_test = Test.objects.get(name='test0')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(first_test.id, resp.data['results'][0]['id'])

    def test_ordering_by_name_reversed_returns_correct_order(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my'), {'ordering': '-name'})
        first_test = Test.objects.get(name='test8')
        self.assertTrue('8' > '28')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(first_test.id, resp.data['results'][0]['id'])

    def test_search_by_name_works(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_my'), {'search': 'test1'})
        self.assertEqual(200, resp.status_code)
        # 10 12 14 16 18
        self.assertEqual(5, len(resp.data['results']))


class CreateTestAPIViewTestCase(TestCase):

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
        self.c = Categories.objects.create(name='new_category')
        self.data = {
            'name': 'cat',
            'category': self.c,
            'description': 'cats',
        }

    def test_view_url_exists_at_desired_location(self):
        self.client.force_login(user=self.u1)
        resp = self.client.post('/api/v1/tests/create/')
        # 400 because of empty post
        self.assertEqual(400, resp.status_code)

    def test_view_url_accessible_by_name(self):
        self.client.force_login(user=self.u1)
        resp = self.client.post(reverse('api:tests_create'))
        self.assertEqual(400, resp.status_code)

    def test_method_get_is_not_allowed(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_create'))
        self.assertEqual(405, resp.status_code)

    def test_anonymous_user_doesnt_have_add_test_page(self):
        resp = self.client.post(reverse('api:tests_create'))
        self.assertEqual(401, resp.status_code)

    def test_not_verified_email_user_doesnt_have_add_test_page(self):
        self.client.login(username='user2', password='testpassword1!')
        resp = self.client.post(reverse('api:tests_create'))
        self.assertEqual(resp.status_code, 403)

    def test_blank_form_cause_error(self):
        self.client.force_login(user=self.u1)
        resp = self.client.post(reverse('api:tests_create'), {})
        self.assertEqual(400, resp.status_code)
        self.assertEqual('This field is required.', resp.data['name'][0])

    def test_invalid_form_cause_error(self):
        self.client.force_login(user=self.u1)
        resp = self.client.post(reverse('api:tests_create'), {'name': '*' * 256, 'description': '*' * 1001})
        self.assertEqual(400, resp.status_code)
        self.assertEqual('Ensure this field has no more than 255 characters.', resp.data['name'][0])
        self.assertEqual('Ensure this field has no more than 1000 characters.', resp.data['description'][0])

    def test_valid_form_assigns_current_user_to_test_owner(self):
        self.client.force_login(user=self.u1)
        resp = self.client.post(reverse('api:tests_create'), {'name': 'asdasdas2'})
        self.assertEqual(201, resp.status_code)
        self.assertEqual(self.u1, Test.objects.get(name='asdasdas2').owner)

    def test_valid_data_creates_a_test(self):
        self.client.force_login(user=self.u1)
        self.client.post(reverse('api:tests_create'), {'name': 'asdasdas'})
        self.assertTrue(Test.objects.filter(name='asdasdas').exists())

    def test_valid_data_creates_fields(self):
        self.client.force_login(user=self.u1)
        data = {
            'name': 'cat2',
            'description': 'aaaaaaa',
            'is_public': True,
            'access_by_link': False,
            'show_results': True,
            'category': self.c.pk
        }
        self.client.post(reverse('api:tests_create'), data)
        test = Test.objects.get(name='cat2')
        self.assertEqual('cat2', test.name)
        self.assertEqual('aaaaaaa', test.description)
        self.assertEqual(True, test.is_public)
        self.assertEqual(False, test.access_by_link)
        self.assertEqual(True, test.show_results)
        self.assertEqual(self.c, test.category)
        self.assertEqual(self.u1, test.owner)


class UpdateDestroyTestAPIViewTestCase(TestCase):

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
        self.url_of_first_test = reverse('api:tests_update', kwargs={'pk': self.test.pk})

    def test_view_url_exists_at_desired_location(self):
        self.client.force_login(user=self.u1)
        url = f'/api/v1/tests/{self.test.pk}/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_update', kwargs={'pk': self.test.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_user_doesnt_have_access_to_test_edit_page(self):
        resp = self.client.get(self.url_of_first_test)
        self.assertEqual(401, resp.status_code)

    def test_not_owner_of_the_test_doesnt_have_access_to_test_edit_page(self):
        self.client.login(username='user2', password='testpassword1!')
        resp = self.client.get(self.url_of_first_test)
        self.assertEqual(403, resp.status_code)

    def test_blank_form_cause_error_on_put(self):
        self.client.force_login(user=self.u1)
        resp = self.client.put(self.url_of_first_test, data={}, content_type='application/json')
        self.assertEqual(400, resp.status_code)
        self.assertEqual('This field is required.', resp.data['name'][0])

    def test_invalid_form_cause_error(self):
        self.client.force_login(user=self.u1)
        resp = self.client.put(self.url_of_first_test, data={'name': '*' * 300}, content_type='application/json')
        self.assertEqual(400, resp.status_code)
        self.assertEqual('Ensure this field has no more than 255 characters.', resp.data['name'][0])

    def test_valid_form_cause_test_changing_on_put(self):
        self.client.force_login(user=self.u1)
        test = Test.objects.get(name='test1')
        self.assertEqual('test1', test.name)
        self.assertEqual(None, test.description)
        resp = self.client.put(self.url_of_first_test, {'name': 'test123', 'description': 'asasd'},
                               content_type='application/json')
        test.refresh_from_db()
        self.assertEqual(200, resp.status_code)
        self.assertEqual('test123', test.name)
        self.assertEqual('asasd', test.description)

    def test_valid_form_cause_test_changing_on_patch(self):
        self.client.force_login(user=self.u1)
        test = Test.objects.get(name='test1')
        self.assertEqual(None, test.description)
        resp = self.client.patch(self.url_of_first_test, {'description': 'asasd1111'},
                                 content_type='application/json')
        test.refresh_from_db()
        self.assertEqual(200, resp.status_code)
        self.assertEqual('asasd1111', test.description)


class TestQuestionsCreateAPIViewTestCase(TestCase):
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

    def test_view_url_exists_at_desired_location(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(f'/api/v1/tests/{self.test.pk}/questions/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:tests_questions', kwargs={'pk': self.test.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_user_doesnt_have_access_to_questions_creation_page(self):
        resp = self.client.get(reverse('api:tests_questions', kwargs={'pk': self.test.pk}))
        self.assertEqual(resp.status_code, 401)

    def test_not_owner_of_the_test_doesnt_have_access_to_test_edit_page(self):
        self.client.force_login(user=self.u2)
        resp = self.client.get(reverse('api:tests_questions', kwargs={'pk': self.test.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_valid_form_creates_a_question(self):
        self.client.force_login(user=self.u1)
        data = {
            'question': '2 + 6',
            'correct_answer': '8',
            'answer_1': '10',
            'answer_2': '23',
            'answer_3': '26',
            'value': 4,
            'test': self.test.pk
        }
        resp = self.client.post(reverse('api:tests_questions', kwargs={'pk': self.test.pk}), data=data)
        self.assertEqual(201, resp.status_code)
        self.assertTrue(Questions.objects.filter(question='2 + 6').exists())

    def test_invalid_form_cause_errors(self):
        self.client.force_login(user=self.u1)
        data = {
            'question': '',
            'correct_answer': '',
            'answer_1': '',
            'answer_2': '*' * 256,
            'answer_3': '*' * 256,
            'value': '',
            'test': 150
        }
        resp = self.client.post(reverse('api:tests_questions', kwargs={'pk': self.test.pk}), data=data)
        self.assertEqual(400, resp.status_code)
        self.assertEqual('This field may not be blank.', resp.data['question'][0])
        self.assertEqual('This field may not be blank.', resp.data['correct_answer'][0])
        self.assertEqual('This field may not be blank.', resp.data['answer_1'][0])
        self.assertEqual('Ensure this field has no more than 255 characters.', resp.data['answer_2'][0])
        self.assertEqual('Ensure this field has no more than 255 characters.', resp.data['answer_3'][0])
        self.assertEqual('Invalid pk "150" - object does not exist.', resp.data['test'][0])


class PassTestAPITestCase(TestCase):

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

    def test_view_url_exists_at_desired_location_and_anonymous_user_get_access_to_public_test(self):
        resp = self.client.get(f'/api/v1/tests/{self.t1.pk}/pass/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('api:pass', kwargs={'pk': self.t1.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_non_owner_user_get_access_to_public_test(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:pass', kwargs={'pk': self.t1.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_private_test_accessible_by_link_and_not_public(self):
        resp = self.client.get(reverse('api:pass', kwargs={'pk': self.t2.pk}))
        self.assertTrue(self.t2.access_by_link)
        self.assertEqual(resp.status_code, 200)
        resp2 = self.client.get(reverse('api:tests'))
        public_tests = [i['id'] for i in resp2.data['results']]
        self.assertTrue(self.t2.pk not in public_tests)

    def test_private_and_not_accessible_by_link_not_accessible(self):
        resp = self.client.get(reverse('api:pass', kwargs={'pk': self.t3.pk}))
        self.assertEqual(403, resp.status_code)

    def test_correct_answers_increase_score(self):
        self.client.login(username='user1', password='testpassword1!')
        data = {'question_1': 'correct_answer', 'question_2': 'correct_answer'}
        resp = self.client.post(reverse('api:pass', kwargs={'pk': self.t1.pk}), data=data)
        self.assertEqual(100.0, resp.data['results']['grade'])
        self.assertEqual(2, resp.data['results']['correct_answers'])
        self.assertTrue(data['question_1'] == resp.data['question_1']['your_answer'])
        self.assertTrue(data['question_2'] == resp.data['question_2']['your_answer'])

    def test_incorrect_answers_doesnt_increase_score(self):
        self.client.login(username='user1', password='testpassword1!')
        data = {'question_1': 'correct_answer', 'question_2': 'asd'}
        resp = self.client.post(reverse('api:pass', kwargs={'pk': self.t1.pk}), data=data)
        self.assertEqual(50.0, resp.data['results']['grade'])
        self.assertEqual(1, resp.data['results']['correct_answers'])
        self.assertTrue(data['question_1'] == resp.data['question_1']['your_answer'])
        self.assertTrue(data['question_2'] == resp.data['question_2']['your_answer'])

    def test_context_is_reduced_if_not_show_results(self):
        self.client.login(username='user1', password='testpassword1!')
        data = {'question_1': 'correct_answer', 'question_2': 'correct_answer'}
        resp = self.client.post(reverse('api:pass', kwargs={'pk': self.t4.pk}), data=data)
        self.assertFalse('question_1' in resp.data)
        self.assertFalse('question_2' in resp.data)
        self.assertEqual(100.0, resp.data['results']['grade'])


class UpdateDestroyQuestionsAPIViewTestCase(TestCase):
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
        self.test = Test.objects.create(name='test1', owner=self.u1)
        self.test2 = Test.objects.create(name='test2', owner=self.u1)

        self.q1 = Questions.objects.create(
            question='why',
            correct_answer='correct_answer',
            answer_1='wrong_answer1',
            answer_2='wrong_answer1',
            answer_3='wrong_answer1',
            value=1,
            test=self.test)

    def test_view_url_exists_at_desired_location(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(f'/api/v1/questions/{self.q1.pk}/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.force_login(user=self.u1)
        resp = self.client.get(reverse('api:questions_update', kwargs={'pk': self.q1.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_user_doesnt_have_access_to_questions_creation_page(self):
        resp = self.client.get(reverse('api:questions_update', kwargs={'pk': self.q1.pk}))
        self.assertEqual(resp.status_code, 401)

    def test_not_owner_of_the_test_doesnt_have_access_to_test_edit_page(self):
        self.client.force_login(user=self.u2)
        resp = self.client.get(reverse('api:questions_update', kwargs={'pk': self.q1.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_valid_put_form_updates_a_question(self):
        self.client.force_login(user=self.u1)
        data = {
            'question': '2 + 12',
            'correct_answer': '14',
            'answer_1': '10',
            'answer_2': '150',
            'answer_3': '26',
            'value': 3,
        }
        q1 = Questions.objects.get(question='why')
        resp = self.client.put(reverse('api:questions_update', kwargs={'pk': self.q1.pk}),
                               data=data, content_type='application/json')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('why', q1.question)
        self.assertEqual('correct_answer', q1.correct_answer)
        self.assertEqual('wrong_answer1', q1.answer_1)
        self.assertEqual('wrong_answer1', q1.answer_2)
        self.assertEqual('wrong_answer1', q1.answer_3)
        self.assertEqual(1, q1.value)
        q1.refresh_from_db()
        self.assertEqual('2 + 12', q1.question)
        self.assertEqual('14', q1.correct_answer)
        self.assertEqual('10', q1.answer_1)
        self.assertEqual('150', q1.answer_2)
        self.assertEqual('26', q1.answer_3)
        self.assertEqual(3, q1.value)

    def test_valid_patch_form_updates_a_question(self):
        self.client.force_login(user=self.u1)
        data = {
            'question': 'aaaa',
            'value': 300
        }
        q1 = Questions.objects.get(question='why')
        resp = self.client.patch(reverse('api:questions_update', kwargs={'pk': self.q1.pk}),
                                 data=data, content_type='application/json')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('why', q1.question)
        self.assertEqual(1, q1.value)
        q1.refresh_from_db()
        self.assertEqual('aaaa', q1.question)
        self.assertEqual(300, q1.value)

    def test_delete_method_deletes_question(self):
        self.client.force_login(user=self.u1)
        resp = self.client.delete(reverse('api:questions_update', kwargs={'pk': self.q1.pk}))
        self.assertEqual(204, resp.status_code)
        self.assertFalse(Questions.objects.filter(question='why').exists())
        self.assertEqual(0, len(Questions.objects.all()))

    def test_updating_questions_is_not_accessible_for_not_owner_or_stuff(self):
        self.client.force_login(user=self.u2)
        data = {
            'question': 'aaaa',
            'value': 300
        }
        resp = self.client.patch(reverse('api:questions_update', kwargs={'pk': self.q1.pk}),
                                 data=data, content_type='application/json')
        self.assertEqual(403, resp.status_code)

        data2 = {
            'question': '2 + 12',
            'correct_answer': '14',
            'answer_1': '10',
            'answer_2': '150',
            'answer_3': '26',
            'value': 3,
        }
        resp2 = self.client.put(reverse('api:questions_update', kwargs={'pk': self.q1.pk}),
                                data=data2, content_type='application/json')
        self.assertEqual(403, resp2.status_code)

        resp3 = self.client.delete(reverse('api:questions_update', kwargs={'pk': self.q1.pk}))
        self.assertEqual(403, resp3.status_code)

        resp4 = self.client.get(reverse('api:questions_update', kwargs={'pk': self.q1.pk}))
        self.assertEqual(403, resp4.status_code)


class PassedTestsAPIViewTestCase(TestCase):

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
                                       grade=random.randint(0, 100),
                                       score=5,
                                       max_score=1)

    def setUp(self):
        self.client = Client()
        self.client.login(username='user1', password='testpassword1!')

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/api/v1/tests/passed/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('api:passed'))
        self.assertEqual(resp.status_code, 200)

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('api:passed'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(10, len(resp.data['results']))
        resp2 = self.client.get(reverse('api:passed') + '?page=2')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(10, len(resp2.data['results']))
        resp3 = self.client.get(reverse('api:passed') + '?page=3')
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(1, len(resp3.data['results']))

    def test_ordering_last_passed_is_first(self):
        resp = self.client.get(reverse('api:passed'))
        last_test = PassedTests.objects.last()
        self.assertEqual(200, resp.status_code)
        self.assertEqual(last_test.id, resp.data['results'][0]['id'])

    def test_anonymous_user_doesnt_have_passed_tests_page(self):
        self.client.logout()
        resp = self.client.get(reverse('api:passed'))
        self.assertEqual(401, resp.status_code)

    def test_ordering_by_data_passed_returns_correct_order(self):
        resp = self.client.get(reverse('api:passed'), {'ordering': 'data_passed'})
        first_passed_test = PassedTests.objects.get(pk=1)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(first_passed_test.id, resp.data['results'][0]['id'])

    def test_ordering_by_data_passed_reversed_returns_correct_order(self):
        resp = self.client.get(reverse('api:passed'), {'ordering': '-data_passed'})
        first_passed_test = PassedTests.objects.get(pk=21)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(first_passed_test.id, resp.data['results'][0]['id'])

    def test_ordering_by_grade_returns_correct_order(self):
        resp = self.client.get(reverse('api:passed'), {'ordering': 'grade'})
        max_grade = min(PassedTests.objects.values_list('grade', flat=True))
        t = PassedTests.objects.filter(grade=max_grade)[0]
        self.assertEqual(200, resp.status_code)
        self.assertEqual(t.id, resp.data['results'][0]['id'])

    def test_ordering_by_grade_reversed_returns_correct_order(self):
        resp = self.client.get(reverse('api:passed'), {'ordering': '-grade'})
        max_grade = max(PassedTests.objects.values_list('grade', flat=True))
        t = PassedTests.objects.filter(grade=max_grade)[0]
        self.assertEqual(200, resp.status_code)
        self.assertEqual(t.id, resp.data['results'][0]['id'])

    def test_search_by_grade_returns_correct_query(self):
        max_grade = max(PassedTests.objects.values_list('grade', flat=True))
        resp = self.client.get(reverse('api:passed'), {'search': max_grade})
        t = PassedTests.objects.filter(grade=max_grade)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(len(t), len(resp.data['results']))


class CreateUserAPIViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.u = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password='password123'
        )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.post('/api/v1/users/create/')
        self.assertEqual(400, resp.status_code)

    def test_view_url_accessible_by_name(self):
        resp = self.client.post(reverse('api:create_user'))
        self.assertEqual(400, resp.status_code)

    def test_valid_form_creates_user(self):
        data = {
            'username': 'user1',
            'email': 'user1@test.com',
            'first_name': 'User',
            'last_name': 'One',
            'password': 'password123',
        }
        self.assertFalse(CustomUser.objects.filter(username='user1').exists())
        resp = self.client.post(reverse('api:create_user'), data=data)

        self.assertEqual(201, resp.status_code)

        self.assertTrue(CustomUser.objects.filter(username='user1').exists())

    def test_activate_email_sends_email_and_verification_link_is_correct(self):
        '''
        this also tests api.views.activate function
        '''
        data = {
            'username': 'user1',
            'email': 'user1@test.com',
            'first_name': 'User',
            'last_name': 'One',
            'password': 'password123',
        }
        self.assertFalse(CustomUser.objects.filter(username='user1').exists())

        resp = self.client.post(reverse('api:create_user'), data=data)
        self.assertEqual(201, resp.status_code)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(CustomUser.objects.filter(username='user1').exists())
        self.assertFalse(CustomUser.objects.get(username='user1').email_confirmed)

        activation_link = ''
        for line in mail.outbox[0].body.splitlines():
            if 'http' in line:
                activation_link = line
        resp2 = self.client.post(activation_link)

        self.assertEqual(200, resp2.status_code)
        self.assertTrue(CustomUser.objects.get(username='user1').email_confirmed)

    def test_wrong_activation_link_doesnt_confirm_an_email_and_returns_a_failure_message(self):
        data = {
            'username': 'user1',
            'email': 'user1@test.com',
            'first_name': 'User',
            'last_name': 'One',
            'password': 'password123',
        }
        self.assertFalse(CustomUser.objects.filter(username='user1').exists())

        resp = self.client.post(reverse('api:create_user'), data=data)
        self.assertEqual(201, resp.status_code)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(CustomUser.objects.filter(username='user1').exists())
        self.assertFalse(CustomUser.objects.get(username='user1').email_confirmed)

        activation_link = ''
        for line in mail.outbox[0].body.splitlines():
            if 'http' in line:
                activation_link = line
        activation_link = activation_link[:-1] + 'a' + '/'
        resp2 = self.client.post(activation_link)

        self.assertEqual(400, resp2.status_code)
        self.assertFalse(CustomUser.objects.get(username='user1').email_confirmed)


class UpdateUserAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user',
            email='user@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.force_login(user=self.user)
        resp = self.client.get('/api/v1/users/update/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.force_login(user=self.user)
        resp = self.client.get(reverse('api:update_user'))
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_user_doesnt_have_access_to_my_profile_update_page(self):
        resp = self.client.get(reverse('api:update_user'))
        self.assertEqual(401, resp.status_code)

    def test_updated_user_data_via_patch_saves_correctly(self):
        self.client.force_login(user=self.user)
        self.assertEqual(None, CustomUser.objects.get(username='user').first_name)
        self.assertEqual(None, CustomUser.objects.get(username='user').last_name)
        data = {
            'first_name': 'User',
        }
        resp = self.client.patch(reverse('api:update_user'), data, content_type='application/json')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('User', CustomUser.objects.get(username='user').first_name)

    def test_updated_user_data_via_put_saves_correctly(self):
        self.client.force_login(user=self.user)
        self.assertEqual(None, CustomUser.objects.get(username='user').first_name)
        self.assertEqual(None, CustomUser.objects.get(username='user').last_name)
        data = {
            'first_name': 'User',
            'last_name': 'Test',
        }
        resp = self.client.put(reverse('api:update_user'), data, content_type='application/json')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('User', CustomUser.objects.get(username='user').first_name)
        self.assertEqual('Test', CustomUser.objects.get(username='user').last_name)
