"""
Settings for the completion app.
"""

from __future__ import absolute_import, unicode_literals

from os.path import abspath, dirname, join


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


USE_TZ = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'completion',
)

LOCALE_PATHS = [
    root('completion', 'conf', 'locale'),
]

ROOT_URLCONF = 'completion.urls'

SECRET_KEY = 'insecure-secret-key'


def plugin_settings(settings):  # pylint: disable=unused-argument
    """
    Defines completion-specific settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    pass
