"""
Views to show a course outline.
"""
import re
import datetime

from completion import waffle as completion_waffle
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from opaque_keys.edx.keys import CourseKey
from pytz import UTC
from waffle.models import Switch
from web_fragments.fragment import Fragment

from courseware.courses import get_course_overview_with_access
from courseware.model_data import FieldDataCache
from courseware.module_render import  get_module_for_descriptor
from courseware.courses import get_current_child

from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from student.models import CourseEnrollment

from util.milestones_helpers import get_course_content_milestones
from xmodule.modulestore.django import modulestore
from ..utils import get_course_outline_block_tree, get_resume_block


DEFAULT_COMPLETION_TRACKING_START = datetime.datetime(2018, 1, 24, tzinfo=UTC)


class CourseOutlineFragmentView(EdxFragmentView):

    """
    Course outline fragment to be shown in the unified course view.
    """

    def render_to_fragment(self, request, course_id=None, page_context=None, **kwargs):
        """
        Renders the course outline as a fragment.
        """
        course_key = CourseKey.from_string(course_id)
        course_overview = get_course_overview_with_access(request.user, 'load', course_key, check_if_enrolled=True)
        course = modulestore().get_course(course_key)

        course_block_tree = get_course_outline_block_tree(request, course_id)
        if not course_block_tree:
            return None

        context = {
            'csrf': csrf(request)['csrf_token'],
            'course': course_overview,
            'due_date_display_format': course.due_date_display_format,
            'blocks': course_block_tree
        }

        resume_block = get_resume_block(course_block_tree)
        if not resume_block:
            self.mark_first_unit_to_resume(course_block_tree)

        xblock_display_names = self.create_xblock_id_and_name_dict(course_block_tree)
        gated_content = self.get_content_milestones(request, course_key)

        context['gated_content'] = gated_content
        context['xblock_display_names'] = xblock_display_names

        html = render_to_string('course_experience/course-outline-fragment.html', context)
        return Fragment(html)

    def create_xblock_id_and_name_dict(self, course_block_tree, xblock_display_names=None):
        """
        Creates a dictionary mapping xblock IDs to their names, using a course block tree.
        """
        if xblock_display_names is None:
            xblock_display_names = {}

        if course_block_tree.get('id'):
            xblock_display_names[course_block_tree['id']] = course_block_tree['display_name']

        if course_block_tree.get('children'):
            for child in course_block_tree['children']:
                self.create_xblock_id_and_name_dict(child, xblock_display_names)

        return xblock_display_names

    def get_content_milestones(self, request, course_key):
        """
        Returns dict of subsections with prerequisites and whether the prerequisite has been completed or not
        """
        def _get_key_of_prerequisite(namespace):
            return re.sub('.gating', '', namespace)

        all_course_milestones = get_course_content_milestones(course_key)

        uncompleted_prereqs = {
            milestone['content_id']
            for milestone in get_course_content_milestones(course_key, user_id=request.user.id)
        }

        gated_content = {
            milestone['content_id']: {
                'completed_prereqs': milestone['content_id'] not in uncompleted_prereqs,
                'prerequisite': _get_key_of_prerequisite(milestone['namespace'])
            }
            for milestone in all_course_milestones
        }

        return gated_content

    def user_enrolled_after_completion_collection(self, user, course_key):
        """
        Checks that the user has enrolled in the course after 01/24/2018, the date that
        the completion API began data collection. If the user has enrolled in the course
        before this date, they may see incomplete collection data. This is a temporary
        check until all active enrollments are created after the date.
        """
        user = User.objects.get(username=user)
        try:
            user_enrollment = CourseEnrollment.objects.get(
                user=user,
                course_id=course_key,
                is_active=True
            )
            return user_enrollment.created > self._completion_data_collection_start()
        except CourseEnrollment.DoesNotExist:
            return False

    def _completion_data_collection_start(self):
        """
        Returns the date that the ENABLE_COMPLETION_TRACKING waffle switch was enabled.
        """
        # pylint: disable=protected-access
        switch_name = completion_waffle.waffle()._namespaced_name(completion_waffle.ENABLE_COMPLETION_TRACKING)
        try:
            return Switch.objects.get(name=switch_name).created
        except Switch.DoesNotExist:
            return DEFAULT_COMPLETION_TRACKING_START

    def mark_first_unit_to_resume(self, block_node):
        children = block_node.get('children')
        if children:
            children[0]['resume_block'] = True
            self.mark_first_unit_to_resume(children[0])

class SelectionPageOutlineFragmentView(CourseOutlineFragmentView):

    def render_to_fragment(self, request, course_id=None, page_context=None, **kwargs):
        """
        Renders the course outline as a fragment.
        """
        course_key = CourseKey.from_string(course_id)
        course_overview = get_course_overview_with_access(request.user, 'load', course_key, check_if_enrolled=True)
        course = modulestore().get_course(course_key)

        course_block_tree = get_course_outline_block_tree(request, course_id)
        if not course_block_tree:
            return None

        course_block_id = ''

        course_grade = CourseGradeFactory().read(request.user, course)
        courseware_summary = course_grade.chapter_grades.values()

        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            course.id, request.user, course, depth=2
        )
        course_module = get_module_for_descriptor(
            request.user, request, course, field_data_cache, course.id, course=course
        )

        chapter_module = get_current_child(course_module)
        section_module = get_current_child(chapter_module)
        active_block_id = section_module.scope_ids.usage_id.block_id
        section_active = ''

        for section in course_block_tree.get('children'):
            for subsection in section.get('children', []):
                if active_block_id == subsection['block_id']:
                    course_block_id = subsection['block_id']
                    section_active = subsection
                    break

        earned = 0
        for chapter in courseware_summary:
            if not chapter['display_name'] == "hidden":
                    for section in chapter['sections']:
                        if course_block_id == section.location.block_id:
                            earned = section.all_total.earned
                            total = section.all_total.possible
                            break


        def unit_grade_level(earned, course_block_tree, section_active):
            """
                Checking the level of the lasst visited lesson
                and filter the by level next lessons
            """

            subsection_vertical = {}
            subsection_vertical['children']=[]

            unit_level = ''

            if 0<= earned <=4.9:
                if section_active['unit_level'] == 'hight':
                    unit_level = 'middle'
                else:
                    unit_level = 'low'
            elif 5<= earned <=7.9:
                    unit_level = section_active['unit_level']
            elif 8<= earned <=10:
                if section_active['unit_level'] == 'low':
                    unit_level = 'middle'
                else:
                    unit_level = 'hight'

            for section in course_block_tree.get('children'):

                # for subsection in section.get('children', []):
                for subsection in section.get('children', []):
                    if unit_level == subsection['unit_level']:
                        subsection_vertical['children'].append(subsection)
                return subsection_vertical

        context = {
            'csrf': csrf(request)['csrf_token'],
            'course': course_overview,
            'due_date_display_format': course.due_date_display_format,
            'blocks': course_block_tree
        }

        resume_block = get_resume_block(course_block_tree)
        if not resume_block:
            self.mark_first_unit_to_resume(course_block_tree)

        xblock_display_names = self.create_xblock_id_and_name_dict(course_block_tree)
        gated_content = self.get_content_milestones(request, course_key)

        context['gated_content'] = gated_content
        context['xblock_display_names'] = xblock_display_names
        context['subsection_vertical'] = unit_grade_level(round(earned/total*10, 1), course_block_tree, section_active)

        html = render_to_string('course_experience/course-lessons-outline-fragment.html', context)
        return Fragment(html)