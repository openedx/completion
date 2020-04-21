"""
Settings for the completion app.
"""

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
    # Once a complete-by-viewing (e.g. HTML) block has been visible on-screen for this many ms, mark it complete
    settings.COMPLETION_BY_VIEWING_DELAY_MS = 5000
    # Once a user has watched this percentage of a video, mark it as complete:
    # (0.0 = 0%, 1.0 = 100%)
    settings.COMPLETION_VIDEO_COMPLETE_PERCENTAGE = 0.95
