import pytest
import requests_mock

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from schools.models import County, District, School
from data.db_loader import DBLoader
from data.serializers import (
    CountyCodeField,
    DistrictCodeField,
    SchoolStatusField
)
from .test_constants import CDE_SCHOOL_DETAIL_JSON

def test_geocoder():
    address = '1600 Amphitheater Parkway, Mountain View, CA 94043'
    assert DBLoader().geocode(address) == (37.4220352, -122.0841244)

def test_code_field_serializers():
    class TestCountySerializer(serializers.Serializer):
        code = CountyCodeField()

    class TestDistrictSerializer(serializers.Serializer):
        code = DistrictCodeField()

    data = {'code': '01100176097562'}

    county_serializer = TestCountySerializer(data=data)
    county_serializer.is_valid(raise_exception=True)
    assert county_serializer.validated_data['code'] == '01'

    district_serializer = TestDistrictSerializer(data=data)
    district_serializer.is_valid(raise_exception=True)
    assert district_serializer.validated_data['code'] == '0110017'

def test_school_status_field_serializer():
    class TestSerializer(serializers.Serializer):
        status = SchoolStatusField()

    with pytest.raises(ValidationError):
        test_serializer = TestSerializer(data={'status': 'bad status'})
        test_serializer.is_valid(raise_exception=True)

    test_serializer = TestSerializer(data={'status': 'Closed (Merged)'})
    assert test_serializer.is_valid(raise_exception=True)


class TestDBLoader:
    @pytest.mark.django_db
    def test_serialize_to_objects(self):
        db_loader = DBLoader()
        for info in CDE_SCHOOL_DETAIL_JSON:
            db_loader.serialize_to_objects(info)

        counties = County.objects.all()
        assert County.objects.get(name='Alameda').code == '01'
        assert County.objects.get(code='19').name == 'Los Angeles'

        districts = District.objects.all()
        assert (
            District.objects.get(code='0110017').name
                == 'Alameda County Office of Education'
        )
        assert District.objects.get(name='ABC Unified').code == '1964212'

        # Get some school objects
        test_school_one = School.objects.get(code='01100170130419')
        test_school_two = School.objects.get(code='19642126200109')
        test_school_three = School.objects.get(name='Test School')
        test_school_four = School.objects.get(name='Best School')

        assert test_school_one.short_code == '0130419'
        assert test_school_one.get_status_display() == 'Active'
        assert test_school_one.lat == 37.6582962
        assert test_school_one.lng == -122.0977664
        assert test_school_two.low_grade == 'K'

        # Missing address
        assert test_school_two.lat is None
        assert test_school_two.lng is None

        # Bad address
        assert test_school_three.lat is None
        assert test_school_three.lng is None

        # Updated address
        assert test_school_four.lat == 37.4220352
        assert test_school_four.lng == -122.0841244
