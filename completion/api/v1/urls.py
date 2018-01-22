"""
API v1 URLs.
"""

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^completion-batch', views.CompletionBatchView.as_view(), name='completion-batch'),
]
