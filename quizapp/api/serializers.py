from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core import validators
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, smart_bytes, force_str
from rest_framework.exceptions import AuthenticationFailed

from main_app.models import Test, Questions, PassedTests
from random import shuffle
from rest_framework import serializers

from users.models import CustomUser
from users.tokens import account_activation_token

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


class CreateTestSerializer(serializers.HyperlinkedModelSerializer):
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


class ContactUsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, min_length=2)
    email = serializers.EmailField(min_length=5, max_length=255,
                                   validators=[validators.EmailValidator(message="Invalid Email")])
    message = serializers.CharField(min_length=1, max_length=1000)

    class Meta:
        fields = '__all__'


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
        fields = ('username', 'email', 'first_name', 'last_name', 'email', 'email_confirmed')
        read_only_fields = ('username', 'email', 'email_confirmed')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = CustomUser


class RestorePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ('email',)

    def validate(self, attrs):
        email = attrs['email']
        request = self.context.get('request')
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relative_link = reverse('api:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            abs_url = ('https' if request.is_secure() else 'http') + '://' + current_site + relative_link
            email_body = f'Hi {user.username},\nTo initiate the password reset process for your account, click the link below: \n\n' \
                         f'{abs_url}' \
                         f"\n\nIf clicking the link above doesn't work, please copy and paste the URL in a new browser window instead." \
                         f"\n\nBest regards,\nQuizapp team."
            email = EmailMessage(subject='Reset your password', body=email_body, to=[user.email])
            if email.send():
                print('sent')
            else:
                print("doesn't")
            print(dir(email))

        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ('password', 'token', 'uidb64')

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user=user, token=token):
                print('if')
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            print('exception', e)
            raise AuthenticationFailed('The reset link is invalid', 401)
