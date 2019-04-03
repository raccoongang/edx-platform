from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Sponsored_course_users,user_view_counter
# Register your models here.

@admin.register(Sponsored_course_users)
class Sponsored_course_usersAdmin(admin.ModelAdmin):

    list_display = ('course_id', 'sponsoringcompany', 'coupon_code')
    search_fields = ('course_id', 'sponsoringcompany', 'coupon_code')

@admin.register(user_view_counter)
class user_view_counterAdmin(admin.ModelAdmin):

    list_display = ('course_id', 'user', 'counter')
    search_fields = ('course_id', 'user__email')