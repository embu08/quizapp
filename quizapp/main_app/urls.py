from django.urls import path
from .views import *
from django.views.decorators.cache import cache_page

app_name = 'tests'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('tests/', ShowAllTestsListVIew.as_view(), name='tests'),
    path('tests/my/', ShowMyTestsListVIew.as_view(), name='my_tests'),
    path('tests/add/', AddTestView.as_view(), name='add'),
    path('pass-test/<int:pk>', pass_test, name='pass'),
    path('tests/<int:pk>/', TestDetailView.as_view(), name='test_detail'),
    path('tests/<int:pk>/questions/edit/', TestQuestionsEditView.as_view(), name='test_questions_edit'),

]
