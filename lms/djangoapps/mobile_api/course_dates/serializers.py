"""
Serializers for course dates.
"""

from edx_when.models import ContentDate
from rest_framework import serializers

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.django import modulestore


class ContentDateSerializer(serializers.ModelSerializer):
    """
    Serializer for ContentDate model with additional fields.
    """

    assignment_block_id = serializers.CharField(source="location")
    due_date = serializers.CharField()
    assignment_title = serializers.SerializerMethodField()
    learner_has_access = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()

    class Meta:
        model = ContentDate
        fields = (
            "course_id",
            "assignment_block_id",
            "due_date",
            "assignment_title",
            "learner_has_access",
            "course_name",
        )

    def get_assignment_title(self, obj):
        return modulestore().get_item(obj.location).display_name

    def get_learner_has_access(self, obj):
        block = modulestore().get_item(obj.location)
        return not getattr(block, "contains_gated_content", False)

    def get_course_name(self, obj):
        course_overview = CourseOverview.objects.get(id=obj.course_id)
        return course_overview.display_name
