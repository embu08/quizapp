from django.test import TestCase

from api.serializers import TestSerializer, CreateTestSerializer, UpdateTestSerializer, QuestionsSerializer, \
    PassTestSerializer, ContactUsSerializer, UpdateDestroyQuestionsSerializer, PassedTestsSerializer
from main_app.models import Categories, Test, Questions, PassedTests
from users.models import CustomUser


class TestSerializerTestCase(TestCase):

    def setUp(self):
        self.c = Categories.objects.create(name='category1')

    def test_test_serializer(self):
        test_test = Test.objects.create(name='test_test', category=self.c, description='description', is_public=False)
        serialized_data = TestSerializer(test_test).data

        expected_data = {
            'id': test_test.id,
            'name': 'test_test',
            'description': 'description',
            'owner': None,
            'category': self.c.id,
            'time_create': test_test.time_create,
            'time_update': test_test.time_update,
            'is_public': False,
            'access_by_link': True,
            'show_results': True,
        }
        for i in expected_data:
            if i not in ['time_create', 'time_update']:
                self.assertEqual(expected_data[i], serialized_data[i])


class CreateTestSerializerTestCase(TestCase):
    def setUp(self):
        self.c = Categories.objects.create(name='category1')

    def test_create_test_serializer(self):
        test_test = Test.objects.create(name='test_test', category=self.c, description='description', is_public=False)
        serialized_data = CreateTestSerializer(test_test).data

        expected_data = {
            'name': 'test_test',
            'description': 'description',
            'category': self.c.id,
            'is_public': False,
            'access_by_link': True,
            'show_results': True,
        }
        self.assertEqual(expected_data, serialized_data)


class UpdateTestSerializerTestCase(TestCase):

    def setUp(self):
        self.c = Categories.objects.create(name='category1')

    def test_update_test_serializer(self):
        test_test = Test.objects.create(name='test_test', category=self.c, description='description', is_public=False)
        serialized_data = UpdateTestSerializer(test_test).data
        expected_data = {
            'name': 'test_test',
            'description': 'description',
            'category': self.c.id,
            'time_create': test_test.time_create,
            'time_update': test_test.time_update,
            'is_public': False,
            'access_by_link': True,
            'show_results': True,
        }
        for i in expected_data:
            if i not in ['time_create', 'time_update']:
                self.assertEqual(expected_data[i], serialized_data[i])

    def test_update_test_serializer_owner_is_read_only(self):
        self.u = CustomUser.objects.create_user(
            username='user',
            email='u@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        serialize_me = {'name': 'cat', 'owner': self.u}
        serialized_data = UpdateTestSerializer(data=serialize_me)
        self.assertTrue(serialized_data.is_valid())
        expected_data = {
            'name': 'cat',
            'description': None,
            'category': None,
            'owner': None
        }
        self.assertEqual(expected_data, serialized_data.data)


class QuestionsSerializerTestCase(TestCase):
    def setUp(self):
        self.u = CustomUser.objects.create_user(
            username='user',
            email='u@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.c = Categories.objects.create(name='cat')
        self.test = Test.objects.create(name='test1', owner=self.u)

    def test_question_creation(self):
        data = {
            'question': '2 + 6',
            'correct_answer': '8',
            'answer_1': '10',
            'answer_2': '23',
            'answer_3': '26',
            'value': 4,
            'test': self.test
        }
        question = Questions.objects.create(**data)
        serialized_data = QuestionsSerializer(question).data
        expected_data = {
            'id': question.id,
            'question': '2 + 6',
            'correct_answer': '8',
            'answer_1': '10',
            'answer_2': '23',
            'answer_3': '26',
            'value': 4,
            'test': self.test.pk
        }
        self.assertEqual(expected_data, serialized_data)


class PassTestSerializerTestCase(TestCase):
    def setUp(self):
        self.u = CustomUser.objects.create_user(
            username='user',
            email='u@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.c = Categories.objects.create(name='cat')
        self.test = Test.objects.create(name='test1', owner=self.u)
        data = {
            'question': '2 + 6',
            'correct_answer': '8',
            'answer_1': '10',
            'answer_2': '23',
            'answer_3': '26',
            'value': 4,
            'test': self.test
        }
        self.question = Questions.objects.create(**data)
        data2 = {
            'question': '2 + 1',
            'correct_answer': '3',
            'answer_1': '10',
            'answer_2': '23',
            'answer_3': '26',
            'value': 4,
            'test': self.test
        }
        self.question2 = Questions.objects.create(**data2)

    def test_to_representation(self):
        questions = Questions.objects.filter(test=self.test.pk)
        self.maxDiff = None
        serialized_data = PassTestSerializer(questions).data
        expected_data = {
            'question_1': {
                'question': '2 + 1',
                'answers': ['26', '10', '23', '3'],
                'value': 4},
            'question_2': {
                'question': '2 + 6',
                'answers': ['26', '10', '23', '8'],
                'value': 4}}
        self.assertEqual(expected_data['question_1']['question'], serialized_data['question_1']['question'])
        self.assertEqual(expected_data['question_1']['value'], serialized_data['question_1']['value'])
        for i in serialized_data['question_1']:
            if i.startswith('answer'):
                self.assertTrue(serialized_data['question_1'][i] in expected_data['question_1']['answers'])

        for i in serialized_data['question_2']:
            if i.startswith('answer'):
                self.assertTrue(serialized_data['question_2'][i] in expected_data['question_2']['answers'])


class ContactUsSerializerTestCase(TestCase):
    def test_valid_data_works(self):
        data = {
            'name': 'cat',
            'email': 'a@test.com',
            'message': 'sassasd'
        }
        serialized_data = ContactUsSerializer(data=data)
        expected_data = {'name': 'cat', 'email': 'a@test.com', 'message': 'sassasd'}
        self.assertTrue(serialized_data.is_valid())
        self.assertEqual(expected_data, serialized_data.data)

    def test_not_valid_data_cause_errors(self):
        data = {
            'name': '*' * 256,
            'email': 'a',
            'message': ''
        }
        serialized_data = ContactUsSerializer(data=data)
        self.assertFalse(serialized_data.is_valid())
        self.assertEqual('Ensure this field has no more than 255 characters.', serialized_data.errors['name'][0])
        self.assertEqual('Invalid Email', serialized_data.errors['email'][0])
        self.assertEqual('Ensure this field has at least 5 characters.', serialized_data.errors['email'][1])
        self.assertEqual('Enter a valid email address.', serialized_data.errors['email'][2])
        self.assertEqual('This field may not be blank.', serialized_data.errors['message'][0])


class UpdateDestroyQuestionsSerializerTestCase(TestCase):
    def setUp(self):
        self.u = CustomUser.objects.create_user(
            username='user',
            email='u@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.c = Categories.objects.create(name='cat')
        self.test = Test.objects.create(name='test1', owner=self.u)
        self.data = {
            'question': '2 + 6',
            'correct_answer': '8',
            'answer_1': '10',
            'answer_2': '23',
            'answer_3': '26',
            'value': 4,
            'test': self.test
        }
        self.question = Questions.objects.create(**self.data)

    def test_serializer_works(self):
        serialized_data = UpdateDestroyQuestionsSerializer(self.question).data
        expected_data = {
            'question': '2 + 6',
            'correct_answer': '8',
            'answer_1': '10',
            'answer_2': '23',
            'answer_3': '26',
            'value': 4,
            'test': self.test.pk}
        self.assertEqual(expected_data, serialized_data)

    def test_test_field_is_read_only(self):
        serialized_data = UpdateDestroyQuestionsSerializer(data=self.data)
        expected_data = {
            'question': '2 + 6',
            'correct_answer': '8',
            'answer_1': '10',
            'answer_2': '23',
            'answer_3': '26',
            'value': 4}
        self.assertTrue(serialized_data.is_valid())
        self.assertEqual(expected_data, serialized_data.data)


class PassedTestsSerializerTestCase(TestCase):
    def setUp(self):
        self.u = CustomUser.objects.create_user(
            username='user',
            email='u@test.com',
            email_confirmed=True,
            password='testpassword1!'
        )
        self.test = Test.objects.create(
            name='test',
            owner=self.u,
            description='cat')
        self.data = {
            'test': self.test,
            'user': self.u,
            'grade': 26,
            'score': 5,
            'max_score': 1
        }
        self.passed_test = PassedTests.objects.create(**self.data)

    def test_serializer_returns_expected_data(self):
        serialized_data = PassedTestsSerializer(self.passed_test).data
        expected_data = {
            'id': self.passed_test.pk,
            'grade': '26.00',
            'score': 5,
            'max_score': 1,
            'data_passed': '2023-01-16T23:11:15.127637+02:00',
            'test': self.test.pk,
            'user': self.u.pk
        }
        for i in expected_data:
            if i != 'data_passed':
                self.assertEqual(expected_data[i], serialized_data[i])
