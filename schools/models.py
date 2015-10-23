from django.db import models
from django.utils.translation import ugettext_lazy as _
from base.mixins import AddressTrackedModelMixin

SCHOOL_STATUS_CHOICES = (
    ('Active', _('Active')),
    ('Pending', _('Pending')),
    ('Closed', _('Closed')),
    ('Merged', _('Closed (Merged)')),
    ('Closed or fewer than 6 students', _('Closed or fewer than 6 students')),
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
    nces_id = models.CharField(max_length=10, blank=True)
    status = models.CharField(choices=SCHOOL_STATUS_CHOICES, max_length=40)
    public = models.BooleanField()
    school_type = models.CharField(max_length=50, blank=True)
    year_round = models.BooleanField(default=False)

    # Charter information
    charter = models.BooleanField(default=False)
    charter_number = models.CharField(max_length=10, blank=True)
    charter_funding = models.CharField(max_length=100, blank=True)

    # Parent units
    county = models.ForeignKey(County, related_name='schools')
    district = models.ForeignKey(District, related_name='schools')

    # School information
    open_date = models.DateField(blank=True, null=True)
    close_date = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    fax = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    administrators = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    mailing_address = models.CharField(max_length=255, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    # Grades
    high_grade = models.CharField(max_length=20, blank=True)
    low_grade = models.CharField(max_length=20, blank=True)

    # Statistics
    stats = models.URLField(blank=True)

    @property
    def short_code(self):
        return self.code[-7:]
