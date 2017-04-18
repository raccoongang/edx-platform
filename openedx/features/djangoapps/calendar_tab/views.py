from django.core.context_processors import csrf
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView

from opaque_keys.edx.keys import CourseKey
from courseware.courses import get_course_with_access
from courseware.access import has_access

from .forms import EventForm


class CalendarView(FormView):
    template_name = 'calendar_tab/calendar_tab_page.html'
    form_class = EventForm

    def form_valid(self, form):
        form.create_event()
        return super(CalendarView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        course_key = CourseKey.from_string(self.kwargs['course_id'])
        course = get_course_with_access(self.request.user, "load", course_key)
        is_staff = bool(has_access(self.request.user, 'staff', course))

        context = super(CalendarView, self).get_context_data(**kwargs)
        context['course'] = course
        context['csrf_token'] = csrf(self.request)["csrf_token"]
        context['is_staff'] = is_staff
        return context

    def get_success_url(self):
        return reverse_lazy('calendar_view', kwargs={'course_id': self.kwargs['course_id']})


def create_course_calendar(request):
    """Creates google calendar and associates it with course"""

    # # create new calendar:
    # calendar = {
    #     'summary': 'calendarSummary',
    #     'timeZone': 'America/Los_Angeles'
    # }
    # created_calendar = gcal_service.calendars().insert(body=calendar).execute()
    # print created_calendar['id']
    pass


def share_course_calendar(request):
    """Shares course google calendar to provided google account"""

    # make calendar public:
    # rule = {
    #     'scope': {
    #         'type': 'default',
    #     },
    #     'role': 'reader'
    # }
    #
    # created_rule = gcal_service.acl().insert(calendarId=calendar_id, body=rule).execute()
    # print created_rule['id']
    pass
