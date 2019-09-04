"""
Hera app admin panel.
"""

from django.contrib import admin
from hera.models import Onboarding, UserOnboarding


class OnboardingAdmin(admin.ModelAdmin):
    """
    Reflection of the hera model on the admin panel.
    """
    pass

class UserOnboardingAdmin(admin.ModelAdmin):
    """
    Reflection of the user onboarding model on the admin panel.
    """
    pass


admin.site.register(Onboarding, OnboardingAdmin)
admin.site.register(UserOnboarding, UserOnboardingAdmin)
