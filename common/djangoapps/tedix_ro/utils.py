"""
Helper Methods
"""
import json
from urlparse import urljoin

from babel.dates import format_datetime
from django.apps import apps
from django.conf import settings
from django.urls import reverse

from courseware.models import StudentModule
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers


def get_payment_link(user):
    if not user:
        return ''
    return 'http://tedix.kloudstores.com/?email={email}&type=student'.format(
        email=user.email
    )


def report_data_preparation(user, course):
    Question = apps.get_model('tedix_ro', 'Question')
    count_answer_first_attempt = 0
    questions_data = []
    video_questions_data = {}
    header = []
    video_questions = Question.objects.filter(video_lesson__course=course.id)

    for section in course.get_children():
        for subsection in section.get_children():
            for unit in subsection.get_children():
                for problem in unit.get_children():
                    if problem.location.block_type == 'problem':
                        student_module = StudentModule.objects.filter(student=user, module_state_key=problem.location).first()
                        if student_module:
                            attempts = json.loads(student_module.state).get("attempts", 0)
                            if attempts == 1:
                                count_answer_first_attempt += 1
                        else:
                            attempts = 0
                        header.append(problem.display_name)
                        questions_data.append((problem.display_name, attempts))

    questions_id = list(video_questions.values_list('question_id', flat=True).distinct())
    header.extend(questions_id)
    for question_id in questions_id:
        video_questions_data.update({question_id: 0})

    for video_question in video_questions.filter(video_lesson__user=user):
        video_questions_data.update({video_question.question_id: video_question.attempt_count})
        if video_question.attempt_count == 1:
            count_answer_first_attempt += 1

    questions_data += list(video_questions_data.items())

    report_data = {
        'full_name': user.profile.name or user.username,
        'completion': not bool([item for item in questions_data if item[1] == 0]),
        'questions': questions_data,
        'count_answer_first_attempt': count_answer_first_attempt,
        'percent': (count_answer_first_attempt * 100 / len(questions_data)) if questions_data else 100
    }
    return header, report_data


def light_report_data_preparation(user, course):
    Question = apps.get_model('tedix_ro', 'Question')
    StudentCourseDueDate = apps.get_model('tedix_ro', 'StudentCourseDueDate')
    count_answer_first_attempt = 0
    questions = 0
    completion = True
    count_questions = 0

    for section in course.get_children():
        for subsection in section.get_children():
            for unit in subsection.get_children():
                for problem in unit.get_children():
                    if problem.location.block_type == 'problem':
                        student_module = StudentModule.objects.filter(
                            student=user,
                            module_state_key=problem.location
                        ).first()
                        if student_module:
                            attempts = json.loads(student_module.state).get("attempts", 0)
                            if attempts == 1:
                                count_answer_first_attempt += 1
                            if attempts == 0:
                                completion = False
                        else:
                            completion = False
                        count_questions += 1
    count_questions += Question.objects.filter(video_lesson__course=course.id).values('question_id').distinct().count()
    count_answer_first_attempt += Question.objects.filter(video_lesson__course=course.id, video_lesson__user=user, attempt_count=1).count()
    student_course_due_date = StudentCourseDueDate.objects.filter(student__user=user, course_id=course.id).first()
    due_date = student_course_due_date.due_date if student_course_due_date else None
    report_data = {
        'student_name': user.profile.name or user.username,
        'lesson': course.display_name,
        'completion': completion,
        'count_answer_first_attempt': count_answer_first_attempt,
        'count_questions': count_questions,
        'percent': (count_answer_first_attempt * 100 / count_questions) if count_questions else 100,
        'due_date': format_datetime(due_date, "yy.MM.dd hh:mm a", locale='en') if due_date else 'N/A',
        'report_url': urljoin(
            configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL),
            reverse('extended_report', kwargs={'course_key': course.id})
        )
    }
    return report_data
