from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import CustomUser
from .permissions import EmailIsConfirmed, UserIsOwnerOrStaff

from .serializers import TestSerializer, CreateTestSerializer, UpdateTestSerializer, QuestionsSerializer, \
    PassTestSerializer, UpdateDestroyQuestionsSerializer, PassedTestsSerializer, CreateUserSerializer, \
    UpdateUserSerializer
from main_app.models import Test, Questions, PassedTests


class TestAPIView(generics.ListAPIView):
    queryset = Test.objects.filter(is_public=True).order_by('pk')
    serializer_class = TestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['id', 'name', 'description', 'category', 'owner', 'show_results']
    search_fields = ['id', 'name', 'description', 'category', 'owner']
    ordering_fields = ['id', 'name', 'category', 'owner', 'time_create', 'time_update']


class MyTestsAPIView(generics.ListAPIView):
    serializer_class = TestSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        print(self.request.user)
        return Test.objects.filter(owner=self.request.user.pk).order_by('pk')


class CreateTestAPIView(generics.ListCreateAPIView):
    queryset = Test.objects.filter(is_public=True).order_by('pk')
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

    def get_queryset(self, *args, **kwargs):
        return Questions.objects.filter(test=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(test_id=self.kwargs['pk'])


@api_view(['GET', 'POST'])
def pass_test(request, pk):
    test = Test.objects.get(pk=pk)
    if not test.access_by_link and not test.is_public and request.user != test.owner and not request.user.is_staff:
        return Response({'detail': 'The test does not exist or it is not accessible.'},
                        status=status.HTTP_404_NOT_FOUND)

    questions = Questions.objects.filter(test=pk)

    if request.method == 'GET':
        serializer = PassTestSerializer(questions)
        return Response(serializer.data)

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
                'your_grade': round(result / max_result * 100, 2),
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
                    'your_answer': answers['question_' + str(n)],
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

        return Response(to_return)


class UpdateDestroyQuestionsAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateDestroyQuestionsSerializer
    permission_classes = (IsAuthenticated, UserIsOwnerOrStaff)

    def get_queryset(self, *args, **kwargs):
        return Questions.objects.filter(pk=self.kwargs['pk'])


class PassedTestsAPIView(generics.ListAPIView):
    serializer_class = PassedTestsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PassedTests.objects.filter(user=self.request.user.pk).order_by('-data_passed', )


class CreateUserAPIView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer


class UpdateUserAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.pk)
