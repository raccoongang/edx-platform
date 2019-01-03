"""Admin interface for the util app. """

from django.contrib import admin
from models import WebScienceCourseOverview
from web_science.forms import WebScienceCourseOverviewForm


@admin.register(WebScienceCourseOverview)
class WebScienceCourseOverviewAdmin(admin.ModelAdmin):
    """Admin for Web Science courses"""
    form = WebScienceCourseOverviewForm
