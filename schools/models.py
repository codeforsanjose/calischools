from django.db import models
from django.utils.translation import ugettext_lazy as _
from base.mixins import AddressTrackedModelMixin

SCHOOL_STATUS_CHOICES = (
    ('AC', _('Active')),
    ('PE', _('Pending')),
    ('CL', _('Closed')),
    ('ME', _('Closed (Merged)')),
    ('CF', _('Closed or fewer than 6 students')),
)


class Unit(models.Model):
    code = models.CharField(max_length=14, primary_key=True)
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


class School(AddressTrackedModelMixin, Unit):
    nces_id = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(choices=SCHOOL_STATUS_CHOICES, max_length=2)
    public = models.BooleanField()

    # Parent units
    county = models.ForeignKey(County, related_name='schools')
    district = models.ForeignKey(District, related_name='schools')

    # School information
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    # Grades
    high_grade = models.CharField(max_length=20, blank=True)
    low_grade = models.CharField(max_length=20, blank=True)

    @property
    def short_code(self):
        return self.code[-7:]
