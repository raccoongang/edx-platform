"""
Tests for the testing xBlock renderers for Offline Mode.
"""

from openedx.features.offline_mode.renderer import XBlockRenderer
from xmodule.capa.tests.response_xml_factory import MultipleChoiceResponseXMLFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, BlockFactory


class XBlockRendererTestCase(ModuleStoreTestCase):
    """
    Test case for the testing `XBlockRenderer`.
    """

    def setup_course(self):
        """
        Helper method to create the course.
        """
        default_store = self.store.default_modulestore.get_modulestore_type()
        with self.store.default_store(default_store):
            self.course = CourseFactory.create()
            chapter = BlockFactory.create(parent=self.course, category='chapter')
            problem_xml = MultipleChoiceResponseXMLFactory().build_xml(
                question_text='The correct answer is Choice 2',
                choices=[False, False, True, False],
                choice_names=['choice_0', 'choice_1', 'choice_2', 'choice_3']
            )
            self.vertical_block = BlockFactory.create(
                parent_location=chapter.location,
                category='vertical',
                display_name="Vertical"
            )
            self.html_block = BlockFactory.create(
                parent=self.vertical_block,
                category='html',
                data="<p>Test HTML Content<p>"
            )
            self.problem_block = BlockFactory.create(
                parent=self.vertical_block,
                category='problem',
                display_name='Problem',
                data=problem_xml
            )

    def test_render_xblock_from_lms_html_block(self):
        self.setup_course()
        xblock_renderer = XBlockRenderer(str(self.html_block.location), user=self.user)

        result = xblock_renderer.render_xblock_from_lms()

        self.assertIsNotNone(result)
        self.assertEqual(type(result), str)

    def test_render_xblock_from_lms_problem_block(self):
        self.setup_course()
        xblock_renderer = XBlockRenderer(str(self.problem_block.location), user=self.user)

        result = xblock_renderer.render_xblock_from_lms()

        self.assertIsNotNone(result)
        self.assertEqual(type(result), str)
