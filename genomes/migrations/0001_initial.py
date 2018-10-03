# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-10-02 15:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('misc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DNASlice_Contains',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DNASlice_Overlaps',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RestrictionSiteDNASlice_Contains',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RestrictionSiteDNASlice_Overlaps',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Assembly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('friendly_name', models.CharField(max_length=50)),
                ('taxa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='misc.Taxa')),
            ],
            options={
                'verbose_name_plural': 'Assemblies',
            },
        ),
        migrations.CreateModel(
            name='Chromosome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('sequence_length', models.IntegerField(null=True)),
                ('cyclic', models.BooleanField()),
                ('assembly', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genomes.Assembly')),
            ],
        ),
        migrations.CreateModel(
            name='DNASlice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_pos', models.IntegerField(db_index=True)),
                ('end_pos', models.IntegerField(db_index=True)),
                ('_sequence', models.CharField(default=None, max_length=300, null=True)),
                ('chromosome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genomes.Chromosome')),
                ('contains', models.ManyToManyField(related_name='contained', through='genomes.DNASlice_Contains', to='genomes.DNASlice')),
                ('overlaps', models.ManyToManyField(related_name='_dnaslice_overlaps_+', through='genomes.DNASlice_Overlaps', to='genomes.DNASlice')),
            ],
            options={
                'ordering': ['chromosome', 'start_pos', 'end_pos'],
            },
        ),
        migrations.CreateModel(
            name='RestrictionSiteDNASlice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_pos', models.IntegerField(db_index=True)),
                ('end_pos', models.IntegerField(db_index=True)),
                ('_sequence', models.CharField(default=None, max_length=300, null=True)),
                ('chromosome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genomes.Chromosome')),
                ('contains', models.ManyToManyField(related_name='contained', through='genomes.RestrictionSiteDNASlice_Contains', to='genomes.RestrictionSiteDNASlice')),
                ('overlaps', models.ManyToManyField(related_name='_restrictionsitednaslice_overlaps_+', through='genomes.RestrictionSiteDNASlice_Overlaps', to='genomes.RestrictionSiteDNASlice')),
            ],
            options={
                'ordering': ['chromosome', 'start_pos', 'end_pos'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='restrictionsitednaslice',
            unique_together=set([('chromosome', 'start_pos', 'end_pos')]),
        ),
        migrations.AlterIndexTogether(
            name='restrictionsitednaslice',
            index_together=set([('chromosome', 'start_pos', 'end_pos')]),
        ),
        migrations.AlterUniqueTogether(
            name='dnaslice',
            unique_together=set([('chromosome', 'start_pos', 'end_pos')]),
        ),
        migrations.AlterIndexTogether(
            name='dnaslice',
            index_together=set([('chromosome', 'start_pos', 'end_pos')]),
        ),
    ]
