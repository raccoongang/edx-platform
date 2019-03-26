from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats

from tedix_ro.models import City, School, StudentParent

admin.site.register(StudentParent)


class CityResource(resources.ModelResource):

    class Meta:
        model = City
        fields = ('name',)
        import_id_fields = ('name',)


@admin.register(City)
class CityAdmin(ImportExportModelAdmin):
    resource_class = CityResource
    formats = (
        base_formats.CSV,
        base_formats.JSON,
    )


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)
