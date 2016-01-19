"""
Utilities for the credit app.
"""
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore
from student.roles import (GlobalStaff, CourseStaffRole, CourseInstructorRole,
                           CourseCreatorRole, OrgRole)
from student.models import CourseAccessRole


def get_course_blocks(course_key, category):
    """
    Retrieve all XBlocks in the course for a particular category.

    Returns only XBlocks that are published and haven't been deleted.
    """
    # Note: we need to check if found components have been orphaned
    # due to a bug in split modulestore (PLAT-799).  Once that bug
    # is resolved, we can skip the `_is_in_course_tree()` check entirely.
    return [
        block for block in modulestore().get_items(
            course_key,
            qualifiers={"category": category},
            revision=ModuleStoreEnum.RevisionOption.published_only,
        )
        if _is_in_course_tree(block)
    ]


def _is_in_course_tree(block):
    """
    Check that the XBlock is in the course tree.

    It's possible that the XBlock is not in the course tree
    if its parent has been deleted and is now an orphan.
    """
    ancestor = block.get_parent()
    while ancestor is not None and ancestor.location.category != "course":
        ancestor = ancestor.get_parent()

    return ancestor is not None


def get_visible_courses(request, courses):
    """
    Check course that it is public, user is staff or author this course
    """

    COURSE_ACCESS_ROLE_LIST = [
        'staff',
        'instructor',
        CourseInstructorRole.ROLE,
        CourseStaffRole.ROLE,
        CourseCreatorRole.ROLE
    ]
    user = request.user
    course_ids = CourseAccessRole.objects.filter(
                user_id=user.id, role__in=COURSE_ACCESS_ROLE_LIST).values_list('course_id', flat=True).distinct()
    orgs = CourseAccessRole.objects.filter(
            user_id=user.id, role__in=COURSE_ACCESS_ROLE_LIST, course_id=None).values_list('org', flat=True).distinct()

    res = lambda course: course.ispublic or course.id.to_deprecated_string() in course_ids or course.org in orgs

    return filter(res, courses)
