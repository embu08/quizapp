from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from main_app.models import Test, Questions, PassedTests
from random import shuffle
from rest_framework import serializers

from users.models import CustomUser
from users.tokens import account_activation_token

# I know this is awful XD
activate_email_message = {}


def activate_email(user, request):
    mail_subject = 'Activate your user account.'
    message = render_to_string('users/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    if email.send():
        activate_email_message['message'] = f'Dear {user}, we sent activation link to your email ' \
                                            f'{user.email}, please click on it to confirm and complete registration.'
    else:
        activate_email_message['message'] = f'A problem while sending verification link' \
                                            f' to {user.email} occurred, check if you typed it correctly!'


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


class CreateUserSerializer(serializers.ModelSerializer):
    email_sending_message = serializers.SerializerMethodField()

    def get_email_sending_message(self, obj):
        return activate_email_message['message']

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'email_sending_message')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        activate_email(user, self.context['request'])
        to_return = {'username': user.username,
                     'first_name': user.first_name,
                     'last_name': user.last_name,
                     'email': user.email}
        return to_return


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'email', 'email_confirmed', 'password')
        read_only_fields = ('username', 'email', 'email_confirmed')
        extra_kwargs = {'password': {'write_only': True}}
