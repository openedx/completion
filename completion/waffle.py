"""
This module contains various configuration settings via
waffle switches for the completion app.
"""
from __future__ import absolute_import, unicode_literals

try:
    from openedx.core.djangoapps.waffle_utils import WaffleSwitchNamespace
except ImportError:
    pass

# Namespace
WAFFLE_NAMESPACE = 'completion'


def waffle():
    """
    Returns the namespaced, cached, audited Waffle class for completion.
    """
    return WaffleSwitchNamespace(name=WAFFLE_NAMESPACE, log_prefix='completion: ')
