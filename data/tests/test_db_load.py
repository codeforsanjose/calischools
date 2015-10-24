import pytest
import requests_mock
import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from schools.models import County, District, School
from data.db_loader import DBLoader
from data.serializers import (
    CountyCodeField,
    DistrictCodeField,
    SchoolStatusField,
    YesNoField,
    OptionalDateField,
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

def test_yes_no_field_serializer():
    class TestSerializer(serializers.Serializer):
        charter = YesNoField()
        year_round = YesNoField()
        empty = YesNoField()

    test_serializer = TestSerializer(
        data={'charter': 'Yes', 'year_round': 'No', 'empty': ''}
    )
    assert test_serializer.is_valid(raise_exception=True)
    assert test_serializer.validated_data['charter'] is True
    assert test_serializer.validated_data['year_round'] is False
    assert test_serializer.validated_data['empty'] is False

def test_school_date_field_serializer():
    class TestSerializer(serializers.Serializer):
        open_date = OptionalDateField()
        close_date = OptionalDateField()

    test_serializer = TestSerializer(
        data={'open_date': '2000-01-01', 'close_date': ''}
    )
    assert test_serializer.is_valid(raise_exception=True)
    assert test_serializer.validated_data['open_date'] == datetime.date(2000,
                                                                        1,
                                                                        1)
    assert test_serializer.validated_data['close_date'] is None

class TestDBLoader:
    @pytest.mark.django_db
    def test_serialize_to_objects(self):
        db_loader = DBLoader()
        for info in CDE_SCHOOL_DETAIL_JSON:
            db_loader.serialize_to_objects(info)

        counties = County.objects.all()
        assert County.objects.get(name='Alameda').code == '01'
        assert County.objects.get(code='20').name == 'Madera'

        districts = District.objects.all()
        assert (
            District.objects.get(code='0110017').name
                == 'Alameda County Office of Education'
        )
        assert District.objects.get(name='Chawanakee Unified').code == '2075606'

        # Get some school objects
        test_school_one = School.objects.get(code='01100170130419')
        test_school_two = School.objects.get(code='01100176141212')
        test_school_three = School.objects.get(code='20756060132936')
        test_school_four = School.objects.get(name='Test School No Address')
        test_school_five = School.objects.get(name='Test School Bad Address')
        test_school_six = School.objects.get(name='Best School')

        assert test_school_one.short_code == '0130419'
        assert test_school_one.status == 'Active'
        assert test_school_one.lat == 37.6582962
        assert test_school_one.lng == -122.0977664
        assert test_school_one.deprecated is False

        assert test_school_two.low_grade == 'K'

        assert test_school_three.charter is True
        assert test_school_three.charter_number == '1763'

        # Missing address
        assert test_school_four.lat is None
        assert test_school_four.lng is None

        # Bad address
        assert test_school_five.lat is None
        assert test_school_five.lng is None

        # Updated address
        assert test_school_six.lat == 37.4220352
        assert test_school_six.lng == -122.0841244
