"""
Tests for edX global analytics application functions, that calculate statistics.
"""

import datetime

from django.test import TestCase
from django.utils import timezone
from django_countries.fields import Country

from student.tests.factories import UserFactory

from courseware.tests.factories import StudentModuleFactory
from openedx.core.djangoapps.content.course_structures.models import CourseStructure
from openedx.core.djangoapps.edx_global_analytics.utils.utilities import fetch_instance_information
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from courseware.models import StudentModule


class TestStudentsAmountPerParticularPeriod(TestCase):
    """
    Cover all methods, that have a deal with statistics calculation.
    """

    @staticmethod
    def create_default_data():
        """
        Default integration database data for active students amount functionality.
        """
        users_last_login = [
            timezone.make_aware(datetime.datetime(2017, 5, 14, 23, 59, 59), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 0, 0, 0), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 15, 23, 59, 59), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 16, 0, 0, 0), timezone.get_default_timezone()),
            timezone.make_aware(datetime.datetime(2017, 5, 16, 0, 0, 1), timezone.get_default_timezone())
        ]

        for user_last_login in users_last_login:
            UserFactory(last_login=user_last_login)

    def test_fetch_active_students(self):
        """
        Verify that fetch_instance_information returns data as expected in particular period and accurate datetime.

        We have no reason to test week and month periods for active students amount,
        all queries are the same, we just go test only day period.
        """
        self.create_default_data()

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)

        result = fetch_instance_information('active_students_amount', activity_period, name_to_cache=None)

        self.assertEqual(2, result)

    def test_fetch_students_per_country(self):
        """
        Verify that students_per_country returns data as expected in particular period and accurate datetime.
        """
        last_login = timezone.make_aware(datetime.datetime(2017, 5, 15, 14, 23, 23), timezone.get_default_timezone())
        countries = [u'US', u'CA']

        for country in countries:
            user = UserFactory.create(last_login=last_login)
            profile = user.profile
            profile.country = Country(country)
            profile.save()

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)

        result = fetch_instance_information('students_per_country', activity_period, name_to_cache=None)

        self.assertItemsEqual({u'US': 1, u'CA': 1}, result)

    def test_no_students_with_country(self):
        """
        Verify that students_per_country returns data as expected if no students with country.
        """
        last_login = timezone.make_aware(datetime.datetime(2017, 5, 15, 14, 23, 23), timezone.get_default_timezone())

        UserFactory.create(last_login=last_login)

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)

        result = fetch_instance_information('students_per_country', activity_period, name_to_cache=None)

        self.assertEqual({None: 0}, result)

    def test_generated_certificates_if_no_certificates(self):
        """
        Verify that the no errors in get generated certificates method if no certificates
        """
        test_result = {}

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)

        result = fetch_instance_information('generated_certificates', activity_period, name_to_cache=None)

        self.assertEqual(test_result, result)

    def test_enthusiastic_users_count_if_no_course_structure(self):
        """
        Verify that the no errors in get Enthusiastic Students method if no CourseStructure
        """

        test_result = {}
        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)
        result = fetch_instance_information('enthusiastic_students', activity_period, name_to_cache=None)

        self.assertEqual(test_result, result)


class TestCollectedDataTestCase(ModuleStoreTestCase):
    """
    Test cases covering Course Structure task-related workflows
    """

    def setUp(self, **kwargs):
        super(TestCollectedDataTestCase, self).setUp()
        course = CourseFactory.create(org='TestX', course='TS101', run='T1')
        CourseStructure.objects.all().delete()

        structure = (
            '{"blocks": {"block-v1:HISTORG+CS1023+2015_T1+type@chapter+block@bfdb4017fe6d4d74b966f18fccf5942f": {' 
            '"block_type": "chapter", "graded": false, "format": null, "usage_key": '
            '"block-v1:HISTORG+CS1023+2015_T1+type@chapter+block@bfdb4017fe6d4d74b966f18fccf5942f", '
            '"children": ["block-v1:HISTORG+CS1023+2015_T1+type@sequential+block@ef8b9857bc9b4e8db72410c1414cf804"], '
            '"display_name": "Section"}, "block-v1:HISTORG+CS1023+2015_T1+type@course+block@course": {'
            '"block_type": "course", "graded": false, "format": null, '
            '"usage_key": "block-v1:HISTORG+CS1023+2015_T1+type@course+block@course", '
            '"children": ["block-v1:HISTORG+CS1023+2015_T1+type@chapter+block@bfdb4017fe6d4d74b966f18fccf5942f"], '
            '"display_name": "History"}, '
            '"block-v1:HISTORG+CS1023+2015_T1+type@sequential+block@ef8b9857bc9b4e8db72410c1414cf804": {'
            '"block_type": "sequential", "graded": false, "format": null, '
            '"usage_key": "block-v1:HISTORG+CS1023+2015_T1+type@sequential+block@ef8b9857bc9b4e8db72410c1414cf804", '
            '"children": ["block-v1:HISTORG+CS1023+2015_T1+type@vertical+block@6d09c8448bd84ccc8aca324dd871c211"], '
            '"display_name": "Subsection"}, '
            '"block-v1:HISTORG+CS1023+2015_T1+type@problem+block@a7d9628670194d66a6c6a87dc2377de0": {'
            '"block_type": "problem", "graded": false, "format": null, '
            '"usage_key": "block-v1:HISTORG+CS1023+2015_T1+type@problem+block@a7d9628670194d66a6c6a87dc2377de0",'
            '"children": [], "display_name": "Blank Common Problem"}, '
            '"block-v1:HISTORG+CS1023+2015_T1+type@problem+block@93c7e26b2c114d11b98e9feab07a5e85": {'
            '"block_type": "problem", "graded": false, "format": null, '
            '"usage_key": "block-v1:HISTORG+CS1023+2015_T1+type@problem+block@93c7e26b2c114d11b98e9feab07a5e85", '
            '"children": [], "display_name": "Checkboxes"}, '
            '"block-v1:HISTORG+CS1023+2015_T1+type@vertical+block@6d09c8448bd84ccc8aca324dd871c211": {'
            '"block_type": "vertical", "graded": false, "format": null, '
            '"usage_key": "block-v1:HISTORG+CS1023+2015_T1+type@vertical+block@6d09c8448bd84ccc8aca324dd871c211", '
            '"children": ["block-v1:HISTORG+CS1023+2015_T1+type@problem+block@a7d9628670194d66a6c6a87dc2377de0", '
            '"block-v1:HISTORG+CS1023+2015_T1+type@problem+block@93c7e26b2c114d11b98e9feab07a5e85"], '
            '"display_name": "Unit"}}, "root": "block-v1:HISTORG+CS1023+2015_T1+type@course+block@course"}'
        )

        CourseStructure.objects.create(course_id=course.id, structure_json=structure)

        StudentModule.objects.create(
            modifeid=datetime.datetime.now(),
            student=UserFactory(),
            module_state_key='block-v1:HISTORG+CS1023+2015_T1+type@problem+block@93c7e26b2c114d11b98e9feab07a5e85',
            course_id=course.id,
            state="{'attempts': 32, 'otherstuff': 'alsorobots'}",
        )

    def test_get_enthusiastic_students(self):
        """
        Verify that enthusiastic_students returns data as expected
        """
        test_result = {datetime.datetime.now().strftime('%Y-%m-%d'): 1}

        activity_period = datetime.date(2017, 5, 15), datetime.date(2017, 5, 16)
        result = fetch_instance_information('enthusiastic_students', activity_period, name_to_cache=None)

        self.assertEqual(test_result, result)
