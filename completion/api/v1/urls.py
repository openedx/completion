"""
API v1 URLs.
"""

from django.conf.urls import url

from . import views

app_name = 'v1'  # pylint: disable=invalid-name
urlpatterns = [
    url(r'^completion-batch', views.CompletionBatchView.as_view(), name='completion-batch'),
    url(r'^subsection-completion/{username}/{course_key}/{subsection_id}'.format(
        username=r'(?P<username>[^/]*)',
        course_key=r'(?P<course_key>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)',
        subsection_id=r'(?P<subsection_id>[^/]*)'
    ),  # noqa
        views.SubsectionCompletionView.as_view(),
        name='subsection-completion')
]
