# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from onboarding.models import Onboarding, UserOnboarding


class OnboardingAdmin(admin.ModelAdmin):
    """
    Reflection of the onboarding model on the admin panel.
    """
    pass

class UserOnboardingAdmin(admin.ModelAdmin):
    """
    Reflection of the user onboarding model on the admin panel.
    """
    pass


admin.site.register(Onboarding, OnboardingAdmin)
admin.site.register(UserOnboarding, UserOnboardingAdmin)
