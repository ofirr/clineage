# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2019-05-12 10:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0014_auto_20170903_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='samplereads',
            name='write_her_files',
            field=models.BinaryField(default=False),
        ),
    ]
