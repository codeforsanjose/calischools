from django.db import models


class Unit(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class County(Unit):
    class Meta:
        verbose_name_plural = 'counties'


class District(Unit):
    county = models.ForeignKey(County, related_name='districts')
    # Add additional information


class School(Unit):
    public = models.BooleanField()

    # Parent units
    county = models.ForeignKey(County, related_name='schools')
    district = models.ForeignKey(District, related_name='schools')

    # School information
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
