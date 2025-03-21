"""
API v0 views.
"""

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.djangoapps.course_to_library_import.py_api import import_library_from_staged_content
from .serializers import ImportBlocksSerializer


class ImportBlocksView(APIView):
    """
    Import blocks from a course to a library.
    """

    permission_classes = (IsAdminUser,)
    serializer_class = ImportBlocksSerializer

    def post(self, request, *args, **kwargs):
        """
        Import blocks from a course to a library.
        """
        data = self.serializer_class(data=request.data)
        data.is_valid(raise_exception=True)

        try:
            import_library_from_staged_content(
                library_key=data.validated_data["library_key"],
                user_id=data.validated_data["user_id"],
                usage_ids=data.validated_data["usage_ids"],
                course_id=data.validated_data["course_id"],
                task_id=data.validated_data["task_id"],
                composition_level=data.validated_data["composition_level"],
                override=data.validated_data["override"],
            )
            return Response({"status": "success"})
        except ValueError as exc:
            return Response({"status": "error", "message": str(exc)}, status=400)
