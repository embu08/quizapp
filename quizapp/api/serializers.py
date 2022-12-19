from main_app.models import Test, Questions, PassedTests
from random import shuffle
from rest_framework import serializers


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'


class CreateTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('name', 'description', 'is_public', 'access_by_link', 'show_results', 'category')


class UpdateTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = (
            'name', 'description', 'time_create', 'time_update', 'is_public', 'access_by_link', 'show_results',
            'category', 'owner')
        read_only_fields = ('owner',)


class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = '__all__'


class PassTestSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        questions = {}
        for n, i in enumerate(instance, 1):
            answers = [i.correct_answer, i.answer_1, i.answer_2, i.answer_3]
            shuffle(answers)
            questions_and_answers = {
                'question': i.question,
                'answer_1': answers.pop(),
                'answer_2': answers.pop(),
                'answer_3': answers.pop(),
                'answer_4': answers.pop(),
                'value': i.value
            }
            questions['question_' + str(n)] = questions_and_answers
        return questions


class UpdateDestroyQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = (
            'question', 'correct_answer', 'answer_1', 'answer_2', 'answer_3',
            'value', 'test'
        )
        read_only_fields = ('test',)


class PassedTestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassedTests
        fields = '__all__'
