"""
Admin registration for Custom Settings Models
"""
from django.contrib import admin

from custom_settings.models import HomepageSlider, HomepageVideo


class HomepageVideoAdmin(admin.ModelAdmin):
    """ Admin interface for the HomepageVideo object. """

    def has_add_permission(self, request):
        """Doesn't allow to add a link if it exists, only edit. """
        if HomepageVideo.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        """Doesn't allow to delete. """
        return False


class HomepageSliderAdmin(admin.ModelAdmin):
    """ Admin interface for the HomepageSlider object. """

    list_display = ('title', 'slide_order', 'is_published',)
    list_editable = ('slide_order', 'is_published',)


admin.site.register(HomepageVideo, HomepageVideoAdmin)
admin.site.register(HomepageSlider, HomepageSliderAdmin)
