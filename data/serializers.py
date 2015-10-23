import six

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from schools.models import SCHOOL_STATUS_CHOICES, School


class CountyCodeField(serializers.CharField):
    def to_internal_value(self, data):
        # We need only the first 2 digits of the full 14 digit school code
        value = data[:2]
        return super(CountyCodeField, self).to_internal_value(value)


class DistrictCodeField(serializers.CharField):
    def to_internal_value(self, data):
        # We need the first 7 digits of the full 14 digit school code
        value = data[:7]
        return super(DistrictCodeField, self).to_internal_value(value)


class SchoolStatusField(serializers.CharField):
    def __init__(self, **kwargs):
        super(SchoolStatusField, self).__init__(**kwargs)
        self.school_status_choices = {
            six.text_type(v): k for k, v in SCHOOL_STATUS_CHOICES
        }

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''

        try:
            return self.school_status_choices[six.text_type(data)]
        except KeyError:
            raise ValidationError(
                _('"{input}" is not a valid status.').format(input=data)
            )


class YesNoField(serializers.BooleanField):
    TRUE_VALUES = {'Yes', 'yes', 't', 'T', 'true',
                   'True', 'TRUE', '1', 1, True}
    FALSE_VALUES = {'', 'No', 'no', 'f', 'F', 'false',
                    'False', 'FALSE', '0', 0, 0.0, False}


class OptionalDateField(serializers.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'allow_null': True, 'required': False})
        super(OptionalDateField, self).__init__(*args, **kwargs)

    def to_internal_value(self, value):
        if not value:
            return None
        return super(OptionalDateField, self).to_internal_value(value)


class CountySerializer(serializers.Serializer):
    code = CountyCodeField(max_length=2)
    county = serializers.CharField(source='name')


class DistrictSerializer(serializers.Serializer):
    code = DistrictCodeField(max_length=7)
    district = serializers.CharField(source='name')


class SchoolSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=14)
    status = SchoolStatusField()
    year_round = YesNoField()
    charter = YesNoField()
    open_date = OptionalDateField()
    close_date = OptionalDateField()

    class Meta:
        model = School
        exclude = ('county', 'district', 'lat', 'lng',)
