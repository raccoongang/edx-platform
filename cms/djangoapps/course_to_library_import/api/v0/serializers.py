"""
Serializers for the Course to Library Import API.
"""

from rest_framework import serializers
from cms.djangoapps.course_to_library_import.validators import (
    validate_composition_level,
)


class ImportBlocksSerializer(serializers.Serializer):
    """
    Serializer for the import blocks API.
    """

    library_key = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)
    usage_ids = serializers.ListField(
        child=serializers.CharField(),
        required=True,
    )
    course_id = serializers.CharField(required=True)
    task_id = serializers.CharField(required=False)
    composition_level = serializers.CharField(
        required=True,
        validators=[validate_composition_level],
    )
    override = serializers.BooleanField(default=False, required=False)
