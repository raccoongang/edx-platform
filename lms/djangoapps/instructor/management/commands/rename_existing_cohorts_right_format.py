"""
Rename cohorts to right format for rg_instructor_analytics app
"""
from __future__ import print_function, unicode_literals

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from student.roles import CourseStaffRole


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Find cohort and compare its name with first part of user's email
        If they match - check users role and rename cohort to format
        "username course_key cohort_name"
        """
        cohorts = CourseUserGroup.objects.all()
        for cohort in cohorts:
            users = User.objects.filter(email__contains=cohort.name)
            for user in users:
                first_part_email = user.email.split('@')[0]
                if cohort.name == first_part_email:
                    staff_role = CourseStaffRole(cohort.course_id)
                    if staff_role.has_user(user):
                        course_key = cohort.course_id.to_deprecated_string()
                        print('=' * 80)
                        print(u'Cohort name: {}'.format(cohort.name))
                        print(u'Username: {}'.format(user.username))
                        print(u'Course KEY: {}'.format(course_key))
                        cohort.name = u"{username} {course_key} {name}".format(
                            username=user.username,
                            course_key=course_key,
                            name=cohort.name
                        )
                        cohort.save()
