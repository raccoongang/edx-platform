"""
Course category enrollment utils.
"""
import logging

from django.conf import settings

from django.core.mail import send_mail
from courseware.courses import get_courses
from enrollment.api import add_enrollment
from enrollment.errors import (
    CourseEnrollmentClosedError, CourseEnrollmentFullError,
    CourseEnrollmentExistsError, UserNotFoundError, InvalidEnrollmentAttribute,
)
from edxmako.shortcuts import render_to_string
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

from .models import CourseCategory


log = logging.getLogger(__name__)

def enroll_category(user, category):
    """
    Enrolls given user to all courses from given category.

    Args:
        user (string): username (request.user). For example: 'DuneTune'.
        category (CourseCategory object).
    Returns:
        result: dict whith two lists (CourseOverview objects) - successfuly enrolled and not enrolled.
    """
    result = {
        'enrolled': [],
        'not_enrolled': [],
    }

    courses = set()

    courses_category = get_courses(user, filter_={'coursecategory__id': category.id})
    courses.update(courses_category)
    # To include subcategories courses:
    subcategories = CourseCategory.objects.filter(parent=category)

    if subcategories:
        for subcategory in subcategories:
            courses_subcategory = get_courses(user, filter_={'coursecategory__id': subcategory.id})
            courses.update(courses_subcategory)

    for course in courses:
        course_id = str(course.id)
        try:
            add_enrollment(user, course_id)
            log.info(
                u"User %s enrolled in %s.",
                user.username,
                course_id
            )
            result['enrolled'].append(course)

        except CourseEnrollmentExistsError as e:
            log.info(
                u"User %s allready enrolled in %s.",
                user.username,
                course_id
            )
            result['not_enrolled'].append(course)

        except CourseEnrollmentClosedError as e:
            log.info(
                u"Enrollment to %s closed.",
                course_id
            )
            result['not_enrolled'].append(course)

        except CourseEnrollmentFullError as e:
            log.info(
                u"Enrollment to %s closed. Course is full.",
                course_id
            )
            result['not_enrolled'].append(course)

        except (UserNotFoundError, InvalidEnrollmentAttribute) as e:
            log.info(e)
            result['not_enrolled'].append(course)

    return result


def send_email_with_enroll_status(site_name, user, category, enroll_info):
    """
    Sends email to user with massage about successful/unsuccessful enrols to category courses.
    Args:
        request: request object.
        user (string): username (request.user). For example: 'DuneTune'.
        category (CourseCategory object).
        enrolls_results: dict whith two lists - successfuly enrolled and not enrolled. For example:
            {'not_enrolled': ['test'], 'enrolled': ['Demo_Course']}.
    Returns:
        1 - if email was successfuly sent.
        0 - if not.
    """
    user_email = user.email

    param_dict = {
        'site_name': site_name,
        'category': category,
        'full_name': user.profile.name,
        'email_address': user_email,
        'enroll_info': enroll_info,
    }

    txt_message = render_to_string('emails/enroll_category.txt', param_dict)
    html_message = render_to_string('emails/enroll_category.html', param_dict)
    subject = render_to_string('emails/enroll_category_subject.txt', param_dict)
    # Header values can't contain newlines
    subject = ''.join(subject.splitlines())

    from_address = configuration_helpers.get_value(
        'email_from_address',
        settings.DEFAULT_FROM_EMAIL
    )

    return send_mail(
        subject=subject,
        message=txt_message,
        from_email=from_address,
        html_message=html_message,
        recipient_list=[user_email],
    )
