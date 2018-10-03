# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-10-02 15:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plate',
            fields=[
                ('code', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('barcode', models.CharField(blank=True, max_length=20)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('state', models.CharField(blank=True, max_length=20)),
                ('lastusedwell', models.CharField(default='A1', max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='PlateContext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='PlatePlastica',
            fields=[
                ('code', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=30)),
                ('rows', models.IntegerField(default=8)),
                ('columns', models.IntegerField(default=12)),
            ],
        ),
        migrations.CreateModel(
            name='PlateStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inner_location', models.CharField(blank=True, max_length=100)),
                ('notes', models.CharField(blank=True, max_length=250)),
                ('plate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wet_storage.Plate')),
            ],
        ),
        migrations.CreateModel(
            name='PlateType',
            fields=[
                ('code', models.AutoField(primary_key=True, serialize=False)),
                ('friendly', models.CharField(max_length=100)),
                ('context', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wet_storage.PlateContext')),
                ('plastic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wet_storage.PlatePlastica')),
            ],
        ),
        migrations.CreateModel(
            name='SampleLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('well', models.CharField(blank=True, db_index=True, max_length=3)),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('volume', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('concentration', models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('plate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wet_storage.Plate')),
            ],
        ),
        migrations.CreateModel(
            name='StorageBox',
            fields=[
                ('code', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('barcode', models.CharField(blank=True, max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='StorageType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('temperature', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='storagebox',
            name='storage_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wet_storage.StorageType'),
        ),
        migrations.AddField(
            model_name='platestorage',
            name='storageBox',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wet_storage.StorageBox'),
        ),
        migrations.AddField(
            model_name='plate',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wet_storage.PlateType'),
        ),
        migrations.AlterIndexTogether(
            name='samplelocation',
            index_together=set([('content_type', 'object_id')]),
        ),
    ]
