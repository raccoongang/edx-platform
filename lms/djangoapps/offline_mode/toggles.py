"""
Toggles for the Offline Mode Experience.
"""

from edx_toggles.toggles import WaffleFlag

# .. toggle_name: offline_node.media_generation_enabled
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: This flag enables media generation for offline mode.
# .. toggle_warnings: None
# .. toggle_use_cases: opt_out
# .. toggle_creation_date: 2024-05-20
# .. toggle_target_removal_date: None
MEDIA_GENERATION_ENABLED = WaffleFlag(
    'offline_node.media_generation_enabled', module_name=__name__, log_prefix='offline_mode'
)
