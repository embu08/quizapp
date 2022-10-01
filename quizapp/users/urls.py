from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='sign_up'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('<int:pk>/my-profile/', MyProfileView.as_view(), name='my_profile'),
    path('<int:pk>/my-profile/update/', UpdateUserView.as_view(), name='my_profile_update'),
    path('<int:pk>/my-profile/password-change/', ChangePasswordView.as_view(), name='password_change'),
    path('activate/<uidb64>/<token>', activate, name='activate')


    # password reset
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/',
    #      auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_done.html'),
    #      name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/',
    #      auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'),
    #      name='password_reset_complete'),
]
