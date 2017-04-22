from django.conf import settings
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View
from django.views.generic.edit import FormView
from opaque_keys import InvalidKeyError

from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from courseware.courses import get_course_with_access
from courseware.access import has_access

from .forms import EventForm
from .utils import gcal_service, publish_calendar


class CalendarView(FormView):
    template_name = 'calendar_tab/calendar_tab_page.html'
    form_class = EventForm

    def form_valid(self, form):
        # TODO: can we get 'calendar_id' without getting the context?
        context = self.get_context_data()
        form.create_event(context['calendar_id'])
        return super(CalendarView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        course_key = CourseKey.from_string(self.kwargs['course_id'])
        course = get_course_with_access(self.request.user, "load", course_key)
        is_staff = bool(has_access(self.request.user, 'staff', course))
        course_overview_data = CourseOverview.objects.filter(id=course_key).values('id', 'calendar_id')
        calendar_id = course_overview_data[0].get('calendar_id') if course_overview_data else ''
        calendar_url = "https://calendar.google.com/calendar/embed?src={0}&ctz={1}".format(
            calendar_id, settings.TIME_ZONE)

        context = super(CalendarView, self).get_context_data(**kwargs)
        context['course'] = course
        context['csrf_token'] = csrf(self.request)["csrf_token"]
        context['is_staff'] = is_staff
        context['calendar_id'] = calendar_id
        context['calendar_url'] = calendar_url
        return context

    def get_success_url(self):
        return reverse_lazy('calendar_view', kwargs={'course_id': self.kwargs['course_id']})


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
            'timeZone': settings.TIME_ZONE
        }

        try:
            created_calendar = gcal_service.calendars().insert(body=calendar_data).execute()
            publish_calendar(created_calendar['id'])
        except Exception as e:
            # TODO: handle errors
            print(e)
            return JsonResponse({"errors": []}, status=400)
        else:
            updated = CourseOverview.objects.filter(id=course_key)\
                                            .update(calendar_id=created_calendar['id'])
            return JsonResponse({"calendarId": created_calendar['id']}, status=201)


def share_course_calendar(request):
    pass

