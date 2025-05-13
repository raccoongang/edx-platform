"""
Serializers for the Course to Library Import API.
"""

from opaque_keys import InvalidKeyError
from opaque_keys.edx.locator import CourseLocator, LibraryLocatorV2
from rest_framework import serializers

from cms.djangoapps.import_from_modulestore.models import Import
from cms.djangoapps.import_from_modulestore.validators import validate_composition_level, validate_usage_keys_to_import


class CreateImportTaskSerializer(serializers.Serializer):
    """
    Serializer for the course to library import creation API.
    """

    source_key = serializers.CharField(
        help_text="The source course key to import from.",
        required=True,
    )
    target = serializers.CharField(
        help_text="The target library key to import into.",
        required=True,
    )
    usage_keys_string = serializers.CharField(
        help_text="Comma separated list of usage keys to import.",
        required=True,
    )
    composition_level = serializers.CharField(
        help_text="The composition level for the import.",
        required=True,
    )
    override = serializers.BooleanField(
        help_text="Whether to override existing content in the target library.",
        default=False,
    )

    def validate_source_key(self, value):
        """
        Validate the source key format.
        """
        try:
            CourseLocator.from_string(value)
        except InvalidKeyError as exc:
            raise serializers.ValidationError(f"Invalid source key: {str(exc)}") from exc
        return value

    def validate_target(self, value):
        """
        Validate the target library key format.
        """
        try:
            LibraryLocatorV2.from_string(value)
        except InvalidKeyError as exc:
            raise serializers.ValidationError(f"Invalid target library key: {str(exc)}") from exc
        return value

    def validate_usage_keys_string(self, value):
        """
        Validate the usage keys string format.
        """
        try:
            validate_usage_keys_to_import(value.split(','))
        except InvalidKeyError as exc:
            raise serializers.ValidationError(f"Invalid usage keys: {str(exc)}") from exc
        return value.split(',')

    def validate_composition_level(self, value):
        """
        Validate the composition level.
        """
        try:
            validate_composition_level(value)
        except ValueError as exc:
            raise serializers.ValidationError(f"Invalid composition level: {str(exc)}") from exc
        return value


class ImportTaskStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for the course to library import task status API.
    """
    uuid = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = Import
        fields = (
            'uuid',
            'created',
            'name',
            'state',
        )
        read_only_fields = fields

    def get_uuid(self, obj):
        """
        Get the UUID of the import task.
        """
        return str(obj.status.uuid)

    def get_state(self, obj):
        """
        Get the state of the import task.
        """
        return obj.status.state

    def get_name(self, obj):
        """
        Get the name of the import task.
        """
        return obj.status.name

    def get_created(self, obj):
        """
        Get the creation date of the import task.
        """
        return obj.status.created
