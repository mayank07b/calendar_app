from __future__ import unicode_literals

from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    gid = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return self.name


class Calendar(models.Model):
    last_synced_at = models.DateTimeField(null=True, blank=True)
    token = models.CharField(max_length=50, blank=True)
