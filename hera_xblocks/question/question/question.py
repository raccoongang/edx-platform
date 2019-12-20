"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import JSONField
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin


loader = ResourceLoader(__name__)

class QuestionXBlock(StudioEditableXBlockMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """
    editable_fields = ('data',)

    data = JSONField()

    @property
    def img_url(self):
        return self.data.get("imgUrl")

    @property
    def iframe_url(self):
        return self.data.get("iframeUrl")

    @property
    def description(self):
        return self.data.get("description")

    @property
    def options(self):
        return self.data.get("options")

    @property
    def user_confidence(self):
        return self.data.get("userConfidence")

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
            "img_url": self.img_url,
            "iframe_url": self.iframe_url,
            "description": self.description,
            "confidence_text": self.confidence_text,
            "options": self.options
        }

    def student_view(self, context=None):
        """
        The primary view of the QuestionXBlock, shown to students
        when viewing courses.
        """
        html = loader.render_django_template(
            'static/html/question.html',
            context=self.get_context()
        )
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/question.css"))
        frag.add_javascript_url("https://cdn.jsdelivr.net/gh/vast-engineering/jquery-popup-overlay@2/jquery.popupoverlay.min.js")
        frag.add_javascript(self.resource_string("static/js/src/question.js"))
        frag.initialize_js('QuestionXBlock')
        return frag

    @XBlock.json_handler
    def submit(self, answer, suffix=''):
        correct_answers = [ option["title"] for option in self.options if option["correct"]==True ]
        print(answer, correct_answers)
        return True if answer in correct_answers else False
