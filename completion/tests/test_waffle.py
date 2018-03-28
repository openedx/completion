"""
Test feature-gating mechanics.
"""

from __future__ import absolute_import, division, unicode_literals

from contextlib import contextmanager

import mock

from .. import waffle


class MockSite(object):
    """
    Stand-in for a Django Site object.
    """
    def __init__(self, config=None):
        if config:
            self._configuration = config

    @property
    def configuration(self):
        """
        Returns the MockSiteConfig attribute of this site, raises
        MockSiteConfig.DoesNotExist if none exists.
        """
        if hasattr(self, '_configuration'):
            return self._configuration
        raise MockSiteConfig.DoesNotExist

    @configuration.setter
    def configuration(self, config):
        """
        Sets the configuration attribute of this site.
        """
        self._configuration = config


class MockSiteConfig(object):
    """
    Stand-in for a Django SiteConfiguration object.
    """
    def __init__(self, **kwargs):
        self.data = {k: v for k, v in kwargs.items()}

    def get_value(self, key, default):
        """
        Returns the value corresponding to `key` in this object's data attribute.
        """
        return self.data.get(key, default)

    class DoesNotExist(Exception):
        """
        Raised if a MockSiteConfig object does not exist on a MockSite.
        """
        pass


@contextmanager
def patch_get_current_site(configuration=None):
    """
    Monkey-patches the `get_current_site()` function and `SiteConfiguration`
    attributes of the waffle module.
    """
    site = MockSite(configuration)

    waffle.get_current_site = mock.Mock(return_value=site)
    waffle.SiteConfiguration = MockSiteConfig

    yield

    del waffle.get_current_site
    del waffle.SiteConfiguration


def test_site_disables_visual_progress_is_disabled():
    configuration = MockSiteConfig(**{waffle.ENABLE_SITE_VISUAL_PROGRESS: False})
    with patch_get_current_site(configuration):
        actual_value = waffle.site_disables_visual_progress()
        assert actual_value is True


def test_site_disables_visual_progress_no_site_config():
    with patch_get_current_site():
        actual_value = waffle.site_disables_visual_progress()
        assert actual_value is False


def test_site_disables_visual_progress_key_missing():
    with patch_get_current_site(MockSiteConfig()):
        actual_value = waffle.site_disables_visual_progress()
        assert actual_value is False
