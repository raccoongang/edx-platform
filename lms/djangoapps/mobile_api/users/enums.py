from enum import Enum
from django.utils.functional import classproperty


class EnrollmentStatuses(Enum):
    """

    """

    ALL = 'all'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    EXPIRED = 'expired'

    # values = [ALL, IN_PROGRESS, COMPLETED, EXPIRED]

    @classproperty
    def values(cls):
        return [e.value for e in cls]
