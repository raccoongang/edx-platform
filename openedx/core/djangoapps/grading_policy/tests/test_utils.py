"""
Test grade utils.
"""
from django.test.client import RequestFactory

from openedx.core.djangoapps.grading_policy.utils import MaxScoresCache, grade_for_percentage, get_score
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from student.models import CourseEnrollment
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase


class TestMaxScoresCache(ModuleStoreTestCase):
    """
    Tests for the MaxScoresCache
    """
    def setUp(self):
        super(TestMaxScoresCache, self).setUp()
        self.student = UserFactory.create()
        self.course = CourseFactory.create()
        self.problems = []
        for _ in xrange(3):
            self.problems.append(
                ItemFactory.create(category='problem', parent=self.course)
            )

        CourseEnrollment.enroll(self.student, self.course.id)
        self.request = RequestFactory().get('/')
        self.locations = [problem.location for problem in self.problems]

    def test_max_scores_cache(self):
        """
        Tests the behavior fo the MaxScoresCache
        """
        max_scores_cache = MaxScoresCache("test_max_scores_cache")
        self.assertEqual(max_scores_cache.num_cached_from_remote(), 0)
        self.assertEqual(max_scores_cache.num_cached_updates(), 0)

        # add score to cache
        max_scores_cache.set(self.locations[0], 1)
        self.assertEqual(max_scores_cache.num_cached_updates(), 1)

        # push to remote cache
        max_scores_cache.push_to_remote()

        # create a new cache with the same params, fetch from remote cache
        max_scores_cache = MaxScoresCache("test_max_scores_cache")
        max_scores_cache.fetch_from_remote(self.locations)

        # see cache is populated
        self.assertEqual(max_scores_cache.num_cached_from_remote(), 1)
