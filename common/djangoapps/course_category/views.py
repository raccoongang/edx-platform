from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .tasks import task_enroll_category
from .models import CourseCategory


@require_POST
@login_required
@ensure_csrf_cookie
def enroll_category(request):
    '''
    Handle student enrollment to all category courses.
    '''
    slug = request.POST['slug']
    # Get the user.
    user = request.user

    task_enroll_category(user.id, slug, request.is_secure())

    return JsonResponse({'Status': 'OK'})
