from opaque_keys.edx.keys import CourseKey
from django.template.loader import render_to_string
from django.template.context_processors import csrf

from web_fragments.fragment import Fragment

from courseware.courses import get_course_overview_with_access
from courseware.model_data import FieldDataCache
from courseware.module_render import  get_module_for_descriptor
from courseware.courses import get_current_child, get_problems_in_section

from openedx.features.course_experience.views.course_outline import CourseOutlineFragmentView
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory

from xmodule.modulestore.django import modulestore
from openedx.features.course_experience.utils import get_course_outline_block_tree, get_resume_block
from lms.djangoapps.hera.mongo import c_selection_page, USER, COURSE_KEY, BLOCK_ID, NEXT_ID, LEVEL

def unit_grade_level(earned, course_block_tree, subsection_active, request, course_id=None):
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
        pair = [{}, {}]
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
        # levels the same and at least one hasn't completed - return current pair
        if lesson_pair[LEVEL] == next_level and (not first_sub.get('complete', True) or not next_sub.get('complete', True)):
            children = []
            if first_sub:
                children.append(first_sub)
            if next_sub:
                children.append(next_sub)

            return {'children': children }
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
    to_unset = {}
    to_update = {}
    
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
        to_unset = {
            NEXT_ID: 1
        }
    
    if to_set:
        to_update['$set'] = to_set
    if to_unset:
        to_update['$unset'] = to_unset
        
    if to_update:
        c_selection_page().update({
            COURSE_KEY: course_id,
            USER: request.user.id},
            to_update
        , upsert=True)

    return subsection_vertical

class SelectionPageOutlineFragmentView(CourseOutlineFragmentView):
    """
    View for Selection page with shown actual pare of the questions (units)
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

        context = {
            'csrf': csrf(request)['csrf_token'],
            'course': course_overview,
            'due_date_display_format': course.due_date_display_format,
            'blocks': course_block_tree
        }

        xblock_display_names = self.create_xblock_id_and_name_dict(course_block_tree)
        gated_content = self.get_content_milestones(request, course_key)

        context['gated_content'] = gated_content
        context['xblock_display_names'] = xblock_display_names
        # earned = 0
        try:
            earned = round(earned/total*10, 1)
        except ZeroDivisionError:
            pass
        context['subsection_vertical'] = unit_grade_level(
            earned,
            course_block_tree,
            subsection_active,
            request,
            course_id)

        html = render_to_string('hera/course-lessons-outline-fragment.html', context)
        return Fragment(html)


class DashboardPageOutlineFragmentView(CourseOutlineFragmentView):
    """
    View for Dashboard Page
    """
    def render_to_fragment(self, request, course_id=None, page_context=None, **kwargs):
        course_key = CourseKey.from_string(course_id)
        course_overview = get_course_overview_with_access(request.user, 'load', course_key, check_if_enrolled=True)
        course = modulestore().get_course(course_key)

        course_block_tree = get_course_outline_block_tree(request, course_id)
        if not course_block_tree:
            return None

        incomplete_subsection = {}
        popup = False
        for section in course_block_tree.get('children'):
            for subsection in section.get('children', []):
                if not subsection['complete']:
                    for unit in subsection.get('children', []):
                        if unit['complete']:
                            incomplete_subsection = subsection
                            popup = True
                            break

        units = incomplete_subsection.get('children', [{}])
        start_over_url = units[0].get('lms_web_url', '')

        xblock_display_names = self.create_xblock_id_and_name_dict(course_block_tree)
        gated_content = self.get_content_milestones(request, course_key)

        context = {
            'popup': popup,
            'resume_course_url': incomplete_subsection.get('lms_web_url', ''),
            'start_over_url': start_over_url or '',
            'csrf': csrf(request)['csrf_token'],
            'course': course_overview,
            'due_date_display_format': course.due_date_display_format,
            'blocks': course_block_tree,
            'gated_content': gated_content,
            'xblock_display_names': xblock_display_names
        }

        html = render_to_string('hera/dashboard-outline-fragment.html', context)
        return Fragment(html)
