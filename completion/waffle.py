"""
This module contains various configuration settings via
waffle switches for the completion app.
"""


from edx_toggles.toggles import WaffleSwitch

# The switch and namespace names variables are preserved for backward compatibility
WAFFLE_NAMESPACE = "completion"
ENABLE_COMPLETION_TRACKING = "enable_completion_tracking"
# .. toggle_name: completion.enable_completion_tracking
# .. toggle_implementation: WaffleSwitch
# .. toggle_default: False
# .. toggle_description: Indicates whether or not to track completion of individual blocks. Keeping this disabled
#   will prevent creation of BlockCompletion objects in the database, as well as preventing completion-related
#   network access by certain xblocks.
# .. toggle_use_cases: open_edx
ENABLE_COMPLETION_TRACKING_SWITCH = WaffleSwitch(
    f"{WAFFLE_NAMESPACE}.{ENABLE_COMPLETION_TRACKING}",
    module_name=__name__,
)
ENABLE_PROGRESS_TRACKING_EVENTS = "enable_progress_tracking_events"
# .. toggle_name: completion.enable_progress_tracking_events
# .. toggle_implementation: WaffleSwitch
# .. toggle_default: False
# .. toggle_description: Indicates whether or not to track progress events of individual blocks.
ENABLE_PROGRESS_TRACKING_EVENTS_SWITCH = WaffleSwitch(
    f"{WAFFLE_NAMESPACE}.{ENABLE_PROGRESS_TRACKING_EVENTS}",
    module_name=__name__,
)
