from common.djangoapps.util.views import ensure_valid_course_key
from lms.djangoapps.courseware.exceptions import Redirect
from openedx.features.course_experience.url_helpers import get_learning_mfe_home_url


@ensure_valid_course_key
def mentoring(request, course_id):
    """
    Simply redirects to the MFE mentoring tab.
    """
    raise Redirect(get_learning_mfe_home_url(course_key=course_id, url_fragment='mentoring', params=request.GET))
