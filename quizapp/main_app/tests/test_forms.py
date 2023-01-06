from django.core import mail
from django.test import TestCase
from main_app.forms import TestQuestionsFormset, Categories, CreateTestForm, UpdateTestForm, ContactForm
from users.models import CustomUser
from main_app.models import Test, Questions


class CreateTestTestCase(TestCase):

    def test_CreateTestForm_form_is_valid(self):
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
        self.assertTrue(form.is_valid())

    def test_CreateTestForm_form_is_not_valid(self):
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
    def test_UpdateTestForm_form_is_valid(self):
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
        self.assertTrue(form.is_valid())

    def test_UpdateTestForm_form_is_not_valid(self):
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


class TestQuestionsFormsetTestCase(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='user1',
            email='u1@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.test = Test.objects.create(name='test1', owner=self.user)
        self.question = Questions.objects.create(
            question='why',
            correct_answer='because',
            answer_1='idk1',
            answer_2='idk2',
            answer_3='idk3',
            test=self.test)

    def test_save_valid_data(self):
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
        formset = TestQuestionsFormset(data=data, instance=self.test)
        self.assertTrue(formset.is_valid())

    def test_invalid_data_cause_error(self):
        data = {
            'question_test-TOTAL_FORMS': '3',
            'question_test-INITIAL_FORMS': '2',
            'question_test-MIN_NUM_FORMS': '0',
            'question_test-MAX_NUM_FORMS': '50',
            'question_test-0-question': '',
            'question_test-0-correct_answer': '',
            'question_test-0-answer_1': '',
            'question_test-0-answer_2': ['23'],
            'question_test-0-answer_3': [''],
            'question_test-0-value': 4,
            'question_test-0-id': str(self.question.pk),
            'question_test-0-test': str(self.test.pk),
        }
        formset = TestQuestionsFormset(data=data, instance=self.test)
        self.assertEqual(3, len(formset.errors[0]))
        self.assertEqual(['This field is required.'], formset.errors[0]['question'])
        self.assertEqual(['This field is required.'], formset.errors[0]['correct_answer'])
        self.assertEqual(['This field is required.'], formset.errors[0]['answer_1'])


class ContactFormTestCase(TestCase):
    def test_valid_data_is_valid(self):
        valid_data = {
            'name': 'test_name',
            'email': 'test@test.com',
            'message': 'hello world',
            'captcha_0': 'actually anything',
            'captcha_1': 'PASSED'
        }
        form = ContactForm(data=valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_returns_error_messages(self):
        invalid_data = {
            'name': '',
            'email': '',
            'message': '',
            'captcha_0': '',
            'captcha_1': ''
        }
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(4, len(form.errors))
        self.assertTrue('This field is required.' in form.errors['name'])
        self.assertTrue('This field is required.' in form.errors['email'])
        self.assertTrue('This field is required.' in form.errors['message'])
        self.assertTrue('This field is required.' in form.errors['captcha'])
        invalid_data2 = {
            'name': 'test_name',
            'email': 'test@test.com',
            'message': 'hello world',
            'captcha_0': 'actually anything',
            'captcha_1': 'cat'
        }
        form2 = ContactForm(data=invalid_data2)

    def test_invalid_captcha_raise_error(self):
        invalid_data = {
            'name': 'test_name',
            'email': 'test@test.com',
            'message': 'hello world',
            'captcha_0': 'actually anything',
            'captcha_1': 'not_passed'
        }
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertTrue('Invalid CAPTCHA' in form.errors['captcha'])
