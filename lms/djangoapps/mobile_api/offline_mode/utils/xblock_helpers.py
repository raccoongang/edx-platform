from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from xmodule.modulestore.django import modulestore

from .utils.html_manipulation import manipulate_html
from .utils.assets_management import save_asset_file, remove_old_files, base_storage_path
from .utils.zip_management import create_zip_file


def is_modified(xblock):
    file_path = f'{base_storage_path(xblock)}content_html.zip'

    try:
        last_modified = default_storage.get_created_time(file_path)
    except OSError:
        return True

    return xblock.published_on > last_modified


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
            return None

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


def generate_offline_content(xblock, html_data):
    if not is_modified(xblock):
        return

    base_path = base_storage_path(xblock)
    remove_old_files(base_path)

    manipulated_html = manipulate_html(html_data, lambda path, filename: save_asset_file(xblock, path, filename))

    default_storage.save(f'{base_path}index.html', ContentFile(manipulated_html))
    create_zip_file(base_path, 'content_html.zip')
