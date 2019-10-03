"""
Module for instructor models.
"""
from django.contrib.auth.models import User
from django.db import models

from openedx.core.djangoapps.course_groups.models import CourseUserGroup


class CohortAssigment(models.Model):
    """
    Link between staff(user) and cohort.
    """
    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    cohort = models.ForeignKey(CourseUserGroup, db_index=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'instructor'
        unique_together = (('cohort', 'user'), )
