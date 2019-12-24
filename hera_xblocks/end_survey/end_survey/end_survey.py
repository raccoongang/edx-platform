import pkg_resources

from django.contrib.auth.models import User
from web_fragments.fragment import Fragment

from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, List, JSONField
from xblock.runtime import Runtime
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.resources import ResourceLoader

from student.models import get_user_by_username_or_email

loader = ResourceLoader(__name__)

@XBlock.wants('user')
class EndSurveyXBlock(StudioEditableXBlockMixin, XBlock):
    """
    XBLock response to take the surver from the student.
    When he passed the lesson.
    """

    editable_fields = ('data',)

    data = JSONField(default={})
    user_count = Integer(default=0, scope=Scope.user_state_summary)
    result_summary = List(default=[], scope=Scope.user_state_summary)
    user_result = List(default=[], scope=Scope.user_state_summary)

    @property
    def questions(self):
        return self.data.get("questions")

    @property
    def title(self):
        return self.data.get("title")

    def user_is_staff(self):
        """
        This is a function which is return differnt html templates, depends on user is staff or not.
             - end_survey_staff is template with statistics from all the students.
             - end_survey_user is template with survey questions for the student.
        """

        user_service = self.runtime.service(self, 'user')
        xb_user = user_service.get_current_user()
        email = xb_user.emails[0] if xb_user.emails else None

        try:
            if email:
                user = get_user_by_username_or_email(username_or_email=email)
        except User.DoesNotExist:
            return None

        if user.is_staff:
            context = self.get_context_staff()
            template = 'static/html/end_survey_staff.html'
        else:
            context = self.get_context()
            template = 'static/html/end_survey_user.html'

        html = loader.render_django_template(
            template,
            context=context
        )

        return html

    def get_context(self):
        """ user context. """
        return {
            "user_result": self.user_result,
            "questions": self.questions,
            "title": self.title,
        }

    def get_context_staff(self):
        """ staff context. """

        return {
            "questions": self.questions,
            "title": self.title,
            "user_count": self.user_count
            # TODO: wrire self.result_summary
            # "result_summary": ''
        }

    def resource_string(self, path):
        """ Handy helper for getting resources from our kit. """
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @XBlock.json_handler
    def get_data(self, data, sufix=''):
        return self.data

    @XBlock.json_handler
    def vote(self, data, sufix=''):
        """ TODO: write what this function do """

        self.user_result = data
        self.result_summary.append(data)
        self.user_count += 1

    def student_view(self, context=None):
        """
        The primary view of the EndSurveyXBlock, shown to students
        when viewing courses.
        """
        
        html = self.user_is_staff()
        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/end_survey.css"))
        frag.add_javascript(self.resource_string("static/js/src/end_survey.js"))
        frag.add_javascript_url("https://cdn.jsdelivr.net/gh/vast-engineering/jquery-popup-overlay@2/jquery.popupoverlay.min.js")

        frag.initialize_js('EndSurveyXBlock')
        return frag
