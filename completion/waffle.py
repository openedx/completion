"""
This module contains various configuration settings via
waffle switches for the completion app.
"""


from edx_toggles.toggles import WaffleSwitch, WaffleSwitchNamespace

# Namespace
WAFFLE_NAMESPACE = "completion"


def waffle():
    """
    Returns the namespaced, cached, audited Waffle class for completion.
    """
    return WaffleSwitchNamespace(name=WAFFLE_NAMESPACE, log_prefix="completion: ")


# Switches

# The switch name variable is preserved for backward compatibility
ENABLE_COMPLETION_TRACKING = "enable_completion_tracking"
# .. toggle_name: completion.enable_completion_tracking
# .. toggle_implementation: WaffleSwitch
# .. toggle_default: False
# .. toggle_description: Indicates whether or not to track completion of individual blocks. Keeping this disabled
#   will prevent creation of BlockCompletion objects in the database, as well as preventing completion-related
#   network access by certain xblocks.
# .. toggle_use_cases: open_edx
ENABLE_COMPLETION_TRACKING_SWITCH = WaffleSwitch(
    waffle(), ENABLE_COMPLETION_TRACKING, module_name=__name__
)
