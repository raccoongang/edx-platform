"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from django.urls import reverse
from lms.djangoapps.hera.utils import get_lesson_summary_xblock_context, get_scaffold, recalculate_coints

from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import JSONField, String
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

loader = ResourceLoader(__name__)


class LessonSummaryXBlock(StudioEditableXBlockMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """
    editable_fields = ('data',)

    display_name = String(default="Lesson Summary")
    data = JSONField(default={})


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_context(self):
        scaffold = get_scaffold()
        return {
            'coins_icon_url': scaffold.coin_icon.url if scaffold.coin_icon else None,
            'user_coins': recalculate_coints(str(self.location.course_key), self.location.block_id, self.scope_ids.user_id),
            'block_id': self.location.block_id,
            'user_dashboard_url': reverse('hera:dashboard'),
            'data': self.data
        }

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the LessonSummaryXBlock, shown to students
        when viewing courses.
        """
        main_html = loader.render_mako_template("static/html/main.html", {'block_id': self.location.block_id})
        frag = Fragment(main_html.format(self=self))
        frag.add_css(self.resource_string("static/css/lesson_summary.css"))
        frag.add_javascript(self.resource_string("static/js/src/lesson_summary.js"))
        frag.initialize_js('LessonSummaryXBlock', json_args=self.get_context())
        return frag

    @XBlock.json_handler
    def get_data(self, somedata, sufix=''):
        return self.data

    @XBlock.json_handler
    def render_html(self, data, sufix=''):
        course_key = self.location.course_key
        user = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        current_unit = self.parent.block_id
        context = self.get_context()
        context.update(get_lesson_summary_xblock_context(user, course_key, current_unit))
        html = loader.render_mako_template("static/html/lesson_summary.html", context)
        return {
            'content': html
        }
