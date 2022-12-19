from .views import *
from django.urls import path

app_name = 'api'

urlpatterns = [
    path('v1/tests/', TestAPIView.as_view(), name='tests'),
    path('v1/tests/my/', MyTestsAPIView.as_view(), name='tests_my'),
    path('v1/tests/create/', CreateTestAPIView.as_view(), name='tests_create'),
    path('v1/tests/<int:pk>/', UpdateDestroyTestAPIView.as_view(), name='tests_update'),
    path('v1/tests/<int:pk>/questions/', TestQuestionsCreateAPIView.as_view(), name='tests_questions'),
    path('v1/tests/<int:pk>/pass/', pass_test, name='tests_pass'),
    path('v1/tests/passed_tests/', PassedTestsAPIView.as_view(), name='passed_tests'),
    path('v1/questions/<int:pk>/', UpdateDestroyQuestionsAPIView.as_view(), name='questions_update'),

]
