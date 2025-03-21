"""

"""
from lxml import etree

from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.generics import CreateAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.response import Response

from cms.djangoapps.course_to_library_import.constants import COURSE_TO_LIBRARY_IMPORT_PURPOSE
from cms.djangoapps.course_to_library_import.models import CourseToLibraryImport
from cms.djangoapps.course_to_library_import.views.v0.serializers import CourseToLibraryImportSerializer
from openedx.core.djangoapps.content_staging import api as content_staging_api


class CreateCourseToLibraryImportView(CreateAPIView):
    """
    Allows to create course to library.

    /course-to-library-import/v0/create-import/lib:org:123/

    """
    serializer_class = CourseToLibraryImportSerializer
    permission_classes = (permissions.IsAdminUser,)
    # authentication_classes = (
    #     JwtAuthentication,
    #     BearerAuthenticationAllowInactiveUser,
    #     SessionAuthenticationAllowInactiveUser,
    # )

    def get_serializer_context(self) -> dict:
        """
        Extra context provided to the serializer class with current provider. We need the provider to
        remove idp_slug from the remote_id if there is any
        """
        context = super().get_serializer_context()
        context["library_id"] = self.kwargs["lib_key_str"]
        return context


class GetCourseStructureToLibraryImportView(RetrieveAPIView):
    """

    """

    queryset = CourseToLibraryImport.objects.all()
    lookup_field = "uuid"
    lookup_url_kwarg = "course_to_lib_uuid"
    permission_classes = (permissions.IsAdminUser,)
    # authentication_classes = (
    #     JwtAuthentication,
    #     BearerAuthenticationAllowInactiveUser,
    #     SessionAuthenticationAllowInactiveUser,
    # )

    def get(self, request, *args, **kwargs) -> Response:
        ctl = get_object_or_404(CourseToLibraryImport, uuid=self.kwargs["course_to_lib_uuid"])
        courses = {}
        for course_id in ctl.course_ids.split():
            courses[course_id] = self.get_structure_for_course_from_stage_content(course_id)

        return Response(courses)


    def get_structure_for_course_from_stage_content(self, course_id: str) -> list[dict]:
        """

        :param course_id:
        :return:
        """
        parser = etree.XMLParser(strip_cdata=False)
        staged_content = content_staging_api.get_ready_staged_content_by_user_and_purpose(
            4, COURSE_TO_LIBRARY_IMPORT_PURPOSE.format(course_id=course_id)
        )

        nodes = []
        from opaque_keys.edx.keys import UsageKey

        for staged_content_item in staged_content:

            staged_keys = [UsageKey.from_string(key) for key in staged_content_item.tags.keys()]
            block_id_to_usage_key = {key.block_id: key for key in staged_keys}


            node = etree.fromstring(staged_content_item.olx, parser=parser)
            nodes.append(self.build_node_dict(node, block_id_to_usage_key))

        return nodes


    def build_node_dict(self, node, block_id_to_usage_key):
        """

        """
        usage_key = block_id_to_usage_key.get(node.get("url_name"))
        if usage_key:
            node_dict = {
                str(usage_key): node.get("display_name") or node.tag,
            }

            children = node.getchildren()
            if children and node.tag in ("chapter", "sequential", "vertical"):
                node_dict.update({
                    "children": [self.build_node_dict(child, block_id_to_usage_key) for child in children]
                })

            return node_dict
