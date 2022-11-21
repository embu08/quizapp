from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from .permissions import EmailIsConfirmed, UserIsOwnerOrStaff

from .serializers import *


class TestAPIView(generics.ListAPIView):
    queryset = Test.objects.filter(is_public=True).order_by('pk')
    serializer_class = TestSerializer


class CreateTestAPIView(generics.ListCreateAPIView):
    queryset = Test.objects.filter(is_public=True).order_by('pk')
    serializer_class = CreateTestSerializer
    permission_classes = (IsAuthenticated, EmailIsConfirmed)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UpdateDestroyTestAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateTestSerializer
    permission_classes = (UserIsOwnerOrStaff, )

    def get_queryset(self, *args, **kwargs):
        return Test.objects.filter(pk=self.kwargs['pk'])
