"""
Api URLs.
"""

from django.conf.urls import include
from django.urls import path

app_name = 'completion'  # pylint: disable=invalid-name
urlpatterns = [
    path('v1/', include('completion.api.v1.urls')),
]
