import quizapp.settings
from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls', namespace='tests')),
    path('users/', include('users.urls', namespace='users')),

    path('api/', include('api.urls', namespace='api')),
    path('api/v1/session_auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'api/v1/auth/', include('djoser.urls')),
    re_path(r'^api/v1/auth/', include('djoser.urls.authtoken')),

    path('captcha/', include('captcha.urls')),
]

if quizapp.local_settings.DEBUG:
    urlpatterns = [path('__debug__/', include('debug_toolbar.urls'))] + urlpatterns
