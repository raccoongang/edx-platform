"""
Test cases for course_to_library_import.api module.
"""

from unittest.mock import patch

import pytest

from common.djangoapps.student.tests.factories import UserFactory
from cms.djangoapps.course_to_library_import.api import (
    create_import,
    import_library_from_staged_content,
)
from cms.djangoapps.course_to_library_import.constants import COURSE_TO_LIBRARY_IMPORT_PURPOSE
from cms.djangoapps.course_to_library_import.models import CourseToLibraryImport
from openedx.core.djangoapps.content_staging import api as content_staging_api
from .factories import CourseToLibraryImportFactory


@pytest.mark.django_db
def test_create_import():
    """
    Test create_import function.
    """
    course_ids = [
        "course-v1:edX+DemoX+Demo_Course",
        "course-v1:edX+DemoX+Demo_Course_2",
    ]
    user = UserFactory()
    library_key = "lib:edX:DemoLib"

    create_import(course_ids, user.id, library_key)

    import_task = CourseToLibraryImport.objects.get()
    assert import_task.course_ids == " ".join(course_ids)
    assert import_task.library_key == library_key
    assert import_task.user_id == user.id

    for course_id in course_ids:
        staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
            user.id, COURSE_TO_LIBRARY_IMPORT_PURPOSE.format(course_id=course_id, import_id=import_task.id)
        )
        assert staged_content is not None


@pytest.mark.django_db
@pytest.mark.parametrize("override", [True, False])
def test_import_library_from_staged_content(override):
    """
    Test import_library_from_staged_content function with different override values.
    """
    ctli = CourseToLibraryImportFactory()
    library_key = ctli.library_key
    user = ctli.user
    usage_ids = [
        "block-v1:edX+DemoX+Demo_Course+type@html+block@123",
        "block-v1:edX+DemoX+Demo_Course+type@html+block@456",
    ]
    course_id = "course-v1:edX+DemoX+Demo_Course"

    with patch(
        "cms.djangoapps.course_to_library_import.api.import_library_from_staged_content_task"
    ) as import_library_from_staged_content_task_mock:
        import_library_from_staged_content(library_key, user.id, usage_ids, course_id, ctli.uuid, 'xblock', override)

    import_library_from_staged_content_task_mock.delay.assert_called_once_with(
        user.id, usage_ids, library_key, COURSE_TO_LIBRARY_IMPORT_PURPOSE, course_id, ctli.uuid, 'xblock', override
    )
