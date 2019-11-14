from django.contrib import admin

from calypso_reg_form.models import ExtraInfo, StateExtraInfo, UserSpendTimeCourse


class StateInline(admin.StackedInline):
    extra = 0
    model = StateExtraInfo


class ExtraInfoAdmin(admin.ModelAdmin):
    inlines = (StateInline,)


admin.site.register(ExtraInfo, ExtraInfoAdmin)
admin.site.register(UserSpendTimeCourse)
