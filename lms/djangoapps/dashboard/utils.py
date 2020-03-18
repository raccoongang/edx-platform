from certificates.models import CertificateWhitelist, certificate_info_for_user
from lms.djangoapps.grades.new.course_grade import CourseGradeFactory
from lms.djangoapps.instructor_task.tasks_helper import _graded_assignments
from lms.djangoapps.verify_student.models import SoftwareSecurePhotoVerification
from student.models import CourseEnrollment


def prepare_course_grades_data(course):
    """
    Prepare grades report for a particular course.

    Mimicked Grade Report, see `upload_grades_csv`.

    Returns:
        course grades for all enrollees and modules (generator)
    """
    certificate_whitelist = CertificateWhitelist.objects.filter(course_id=course.id,
                                                                whitelist=True)
    whitelisted_user_ids = [entry.user_id for entry in certificate_whitelist]
    graded_assignments = _graded_assignments(course.id)
    enrolled_students = CourseEnrollment.objects.users_enrolled_in(course.id)

    for student, course_grade, err_msg in CourseGradeFactory().iter(course, enrolled_students):

        if not course_grade:
            # We don't collect errors, unlike standard grade reports
            continue

        enrollment_mode = CourseEnrollment.enrollment_mode_for_user(student, course.id)[0]
        verification_status = SoftwareSecurePhotoVerification.verification_status_for_user(
            student,
            course.id,
            enrollment_mode
        )
        certificate_info = certificate_info_for_user(
            student,
            course.id,
            course_grade.letter_grade,
            student.id in whitelisted_user_ids
        )

        for assignment_type, assignment_info in graded_assignments.iteritems():

            assignment_average = '-'
            if assignment_info['use_subsection_headers']:
                assignment_average = course_grade.grade_value['grade_breakdown'].get(
                    assignment_type, {}).get('percent')

            for i, subsection_location in enumerate(assignment_info['subsection_headers']):

                try:
                    subsection_grade = course_grade.graded_subsections_by_format[assignment_type][
                        subsection_location]
                except KeyError:
                    score = u'Not Available'
                else:
                    if subsection_grade.graded_total.attempted:
                        score = subsection_grade.graded_total.earned / subsection_grade.graded_total.possible
                    else:
                        score = u'Not Attempted'

                datum = [
                    course.id,
                    student.id,
                    student.email,
                    student.username,
                    course_grade.percent,
                    assignment_info['subsection_headers'].values()[i],
                    score,
                    assignment_average,
                    enrollment_mode,
                    verification_status,
                ]
                datum.extend(certificate_info)
                yield datum
