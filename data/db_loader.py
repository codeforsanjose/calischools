import geopy
import time
import logging

from django.db import transaction
from schools.models import County, District, School
from .api.cde import (
    MODE_PUBLIC,
    MODE_PRIVATE,
    CdeSchoolSearchList,
    CdeSchoolDetail
)
from .serializers import CountySerializer, DistrictSerializer, SchoolSerializer

# Constants
DEFAULT_GEOCODER_TIMEOUT = 10
DEFAULT_GEOCODER_RETRIES = 3
DEFAULT_GEOCODER_INTERVAL_BETWEEN_RETRIES = 5

logger = logging.getLogger(__name__)


class DBLoader(object):
    # Use Google Maps Geocoding API
    geocoder = geopy.geocoders.GoogleV3(timeout=DEFAULT_GEOCODER_TIMEOUT)

    def geocode(self, address):
        for itr in xrange(DEFAULT_GEOCODER_RETRIES):
            try:
                loc = self.geocoder.geocode(address) if address else None
                return (
                    getattr(loc, 'latitude', None),
                    getattr(loc, 'longitude', None)
                )
            except Exception, e:
                logger.warning(
                    'Error while geocoding address: {0}. '
                    'Retrying in {1} seconds...'.format(
                        address,
                        DEFAULT_GEOCODER_INTERVAL_BETWEEN_RETRIES
                    )
                )
                time.sleep(DEFAULT_GEOCODER_INTERVAL_BETWEEN_RETRIES)
                continue
        else:
            # Exhausted all retries
            raise geopy.exc.GeocoderServiceError

    def add_or_update_geo_coords_for_school(self, school):
        if school.updated:
            logger.info(
                'Geocoding school: <Name: {0}, Code: {1}>'.format(school.name,
                                                                  school.code)
            )
            school.lat, school.lng = self.geocode(school.address)
            school.save()

    def serialize_to_objects(self, info):
        # Get/Create county - highest in the hierarchy
        county_serializer = CountySerializer(data=info)
        county_serializer.is_valid(raise_exception=True)
        county, _ = County.objects.get_or_create(
            **county_serializer.validated_data
        )

        # Get/Create district
        district_serializer = DistrictSerializer(data=info)
        district_serializer.is_valid(raise_exception=True)
        district, _ = District.objects.get_or_create(
            county=county,
            **district_serializer.validated_data
        )

        # Finally update/create school in the above county and district
        school_serializer = SchoolSerializer(data=info)
        school_serializer.is_valid(raise_exception=True)
        school, _ = School.objects.update_or_create(
            defaults=school_serializer.validated_data,
            code=school_serializer.validated_data['code'],
            county=county,
            district=district
        )
        self.add_or_update_geo_coords_for_school(school)

    def source(self):
        # Mark existing school records as deprecated, valid records will then
        # have their flags updated
        School.objects.update(deprecated=True)

        for mode in (MODE_PUBLIC, MODE_PRIVATE):
            logger.info('Fetching a list of schools to parse...')
            school_endpoints = CdeSchoolSearchList(mode=mode).schools
            logger.info(
                '{0} schools found. Commencing parsing of '
                'school details...'.format(len(school_endpoints))
            )
            for endpoint in school_endpoints:
                # Source info from CDE school directory
                info = CdeSchoolDetail(endpoint).to_dict()
                info['public'] = mode == MODE_PUBLIC
                # Save school details to DB
                self.serialize_to_objects(info)

    def update_db(self):
        try:
            logger.info('Updating database...')
            with transaction.atomic():
                self.source()
            logger.info('Database update successfully completed.')
        except Exception, e:
            logger.exception(e)
