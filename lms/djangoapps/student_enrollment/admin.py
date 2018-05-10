from django.contrib import admin
from lms.djangoapps.student_enrollment.models import (
    EnrollmentStatusHistory,
    ProgramAccessStatus
)


class EnrollmentStatusHistoryAdmin(admin.ModelAdmin):
    search_fields = ['student', 'student__email', 'student__username']

    list_filter = (
        ('enrollment_attempt', admin.DateFieldListFilter),
        ('email_sent', admin.BooleanFieldListFilter),
        ('enrolled', admin.BooleanFieldListFilter),
        ('registered', admin.BooleanFieldListFilter)
    )

admin.site.register(EnrollmentStatusHistory, EnrollmentStatusHistoryAdmin)
admin.site.register(ProgramAccessStatus)
