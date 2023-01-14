from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_decode
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, status, mixins
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from quizapp.local_settings import EMAIL_FROM
from django.core.mail import EmailMessage

from users.models import CustomUser
from users.tokens import account_activation_token
from .permissions import EmailIsConfirmed, UserIsOwnerOrStaff

from .serializers import TestSerializer, CreateTestSerializer, UpdateTestSerializer, QuestionsSerializer, \
    PassTestSerializer, UpdateDestroyQuestionsSerializer, PassedTestsSerializer, CreateUserSerializer, \
    UpdateUserSerializer, ChangePasswordSerializer, RestorePasswordSerializer, SetNewPasswordSerializer, \
    ContactUsSerializer
from main_app.models import Test, Questions, PassedTests


@api_view(['POST'])
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.email_confirmed = True
        user.save()
        return Response({'status': 'success', 'details': 'Your email was successfully confirmed!'},
                        status=status.HTTP_200_OK)
    else:
        return Response({'status': 'failure', 'details': 'Activation link is invalid!'},
                        status=status.HTTP_400_BAD_REQUEST)


class TestAPIView(generics.ListAPIView):
    serializer_class = TestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['id', 'name', 'description', 'category__name', 'owner__username', 'show_results']
    search_fields = ['name', 'description', 'category__name', 'owner__username']
    ordering_fields = ['name', 'category__name', 'owner__username', 'time_create', 'time_update']

    def get_queryset(self):
        tests_with_questions = [b[0] for b in [q for q in Questions.objects.values_list('test').distinct()]]
        return Test.objects.filter(pk__in=tests_with_questions, is_public=True).select_related('category',
                                                                                               'owner').order_by(
            '-time_update')


@api_view(['POST'])
def contact_us(request):
    data = {}
    for k in request.data:
        data[k] = request.data[k]
    if request.user.is_authenticated:
        data.setdefault('name', request.user.username)
        data.setdefault('email', request.user.email)
    serializer = ContactUsSerializer(data=data)
    if serializer.is_valid():
        mail_subject = f'A Message from Quizapp Contact Us Form'
        message = f"Sender's name: {serializer.data['name']}, sender's email: {serializer.data['email']}\nMessage:\n{serializer.data['message']}"
        email = EmailMessage(mail_subject, message, to=[EMAIL_FROM])
        if email.send():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': "Mail wasn't sent, we are working on fixing this issue."},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTestsAPIView(generics.ListAPIView):
    serializer_class = TestSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['id', 'name', 'description', 'category__name', 'show_results']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'category__name', 'time_create', 'time_update']

    def get_queryset(self):
        return Test.objects.filter(owner=self.request.user.pk).order_by('-time_update')


class CreateTestAPIView(generics.CreateAPIView):
    serializer_class = CreateTestSerializer
    permission_classes = (IsAuthenticated, EmailIsConfirmed)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UpdateDestroyTestAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateTestSerializer
    permission_classes = (IsAuthenticated, UserIsOwnerOrStaff)

    def get_queryset(self, *args, **kwargs):
        return Test.objects.filter(pk=self.kwargs['pk'])


class TestQuestionsCreateAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionsSerializer
    permission_classes = (IsAuthenticated, UserIsOwnerOrStaff)

    def get_object(self):
        return Test.objects.get(pk=self.kwargs['pk'])

    def get_queryset(self, *args, **kwargs):
        return Questions.objects.filter(test=self.kwargs['pk']).order_by('pk')

    def perform_create(self, serializer):
        serializer.save(test_id=self.kwargs['pk'])


@api_view(['GET', 'POST'])
def pass_test(request, pk):
    try:
        test = Test.objects.get(pk=pk)
    except Test.DoesNotExist:
        test = None
    questions = Questions.objects.filter(test=pk)
    if not (questions and test) or ((not test.access_by_link and not test.is_public) and (
            request.user != test.owner and not request.user.is_staff)):
        msg = 'You cannot pass the test.'
        if not test:
            msg += ' Test does not exist.'
        else:
            if not questions:
                msg += ' Test have no questions.'
            elif not test.access_by_link and not test.is_public:
                msg += ' Test is not accessible.'
        return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = PassTestSerializer(questions)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        answers = {}
        show_results = Test.objects.filter(pk=pk).values('show_results')[0]['show_results']
        correct, total_questions = 0, len(questions)
        result, max_result = 0, 0

        # user answers
        for i in request.data:
            if i.startswith('question_'):
                answers[i] = request.data.get(i).lower()

        correct_answers = {'question_' + str(n): v.correct_answer.lower() for n, v in enumerate(questions, 1)}

        # result, max_result
        for k, v in correct_answers.items():
            user_answer = answers.get(k, None)
            value = questions[int(k[-1]) - 1].value
            max_result += value
            if user_answer == v:
                result += value
                correct += 1

        to_return = {
            'results': {
                'grade': round(result / max_result * 100, 2),
                'scored': result,
                'max_result': max_result,
                'total_questions': total_questions,
                'correct_answers': correct
            },
        }
        if show_results:
            to_return_questions = {}
            for n, v in enumerate(questions, 1):
                to_return_questions['question_' + str(n)] = {
                    'question': v.question,
                    'your_answer': answers.get('question_' + str(n), None),
                    'correct_answer': v.correct_answer,
                    'value': v.value,
                }
            to_return.update(to_return_questions)

        if request.user.is_authenticated:
            PassedTests.objects.create(test=test,
                                       user=CustomUser.objects.get(pk=request.user.pk),
                                       grade=round(result / max_result * 100, 2),
                                       score=int(result),
                                       max_score=int(max_result))

        return Response(to_return, status=status.HTTP_200_OK)


class UpdateDestroyQuestionsAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateDestroyQuestionsSerializer
    permission_classes = (IsAuthenticated, UserIsOwnerOrStaff)

    def get_queryset(self, *args, **kwargs):
        return Questions.objects.filter(pk=self.kwargs['pk'])


class PassedTestsAPIView(generics.ListAPIView):
    serializer_class = PassedTestsSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['test__name', 'grade', 'data_passed']
    ordering_fields = ['test__name', 'grade', 'data_passed']

    def get_queryset(self):
        return PassedTests.objects.filter(user=self.request.user.pk).order_by('-data_passed', )


class CreateUserAPIView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer


class UpdateUserAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.pk)


class ChangePasswordAPIView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password. Note that both fields are case-sensitive."]},
                                status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'message': 'Password updated successfully',
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RestorePasswordAPIView(GenericAPIView):
    serializer_class = RestorePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'success': 'Password reset link has been sent to your email, if you are already registered.'},
                        status=status.HTTP_200_OK)


class PasswordTokenCheckAPIView(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(token=token, user=user):
                return Response({'error': 'Token is not valid anymore, please request a new one.'},
                                status=status.HTTP_401_UNAUTHORIZED)

            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token},
                            status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as e:
            return Response({'error': 'Token is not valid anymore, please request a new one.'},
                            status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPIView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)
