from opaque_keys.edx.keys import CourseKey

from xmodule.modulestore.django import modulestore


def get_course_structure(course_id):
    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key, depth=4)
    course_structure = {
        "course": {
            "name": course.display_name,
            "organization": course.org,
            "sections": [],
        }
    }

    for chapter in course.get_children():
        chapter_data = {"name": chapter.display_name, "subsections": []}

        for sequence in chapter.get_children():
            sequence_data = {"name": sequence.display_name, "units": []}

            for vertical in sequence.get_children():
                vertical_data = {"name": vertical.display_name, "blocks": []}

                for block in vertical.get_children():
                    block_data = {
                        "name": block.display_name,
                        "data": block.data,
                    }
                    vertical_data["blocks"].append(block_data)
                sequence_data["units"].append(vertical_data)
            chapter_data["subsections"].append(sequence_data)
        course_structure["course"]["sections"].append(chapter_data)

    return course_structure
