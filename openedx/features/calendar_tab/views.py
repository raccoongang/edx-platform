from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from web_fragments.fragment import Fragment

from courseware.access import has_access
from courseware.courses import get_course_with_access
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from .utils import gcal_service


def from_google_datetime(g_datetime):
    """Formats google calendar API datetime string to dhxscheduler datetime string.
    Example: "2017-04-25T16:00:00-04:00" >> "04/25/2017 16:00"
    """
    return datetime.strptime(g_datetime[:-6], "%Y-%m-%dT%H:%M:%S").strftime("%m/%d/%Y %H:%M")


def to_google_datetime(dhx_datetime):
    """Formats google dhxscheduler datetime string to calendar API datetime string.
    Example: "04/25/2017 16:00" >> "2017-04-25T16:00:00-04:00"
    """
    dt_unaware = datetime.strptime(dhx_datetime, "%m/%d/%Y %H:%M")
    dt_aware = timezone.make_aware(dt_unaware, timezone.get_current_timezone())
    return dt_aware.isoformat()


def get_calendar_id_by_course_id(course_key):
    """Returns google calendar ID by given course key"""
    course_overview_data = CourseOverview.objects.filter(id=course_key).values('id', 'calendar_id')
    calendar_id = course_overview_data[0].get('calendar_id') if course_overview_data else ''
    return calendar_id


def _create_base_calendar_view_context(request, course_key):
    """
    Returns the default template context for rendering calendar view.
    """
    user = request.user
    course = get_course_with_access(user, 'load', course_key, check_if_enrolled=True)
    return {
        'csrf': csrf(request)['csrf_token'],
        'course': course,
        'user': user,
        'is_staff': bool(has_access(user, 'staff', course)),
        'calendar_id': get_calendar_id_by_course_id(course_key),
    }


class CalendarTabFragmentView(EdxFragmentView):
    """
    Component implementation of the calendar tab.
    """
    def render_to_fragment(self, request, course_id=None, **kwargs):
        """
        Render the calendar tab to a fragment.
        Args:
            request: The Django request.
            course_id: The id of the course.

        Returns:
            Fragment: The fragment representing the calendar tab.
        """

        course_key = CourseKey.from_string(course_id)
        try:
            context = _create_base_calendar_view_context(request, course_key)
            html = render_to_string('calendar_tab/calendar_tab_fragment.html', context)
            fragment = Fragment(html)
            self.add_fragment_resource_urls(fragment)

            inline_js = render_to_string('calendar_tab/calendar_tab_js.template', context)
            fragment.add_javascript(inline_js)
            return fragment

        except Exception as e:   # TODO: make it Google API specific
            html = render_to_string('calendar_tab/500_fragment.html')
            return Fragment(html)


    def vendor_js_dependencies(self):
        """
        Returns list of vendor JS files that this view depends on.
        The helper function that it uses to obtain the list of vendor JS files
        works in conjunction with the Django pipeline to ensure that in development mode
        the files are loaded individually, but in production just the single bundle is loaded.
        """
        dependencies = set()
        dependencies.update(self.get_js_dependencies('calendar_tab_vendor'))
        return list(dependencies)

    def js_dependencies(self):
        """
        Returns list of JS files that this view depends on.
        The helper function that it uses to obtain the list of JS files
        works in conjunction with the Django pipeline to ensure that in development mode
        the files are loaded individually, but in production just the single bundle is loaded.
        """
        return self.get_js_dependencies('calendar_tab')

    def css_dependencies(self):
        """
        Returns list of CSS files that this view depends on.
        The helper function that it uses to obtain the list of CSS files
        works in conjunction with the Django pipeline to ensure that in development mode
        the files are loaded individually, but in production just the single bundle is loaded.
        """
        return self.get_css_dependencies('style-calendar-tab')


def events_view(request, course_id):
    """Returns all google calendar events for given course"""
    course_key = CourseKey.from_string(course_id)
    calendar_id = get_calendar_id_by_course_id(course_key)
    try:
        response = gcal_service.events().list(calendarId=calendar_id, pageToken=None).execute()
        events = [{
                      "id": event["id"],
                      "text": event["summary"],
                      "start_date": from_google_datetime(event["start"]["dateTime"]),
                      "end_date": from_google_datetime(event["end"]["dateTime"])
                  } for event in response['items']]
    except Exception as e:
        # TODO: handle errors
        print(e)
        return JsonResponse(data={'errors': e}, status=500, safe=False)
    else:
        return JsonResponse(data=events, status=200, safe=False)


@csrf_exempt
def dataprocessor_view(request, course_id):
    """Processes insert/update/delete event requests"""
    course_key = CourseKey.from_string(course_id)
    calendar_id = get_calendar_id_by_course_id(course_key)
    status = 401
    response = {'action': 'error',
                'sid': request.POST['id'],
                'tid': '0'}

    def get_event_data(post_data):
        event = {
            'id': post_data.get('id'),
            'summary': post_data['text'],
            'location': post_data.get('location') or '',
            'description': post_data.get('description') or '',
            'start': {
                'dateTime': to_google_datetime(post_data['start_date']),
            },
            'end': {
                'dateTime': to_google_datetime(post_data['end_date']),
            },
        }
        return event

    if request.method == 'POST':
        command = request.POST['!nativeeditor_status']

        if command == 'inserted':
            event = get_event_data(request.POST)
            try:
                new_event = gcal_service.events().insert(calendarId=calendar_id,
                                                         body=event).execute()
            except Exception as e:
                # TODO: handle errors
                print(e)
                status = 500
            else:
                status = 201
                response = {"action": "inserted",
                            "sid": request.POST['id'],
                            "tid": new_event['id']}

        elif command == 'updated':
            event = get_event_data(request.POST)
            try:
                updated_event = gcal_service.events().update(calendarId=calendar_id,
                                                             eventId=event['id'],
                                                             body=event).execute()
            except Exception as e:
                # TODO: handle errors
                print(e)
                status = 500
            else:
                status = 200
                response = {"action": "updated",
                            "sid": event['id'],
                            "tid": updated_event['id']}

        elif command == 'deleted':
            event = get_event_data(request.POST)
            try:
                gcal_service.events().delete(calendarId=calendar_id,
                                             eventId=event['id']).execute()
            except Exception as e:
                # TODO: handle errors
                print(e)
                status = 500
            else:
                status = 200
                response = {"action": "deleted",
                            "sid": event['id']}

    return JsonResponse(data=response, status=status, safe=False)


class InitCalendarView(View):
    """Creates google calendar and associates it with course"""

    def post(self, request, *args, **kwargs):
        course_id = request.POST.get('courseId')
        if course_id is None:
            return HttpResponse("Provide courseID", status=400)

        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            return HttpResponse("Provide valid courseID", status=403)

        calendar_data = {
            'summary': request.POST.get('courseId'),
            'timeZone': settings.TIME_ZONE}

        try:
            created_calendar = gcal_service.calendars().insert(body=calendar_data).execute()
        except Exception as e:
            # TODO: handle errors
            print(e)
            return JsonResponse({"errors": []}, status=400)
        else:
            updated = CourseOverview.objects.filter(id=course_key) \
                                            .update(calendar_id=created_calendar['id'])
            return JsonResponse({"calendarId": created_calendar['id']}, status=201)
