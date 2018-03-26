"""
API v1 URLs.
"""

from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^completion-batch', views.CompletionBatchView.as_view(), name='completion-batch'),
    url(r'^subsection-completion/{username}/{course_key}/{subsection_id}'.format(
        username=r'(?P<username>[^/]*)',
        course_key=r'(?P<course_key>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)',
        subsection_id=r'(?P<subsection_id>[^/]*)'
        ),
        views.SubsectionCompletionView.as_view(),
        name='subsection-completion')
]
