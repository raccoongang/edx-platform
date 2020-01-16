"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import JSONField, String
from xblockutils.studio_editable import StudioEditableXBlockMixin


class HeraTitleXBlock(StudioEditableXBlockMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """
    editable_fields = ('data',)

    display_name = String(default="Hera Title")
    data = JSONField(default={})


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the HeraTitleXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/hera_title.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/hera_title.css"))
        frag.add_javascript(self.resource_string("static/js/src/hera_title.js"))
        frag.initialize_js('HeraTitleXBlock')
        return frag

    @XBlock.json_handler
    def get_data(self, somedata, sufix=''):
        return self.data
