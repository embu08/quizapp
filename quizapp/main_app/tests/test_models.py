from django.test import TestCase
from main_app.models import *
from django.db.utils import IntegrityError

from users.models import CustomUser


class CategoriesTestCase(TestCase):
    def test_str_is_test_name_and_question(self):
        c = Categories.objects.create(name='cat dog')
        s = 'Cat Dog'
        self.assertEqual(s, str(c))

    def test_len_name_lower_than_3_cause_validation_error(self):
        c = Categories(name='ca')
        with self.assertRaises(ValidationError):
            c.clean()


class TestTestCase(TestCase):

    def setUp(self):
        self.o = CustomUser.objects.create(username='user1',
                                           email='test@test.com',
                                           email_confirmed=True)
        self.c = Categories.objects.create(name='category')
        self.t = Test.objects.create(
            name='test',
            owner=self.o,
            description='cat',
            is_public=True,
            access_by_link=True,
            show_results=True,
            category=self.c
        )

    def test_str_is_test_name_and_question(self):
        s = 'Test "test" by user1'
        self.assertEqual(s, str(self.t))

    def test_get_absolute_url_returns_correct_url(self):
        t1 = Test.objects.first()
        self.assertEqual('/tests/' + str(t1.pk) + '/', t1.get_absolute_url())

    def test_get_pass_url_returns_correct_url(self):
        t1 = Test.objects.first()
        self.assertEqual('/tests/' + str(t1.pk) + '/edit/', t1.get_edit_url())

    def test_get_edit_url_returns_correct_url(self):
        t1 = Test.objects.first()
        self.assertEqual('/tests/' + str(t1.pk) + '/pass/', t1.get_pass_url())


class QuestionsModelTestCase(TestCase):

    def setUp(self):
        self.t = Test.objects.create(name='Test')
        self.q1 = Questions.objects.create(
            question='why',
            correct_answer='because',
            answer_1='idk1',
            answer_2='idk2',
            answer_3='idk3',
            test=self.t)

    def test_question_is_already_in_the_test(self):
        q2 = Questions(question='why',
                       correct_answer='123',
                       answer_1='321',
                       test=self.t)
        with self.assertRaises(IntegrityError):
            q2.save()

    def test_str_is_test_name_and_question(self):
        s = 'Test: Test "Test" By None, question: Why'
        self.assertEqual(s, str(self.q1))


class PassedTestTestCase(TestCase):
    def setUp(self):
        self.u = CustomUser.objects.create(username='user1',
                                           email='test@test.com',
                                           email_confirmed=True)
        self.t = Test.objects.create(name='Test')
        self.pt = PassedTests.objects.create(
            test=self.t,
            user=self.u,
            grade=99.33,
            score=50,
            max_score=200500,
        )

    def test_passed_test_str_returns_long_string(self):
        s = f"user1's grade is 99.33. Scored 50 out of 200500 points."
        self.assertEqual(s, str(self.pt))
