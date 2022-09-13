from django.urls import include, path
from .views import *
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', home, name='home'),
    path('create-test/', create_test_view, name='create'),
    path('show-tests/', ShowAllTests.as_view(), name='show-test')
]
