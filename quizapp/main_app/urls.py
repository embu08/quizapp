from django.urls import path
from .views import *
from django.views.decorators.cache import cache_page

app_name = 'tests'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('show-tests/', ShowAllTestsListVIew.as_view(), name='tests'),
    path('create-test/', create_test, name='create'),
    path('edit-test/<int:pk>', edit_test, name='edit'),
    path('pass-test/<int:pk>', pass_test, name='pass'),
]
