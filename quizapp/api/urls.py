from .views import *
from django.urls import path

app_name = 'api'

urlpatterns = [
    path('v1/tests/', TestAPIView.as_view(), name='tests'),
    path('v1/tests/my/', MyTestsAPIView.as_view(), name='tests_my'),
    path('v1/tests/create/', CreateTestAPIView.as_view(), name='tests_create'),
    path('v1/tests/<int:pk>/', UpdateDestroyTestAPIView.as_view(), name='tests_update'),
    path('v1/tests/<int:pk>/questions/', TestQuestionsCreateAPIView.as_view(), name='tests_questions'),
    path('v1/tests/<int:pk>/pass/', pass_test, name='pass'),
    path('v1/tests/passed/', PassedTestsAPIView.as_view(), name='passed'),
    path('v1/questions/<int:pk>/', UpdateDestroyQuestionsAPIView.as_view(), name='questions_update'),

    path('v1/users/create/', CreateUserAPIView.as_view(), name='create_user'),
    path('v1/users/update/', UpdateUserAPIView.as_view(), name='update_user'),
    path('v1/users/change-password/', ChangePasswordAPIView.as_view(), name='change_password'),

    path('v1/users/password-reset/', RestorePasswordAPIView.as_view(), name='password_reset'),
    path('v1/users/password-reset/<uidb64>/<token>/', PasswordTokenCheckAPIView.as_view(),
         name='password_reset_confirm'),
    path('v1/users/password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password_reset_complete'),


]
