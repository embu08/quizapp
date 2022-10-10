from django.test import TestCase
from main_app.models import *
from django.db.utils import IntegrityError


class QuestionsModelTestCase(TestCase):

    def setUp(self):
        self.t = Test.objects.create(name='Test')
        self.q1 = Questions.objects.create(
            question='why',
            correct_answer='because',
            answer_1='idk',
            test=self.t)

    def test_question_is_already_in_the_test(self):
        q2 = Questions(question='why',
                       correct_answer='123',
                       answer_1='321',
                       test=self.t)
        with self.assertRaises(IntegrityError):
            q2.save()
