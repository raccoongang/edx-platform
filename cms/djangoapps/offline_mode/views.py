from django.http import HttpResponse

from .tasks import generate_offline_content_for_course


def generate_offline_archive(request, course_id):
    generate_offline_content_for_course.apply_async([str(course_id)])
    return HttpResponse("Offline archive generation started.")
