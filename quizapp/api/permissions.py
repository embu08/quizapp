from rest_framework import permissions

from main_app.models import Questions, Test


class EmailIsConfirmed(permissions.BasePermission):
    message = 'Please verify your email address. You cannot add tests.'

    def has_permission(self, request, view):
        return request.user.email_confirmed


class UserIsOwnerOrStaff(permissions.BasePermission):
    message = "Object doesn't exist or you are not the owner."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_staff:
            if isinstance(obj, Test):
                return request.user == obj.owner
            elif isinstance(obj, Questions):
                return request.user == obj.test.owner
