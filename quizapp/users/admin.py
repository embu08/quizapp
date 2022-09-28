from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import *
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = RegisterUserForm
    form = UpdateUserForm
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_active', 'last_login')
    list_filter = ('username', 'email', 'is_staff', 'is_active', 'last_login')
    # this for changing user in admin
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name'), 'classes': ('collapse',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    # this for adding user in admin
    add_fieldsets = (
        (None, {
            'fields': (
                'username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
