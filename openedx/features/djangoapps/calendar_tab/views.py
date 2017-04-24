from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View

from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from courseware.courses import get_course_with_access
from courseware.access import has_access

from .utils import gcal_service, publish_calendar


def from_google_datetime(g_datatime):
    """Formats google calendar API datetime string to dhxscheduler datetime string.
    Example: "2017-04-25T16:00:00-04:00" >> "04/25/2017 16:00"
    """
    return datetime.strptime(g_datatime[:-6], "%Y-%m-%dT%H:%M:%S").strftime("%m/%d/%Y %H:%M")


def to_google_datetime(dhx_datatime):
    """Formats google dhxscheduler datetime string to calendar API datetime string.
    Example: "04/25/2017 16:00" >> "2017-04-25T16:00:00-04:00"
    """
    dt_unaware = datetime.strptime(dhx_datatime, "%m/%d/%Y %H:%M")
    dt_aware = timezone.make_aware(dt_unaware, timezone.get_current_timezone())
    return dt_aware.isoformat()


def get_calendar_id_by_course_id(course_key):
    """Returns google calendar ID by given course key"""
    course_overview_data = CourseOverview.objects.filter(id=course_key).values('id', 'calendar_id')
    calendar_id = course_overview_data[0].get('calendar_id') if course_overview_data else ''
    return calendar_id


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
            publish_calendar(created_calendar['id'])
        except Exception as e:
            # TODO: handle errors
            print(e)
            return JsonResponse({"errors": []}, status=400)
        else:
            updated = CourseOverview.objects.filter(id=course_key) \
                                            .update(calendar_id=created_calendar['id'])
            return JsonResponse({"calendarId": created_calendar['id']}, status=201)


class CalendarView(TemplateView):
    """Main view: renders calendar"""
    template_name = 'calendar_tab/calendar_tab_page.html'

    def get_context_data(self, **kwargs):
        course_key = CourseKey.from_string(self.kwargs['course_id'])
        course = get_course_with_access(self.request.user, "load", course_key)
        is_staff = bool(has_access(self.request.user, 'staff', course))
        calendar_id = get_calendar_id_by_course_id(course_key)

        context = super(CalendarView, self).get_context_data(**kwargs)
        context['course'] = course
        context['is_staff'] = is_staff
        context['calendar_id'] = calendar_id
        return context


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
