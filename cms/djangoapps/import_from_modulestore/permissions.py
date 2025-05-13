"""
Permission classes for the import_from_modulestore app.
"""
from django.shortcuts import get_object_or_404
from rest_framework import permissions

from cms.djangoapps.import_from_modulestore.models import Import


class IsImportAuthor(permissions.BasePermission):
    """
    Permission class to check if the user is the author of the import.
    """

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            import_event = get_object_or_404(Import, status__uuid=view.kwargs.get('uuid'))
            return import_event.user_id == request.user.pk
        return True
