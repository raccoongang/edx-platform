import unicodecsv as csv

from django.utils import timezone

from lms.djangoapps.grades.models import PersistentCourseGrade

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


def csv_course_report(f):
    field_names = [
        'Candidate RSA ID number',
        'Candidate First Name',
        'Candidate Last Name',
        'Enrollment Date',
        '% Complete to date',
        'Completion Date',
        'Duration between enrollment and completion',
    ]
    writer = csv.DictWriter(f, fieldnames=field_names)
    for course in CourseOverview.objects.all():
        course_title = [course.display_name]
        course_title.extend([''] * (len(field_names) - 1))
        writer.writerow(dict(zip(field_names, course_title)))
        writer.writeheader()

        for enrollment in course.courseenrollment_set.filter(is_active=True):
            row_values = []
            user = enrollment.user
            row_values.append(user.username)
            row_values.append(user.first_name)
            row_values.append(user.last_name)
            row_values.append(timezone.localtime(enrollment.created))

            try:
                grade = PersistentCourseGrade.objects.get(user_id=user.id, course_id=course.id)
                row_values.append(grade.percent_grade * 100)
                row_values.append(timezone.localtime(grade.passed_timestamp))
                row_values.append(grade.passed_timestamp - enrollment.created)
            except:
                row_values.extend([''] * (len(field_names) - len(row_values)))

            writer.writerow(dict(zip(field_names, row_values)))

        writer.writerow(dict(zip(field_names, [''] * len(field_names))))
