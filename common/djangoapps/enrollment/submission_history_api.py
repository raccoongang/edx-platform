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


@can_disable_rate_limit
class SubmissionHistoryView(APIView, ApiKeyPermissionMixIn):
    authentication_classes = (OAuth2AuthenticationAllowInactiveUser, EnrollmentCrossDomainSessionAuth)
    permission_classes = (ApiKeyHeaderPermissionIsAuthenticated, )

    def get(self, request):
        username = request.GET.get('user', request.user.username)
        data = []

        if not (username == request.user.username or GlobalStaff().has_user(request.user) or
                self.has_api_key_permissions(request)):
            return Response(data)

        course_enrollments = CourseEnrollment.objects.filter(
            user__username=username,
            is_active=True
        ).order_by('created')

        for course_enrollment in course_enrollments:
            try:
                course = get_course(course_enrollment.course_id, depth=4)
            except ValueError:
                continue

            course_data = {
                'course_id': unicode(course_enrollment.course_id),
                'course_name': course.display_name_with_default,
                'problems': []
            }
            for section in course.get_children():
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
                                    student__username=username,
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
