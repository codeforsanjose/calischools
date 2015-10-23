from rest_framework import serializers

from .models import County, District, School


class CountySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = County


class CountyMixin(serializers.Serializer):
    county = CountySerializer(read_only=True)


class DistrictCompactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = District
        exclude = ('county',)


class DistrictSerializer(CountyMixin,
                         serializers.HyperlinkedModelSerializer):
    class Meta:
        model = District


class DistrictCompactMixin(serializers.Serializer):
    district = DistrictCompactSerializer(read_only=True)


class SchoolCompactSerializer(serializers.HyperlinkedModelSerializer):
    short_code = serializers.ReadOnlyField()

    class Meta:
        model = School
        fields = ('url', 'short_code', 'name',)


class SchoolSerializer(DistrictCompactMixin,
                       CountyMixin,
                       serializers.HyperlinkedModelSerializer):
    short_code = serializers.ReadOnlyField()

    class Meta:
        model = School
