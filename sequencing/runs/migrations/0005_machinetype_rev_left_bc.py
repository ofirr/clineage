# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-30 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('runs', '0004_increase_filename_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='machinetype',
            name='rev_left_bc',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
