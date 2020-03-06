"""TO-DO: Write a description of what this XBlock is."""
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import JSONField, Scope, Integer, String, Boolean
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from hera.utils import recalculate_coins, get_scaffolds_settings


loader = ResourceLoader(__name__)

MAX_ALLOWED_SUBMISSON = 2

REPHRASE = 'rephrase'
BREAK_IT_DOWN = 'break_it_down'
TEACH_ME = 'teach_me'

class QuestionXBlock(StudioEditableXBlockMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """
    editable_fields = ('data',)
    has_score = True
    icon_class = 'problem'

    def get_icon_class(self):
        return self.icon_class

    display_name = String(default="Question")
    data = JSONField(default={})
    user_confidence = Integer(scope=Scope.user_state)
    user_answer = JSONField(scope=Scope.user_state, default='')
    user_answer_correct = Boolean(scope=Scope.user_state, default=False)
    submission_counter = Integer(scope=Scope.user_state, default=0)
    rephrase_paid = Boolean(scope=Scope.user_state, default=False)
    break_it_down_paid = Boolean(scope=Scope.user_state, default=False)
    teach_me_paid = Boolean(scope=Scope.user_state, default=False)

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
    def problem_types(self):
        return self.data.get("problemTypes", [])

    def preciseness(self, problem_type):
        preciseness = problem_type.get("preciseness")
        preciseness_values = preciseness.split('%')
        try:
            preciseness_value = float(preciseness_values[0]) if preciseness_values else 0
        except ValueError:
            preciseness_value = 0

        if preciseness.rfind('%') > -1:
            return preciseness_value * float(problem_type['answer']) / 100
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
    def break_it_down(self):
        return self.data.get("breakDown")

    @property
    def teach_me(self):
        return self.data.get("teachMe")

    @property
    def is_submission_allowed(self):
        return not self.user_answer_correct and self.submission_counter < MAX_ALLOWED_SUBMISSON

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_context(self):
        scaffolds = get_scaffolds_settings()
        return {
            "user_answer_correct": self.user_answer_correct,
            "user_answer": self.user_answer,
            "is_submission_allowed": self.is_submission_allowed,
            "submission_counter": self.submission_counter,
            "problem_types": self.problem_types,
            "img_urls": self.img_urls,
            "iframe_url": self.iframe_url,
            "description": self.description,
            "confidence_text": self.confidence_text,
            "correct_answer_text": self.correct_answer_text,
            "incorrect_answer_text": self.incorrect_answer_text,
            "rephrase_name": REPHRASE,
            "break_it_down_name": BREAK_IT_DOWN,
            "teach_me_name": TEACH_ME,
            "block_id": self.location.block_id,
            "scaffolds": {
                REPHRASE: {
                    "cost": scaffolds.rephrase_cost,
                    "color": scaffolds.rephrase_color,
                    "paid": self.rephrase_paid,
                    "data": self.rephrase,
                },
                BREAK_IT_DOWN: {
                    "cost": scaffolds.break_it_down_cost,
                    "color": scaffolds.break_it_down_color,
                    "paid": self.break_it_down_paid,
                    "data": self.break_it_down,
                },
                TEACH_ME: {
                    "cost": scaffolds.teach_me_cost,
                    "color": scaffolds.teach_me_color,
                    "paid": self.teach_me_paid,
                    "data": self.teach_me,
                },
            },
            'correct_answers': self.get_correct_answers(),
            'has_many_types': self.has_many_types(),
        }

    def get_content_html(self):
        context = self.get_context()
        html = loader.render_mako_template(
            'static/html/question.html',
            context=context
        )
        return html

    def get_correct_answers(self):
        answer = ''
        for question in self.problem_types:
            if question['type'] in ["number", "text"]:
                answer = question['answer']
            if question['type'] in ["select", "radio", "checkbox"]:
                answer = ', '.join([option["title"] for option in question['options'] if option["correct"]])
        return answer

    def has_many_types(self):
        return len(set(map(lambda x: x['type'], self.problem_types))) > 1

    def student_view(self, context=None):
        """
        The primary view of the QuestionXBlock, shown to students
        when viewing courses.
        """
        html = loader.render_mako_template(
            'static/html/main.html'
        )
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/question.css"))
        frag.add_javascript(self.resource_string("static/js/src/question.js"))

        frag.initialize_js('QuestionXBlock', json_args=self.get_context())
        return frag

    @XBlock.json_handler
    def render_html(self, data, sufix=''):
        context = self.get_context()
        context.update({
            'content': self.get_content_html()
        })
        return context

    @XBlock.json_handler
    def get_filled_tables(self, data, sufix=''):
        tables_html = []
        for problem in self.problem_types:
            if problem['type'] == 'table':
                table_html = loader.render_mako_template(
                    'static/html/table.html',
                    context={
                        'problem_type': problem
                    }
                )
                tables_html.append(table_html)
        return {
            'tables_html': tables_html
        }

    @XBlock.json_handler
    def get_data(self, somedata, sufix=''):
        return self.data

    @XBlock.json_handler
    def scaffold_payment(self, data, sufix=''):
        scaffold_name = data.get("scaffold_name")
        scaffolds_settings = get_scaffolds_settings()

        scaffold_name_mapping = {
            REPHRASE: scaffolds_settings.rephrase_cost,
            BREAK_IT_DOWN: scaffolds_settings.break_it_down_cost,
            TEACH_ME: scaffolds_settings.teach_me_cost
        }
        coins = recalculate_coins(
            str(self.course_id),
            self.location.block_id,
            self.scope_ids.user_id,
            scaffold_name_mapping[scaffold_name]
        )

        scaffold_paid_mapping = {
            REPHRASE: 'rephrase_paid',
            BREAK_IT_DOWN: 'break_it_down_paid',
            TEACH_ME: 'teach_me_paid'
        }
        if coins is not None:
            setattr(self, scaffold_paid_mapping[scaffold_name], True)
        return {
            'coins': coins,
            'scaffold_paid': getattr(self, scaffold_paid_mapping[scaffold_name])
        }

    @XBlock.json_handler
    def submit(self, data, suffix=''):
        answers = data.get("answers")
        self.submission_counter += 1
        try:
            user_confidence = int(data.get("confidence"))
        except ValueError:
            user_confidence = None

        user_answers = []

        for index, question in enumerate(self.problem_types):

            if question['type'] == "number":
                answer = False
                if answers[index][0]:
                    try:
                        temp_answer = float(answers[index][0])
                        correct_answer = float(question['answer'])
                        preciseness = self.preciseness(question)
                        answer = correct_answer - preciseness <= temp_answer <= correct_answer + preciseness
                    except ValueError:
                        pass
                user_answers.append(answer)

            elif question['type'] == "text":
                answer = answers[index][0].replace(' ', '') == question['answer'].replace(' ', '')
                user_answers.append(answer)

            elif question['type'] in ["select", "radio", "checkbox"]:
                correct_answers = [option["title"] for option in question['options'] if option["correct"]]
                answer = set(answers[index]) == set(correct_answers)
                user_answers.append(answer)

            elif question['type'] == "table":
                correct_answers = []
                for row in question['tableData'].get('rows', []):
                    correct_answers += [
                        val['value'].replace('?', '', 1) for key, val in row.items() if val['value'].startswith('?')
                    ]
                answer = set(answers[index]) == set(correct_answers)
                user_answers.append(answer)

        self.user_answer_correct = all(user_answers)

        grade_value = 1 if self.user_answer_correct else 0

        self.runtime.publish(self, 'grade', {'value': grade_value, 'max_value': 1})
        self.user_answer = answers
        self.user_confidence = user_confidence
        return {
            'correct': self.user_answer_correct,
            'is_submission_allowed': self.is_submission_allowed,
            'correct_answers': self.get_correct_answers(),
            'submission_count': self.submission_counter,
            'has_many_types': self.has_many_types(),
        }

    @XBlock.json_handler
    def skip(self, somedata, sufix=''):
        self.submission_counter += 1

        return {
            'is_submission_allowed': self.is_submission_allowed,
            'correct_answers': self.get_correct_answers(),
            'has_many_types': self.has_many_types(),
        }
