"""
Api URLs.
"""

from django.urls import include  # pragma: no cover
from django.urls import path

app_name = 'completion'  # pylint: disable=invalid-name
urlpatterns = [
    path('v1/', include('completion.api.v1.urls')),
]
