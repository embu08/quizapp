from django.urls import path, include, re_path
from .views import *

app_name = 'api'

urlpatterns = [
    path('v1/tests/', TestAPIView.as_view(), name='tests'),
    path('v1/tests/my/', MyTestsAPIView.as_view(), name='tests_my'),
    path('v1/tests/create/', CreateTestAPIView.as_view(), name='tests_create'),
    path('v1/tests/<int:pk>/', UpdateDestroyTestAPIView.as_view(), name='tests_update'),

    path('v1/tests/<int:pk>/questions/', UpdateDestroyTestAPIView.as_view(), name='tests_update'),

]
