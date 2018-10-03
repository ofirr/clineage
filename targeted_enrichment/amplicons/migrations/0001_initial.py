# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-10-02 15:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('planning', '0001_initial'),
        ('genomes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Amplicon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AmpliconCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PlainTargetedAmplicon',
            fields=[
                ('amplicon_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='amplicons.Amplicon')),
                ('left_ugs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.UGSPlus')),
                ('right_ugs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.UGSMinus')),
            ],
            options={
                'abstract': False,
            },
            bases=('amplicons.amplicon',),
        ),
        migrations.CreateModel(
            name='RawAmplicon',
            fields=[
                ('amplicon_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='amplicons.Amplicon')),
            ],
            bases=('amplicons.amplicon',),
        ),
        migrations.CreateModel(
            name='TargetedAmpliconWithCompanyTag',
            fields=[
                ('amplicon_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='amplicons.Amplicon')),
                ('left_tag', models.CharField(max_length=1)),
                ('right_tag', models.CharField(max_length=1)),
                ('left_ugs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.UGSPlus')),
                ('right_ugs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.UGSMinus')),
            ],
            options={
                'abstract': False,
            },
            bases=('amplicons.amplicon',),
        ),
        migrations.CreateModel(
            name='UMITargetedAmplicon',
            fields=[
                ('amplicon_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='amplicons.Amplicon')),
                ('umi_length', models.PositiveSmallIntegerField()),
                ('left_ugs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.UGSPlus')),
                ('right_ugs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.UGSMinus')),
            ],
            options={
                'abstract': False,
            },
            bases=('amplicons.amplicon',),
        ),
        migrations.AddField(
            model_name='ampliconcollection',
            name='amplicons',
            field=models.ManyToManyField(to='amplicons.Amplicon'),
        ),
        migrations.AddField(
            model_name='amplicon',
            name='slice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genomes.DNASlice'),
        ),
    ]
