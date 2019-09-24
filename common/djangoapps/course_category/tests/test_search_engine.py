import pytest

from course_category.models import CourseCategory, Program
from course_category.search_engine import _search_programs


@pytest.mark.django_db
@pytest.mark.parametrize(
    "search_param,expected", [
        ({'query_string': '',
            'field_dictionary': {'category': ''}}, 4),
        ({'query_string': 'test',
            'field_dictionary': {'category': ''}}, 2),
        ({'query_string': '',
            'field_dictionary': {'category': 'test_category'}}, 1),
        ({'query_string': 'test',
            'field_dictionary': {'category': 'test_category'}}, 1)
    ]
)
def test_search_programs(search_param, expected):
    """
    Test search results for programs.
    """

    uuids = [1, 2, 3, 4]
    titles = ['test', 'not_match', 'not_match2', 'not_match3']
    subtitles = ['not_match', 'not_match2', 'not_match3', 'test']
    course_categories = ['test_category', 'not_match', 'not_match2', 'not_match3']
    for i in range(len(uuids)):
        program = Program.objects.create(
                    uuid=uuids[i],
                    title=titles[i],
                    subtitle=subtitles[i],
                )
        category = CourseCategory.objects.create(
                    name=course_categories[i],
                    id=uuids[i],
                    slug=course_categories[i]
                )
        category.programs.add(program)
    test_call = _search_programs(**search_param)
    result = len(test_call)
    assert result == expected
