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
from courseware.courses import get_current_child, get_problems_in_section

from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from student.models import CourseEnrollment

from util.milestones_helpers import get_course_content_milestones
from xmodule.modulestore.django import modulestore
from ..utils import get_course_outline_block_tree, get_resume_block
from lms.djangoapps.selection_page.models import c_selection_page, USER, COURSE_KEY, BLOCK_ID, NEXT_ID, LEVEL


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
    """
    earned - what the grade student earned after passing the lesson
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
        subsection_active = ''

        for section in course_block_tree.get('children'):
            for subsection in section.get('children', []):
                if active_block_id == subsection['block_id']:
                    course_block_id = subsection['block_id']
                    subsection_active = subsection
                    break

        earned = 0
        for chapter in courseware_summary:
            if not chapter['display_name'] == "hidden":
                    for section in chapter['sections']:
                        if course_block_id == section.location.block_id:
                            earned = section.all_total.earned
                            total = section.all_total.possible
                            break
        

        def unit_grade_level(earned, course_block_tree, subsection_active):
            """
                Checking the level of the last visited lesson
                and filter the next lessons by level
            """

            subsection_vertical = {'children': []}

            def get_next_level(earned, level=None):
                """
                Get user's next level depending on earned points.

                    Arguments:
                        earned (float): Points student has earned.
                        level (str): One of "low", "middle", "hight". Default one is "middle"
                    Return level.
                """
                subsection_level = 'middle' # default
                if level:
                    if 0 <= earned <= 4.9:
                        if level == 'hight':
                            subsection_level = 'middle'
                        else:
                            subsection_level = 'low'
                    elif 5 <= earned <= 7.9:
                        subsection_level = level
                    elif 8 <= earned <= 10:
                        if level == 'low':
                            subsection_level = 'middle'
                        else:
                            subsection_level = 'hight'
                    return subsection_level
                return subsection_level

            def get_pair(first_id, next_id, tree):
                """
                Get whole subsection data by ids.

                    Arguments:
                        first_id (str): First block's ID.
                        next_id (str): Next block's ID
                        tree (dict): Contains whole data of the course.
                    Return pair of two blocks to be dispayed to user.
                """
                pair = [{},{}]
                for section in tree['children']:
                    for sub in section['children']:
                        if sub['block_id'] == first_id:
                            pair[0] = sub
                        if sub['block_id'] == next_id:
                            pair[1] = sub
                return pair

            lesson_pair = c_selection_page().find_one({
                COURSE_KEY: course_id,
                USER: request.user.id,
            })
            subsection_level = subsection_active['unit_level']
            is_complete = subsection_active['complete']
            next_level = get_next_level(earned, subsection_level)
            if lesson_pair:
                # get next level only if user finished the previous one.
                next_level = next_level if is_complete else lesson_pair[LEVEL]
                first_sub, next_sub = get_pair(lesson_pair.get('block_id'), lesson_pair.get('next_id'), course_block_tree)
                pair = []
                # levels the same and at least one hasn't completed - return current pair
                if lesson_pair[LEVEL] == next_level and (not first_sub.get('complete', True) or not next_sub.get('complete', True)):
                    return {'children': [first_sub, next_sub]}
            else: # means that student is here for the first time
                next_level = get_next_level(earned)

            for section in course_block_tree.get('children'):
                for subsection in section.get('children', []):
                    if next_level == subsection['unit_level'] and not subsection['complete']:
                        subsection_vertical['children'].append(subsection)
                        if len(subsection_vertical['children']) >= 2:
                            break
                        continue
            to_set = {}
            if subsection_vertical['children'] and len(subsection_vertical['children']) > 1:
                to_set = {
                        BLOCK_ID: subsection_vertical['children'][0]['block_id'],
                        NEXT_ID: subsection_vertical['children'][1]['block_id'],
                        LEVEL: next_level
                    }
            elif subsection_vertical['children']:
                to_set = {
                        BLOCK_ID: subsection_vertical['children'][0]['block_id'],
                        LEVEL: next_level
                }

            if to_set:
                c_selection_page().update({
                    COURSE_KEY: course_id,
                    USER: request.user.id},
                    {'$set': to_set}
                , upsert=True)

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
        # earned = 0
        try:
            earned = round(earned/total*10, 1)
        except ZeroDivisionError:
            pass
        context['subsection_vertical'] = unit_grade_level(earned, course_block_tree, subsection_active)

        html = render_to_string('course_experience/course-lessons-outline-fragment.html', context)
        return Fragment(html)
        