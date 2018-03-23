"""
Api URLs.
"""

from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url

urlpatterns = [
    url(r'^v1/', include('completion.api.v1.urls', namespace='v1')),
]
