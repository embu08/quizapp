from django.urls import include, path
from .views import *
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', home, name='home'),
]
