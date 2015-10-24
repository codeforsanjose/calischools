# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.mixins


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='County',
            fields=[
                ('code', models.CharField(max_length=14, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'counties',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('code', models.CharField(max_length=14, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('county', models.ForeignKey(related_name='districts', to='schools.County')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('code', models.CharField(max_length=14, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('nces_id', models.CharField(max_length=10, blank=True)),
                ('status', models.CharField(max_length=40, choices=[(b'Active', 'Active'), (b'Pending', 'Pending'), (b'Closed', 'Closed'), (b'Merged', 'Closed (Merged)'), (b'Closed or fewer than 6 students', 'Closed or fewer than 6 students')])),
                ('public', models.BooleanField()),
                ('school_type', models.CharField(max_length=50, blank=True)),
                ('year_round', models.BooleanField(default=False)),
                ('charter', models.BooleanField(default=False)),
                ('charter_number', models.CharField(max_length=10, blank=True)),
                ('charter_funding', models.CharField(max_length=100, blank=True)),
                ('open_date', models.DateField(null=True, blank=True)),
                ('close_date', models.DateField(null=True, blank=True)),
                ('phone', models.CharField(max_length=15, blank=True)),
                ('fax', models.CharField(max_length=15, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('administrators', models.TextField(blank=True)),
                ('address', models.CharField(max_length=255, blank=True)),
                ('mailing_address', models.CharField(max_length=255, blank=True)),
                ('lat', models.FloatField(null=True, blank=True)),
                ('lng', models.FloatField(null=True, blank=True)),
                ('high_grade', models.CharField(max_length=20, blank=True)),
                ('low_grade', models.CharField(max_length=20, blank=True)),
                ('stats', models.URLField(blank=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deprecated', models.BooleanField(default=False)),
                ('county', models.ForeignKey(related_name='schools', to='schools.County')),
                ('district', models.ForeignKey(related_name='schools', to='schools.District')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.mixins.AddressTrackedModelMixin, models.Model),
        ),
    ]
