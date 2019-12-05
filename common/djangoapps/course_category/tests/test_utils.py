import unittest

from django.conf import settings
from openedx.core.djangoapps.content.course_overviews.models import \
    CourseOverview
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from .factories import CourseCategoryFactory
from ..utils import enroll_category


@unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
class TestUtils(ModuleStoreTestCase):
    """
    Test course_category.utils.py.
    """
    def test_enroll_category(self):
        """
        Test enroll_category functionality.
        """
        user = UserFactory.create()

        course1 = CourseFactory.create()
        course_overview1 = CourseOverview.get_from_id(course1.id)
        course2 = CourseFactory.create()
        course_overview2 = CourseOverview.get_from_id(course2.id)

        category1 = CourseCategoryFactory.create(courses=(course_overview1,))
        category2 = CourseCategoryFactory.create(courses=(course_overview1, course_overview2,))

        result1 = enroll_category(user, category1)
        result2 = enroll_category(user, category2)

        self.assertEqual(result1['enrolled'], [course_overview1])
        self.assertEqual(result2['enrolled'], [course_overview2])
        self.assertEqual(result2['not_enrolled'], [course_overview1])
