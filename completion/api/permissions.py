"""
Permissions classes for the API.
"""


from django.http import Http404
from rest_framework.permissions import BasePermission


class IsStaffOrOwner(BasePermission):
    """
    Permission that allows access to admin users or the owner of an object.
    The owner is considered the User object represented by obj.user.

    Copied from edx-platform/openedx/core/lib/api/permissions.py
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


class IsUserInUrl(BasePermission):
    """
    Permission that checks to see if the request user matches the user in the URL.
    """

    def has_permission(self, request, view):
        """
        Returns true if the current request is by the user themselves.

        Note: a 404 is returned for non-staff instead of a 403. This is to prevent
        users from being able to detect the existence of accounts.
        """
        url_username = request.parser_context.get('kwargs', {}).get('username', '')
        if request.user.username.lower() != url_username.lower():
            if request.user.is_staff:
                return False  # staff gets 403
            raise Http404()
        return True
