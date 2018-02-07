"""
Permissions classes for the API.
"""
from __future__ import unicode_literals

from rest_framework.permissions import BasePermission


class IsStaffOrOwner(BasePermission):
    """
    Permission that allows access to admin users or the owner of an object.
    The owner is considered the User object represented by obj.user.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user

    def has_permission(self, request, view):
        user = request.user
        return user.is_staff \
            or (user.username == request.GET.get('username')) \
            or (user.username == getattr(request, 'data', {}).get('username')) \
            or (user.username == getattr(request, 'data', {}).get('user')) \
            or (user.username == getattr(view, 'kwargs', {}).get('username'))
