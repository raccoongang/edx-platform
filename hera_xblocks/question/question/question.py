"""TO-DO: Write a description of what this XBlock is."""
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import JSONField, Scope, List, Integer
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

loader = ResourceLoader(__name__)


class QuestionXBlock(StudioEditableXBlockMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """
    editable_fields = ('data',)
    has_score = True

    data = JSONField(default={})
    user_confidence = Integer(scope=Scope.user_state)
    user_answer = JSONField(scope=Scope.user_state)

    @property
    def img_urls(self):
        return self.data.get("imgUrls", [])

    @property
    def iframe_url(self):
        return self.data.get("iframeUrl")

    @property
    def description(self):
        return self.data.get("description")

    @property
    def question(self):
        return self.data.get("question")

    @property
    def options(self):
        return self.data.get("question", {}).get("options")

    @property
    def correct_answer(self):
        return self.question.get("answer")

    @property
    def preciseness(self):
        preciseness = self.question.get("preciseness")
        preciseness_values = preciseness.split('%')
        try:
            preciseness_value = float(preciseness_values[0]) if preciseness_values else 0
        except ValueError:
            preciseness_value = 0

        if preciseness.rfind('%') > -1:
            return preciseness_value * self.correct_answer / 100
        else:
            return preciseness_value

    @property
    def confidence_text(self):
        return self.data.get("confidenceText")

    @property
    def correct_answer_text(self):
        return self.data.get("correctAnswerText")

    @property
    def incorrect_answer_text(self):
        return self.data.get("incorrectAnswerText")

    @property
    def rephrase(self):
        return self.data.get("rephrase")

    @property
    def break_down(self):
        return self.data.get("breakDown")

    @property
    def teach_me(self):
        return self.data.get("teachMe")

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_context(self):
        return {
            "user_answer": self.user_answer,
            "question": self.question,
            "img_urls": self.img_urls,
            "iframe_url": self.iframe_url,
            "description": self.description,
            "confidence_text": self.confidence_text,
            "correct_answer_text": self.correct_answer_text,
            "incorrect_answer_text": self.incorrect_answer_text,
            "options": self.options,
            "rephrase": self.rephrase,
            "break_down": self.break_down,
            "teach_me": self.teach_me
        }

    def student_view(self, context=None):
        """
        The primary view of the QuestionXBlock, shown to students
        when viewing courses.
        """
        context = self.get_context()
        html = loader.render_django_template(
            'static/html/question.html',
            context=context
        )
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/question.css"))
        frag.add_javascript(self.resource_string("static/js/src/question.js"))

        frag.add_css_url("https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.css")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.js")

        frag.initialize_js('QuestionXBlock', json_args=context)
        return frag

    @XBlock.json_handler
    def get_data(self, somedata, sufix=''):
        return self.data

    @XBlock.json_handler
    def submit(self, data, suffix=''):
        correct = False
        answer = data.get("answer")
        question_type = self.question.get('questionType')

        try:
            user_confidence = int(data.get("confidence"))
        except ValueError:
            user_confidence = None

        if question_type == "number":
            try:
                answer = float(answer)
                preciseness = self.preciseness
                if self.correct_answer - preciseness <= answer <= self.correct_answer + preciseness:
                    correct = True
            except ValueError:
                answer = None

        elif question_type == "text":
            if answer == self.correct_answer:
                correct = True

        elif question_type in ["select", "radio", "checkbox"]:
            correct_answers = [ option["title"] for option in self.options if option["correct"] is True ]
            if set(answer) == set(correct_answers):
                correct = True

        grade_value = 1 if correct else 0
        self.runtime.publish(self, 'grade', {'value': grade_value, 'max_value': 1})

        self.user_answer = answer
        self.user_confidence = user_confidence
        return correct
