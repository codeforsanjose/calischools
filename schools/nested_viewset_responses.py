from base.nested_viewset_responses import NestedViewSetList

from .models import District, School
from .serializers import (
    DistrictCompactSerializer,
    SchoolCompactSerializer
)
from .filters import DistrictFilter, SchoolFilter


class NestedViewSetDistrictList(NestedViewSetList):
    model = District
    serializer_class = DistrictCompactSerializer
    filter_class = DistrictFilter


class NestedViewSetSchoolList(NestedViewSetList):
    model = School
    serializer_class = SchoolCompactSerializer
    filter_class = SchoolFilter
