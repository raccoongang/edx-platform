from StringIO import StringIO

import ddt
from django.core.management import call_command, CommandError
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

TEST_COURSE_ID = 'course-v1:edX+DemoX+Demo_Course'


@ddt.ddt
class UpdateCourseSettingsFromJsonTestCase(ModuleStoreTestCase):
    """
    Tests update course data from json input
    """

    def setUp(self):
        super(UpdateCourseSettingsFromJsonTestCase, self).setUp()
        org, number, run = TEST_COURSE_ID.split(':', 1)[1].split('+')
        self.course = CourseFactory.create(org=org, number=number, run=run, default_store=ModuleStoreEnum.Type.split)

    @ddt.data(
        # without courses and --all
        ((u'-j {"start_date": "2017-1-31T00:00:00.000Z"}',), u'At least one course or --all must be specified.'),

        ((u'-j {"start_date": "2017-1-31T00:00:00.000Z"}', u'--all'), None),
        ((u'-j {"start_date": "2017-1-31T00:00:00.000Z"}', u'--all', u'--no-validate'), None),

        # bad json
        ((u'-j {bad...json}', u'--all'), u'Bad json data'),
        # bad keys
        ((u'-j {"wrong_key": "2017-1-31T00:00:00.000Z"}', u'--all'),
            u'Only start_date, end_date, enrollment_start, enrollment_end keys allowed in json'),
        # bad date
        ((u'-j {"start_date": "2018wrong_date"}', u'--all'), u'Bad 2018wrong_date value for `start_date` field'),
        # invalid key
        ((u'-j {"start_date": "2017-1-31T00:00:00.000Z"}', u'INVALID_KEY'), u'Invalid key specified: INVALID_KEY'),
        # invalid course
        ((u'-j {"start_date": "2017-1-31T00:00:00.000Z"}', u'{}-INVALID'.format(TEST_COURSE_ID)),
            u'Invalid course: {}-INVALID'.format(TEST_COURSE_ID)),

        ((u'-j {"start_date": "2017-1-31T00:00:00.000Z", "end_date": "2017-1-31T01:00:00.000Z"}',
            TEST_COURSE_ID), None),
        # bad start_date
        ((u'-j {"start_date": "2017-1-31T01:00:00.000Z", "end_date": "2017-1-31T00:00:00.000Z"}',
            TEST_COURSE_ID), u'`end_date` should be > `start_date`'),

        ((u'-j {"enrollment_start": "2017-1-31T00:00:00.000Z", "enrollment_end": "2017-1-31T01:00:00.000Z"}',
          TEST_COURSE_ID), None),
        # bad enrollment_start
        ((u'-j {"enrollment_start": "2017-1-31T01:00:00.000Z", "end_date": "2017-1-31T00:00:00.000Z"}',
          TEST_COURSE_ID), u'`end_date` should be > `enrollment_start`'),
        ((u'-j {"enrollment_start": "2017-1-31T01:00:00.000Z", "enrollment_end": "2017-1-31T00:00:00.000Z"}',
          TEST_COURSE_ID), u'`enrollment_end` should be > `enrollment_start`'),
        # bad enrollment_end
        ((u'-j {"end_date": "2017-1-31T01:00:00.000Z", "enrollment_end": "2017-3-31T00:00:00.000Z"}',
          TEST_COURSE_ID), u'`enrollment_end` should be < `end_date`'),
    )
    def test_dates(self, arguments):
        """
        Tests validation of start_date, end_date, enrollment_start, enrollment_end
        """
        command_arguments, expected_exception = arguments
        if expected_exception:
            with self.assertRaises(CommandError) as cm:
                call_command('update_course_settings_from_json', *command_arguments)
            self.assertEqual(cm.exception.message, expected_exception)
        else:
            out = StringIO()
            status = call_command('update_course_settings_from_json', *command_arguments, stdout=out)
            self.assertIsNone(status)
