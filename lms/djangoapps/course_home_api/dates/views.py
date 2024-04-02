"""
Dates Tab Views
"""

from django.conf import settings
from edx_django_utils import monitoring as monitoring_utils
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys.edx.keys import CourseKey
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.djangoapps.student.models import CourseEnrollment
from lms.djangoapps.course_goals.models import UserActivity
from lms.djangoapps.course_home_api.dates.serializers import DatesTabSerializer
from lms.djangoapps.course_home_api.utils import get_course_or_403
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.context_processor import user_timezone_locale_prefs
from lms.djangoapps.courseware.courses import get_course_date_blocks
from lms.djangoapps.courseware.date_summary import TodaysDate
from lms.djangoapps.courseware.masquerade import setup_masquerade
from openedx.core.lib.api.authentication import BearerAuthenticationAllowInactiveUser
from openedx.features.content_type_gating.models import ContentTypeGatingConfig
from xmodule.modulestore.django import modulestore


def enclosing_sequence_for_gating_checks(block):
    seq_tags = ['sequential']
    if block.location.block_type in seq_tags:
        return None

    ancestor = block
    while ancestor and ancestor.location.block_type not in seq_tags:
        ancestor = ancestor.get_parent()  # Note: CourseBlock's parent is None

    if ancestor:
        return block.runtime.get_block(ancestor.location)
    return None


def xblock_view_handler(request, xblock, check_if_enrolled=True, disable_staff_debug_info=False):
    """
    Helper function to render an XBlock and return the rendered HTML content.
    """
    from edx_django_utils.monitoring import set_custom_attribute, set_custom_attributes_for_course_key
    from lms.djangoapps.courseware.courses import get_course_with_access
    from lms.djangoapps.courseware.block_render import get_block, get_block_by_usage_id, get_block_for_descriptor
    from xmodule.modulestore.exceptions import ItemNotFoundError, NoPathToItem
    from openedx.features.course_experience.url_helpers import (
        get_courseware_url,
        get_learning_mfe_home_url,
        is_request_from_learning_mfe
    )
    from openedx.core.lib.mobile_utils import is_request_from_mobile_app
    from openedx.features.course_experience.utils import dates_banner_should_display
    from lms.djangoapps.courseware.masquerade import is_masquerading_as_specific_student, setup_masquerade
    from lms.djangoapps.courseware.views.views import get_optimization_flags_for_content
    from lms.djangoapps.edxnotes.helpers import is_feature_enabled
    from lms.djangoapps.courseware.date_summary import verified_upgrade_deadline_link
    from common.djangoapps.edxmako.shortcuts import marketing_link, render_to_response, render_to_string
    usage_key = xblock.usage_key

    usage_key = usage_key.replace(course_key=modulestore().fill_in_run(usage_key.course_key))
    course_key = usage_key.course_key

    # Gathering metrics to make performance measurements easier.
    set_custom_attributes_for_course_key(course_key)
    set_custom_attribute('usage_key', str(usage_key))
    set_custom_attribute('block_type', usage_key.block_type)

    staff_access = has_access(request.user, 'staff', course_key)

    with modulestore().bulk_operations(course_key):
        # verify the user has access to the course, including enrollment check
        try:
            course = get_course_with_access(request.user, 'load', course_key, check_if_enrolled=check_if_enrolled)
        except:
            return None

        _course_masquerade, request.user = setup_masquerade(
            request,
            course_key,
            staff_access,
        )

        UserActivity.record_user_activity(
            request.user, usage_key.course_key, request=request, only_if_mobile_app=True
        )

        recheck_access = request.GET.get('recheck_access') == '1'
        try:
            block, _ = get_block_by_usage_id(
                request,
                str(course_key),
                str(usage_key),
                disable_staff_debug_info=disable_staff_debug_info,
                course=course,
                will_recheck_access=recheck_access,
            )
        except:
            return

        student_view_context = request.GET.dict()
        student_view_context['show_bookmark_button'] = request.GET.get('show_bookmark_button', '0') == '1'
        student_view_context['show_title'] = request.GET.get('show_title', '1') == '1'

        is_learning_mfe = is_request_from_learning_mfe(request)
        student_view_context['hide_access_error_blocks'] = is_learning_mfe and recheck_access
        is_mobile_app = is_request_from_mobile_app(request)
        student_view_context['is_mobile_app'] = is_mobile_app

        enable_completion_on_view_service = False
        completion_service = block.runtime.service(block, 'completion')
        if completion_service and completion_service.completion_tracking_enabled():
            if completion_service.blocks_to_mark_complete_on_view({block}):
                enable_completion_on_view_service = True
                student_view_context['wrap_xblock_data'] = {
                    'mark-completed-on-view-after-delay': completion_service.get_complete_on_view_delay_ms()
                }

        missed_deadlines, missed_gated_content = dates_banner_should_display(course_key, request.user)

        ancestor_sequence_block = enclosing_sequence_for_gating_checks(block)
        if False:
            context = {'specific_masquerade': is_masquerading_as_specific_student(request.user, course_key)}
            if ancestor_sequence_block.descendants_are_gated(context):
                return redirect(
                    reverse(
                        'render_xblock',
                        kwargs={'usage_key_string': str(ancestor_sequence_block.location)}
                    )
                )

        if False:
            seq_block = ancestor_sequence_block if ancestor_sequence_block else block
            if getattr(seq_block, 'is_time_limited', None):
                if not _check_sequence_exam_access(request, seq_block.location):
                    return HttpResponseForbidden("Access to exam content is restricted")

        fragment = block.render('student_view', context=student_view_context)
        optimization_flags = get_optimization_flags_for_content(block, fragment)

        context = {
            'fragment': fragment,
            'course': course,
            'block': block,
            'disable_accordion': True,
            'allow_iframing': True,
            'disable_header': True,
            'disable_footer': True,
            'disable_window_wrap': True,
            'enable_completion_on_view_service': enable_completion_on_view_service,
            'edx_notes_enabled': is_feature_enabled(course, request.user),
            'staff_access': staff_access,
            'xqa_server': settings.FEATURES.get('XQA_SERVER', 'http://your_xqa_server.com'),
            'missed_deadlines': missed_deadlines,
            'missed_gated_content': missed_gated_content,
            'has_ended': course.has_ended(),
            'web_app_course_url': get_learning_mfe_home_url(course_key=course.id, url_fragment='home'),
            'on_courseware_page': True,
            'verified_upgrade_link': verified_upgrade_deadline_link(request.user, course=course),
            'is_learning_mfe': is_learning_mfe,
            'is_mobile_app': is_mobile_app,
            'render_course_wide_assets': True,

            **optimization_flags,
        }
        return render_to_string('courseware/courseware-chromeless.html', context)

class DatesTabView(RetrieveAPIView):
    """
    **Use Cases**

        Request details for the Dates Tab

    **Example Requests**

        GET api/course_home/v1/dates/{course_key}

    **Response Values**

        Body consists of the following fields:

        course_date_blocks: List of serialized DateSummary objects. Each serialization has the following fields:
            complete: (bool) Meant to only be used by assignments. Indicates completeness for an
                assignment.
            date: (datetime) The date time corresponding for the event
            date_type: (str) The type of date (ex. course-start-date, assignment-due-date, etc.)
            description: (str) The description for the date event
            learner_has_access: (bool) Indicates if the learner has access to the date event
            link: (str) An absolute link to content related to the date event
                (ex. verified link or link to assignment)
            title: (str) The title of the date event
        dates_banner_info: (obj)
            content_type_gating_enabled: (bool) Whether content type gating is enabled for this enrollment.
            missed_deadlines: (bool) Indicates whether the user missed any graded content deadlines
            missed_gated_content: (bool) Indicates whether the user missed gated content
            verified_upgrade_link: (str) The link for upgrading to the Verified track in a course
        has_ended: (bool) Indicates whether course has ended
        learner_is_full_access: (bool) Indicates if the user is verified in the course
        user_timezone: (str) The user's preferred timezone

    **Returns**

        * 200 on success with above fields.
        * 401 if the user is not authenticated.
        * 403 if the user does not have access to the course.
        * 404 if the course is not available or cannot be seen.
    """

    authentication_classes = (
        JwtAuthentication,
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (IsAuthenticated,)
    serializer_class = DatesTabSerializer

    def get(self, request, *args, **kwargs):
        course_key_string = kwargs.get('course_key_string')
        course_key = CourseKey.from_string(course_key_string)
        import pdb; pdb.set_trace()
        for xblock in modulestore().get_items(course_key, qualifiers={'category': 'problem'}):
            try:
                response_xblock = xblock_view_handler(request, xblock)
                xblock.update_info_api(response_xblock)
            except:
                pass

        # Enable NR tracing for this view based on course
        monitoring_utils.set_custom_attribute('course_id', course_key_string)
        monitoring_utils.set_custom_attribute('user_id', request.user.id)
        monitoring_utils.set_custom_attribute('is_staff', request.user.is_staff)

        course = get_course_or_403(request.user, 'load', course_key, check_if_enrolled=False)
        is_staff = bool(has_access(request.user, 'staff', course_key))

        _, request.user = setup_masquerade(
            request,
            course_key,
            staff_access=is_staff,
            reset_masquerade_data=True,
        )

        # Record user activity for tracking progress towards a user's course goals (for mobile app)
        UserActivity.record_user_activity(request.user, course.id, request=request, only_if_mobile_app=True)

        if not CourseEnrollment.is_enrolled(request.user, course_key) and not is_staff:
            return Response('User not enrolled.', status=401)

        blocks = get_course_date_blocks(course, request.user, request, include_access=True, include_past_dates=True)

        learner_is_full_access = not ContentTypeGatingConfig.enabled_for_enrollment(
            user=request.user,
            course_key=course_key,
        )

        # User locale settings
        user_timezone_locale = user_timezone_locale_prefs(request)
        user_timezone = user_timezone_locale['user_timezone']

        data = {
            'has_ended': course.has_ended(),
            'course_date_blocks': [block for block in blocks if not isinstance(block, TodaysDate)],
            'learner_is_full_access': learner_is_full_access,
            'user_timezone': user_timezone,
        }
        context = self.get_serializer_context()
        context['learner_is_full_access'] = learner_is_full_access
        serializer = self.get_serializer_class()(data, context=context)

        return Response(serializer.data)
