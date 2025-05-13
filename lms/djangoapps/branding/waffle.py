"""
Configuration for features of Branding
"""
from edx_toggles.toggles import WaffleFlag

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

# Namespace for Branding MFE waffle flags.
WAFFLE_FLAG_NAMESPACE = "catalog_mfe"

# .. toggle_name: catalog_mfe.enabled
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: Waffle flag to enable to redirect user to catalog mfe
# .. toggle_use_cases: open_edx
# .. toggle_creation_date: 2022-10-11
# .. toggle_tickets: AU-879
ENABLE_CATALOG_MFE = WaffleFlag(
    f"{WAFFLE_FLAG_NAMESPACE}.enabled",
    __name__,
)


def catalog_mfe_enabled():
    """
    Determine if Catalog MFE is enabled, replacing student_dashboard
    """

    return configuration_helpers.get_value(
        "ENABLE_CATALOG_MFE",
        ENABLE_CATALOG_MFE.is_enabled(),
    )
