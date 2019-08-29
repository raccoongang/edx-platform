from django.contrib.auth.models import User

from courseware.courses import get_course_with_access
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory


def calculate_students_grades_report(course_id):
    """
    Util function that generates custom students grades report.

    :param course_id: CourseKey
    :return: List of lists for generating csv file.
    example output: [
        ['header_1', header_2],
        ['first_row_1', 'first_row_2'],
        ...
    ]
    """

    students = User.objects.filter(
        courseenrollment__course_id=course_id,
        courseenrollment__is_active=1,
    ).order_by('id').prefetch_related('course_groups')

    output = list()

    headers = ['email', 'cohort']

    for student in students:

        # Check student access
        course = get_course_with_access(student, 'load', course_id, check_if_enrolled=True)

        # Get students grade
        course_grade = CourseGradeFactory().read(student, course)
        courseware_summary = course_grade.chapter_grades.values()

        # Add headers for csv report
        if len(headers) == 2:
            for chapter in courseware_summary:
                if chapter['sections']:
                    for section in chapter['sections']:
                        if section.problem_scores.values():
                            headers += [
                                u'{chapter} / {section} ({score})'.format(
                                    chapter=chapter['display_name'],
                                    section=section.display_name,
                                    score=float(score.possible)
                                )
                                for score in section.problem_scores.values()]
                        else:
                            headers += [
                                u'{chapter} / {section} (n/g)'.format(
                                    chapter=chapter['display_name'],
                                    section=section.display_name,
                                )
                            ]
                else:
                    headers += [u'{} (n/g)'.format(chapter['display_name'])]

            output.append(headers)

        student_cohort = student.course_groups.first().name if student.course_groups.first() else '-'
        rows = [student.email, student_cohort]

        for chapter in courseware_summary:
            if not chapter['display_name'] == "hidden":
                if chapter['sections']:
                    for section in chapter['sections']:
                        if section.problem_scores.values():
                            rows += [float(score.earned) for score in section.problem_scores.values()]
                        else:
                            rows.append('-')
                else:
                    rows.append('-')
        output.append(rows)

    return output
