from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView

from opaque_keys.edx.keys import CourseKey
from courseware.courses import get_course_with_access

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

        context = super(CalendarView, self).get_context_data(**kwargs)
        context['course'] = course
        context['csrf_token'] = csrf(self.request)["csrf_token"]
        return context

    def get_success_url(self):
        return reverse_lazy('calendar_view', kwargs={'course_id': self.kwargs['course_id']})
