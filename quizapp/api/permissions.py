from rest_framework import permissions


class EmailIsConfirmed(permissions.BasePermission):
    message = 'Please verify your email address. You cannot add tests.'

    def has_permission(self, request, view):
        return request.user.email_confirmed


class UserIsOwnerOrStaff(permissions.BasePermission):
    message = "Test doesn't exist or you are not the owner."

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user.is_staff
