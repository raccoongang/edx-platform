""" Django admin pages for edeox app """
from ratelimitbackend import admin

from edeos.models import UserSocialLink


class UserSocialLinkAdmin(admin.ModelAdmin):
    """ Admin interface for the User model. """

    def get_readonly_fields(self, request, obj=None):
        """
        Allows staff to approve social links.
        """
        django_readonly = super(UserSocialLinkAdmin, self).get_readonly_fields(request, obj)

        if obj and not obj.is_verified and not request.user.is_superuser:
            return django_readonly + ('user_profile', 'platform', 'social_link')
        elif obj and not request.user.is_superuser:
            return django_readonly + ('user_profile', 'platform', 'social_link', 'is_verified')

        return django_readonly

    def save_model(self, request, obj, form, change):
        # TODO send event {'staff_email': request.user.email, 'student_email': obj.user_profile.user.email, 'platform': obj.platform}
        if 'is_verified' in form.changed_data and obj.is_verified is True:
            pass
        super(UserSocialLinkAdmin, self).save_model(request, obj, form, change)


admin.site.register(UserSocialLink, UserSocialLinkAdmin)
