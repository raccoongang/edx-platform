"""
Celery tasks for Sysadmin.
"""

import logging

from celery.task import task

from dashboard.background_download.tasks_utils import export_courses_grades

log = logging.getLogger('edx.celery.task')


@task()
def export_courses_grades_csv_data(**kwargs):
    """
    Export overall courses grades report.

    Asynchronously export given data as a CSV file.
    """
    user_id = kwargs.get("user_id", "")
    log.info("Starting the task on grades report export for a user with id {!s}".format(user_id))
    export_courses_grades(user_id=user_id)
    log.info("Finished the task on grades report export for a user with id {!s}".format(user_id))
