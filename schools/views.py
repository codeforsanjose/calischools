from rest_framework import viewsets
from rest_framework.decorators import detail_route

from .models import County, District, School
from .serializers import CountySerializer, DistrictSerializer, SchoolSerializer
from .filters import CountyFilter, DistrictFilter, SchoolFilter
from .nested_viewset_responses import (
    NestedViewSetDistrictList,
    NestedViewSetSchoolList
)


class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = County.objects.all()
    serializer_class = CountySerializer
    filter_class = CountyFilter

    @detail_route()
    def districts(self, request, pk=None):
        return NestedViewSetDistrictList(
            view=self,
            request=request,
            qs_filter={'county__pk': pk}
        ).response

    @detail_route()
    def schools(self, request, pk=None):
        return NestedViewSetSchoolList(
            view=self,
            request=request,
            qs_filter={'county__pk': pk}
        ).response


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filter_class = DistrictFilter

    @detail_route()
    def schools(self, request, pk=None):
        return NestedViewSetSchoolList(
            view=self,
            request=request,
            qs_filter={'district__pk': pk}
        ).response


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filter_class = SchoolFilter
