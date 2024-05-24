from django.urls import reverse, resolve
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest

from xmodule.modulestore.django import modulestore

from .html_manipulator import HtmlManipulator
from .assets_management import save_asset_file, remove_old_files, base_storage_path
from .zip_management import create_zip_file

User = get_user_model()

OFFLINE_SUPPORTED_XBLOCKS = ['html', 'problem']


def is_offline_supported(xblock):
    return xblock.location.block_type in OFFLINE_SUPPORTED_XBLOCKS


def is_modified(xblock):
    file_path = f'{base_storage_path(xblock)}content_html.zip'

    try:
        last_modified = default_storage.get_created_time(file_path)
    except OSError:
        return True

    return xblock.published_on > last_modified


def generate_request_with_service_user():
    user = User.objects.get(email='edx@example.com')
    request = HttpRequest()
    request.user = user
    # Set up the session
    session = SessionStore()
    session.create()
    request.session = session

    return request


def cms_xblock_view_handler(usage_key_string, view_name):
    # Generate the URL for the view
    url = reverse('xblock_view_handler', kwargs={'usage_key_string': usage_key_string, 'view_name': view_name})

    # Create a mock request object
    request = generate_request_with_service_user()
    request.method = 'GET'
    request.META['HTTP_ACCEPT'] = 'application/json'

    # Resolve the URL to get the view function
    view_func, args, kwargs = resolve(url)

    try:
        # Call the view function with the request and resolved kwargs
        response = view_func(request, *args, **kwargs)
    except Exception as e:
        return None

    return response


def get_xblock_view_response(request, usage_key_string, view_name):
    from collections import OrderedDict
    from functools import partial

    from django.utils.translation import gettext as _
    from web_fragments.fragment import Fragment

    from cms.lib.xblock.authoring_mixin import VISIBILITY_VIEW
    from common.djangoapps.edxmako.shortcuts import render_to_string
    from common.djangoapps.student.auth import (
        has_studio_read_access,
        has_studio_write_access,
    )
    from openedx.core.lib.xblock_utils import (
        hash_resource,
        request_token,
        wrap_xblock,
        wrap_xblock_aside,
    )
    from xmodule.modulestore.django import modulestore
    from cms.djangoapps.contentstore.toggles import use_tagging_taxonomy_list_page

    from xmodule.x_module import (
        AUTHOR_VIEW,
        PREVIEW_VIEWS,
        STUDENT_VIEW,
        STUDIO_VIEW,
    )

    from cms.djangoapps.contentstore.helpers import is_unit
    from cms.djangoapps.contentstore.views.preview import get_preview_fragment
    from cms.djangoapps.contentstore.xblock_storage_handlers.xblock_helpers import (
        usage_key_with_run,
        get_children_tags_count,
    )

    usage_key = usage_key_with_run(usage_key_string)
    if not has_studio_read_access(request.user, usage_key.course_key):
        return None

    accept_header = request.META.get("HTTP_ACCEPT", "application/json")

    if "application/json" in accept_header:
        store = modulestore()
        xblock = store.get_item(usage_key)
        container_views = [
            "container_preview",
            "reorderable_container_child_preview",
            "container_child_preview",
        ]

        xblock.runtime.wrappers.append(
            partial(
                wrap_xblock,
                "StudioRuntime",
                usage_id_serializer=str,
                request_token=request_token(request),
            )
        )

        xblock.runtime.wrappers_asides.append(
            partial(
                wrap_xblock_aside,
                "StudioRuntime",
                usage_id_serializer=str,
                request_token=request_token(request),
                extra_classes=["wrapper-comp-plugins"],
            )
        )

        if view_name in (STUDIO_VIEW, VISIBILITY_VIEW):
            if view_name == STUDIO_VIEW:
                load_services_for_studio(xblock.runtime, request.user)

            try:
                fragment = xblock.render(view_name)
            except Exception as exc:
                log.debug(
                    "Unable to render %s for %r", view_name, xblock, exc_info=True
                )
                fragment = Fragment(
                    render_to_string("html_error.html", {"message": str(exc)})
                )

        elif view_name in PREVIEW_VIEWS + container_views:
            is_pages_view = view_name == STUDENT_VIEW
            can_edit = has_studio_write_access(request.user, usage_key.course_key)

            reorderable_items = set()
            if view_name == "reorderable_container_child_preview":
                reorderable_items.add(xblock.location)

            paging = None
            try:
                if request.GET.get("enable_paging", "false") == "true":
                    paging = {
                        "page_number": int(request.GET.get("page_number", 0)),
                        "page_size": int(request.GET.get("page_size", 0)),
                    }
            except ValueError:
                return None

            force_render = request.GET.get("force_render", None)

            tags_count_map = {}
            if use_tagging_taxonomy_list_page():
                tags_count_map = get_children_tags_count(xblock)

            context = request.GET.dict()
            context.update(
                {
                    "is_pages_view": is_pages_view or view_name == AUTHOR_VIEW,
                    "is_unit_page": is_unit(xblock),
                    "can_edit": can_edit,
                    "root_xblock": xblock if (view_name == "container_preview") else None,
                    "reorderable_items": reorderable_items,
                    "paging": paging,
                    "force_render": force_render,
                    "item_url": "/container/{usage_key}",
                    "tags_count_map": tags_count_map,
                }
            )
            fragment = get_preview_fragment(request, xblock, context)

            display_label = xblock.display_name or xblock.scope_ids.block_type
            if not xblock.display_name and xblock.scope_ids.block_type == "html":
                display_label = _("Text")
            if is_pages_view:
                fragment.content = render_to_string(
                    "component.html",
                    {
                        "xblock_context": context,
                        "xblock": xblock,
                        "locator": usage_key,
                        "preview": fragment.content,
                        "label": display_label,
                    },
                )
        else:
            return None

        hashed_resources = OrderedDict()
        for resource in fragment.resources:
            hashed_resources[hash_resource(resource)] = resource._asdict()

        fragment_content = fragment.content
        if isinstance(fragment_content, bytes):
            fragment_content = fragment.content.decode("utf-8")

        return {"html": fragment_content, "resources": list(hashed_resources.items())}

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
    from lms.djangoapps.courseware.access import has_access
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

        try:
            block, _ = get_block_by_usage_id(
                request,
                str(course_key),
                str(usage_key),
                disable_staff_debug_info=disable_staff_debug_info,
                course=course,
                will_recheck_access=False,
            )
        except:
            return None

        student_view_context = request.GET.dict()
        student_view_context['show_bookmark_button'] = request.GET.get('show_bookmark_button', '0') == '1'
        student_view_context['show_title'] = request.GET.get('show_title', '1') == '1'

        # is_learning_mfe = is_request_from_learning_mfe(request)
        student_view_context['hide_access_error_blocks'] = False
        is_mobile_app = True
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
    remove_old_files(xblock)
    html_manipulator = HtmlManipulator(xblock, html_data)
    updated_html = html_manipulator.process_html()

    default_storage.save(f'{base_path}index.html', ContentFile(updated_html))
    create_zip_file(base_path, 'offline_content.zip')
