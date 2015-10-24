import django_filters

from base.filters import BaseFilterSet

from .models import County, District, School


class CountyFilter(BaseFilterSet):
    class Meta:
        model = County
        fields = ('name',)


class DistrictFilter(BaseFilterSet):
    county = django_filters.CharFilter(name='county__name')

    class Meta:
        model = District
        fields = ('name', 'county',)


class SchoolFilter(BaseFilterSet):
    county = django_filters.CharFilter(name='county__name')
    district = django_filters.CharFilter(name='district__name')

    class Meta:
        model = School
        fields = ('code', 'name', 'public', 'county', 'district', 'status',
                  'deprecated',)
