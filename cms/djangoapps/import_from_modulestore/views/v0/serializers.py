"""
Serializers for the Course to Library Import API.
"""

from rest_framework import serializers

from cms.djangoapps.import_from_modulestore import api
from cms.djangoapps.import_from_modulestore.models import Import
from cms.djangoapps.import_from_modulestore.validators import validate_composition_level


class ImportBlocksSerializer(serializers.Serializer):
    """
    Serializer for the import blocks API.
    """

    library_key = serializers.CharField(required=True)
    usage_ids = serializers.ListField(
        child=serializers.CharField(),
        required=True,
    )
    course_id = serializers.CharField(required=True)
    import_uuid = serializers.CharField(required=True)
    composition_level = serializers.CharField(
        required=True,
        validators=[validate_composition_level],
    )
    override = serializers.BooleanField(default=False, required=False)


class CourseToLibraryImportSerializer(serializers.Serializer):
    """
    Serializer for CourseToLibraryImport model.
    """

    course_ids = serializers.ListField()
    status = serializers.CharField(allow_blank=True, required=False)
    library_key = serializers.CharField(allow_blank=True, required=False)
    uuid = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        fields = ('course_ids', 'status', 'library_key', 'uuid')

    def to_representation(self, instance):
        """
        Converts a string with course IDs into a list of strings with course IDs.
        """
        representation = super().to_representation(instance)
        representation['course_ids'] = ''.join(representation['course_ids']).split()
        return representation
