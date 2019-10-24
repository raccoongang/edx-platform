'''
django admin pages for courseware model
'''

from config_models.admin import ConfigurationModelAdmin
from ratelimitbackend import admin

from courseware.models import (
    OfflineComputedGrade, OfflineComputedGradeLog,
    StudentModule, UserCheckActivityConfig
)

admin.site.register(StudentModule)

admin.site.register(OfflineComputedGrade)

admin.site.register(OfflineComputedGradeLog)

admin.site.register(UserCheckActivityConfig, ConfigurationModelAdmin)
