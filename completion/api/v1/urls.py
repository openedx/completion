"""
API v1 URLs.
"""
from django.urls import path, re_path

from . import views

app_name = 'v1'  # pylint: disable=invalid-name
urlpatterns = [
    path('completion-batch', views.CompletionBatchView.as_view(), name='completion-batch'),
    re_path(r'^subsection-completion/{username}/{course_key}/{subsection_id}'.format(  # pylint: disable=consider-using-f-string
        username=r'(?P<username>[^/]*)',
        course_key=r'(?P<course_key>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)',
        subsection_id=r'(?P<subsection_id>[^/]*)'
    ),  # noqa
        views.SubsectionCompletionView.as_view(),
        name='subsection-completion')
]
