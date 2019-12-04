from django.http import Http404


class RestrictPages(object):
    """
    Checks the path user are going to and raise 404 if it's not allowed.
    """
    allowed_paths = [
        '/courseware',
        '/dashboard',
        '/onboarding',
        '/selection_page'
    ]

    def is_allowed(self, path):
        return any(map(lambda x: x in path, self.allowed_paths))

    def process_request(self, request):
        if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest' and not self.is_allowed(request.path):
            raise Http404()
