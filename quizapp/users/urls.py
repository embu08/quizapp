from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='sign_up'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('my-profile/', MyProfileView.as_view(), name='my_profile'),
    path('my-profile/update/', UpdateUserView.as_view(), name='my_profile_update'),
]
