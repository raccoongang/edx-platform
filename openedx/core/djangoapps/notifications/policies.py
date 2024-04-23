"""Policies for the notifications app."""

from edx_ace.channel import ChannelType
from edx_ace.policy import Policy, PolicyResult
from opaque_keys.edx.keys import CourseKey

from .models import CourseNotificationPreference


class CoursePushNotificationOptout(Policy):
    """
    Course Push Notification optOut Policy.
    """

    def check(self, message):
        """
        Check if the user has opted out of push notifications for the given course.
        :param message:
        :return:
        """
        course_ids = message.context.get('course_ids', [])
        notification_type = message.context.get('notification_type', 'push')
        app_name = message.context.get('app_name')

        if not app_name:
            return PolicyResult(deny={ChannelType.PUSH})

        course_keys = [CourseKey.from_string(course_id) for course_id in course_ids]
        for course_key in course_keys:
            course_notif_preference = CourseNotificationPreference.get_user_course_preference(
                message.recipient.lms_user_id,
                course_key
            )

            if not course_notif_preference.get_notification_type_config(app_name, notification_type).get('push', False):
                return PolicyResult(deny={ChannelType.PUSH})

        return PolicyResult(deny=frozenset())
