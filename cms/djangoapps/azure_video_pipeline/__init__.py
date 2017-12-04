from django.conf import settings
from mock import Mock

modules_to_mock = getattr(settings, 'MOCKED_MODULES', None)
if modules_to_mock:
    import sys
    for module_name in modules_to_mock:
        sys.modules[module_name] = Mock()

else:
    import jobs  # noqa: F401
