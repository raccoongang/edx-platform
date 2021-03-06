"""
Tests for the course import API views
"""
import os
import shutil
import tarfile
import tempfile
from datetime import datetime
from urllib import urlencode

from django.core.urlresolvers import reverse
from path import Path as path
from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from lms.djangoapps.courseware.tests.factories import GlobalStaffFactory, StaffFactory
from student.tests.factories import UserFactory
from user_tasks.models import UserTaskStatus
from xmodule.modulestore.tests.django_utils import TEST_DATA_SPLIT_MODULESTORE, SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
import ddt
from mock import Mock, MagicMock, patch

@ddt.ddt
class CourseImportViewTest(SharedModuleStoreTestCase, APITestCase):
    """
    Test importing courses via a RESTful API (POST method only)
    """
    MODULESTORE = TEST_DATA_SPLIT_MODULESTORE

    @classmethod
    def setUpClass(cls):
        super(CourseImportViewTest, cls).setUpClass()

        cls.course = CourseFactory.create(display_name='test course', run="Testing_course")
        cls.course_key = cls.course.id

        cls.restricted_course = CourseFactory.create(display_name='restricted test course', run="Restricted_course")
        cls.restricted_course_key = cls.restricted_course.id

        cls.password = 'test'
        cls.student = UserFactory(username='dummy', password=cls.password)
        cls.staff = StaffFactory(course_key=cls.course.id, password=cls.password)
        cls.restricted_staff = StaffFactory(course_key=cls.restricted_course.id, password=cls.password)

        cls.content_dir = path(tempfile.mkdtemp())

        # Create tar test files -----------------------------------------------
        # OK course:
        good_dir = tempfile.mkdtemp(dir=cls.content_dir)
        # test course being deeper down than top of tar file
        embedded_dir = os.path.join(good_dir, "grandparent", "parent")
        os.makedirs(os.path.join(embedded_dir, "course"))
        with open(os.path.join(embedded_dir, "course.xml"), "w+") as f:
            f.write('<course url_name="2013_Spring" org="EDx" course="0.00x"/>')

        with open(os.path.join(embedded_dir, "course", "2013_Spring.xml"), "w+") as f:
            f.write('<course></course>')

        cls.good_tar_filename = "good.tar.gz"
        cls.good_tar_fullpath = os.path.join(cls.content_dir, cls.good_tar_filename)
        with tarfile.open(cls.good_tar_fullpath, "w:gz") as gtar:
            gtar.add(good_dir)

    def get_url(self, course_id):
        """
        Helper function to create the url
        """
        return reverse(
            'courses_api:course_import',
            kwargs={
                'course_id': course_id
            }
        )

    def test_anonymous_import_fails(self):
        """
        Test that an anonymous user cannot access the API and an error is received.
        """
        with open(self.good_tar_fullpath, 'rb') as fp:
            resp = self.client.post(self.get_url(self.course_key), {'course_data': fp}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_import_fails(self):
        """
        Test that a student user cannot access the API and an error is received.
        """
        self.client.login(username=self.student.username, password=self.password)
        with open(self.good_tar_fullpath, 'rb') as fp:
            resp = self.client.post(self.get_url(self.course_key), {'course_data': fp}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_with_access_import_succeeds(self):
        """
        Test that a staff user can access the API and successfully upload a course
        """
        self.client.login(username=self.staff.username, password=self.password)
        with open(self.good_tar_fullpath, 'rb') as fp:
            resp = self.client.post(self.get_url(self.course_key), {'course_data': fp}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_staff_has_no_access_import_fails(self):
        """
        Test that a staff user can't access another course via the API
        """
        self.client.login(username=self.staff.username, password=self.password)
        with open(self.good_tar_fullpath, 'rb') as fp:
            resp = self.client.post(self.get_url(self.restricted_course_key), {'course_data': fp}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_status_fails(self):
        """
        Test that a student user cannot access the API and an error is received.
        """
        self.client.login(username=self.student.username, password=self.password)
        resp = self.client.get(self.get_url(self.course_key), {'task_id': '1234', 'filename': self.good_tar_filename})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_get_status_fails(self):
        """
        Test that an anonymous user cannot access the API and an error is received.
        """
        resp = self.client.get(self.get_url(self.course_key), {'task_id': '1234', 'filename': self.good_tar_filename})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_get_status_succeeds(self):
        """
        Test that an import followed by a get status results in success

        Note: This relies on the fact that we process imports synchronously during testing
        """
        self.client.login(username=self.staff.username, password=self.password)
        with open(self.good_tar_fullpath, 'rb') as fp:
            resp = self.client.post(self.get_url(self.course_key), {'course_data': fp}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.get(
            self.get_url(self.course_key),
            {'task_id': resp.data['task_id'], 'filename': self.good_tar_filename},
            format='multipart'
        )
        self.assertEqual(resp.data['state'], UserTaskStatus.SUCCEEDED)

    def test_staff_no_access_get_status_fails(self):
        """
        Test that an import followed by a get status as an unauthorized staff fails

        Note: This relies on the fact that we process imports synchronously during testing
        """
        self.client.login(username=self.staff.username, password=self.password)
        with open(self.good_tar_fullpath, 'rb') as fp:
            resp = self.client.post(self.get_url(self.course_key), {'course_data': fp}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        task_id = resp.data['task_id']
        resp = self.client.get(
            self.get_url(self.course_key),
            {'task_id': task_id, 'filename': self.good_tar_filename},
            format='multipart'
        )
        self.assertEqual(resp.data['state'], UserTaskStatus.SUCCEEDED)

        self.client.logout()

        self.client.login(username=self.restricted_staff.username, password=self.password)
        resp = self.client.get(
            self.get_url(self.course_key),
            {'task_id': task_id, 'filename': self.good_tar_filename},
            format='multipart'
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_task_mismatch_get_status_fails(self):
        """
        Test that an import followed by a get status as an unauthorized staff fails

        Note: This relies on the fact that we process imports synchronously during testing
        """
        self.client.login(username=self.staff.username, password=self.password)
        with open(self.good_tar_fullpath, 'rb') as fp:
            resp = self.client.post(self.get_url(self.course_key), {'course_data': fp}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        task_id = resp.data['task_id']
        resp = self.client.get(
            self.get_url(self.restricted_course_key),
            {'task_id': task_id, 'filename': self.good_tar_filename},
            format='multipart'
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @ddt.data(
        [{'courses_ids': ['1'], 'rerun_courses_keys': ['0'], 'has_studio_read_access': True, 'is_reload': '{"is_reload": true}'}],
        [{'courses_ids': ['2'], 'rerun_courses_keys': ['1', '2'], 'has_studio_read_access': True, 'is_reload': '{"is_reload": false}'}],
        [{'courses_ids': ['3'], 'rerun_courses_keys': [], 'has_studio_read_access': False, 'is_reload': '{"is_reload": true}'}],
    )
    @ddt.unpack
    def test_check_rerun_courses(self, options):
        self.client.login(username=self.staff.username, password=self.password)
        #course_action_state.models.CourseRerunState
        #student.auth.has_studio_read_access
        find_all = []
        for course_id in options['rerun_courses_keys']:
            mock = Mock()
            mock.course_key = course_id
            find_all.append(mock)
        with patch('student.auth.has_studio_read_access',
                   Mock(side_effect=lambda user,course_key: options['has_studio_read_access'])) as has_access_mock:
            with patch('course_action_state.models.CourseRerunState.objects.find_all',
                       Mock(side_effect=lambda exclude_args,should_display: find_all )) as course_rerun_mock:
                resp = self.client.post('/api/courses/v0/check_rerun_courses/', {'courses': options['courses_ids']})
                self.assertEqual(resp.content, '{}'.format(options['is_reload']))