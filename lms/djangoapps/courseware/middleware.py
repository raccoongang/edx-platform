"""
Middleware for the courseware app
"""
import crum
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from courseware.courses import UserNotEnrolled


class RedirectUnenrolledMiddleware(object):
    """
    Catch UserNotEnrolled errors thrown by `get_course_with_access` and redirect
    users to the course about page
    """
    
    def process_exception(self, _request, exception):
        if isinstance(exception, UserNotEnrolled):
            course_key = exception.course_key
            return redirect(
                reverse(
                    'courseware.views.views.course_about',
                    args=[course_key.to_deprecated_string()]
                )
            )


class CustomCurrentRequestUserMiddleware(crum.CurrentRequestUserMiddleware):
    """
    Overide the process_exception() method in CurrentRequestUserMiddleware class for
    using custom theme with 404 page.
    """

    def process_exception(self, request, exception):
        # overided method to not clear the request
        pass
