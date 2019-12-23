"""
Utility functions for validating model fields.
"""

from datetime import date


def validate_date_of_birth(value):
    """
    Validate date of birth which should be in the past.

    :param value: DateTime object.
    """
    if value is not None:
        if value > date.today():
            raise ValueError("Date of birth should be in the past")
