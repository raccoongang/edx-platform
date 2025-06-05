"""
Tests for course dates views.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from edx_toggles.toggles.testutils import override_waffle_flag
from milestones.tests.utils import MilestonesTestCaseMixin

from common.djangoapps.student.models import CourseEnrollment
from lms.djangoapps.mobile_api.testutils import MobileAPITestCase
from openedx.features.course_experience import RELATIVE_DATES_FLAG
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.utils import MixedSplitTestCase

User = get_user_model()


class TestAllCourseDatesAPIView(
    MobileAPITestCase, MixedSplitTestCase, MilestonesTestCaseMixin
):  # lint-amnesty, pylint: disable=test-inherits-tests
    """
    Tests for AllCourseDatesAPIView.
    """

    def setUp(self):
        """
        Set up the test cases.
        """
        super().setUp()
        self.url = reverse("all-course-dates", args=["v1", self.user.username])
        self.login()

    def test_get_with_only_course_starts_date(self):
        """
        Test to check if only course start date is returned for a course without any sequentials.
        """
        self.enroll()
        response = self.client.get(self.url)

        first_result = response.data["results"][0]
        assert first_result["learner_has_access"] is True
        assert first_result["course_id"] == str(self.course.id)
        assert first_result["due_date"] == self.course.start.strftime("%Y-%m-%dT%H:%M:%S+0000")
        assert first_result["assignment_title"] == "Course starts"
        assert first_result["first_component_block_id"] == ""
        assert first_result["course_name"] == self.course.display_name
        assert first_result["location"] == str(self.course.id)
        assert first_result["relative"] is False

    @override_waffle_flag(RELATIVE_DATES_FLAG, active=True)
    def test_get_self_paced_course_with_past_due_date(self):
        """
        Test to check if the date is returned for a graded sequence with past due date from self-paced course.
        """
        self_paced_course = CourseFactory.create(
            mobile_available=True,
            start=timezone.now() - timedelta(days=1),
            self_paced=True,
            relative_weeks_due=2,
        )
        self.enroll(self_paced_course.id)
        enrollment = CourseEnrollment.objects.get(user=self.user, course_id=self_paced_course.id)
        chapter = self.make_block("chapter", self_paced_course, publish_item=True)
        sequential = self.make_block(
            "sequential", chapter, publish_item=True, due=timezone.now() - timedelta(days=1), graded=True
        )
        response = self.client.get(self.url)

        assert dict(response.data["results"][0]) == {
            "learner_has_access": True,
            "course_id": str(self_paced_course.id),
            "due_date": sequential.due.strftime("%Y-%m-%dT%H:%M:%S+0000"),
            "assignment_title": sequential.display_name,
            "first_component_block_id": str(sequential.location),
            "course_name": self_paced_course.display_name,
            "location": str(sequential.location),
            "relative": True,
        }

        assert dict(response.data["results"][1]) == {
            "learner_has_access": True,
            "course_id": str(self_paced_course.id),
            "due_date": enrollment.created.strftime("%Y-%m-%dT%H:%M:%S+0000"),
            "assignment_title": "Enrollment Date",
            "first_component_block_id": "",
            "course_name": self_paced_course.display_name,
            "location": str(self_paced_course.id),
            "relative": True,
        }

    @override_waffle_flag(RELATIVE_DATES_FLAG, active=True)
    def test_get_not_self_paced_course_with_past_due_date(self):
        """
        Test to check if the past date is not returned for a non-self-paced course.
        """
        self.enroll()
        chapter = self.make_block("chapter", self.course, publish_item=True)
        self.make_block("sequential", chapter, publish_item=True, due=timezone.now() - timedelta(days=1), graded=True)
        response = self.client.get(self.url)

        # Only course start date should be returned.
        assert len(response.data["results"]) == 1
