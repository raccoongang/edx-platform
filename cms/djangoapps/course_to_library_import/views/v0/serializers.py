"""

"""
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cms.djangoapps.course_to_library_import.api import create_import
from cms.djangoapps.course_to_library_import.models import CourseToLibraryImport

class CourseToLibraryImportSerializer(ModelSerializer):
    """
    Serializer for CourseToLibraryImport model.

    """

    course_ids = serializers.ListField()
    status = serializers.CharField(allow_blank=True, required=False)
    library_key = serializers.CharField(allow_blank=True, required=False)
    uuid = serializers.CharField(allow_blank=True, required=False)


    class Meta:
        model = CourseToLibraryImport
        fields = ("course_ids", "status", "library_key", "uuid")

    def create(self, validated_data):
        """

        :param validated_data:
        :return:
        """
        user = getattr(self.context.get("request"), "user", None)
        library_id = self.context.get("library_id")
        course_to_library_import = create_import(validated_data["course_ids"], getattr(user, "pk", None), library_id)
        return course_to_library_import

    def to_representation(self, instance):
        """

        :param instance:
        :return:
        """
        representation = super().to_representation(instance)
        representation["course_ids"] = "".join(representation["course_ids"])
        return representation
