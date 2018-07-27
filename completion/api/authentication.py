"""
Authentication classes for the API.
"""
from __future__ import absolute_import, unicode_literals

from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
