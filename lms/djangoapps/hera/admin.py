"""
Hera app admin panel.
"""
from django import forms
from django.conf import settings
from django.contrib import admin
from opaque_keys.edx.keys import CourseKey

from hera.models import ActiveCourseSetting, Onboarding, UserOnboarding
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class OnboardingAdmin(admin.ModelAdmin):
    """
    Reflection of the hera model on the admin panel.
    """
    class Media:
        css = {
            'all': (
                'css/hera.css',
                settings.PIPELINE_CSS['style-vendor-tinymce-content']['source_filenames'][0],
                settings.PIPELINE_CSS['style-vendor-tinymce-skin']['source_filenames'][0],
            )
        }
        js = (
            'js/vendor/tinymce/js/tinymce/jquery.tinymce.min.js',
            "js/vendor/tinymce/js/tinymce/tinymce.full.min.js",
            'js/tinymce_initializer.js'
        )

    def get_queryset(self, request):
        """
        Create a default onboarding object in case we have none yet.
        """
        qs = super(OnboardingAdmin, self).get_queryset(request)

        if not qs:
            default_onboarding = self.model()
            default_onboarding.save()

            qs = super(OnboardingAdmin, self).get_queryset(request)

        return qs

    def has_add_permission(self, request):
        """
        Allow to add Onboarding only if no objects exist.
        """
        return not self.model.objects.exists()

    def get_actions(self, request):
        """
        Remove all actions by returning an empty dictionary.
        """
        return dict()

class UserOnboardingAdmin(admin.ModelAdmin):
    """
    Reflection of the user onboarding model on the admin panel.
    """
    pass


class CourseModelChoiceField(forms.ModelChoiceField):

    def clean(self, value):
        if value:
            value = CourseKey.from_string(value)
        return super(CourseModelChoiceField, self).clean(value)


class ActiveCourseSettingForm(forms.ModelForm):
    course = CourseModelChoiceField(queryset=CourseOverview.objects.all())


class ActiveCourseSettingAdmin(admin.ModelAdmin):
    form = ActiveCourseSettingForm

    def has_add_permission(self, request, obj=None):
        if ActiveCourseSetting.objects.all().count() > 0:
            return False
        return True


admin.site.register(Onboarding, OnboardingAdmin)
admin.site.register(UserOnboarding, UserOnboardingAdmin)
admin.site.register(ActiveCourseSetting, ActiveCourseSettingAdmin)
