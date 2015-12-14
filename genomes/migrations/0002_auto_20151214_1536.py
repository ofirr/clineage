# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_prep', '0003_kill'),
        ('genomes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DNASlice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_pos', models.IntegerField(db_index=True)),
                ('end_pos', models.IntegerField(db_index=True)),
                ('_sequence', models.ForeignKey(default=None, to='genomes.Sequence', null=True)),
                ('chromosome', models.ForeignKey(to='genomes.Chromosome')),
            ],
        ),
        migrations.RemoveField(
            model_name='microsatellite',
            name='target_ptr',
        ),
        migrations.RemoveField(
            model_name='primer',
            name='sequence',
        ),
        migrations.RemoveField(
            model_name='primer',
            name='tail',
        ),
        migrations.RemoveField(
            model_name='primer',
            name='target_ptr',
        ),
        migrations.RemoveField(
            model_name='restrictionsite',
            name='restriction_type',
        ),
        migrations.RemoveField(
            model_name='restrictionsite',
            name='target_ptr',
        ),
        migrations.RemoveField(
            model_name='snp',
            name='target_ptr',
        ),
        migrations.RemoveField(
            model_name='target',
            name='chromosome',
        ),
        migrations.RemoveField(
            model_name='target',
            name='partner',
        ),
        migrations.RemoveField(
            model_name='target',
            name='referencevalue',
        ),
        migrations.RemoveField(
            model_name='target',
            name='type',
        ),
        migrations.RemoveField(
            model_name='targetenrichment',
            name='chromosome',
        ),
        migrations.RemoveField(
            model_name='targetenrichment',
            name='left',
        ),
        migrations.RemoveField(
            model_name='targetenrichment',
            name='partner',
        ),
        migrations.RemoveField(
            model_name='targetenrichment',
            name='right',
        ),
        migrations.RemoveField(
            model_name='targetenrichment',
            name='targets',
        ),
        migrations.RemoveField(
            model_name='targetenrichment',
            name='type',
        ),
        migrations.RemoveField(
            model_name='targetenrichment',
            name='validation_failure',
        ),
        migrations.RemoveField(
            model_name='targetenrichmenttype',
            name='protocol',
        ),
        migrations.DeleteModel(
            name='Microsatellite',
        ),
        migrations.DeleteModel(
            name='Primer',
        ),
        migrations.DeleteModel(
            name='PrimerTail',
        ),
        migrations.DeleteModel(
            name='RestrictionSite',
        ),
        migrations.DeleteModel(
            name='RestrictionSiteType',
        ),
        migrations.DeleteModel(
            name='SNP',
        ),
        migrations.DeleteModel(
            name='Target',
        ),
        migrations.DeleteModel(
            name='TargetEnrichment',
        ),
        migrations.DeleteModel(
            name='TargetEnrichmentFailureType',
        ),
        migrations.DeleteModel(
            name='TargetEnrichmentType',
        ),
        migrations.DeleteModel(
            name='TargetType',
        ),
    ]
