from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from .permissions import EmailIsConfirmed, UserIsOwnerOrStaff

from .serializers import *


class TestAPIView(generics.ListAPIView):
    queryset = Test.objects.filter(is_public=True).order_by('pk')
    serializer_class = TestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['id', 'name', 'description', 'category', 'owner', 'show_results']
    search_fields = ['id', 'name', 'description', 'category', 'owner']
    ordering_fields = ['id', 'name', 'category', 'owner', 'time_create', 'time_update']


class MyTestsAPIView(generics.ListAPIView):
    serializer_class = TestSerializer
    permission_classes = (IsAuthenticated, UserIsOwnerOrStaff)

    def get_queryset(self):
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
    serializers = QuestionsSerializer

    def get_queryset(self, *args, **kwargs):
        return Questions.objects.filter(test=self.kwargs['pk'])
