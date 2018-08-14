import json

from openedx.core.lib.api.authentication import OAuth2AuthenticationAllowInactiveUser
from openedx.core.lib.api.permissions import ApiKeyHeaderPermissionIsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from courseware.courses import get_course
from courseware.models import StudentModule, BaseStudentModuleHistory
from enrollment.views import ApiKeyPermissionMixIn, EnrollmentCrossDomainSessionAuth
from student.models import CourseEnrollment
from student.roles import GlobalStaff
from util.disable_rate_limit import can_disable_rate_limit
from opaque_keys.edx.locator import CourseLocator
import re

@can_disable_rate_limit
class SubmissionHistoryView(APIView, ApiKeyPermissionMixIn):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser, EnrollmentCrossDomainSessionAuth)
    permission_classes = (ApiKeyHeaderPermissionIsAuthenticated, )

    def get(self, request):
        username = request.GET.get('user', request.user.username)
        data = []
        all_users = request.GET.get('all', '').lower() in ('1', 'true', 'ok') and GlobalStaff().has_user(request.user)
        course_id = request.GET.get('course_id', None)

        if not (all_users or username == request.user.username or GlobalStaff().has_user(request.user) or
                self.has_api_key_permissions(request)):
            return Response(data)

        course_enrollments = CourseEnrollment.objects.select_related('user').filter(is_active=True)
        if course_id:
            if not re.match("course-v1:", course_id):
                course_id = "course-v1:{}".format(course_id)
            try:
                course_enrollments = course_enrollments.filter(
                    course_id=CourseLocator.from_string(course_id.replace(' ', '+'))
                ).order_by('created')
            except KeyError:
                return Response(data)

        if not all_users:
            course_enrollments = course_enrollments.filter(user__username=username).order_by('created')

        courses = {}
        for course_enrollment in course_enrollments:
            try:
                course_list = courses.get(course_enrollment.course_id)
                if course_list:
                    course, course_children = course_list
                else:
                    course = get_course(course_enrollment.course_id, depth=4)
                    course_children = course.get_children()
                    courses[course_enrollment.course_id] = [course, course_children]
            except ValueError:
                continue

            course_data = {
                'course_id': unicode(course_enrollment.course_id),
                'course_name': course.display_name_with_default,
                'user': course_enrollment.user.username,
                'problems': []
            }
            for section in course_children:
                for subsection in section.get_children():
                    for vertical in subsection.get_children():
                        for component in vertical.get_children():
                            if component.location.category == 'problem' and getattr(component, 'has_score', False):
                                problem_data = {
                                    'location': unicode(component.location),
                                    'name': component.display_name,
                                    'submission_history': [],
                                    'data': component.data
                                }

                                csm = StudentModule.objects.filter(
                                    module_state_key=component.location,
                                    student__username=course_enrollment.user.username,
                                    course_id=course_enrollment.course_id)

                                scores = BaseStudentModuleHistory.get_history(csm)
                                for i, score in enumerate(scores):
                                    if i % 2 == 1:
                                        continue

                                    state = score.state
                                    if state is not None:
                                        state = json.loads(state)

                                    history_data = {
                                        'state': state,
                                        'grade': score.grade,
                                        'max_grade': score.max_grade
                                    }
                                    problem_data['submission_history'].append(history_data)

                                course_data['problems'].append(problem_data)
            data.append(course_data)

        return Response(data)
