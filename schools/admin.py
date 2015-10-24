from django.contrib import admin

from .models import County, District, School


class UnitAdminMixin(object):
    list_display = ('code', 'name',)
    search_fields = ('code', 'name',)

@admin.register(County)
class CountyAdmin(UnitAdminMixin, admin.ModelAdmin):
    pass


@admin.register(District)
class DistrictAdmin(UnitAdminMixin, admin.ModelAdmin):
    pass


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'county', 'district', 'phone', 'address',
                    'lat', 'lng', 'public',)
    list_filter = ('county', 'district', 'public', 'deprecated',)
    search_fields = ('code', 'name', 'address',)
