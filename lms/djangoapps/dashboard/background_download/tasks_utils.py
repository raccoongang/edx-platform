"""
Tasks utility logic.
"""

from datetime import datetime
import time
import logging
import os

from django.conf import settings
from django.utils.translation import ugettext as _
from pytz import UTC

from dashboard.background_download.io_utils import (
    cleanup_directory_user_files,
    store_row,
)
from dashboard.background_download.data_utils import (
    fetch_course_grades,
    get_courses,
)

log = logging.getLogger('edx.celery.task')


def export_courses_grades(user_id):
    """
    Utility to export data for the courses grades report.

    Does all the mechanics: clean up, prepare the data, create a file,
    store, mark for readiness (remove the tmp marker).
    """

    # `Path` type
    if not settings.COURSES_GRADES_REPORTS_DIR.isdir():
        settings.COURSES_GRADES_REPORTS_DIR.mkdir()

    # Clean up the dir on a per-user basis.
    cleanup_directory_user_files(
        dir_path=settings.COURSES_GRADES_REPORTS_DIR,
        user_id=user_id,
        filename_user_id_getter=get_grades_report_file_user_id,
    )

    log.info("Starting to prepare courses grades for a user with id {!s}".format(user_id))

    formatted_date = datetime.now(UTC).strftime('%m-%d-%Y')

    # User id is required in the filename to support the solution
    filename = 'Grade_Report_All_courses_{!s}_{!s}.csv'.format(formatted_date, user_id)
    report_filepath = os.path.join(settings.COURSES_GRADES_REPORTS_DIR, filename + ".tmp")

    header = [
        _('Course ID'),
        _('Student ID'),
        _('Email'),
        _('Username'),
        _('Course Grade'),
        _('Assignment'),
        _('Assignment Score'),
        _('Assignment Type (Avg)'),
        _('Enrollment Track'),
        _('Verification Status'),
        _('Certificate Eligible'),
        _('Certificate Delivered'),
        _('Certificate Type'),
    ]
    store_row(header, report_filepath)

    # Store grades data in the report file
    for course in get_courses():
        # NOTE: might want to introduce slicing here
        map(lambda data: store_row(data, report_filepath), fetch_course_grades(course))
        log.info("Stored grades for a course {!s} in the courses grades report "
                 "for a user with id {!s}".format(course.id, user_id))

    # Finish up (the report will then show up on a sysadmin page)
    os.rename(
        settings.COURSES_GRADES_REPORTS_DIR / filename + ".tmp",
        settings.COURSES_GRADES_REPORTS_DIR / filename
    )

    log.info("The courses grades report is exported for a user with id {!s}".format(user_id))


def get_grades_report_file_user_id(filename):
    """
    Fetch user id from the grades report filename.

    Examples of a `filename`:
     'Grade_Report_All_courses_12-31-2020_11.csv'
     'Grade_Report_All_courses_12-31-2020_11.csv.tmp'
    """
    return filename.split("_")[-1].split(".")[0]
