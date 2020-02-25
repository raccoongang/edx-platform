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
    XBLock response to take the survey from the student
    when he passed the lesson.
    """

    editable_fields = ('data',)

    user_count = Integer(default=0, scope=Scope.user_state_summary)
    data = JSONField(default={})
    user_result = JSONField(default={}, scope=Scope.user_state)
    result_summary = List(default=[], scope=Scope.user_state_summary)
    results_percentage = JSONField(default={}, scope=Scope.user_state_summary)

    @property
    def questions(self):
        return self.data.get("questions")

    @property
    def confidence(self):
        return self.data.get("confidence")

    @property
    def title(self):
        return self.data.get("heading")

    @property
    def mascot_url(self):
        return self.data.get("imgUrl")

    def result_summary_count(self):
        """
        Counter for survey results.

        Returns dict in following format:
            {
                "questions": {
                    "question1": {
                        "possible_answer1": procent,
                        "possible_answer2": procent,
                    },
                    "question2": {
                        "possible_answer1": procent,
                        "possible_answer2": procent,
                    },
                },
                "confidence": {
                    "question": {
                        "possible_answer1": procent,
                        "possible_answer2": procent,
                    },
                },
            }
        """
        # Initialise dict:
        results = {
            "questions": {
                question.get("questionText"): {
                    answer: 0 for answer in question.get("possibleAnswers", [])
                } for question in self.questions
            },
            "confidence": {
                self.confidence.get("questionText"): {
                    answer: 0 for answer in self.confidence.get("possibleAnswers", [])
                }
            }
        }
        # Count percentage:
        for single_student_result in self.result_summary:
            for question, answer in single_student_result['answersData'].items():
                results["questions"][question][answer] += (round((1.0/float(self.user_count))*100, 1))
            for question, answer in single_student_result['confidenceData'].items():
                results["confidence"][question][answer] += (round((1.0/float(self.user_count))*100, 1))

        return results

    def get_user(self):
        user_service = self.runtime.service(self, 'user')
        xb_user = user_service.get_current_user()
        email = xb_user.emails[0] if xb_user.emails else None
        if email:
            try:
                user = get_user_by_username_or_email(username_or_email=email)
            except User.DoesNotExist:
                pass
            return user

    def html_for_role(self):
        """
        This is a function which return different html templates, depends whether user is staff or not.
             - end_survey_staff is template with statistics from all the students.
             - end_survey_user is template with survey questions or results for the current student.
        """
        user = self.get_user()
        if user and user.is_staff:
            context = self.get_context_staff()
            template = 'static/html/end_survey_staff.html'
        else:
            # Main context for student.
            context = self.get_context()
            # Main template for student.
            template = 'static/html/end_survey_user.html'

            if self.user_result:
                # User already submited his answer, add his results to context.
                content = loader.render_mako_template(
                    'static/html/student_completed.html',
                    context=context
                )
            else:
                # Add survey form to context.
                content = loader.render_mako_template(
                    'static/html/student_form.html',
                    context=context
                )
            context.update({'content': content})

        html = loader.render_mako_template(
            template,
            context=context
        )

        return html

    def get_common_context(self):
        return {
            'block_id': self.location.block_id,
            'user': self.get_user()
        }

    def get_context(self):
        """User context."""
        context = self.get_common_context()
        context.update({
            "user_result": self.user_result,
            "questions": self.questions,
            "title": self.title,
            "confidence": self.confidence,
            "mascot_url": self.mascot_url
        })
        return context

    def get_context_staff(self):
        """Staff context."""
        context = self.get_common_context()
        context.update({
            "title": self.title,
            "results_percentage": self.result_summary_count(),
        })
        return context

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @XBlock.json_handler
    def get_data(self, data, sufix=''):
        return self.data

    @XBlock.json_handler
    def vote(self, data, sufix=''):
        """
        Save current user result, start recalculating total students results
        and returns rendered student result html fragment.
        """
        self.user_count += 1
        self.user_result = data
        self.result_summary.append(data)
        context = self.get_context()
        return loader.render_mako_template(
            'static/html/student_completed.html',
            context=context
        )

    def student_view(self, context=None):
        """
        The primary view of the EndSurveyXBlock, shown to students
        when viewing courses.
        """
        html = self.html_for_role()
        context = self.get_common_context()
        context.update({
            'content': html
        })
        main = loader.render_mako_template(
            'static/html/main.html', context
        )
        frag = Fragment(main)
        frag.add_css(self.resource_string("static/css/end_survey.css"))
        frag.add_javascript(self.resource_string("static/js/src/end_survey.js"))

        frag.initialize_js('EndSurveyXBlock', json_args={'block_id': self.location.block_id})
        return frag
