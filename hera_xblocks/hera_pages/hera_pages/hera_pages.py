"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import JSONField
from xblockutils.studio_editable import StudioEditableXBlockMixin


class HeraPagesXBlock(StudioEditableXBlockMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    data = JSONField()

    @property
    def img_url(self):
        """return images for the pages"""
        return self.data.get('imgUrl')

    @property
    def frame_url(self):
        """return iframe for the pages"""
        return self.data.get('iframeUrl')

    @property
    def slide_bar(self):
        """return html content for the slide bar in pages"""
        return self.data.get('sliderBar')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the HeraPagesXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/hera_pages.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/hera_pages.css"))
        frag.add_javascript(self.resource_string("static/js/src/hera_pages.js"))
        frag.initialize_js('HeraPagesXBlock')
        return frag
