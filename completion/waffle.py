"""
This module contains various configuration settings via
waffle switches for the completion app.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from openedx.core.djangoapps.waffle_utils import CourseWaffleFlag, WaffleFlagNamespace, WaffleSwitchNamespace
    from openedx.core.djangoapps.site_configuration.models import SiteConfiguration
    from openedx.core.djangoapps.theming.helpers import get_current_site
except ImportError:
    pass

# Namespace
WAFFLE_NAMESPACE = 'completion'

# Switches

# Full name: completion.enable_completion_tracking
# Indicates whether or not to track completion of individual blocks.  Keeping
# this disabled will prevent creation of BlockCompletion objects in the
# database, as well as preventing completion-related network access by certain
# xblocks.
ENABLE_COMPLETION_TRACKING = 'enable_completion_tracking'

# Full name completion.enable_visual_progress
# Overrides completion.enable_course_visual_progress
# Acts as a global override -- enable visual progress indicators
# sitewide.
ENABLE_VISUAL_PROGRESS = 'enable_visual_progress'

# Full name completion.enable_course_visual_progress
# Acts as a course-by-course enabling of visual progress
# indicators, e.g. updated 'resume button' functionality
ENABLE_COURSE_VISUAL_PROGRESS = 'enable_course_visual_progress'

# SiteConfiguration visual progress enablement
ENABLE_SITE_VISUAL_PROGRESS = 'enable_site_visual_progress'


def waffle():
    """
    Returns the namespaced, cached, audited Waffle class for completion.
    """
    return WaffleSwitchNamespace(name=WAFFLE_NAMESPACE, log_prefix='completion: ')


def waffle_flag():
    """
    Returns the namespaced, cached, audited Waffle flags dictionary for Completion.

    By default, disable visual progress. Can be enabled on a course-by-course basis.
    And overridden site-globally by ENABLE_VISUAL_PROGRESS

    """
    namespace = WaffleFlagNamespace(name=WAFFLE_NAMESPACE, log_prefix=u'completion: ')
    return CourseWaffleFlag(
        namespace,
        ENABLE_COURSE_VISUAL_PROGRESS,
        flag_undefined_default=False
    )


def visual_progress_enabled(course_key):
    """
    Exposes the visual progress feature based on waffle and SiteConfiguration objects.  To return True,
    the following must hold:
      - ENABLE_COMPLETION_TRACKING: must be activated.
      - The current Site's configuration must not explicitly disable this feature.
      - The ENABLE_VISUAL_PROGRESS switch must be activate, or if not, the course waffle flag for this feature
      must be activated.
    This returns False otherwise.
    """
    if not waffle().is_enabled(ENABLE_COMPLETION_TRACKING):
        return False

    if site_disables_visual_progress():
        return False

    # Site-aware global override
    if not waffle().is_enabled(ENABLE_VISUAL_PROGRESS):
        # Course enabled
        return waffle_flag().is_enabled(course_key)

    return True


def site_disables_visual_progress():
    """
    Returns True if and only if the SiteConfiguration for the current Site
    explicitly disables visual progress.
    """
    try:
        site_config = get_current_site().configuration
    except SiteConfiguration.DoesNotExist:
        return False
    return not site_config.get_value(ENABLE_SITE_VISUAL_PROGRESS, True)
