# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2019-07-30 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0016_add_numreads_to_fmsvmr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='samplereads',
            name='write_her_files',
            field=models.BooleanField(default=False),
        ),
    ]