# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-01 12:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_synced_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
