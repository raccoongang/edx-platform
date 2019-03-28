from rest_framework import serializers
from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext as _

from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import DuplicateCourseError
from opaque_keys import InvalidKeyError
from cms.djangoapps.contentstore.views.course import create_new_course
from util.string_utils import _has_non_ascii_characters
from util.organizations_helpers import (
    add_organization_course, get_organization_by_short_name, organizations_enabled
)


class CourseCreateSerializer(serializers.Serializer):
    org = serializers.CharField(required=True)
    number = serializers.CharField(required=True)
    run = serializers.CharField(required=True)
    display_name = serializers.CharField(required=True)

    def to_representation(self, obj):
        return {'course_id': unicode(obj.id)}

    def _non_ascii_error(self, field):
        return _('Special characters not allowed in \'{field}\' field.').format(field=field)

    def create(self, validated_data):
        errors = {}
        org = validated_data.pop('org')
        number = validated_data.pop('number')
        run = validated_data.pop('run')
        user = self.context['request'].user

        if not settings.FEATURES.get('ALLOW_UNICODE_COURSE_ID'):
            if _has_non_ascii_characters(org):
                errors['org'] = [self._non_ascii_error('org')]

            if _has_non_ascii_characters(number):
                errors['number'] = [self._non_ascii_error('number')]

            if _has_non_ascii_characters(run):
                errors['run'] = [self._non_ascii_error('run')]

        org_data = get_organization_by_short_name(org)
        if not org_data and organizations_enabled():
            errors['org'] = errors.get('org', []) + [
                _('You must link this course to an organization in order to continue. Organization '
                'you selected does not exist in the system, you will need to add it to the system')
            ]

        if errors:
            raise serializers.ValidationError(errors)

        with transaction.atomic():
            try:
                store = modulestore().default_modulestore.get_modulestore_type()
                validated_data.update({
                    'language': getattr(settings, 'DEFAULT_COURSE_LANGUAGE', 'en'),
                    'cert_html_view_enabled': True,
                })

                with modulestore().default_store(store):
                    new_course = modulestore().create_course(
                        org,
                        number,
                        run,
                        None,
                        fields=validated_data,
                    )
            except DuplicateCourseError  as e:
                raise serializers.ValidationError({'error': [_('Cannot create duplicate course {course_id}'.format(course_id=e.course_id))]})
            except InvalidKeyError as e:
                raise serializers.ValidationError({'error': 'Unable to create course: \'{error}\''.format(error=e.message)})
            else:
                add_organization_course(org_data, new_course.id)
            return new_course
