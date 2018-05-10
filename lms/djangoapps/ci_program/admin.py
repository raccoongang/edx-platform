from django.contrib import admin
from ci_program.models import ProgramCourseCode, CourseCode, Program

admin.site.register(ProgramCourseCode)
admin.site.register(CourseCode)
admin.site.register(Program)