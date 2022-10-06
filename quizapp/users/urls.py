from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='sign_up'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('<int:pk>/my-profile/', MyProfileView.as_view(), name='my_profile'),
    path('<int:pk>/my-profile/update/', UpdateUserView.as_view(), name='my_profile_update'),
    path('<int:pk>/my-profile/password-change/', ChangePasswordView.as_view(), name='password_change'),
    path('activate/<uidb64>/<token>', activate, name='activate'),

    path('password_reset/',
         PasswordResetViewCustom.as_view(),
         name='password_reset'),

    path('password_reset_done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmViewCustom.as_view(),
         name='password_reset_confirm'),
]

app_name = 'users'
