from django.urls import path
from .views import *

app_name = 'api'

urlpatterns = [
    path('v1/test/', TestAPIView.as_view(), name='test'),
    path('v1/test/create/', CreateTestAPIView.as_view(), name='test_create'),
    path('v1/test/<int:pk>/', UpdateDestroyTestAPIView.as_view(), name='test_update'),
]
