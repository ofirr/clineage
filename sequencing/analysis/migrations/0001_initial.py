# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-10-02 15:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('planning', '0001_initial'),
        ('amplicons', '0001_initial'),
        ('workflows', '0001_initial'),
        ('runs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdamAmpliconReads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fastq1', models.FilePathField(max_length=200)),
                ('fastq2', models.FilePathField(max_length=200)),
                ('fastqm', models.FilePathField(max_length=200)),
                ('amplicon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amplicons.Amplicon')),
            ],
        ),
        migrations.CreateModel(
            name='AdamMarginAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment_sam', models.FilePathField(max_length=200)),
                ('separation_finished', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AdamMergedReads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pear_dump_dir', models.FilePathField(allow_files=False, allow_folders=True, max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdamMSVariations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_dump_dir', models.FilePathField(allow_files=False, allow_folders=True, max_length=200)),
                ('padding', models.PositiveIntegerField()),
                ('microsatellites_version', models.IntegerField()),
                ('amplicon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amplicons.Amplicon')),
            ],
        ),
        migrations.CreateModel(
            name='AdamReadsIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_dump_dir', models.FilePathField(allow_files=False, allow_folders=True, max_length=200)),
                ('included_reads', models.CharField(choices=[('M', 'Only merged'), ('F', 'Merged and unassembled_forward')], max_length=1)),
                ('padding', models.IntegerField(default=5)),
                ('merged_reads', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.AdamMergedReads')),
            ],
        ),
        migrations.CreateModel(
            name='AmpliconCollectionBWAIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fasta_file', models.FilePathField(allow_folders=True, max_length=200)),
                ('faidx_file', models.FilePathField(allow_folders=True, max_length=200)),
                ('index_dump_dir', models.FilePathField(allow_files=False, allow_folders=True, max_length=200)),
                ('amplicon_collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amplicons.AmpliconCollection', unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FullMSVariations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_dump_dir', models.FilePathField(allow_files=False, allow_folders=True, max_length=200)),
                ('padding', models.PositiveIntegerField()),
                ('microsatellites_version', models.IntegerField()),
                ('amplicon_collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amplicons.AmpliconCollection')),
            ],
        ),
        migrations.CreateModel(
            name='FullMSVAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sorted_assignment_bam', models.FilePathField(max_length=200)),
                ('separation_finished', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FullMSVAssignmentPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment_bam', models.FilePathField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FullMSVMergedReads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pear_dump_dir', models.FilePathField(allow_files=False, allow_folders=True, max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FullMSVMergedReadsPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fastq_part', models.FilePathField(max_length=200)),
                ('start_row', models.IntegerField()),
                ('rows', models.IntegerField()),
                ('merged_reads', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.FullMSVMergedReads')),
            ],
        ),
        migrations.CreateModel(
            name='Histogram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('microsatellites_version', models.IntegerField()),
                ('num_reads', models.PositiveIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HistogramEntryReads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_reads', models.PositiveIntegerField()),
                ('fastq1', models.FilePathField(max_length=200)),
                ('fastq2', models.FilePathField(max_length=200)),
                ('fastqm', models.FilePathField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MicrosatelliteHistogramGenotype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repeat_number', models.PositiveIntegerField()),
                ('microsatellite', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='planning.Microsatellite')),
            ],
        ),
        migrations.CreateModel(
            name='MicrosatelliteHistogramGenotypeSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('microsatellite_genotype1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.MicrosatelliteHistogramGenotype')),
                ('microsatellite_genotype2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.MicrosatelliteHistogramGenotype')),
                ('microsatellite_genotype3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.MicrosatelliteHistogramGenotype')),
                ('microsatellite_genotype4', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.MicrosatelliteHistogramGenotype')),
                ('microsatellite_genotype5', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.MicrosatelliteHistogramGenotype')),
                ('microsatellite_genotype6', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.MicrosatelliteHistogramGenotype')),
                ('microsatellite_genotype7', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.MicrosatelliteHistogramGenotype')),
                ('microsatellite_genotype8', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.MicrosatelliteHistogramGenotype')),
            ],
        ),
        migrations.CreateModel(
            name='ReadsAlignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bam_file', models.FilePathField(max_length=200)),
                ('alignment_reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.AmpliconCollectionBWAIndex')),
            ],
        ),
        migrations.CreateModel(
            name='SampleReads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_reads', models.PositiveIntegerField()),
                ('fastq1', models.FilePathField(max_length=200)),
                ('fastq2', models.FilePathField(max_length=200)),
                ('barcoded_content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflows.BarcodedContent')),
                ('demux', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='runs.Demultiplexing')),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflows.Library')),
            ],
        ),
        migrations.CreateModel(
            name='SNPHistogramGenotype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base', models.CharField(max_length=1)),
                ('snp', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='planning.SNP')),
            ],
        ),
        migrations.CreateModel(
            name='SNPHistogramGenotypeSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snp_genotype1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.SNPHistogramGenotype')),
                ('snp_genotype2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.SNPHistogramGenotype')),
                ('snp_genotype3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.SNPHistogramGenotype')),
                ('snp_genotype4', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.SNPHistogramGenotype')),
                ('snp_genotype5', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.SNPHistogramGenotype')),
                ('snp_genotype6', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.SNPHistogramGenotype')),
                ('snp_genotype7', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.SNPHistogramGenotype')),
                ('snp_genotype8', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='analysis.SNPHistogramGenotype')),
            ],
        ),
        migrations.CreateModel(
            name='SNPReads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_cover', models.IntegerField()),
                ('snps_dict', models.FilePathField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='VCFReads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vcf_file', models.FilePathField(max_length=200)),
                ('reads_alignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.ReadsAlignment', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AdamHistogram',
            fields=[
                ('histogram_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='analysis.Histogram')),
                ('assignment_sam', models.FilePathField(max_length=200)),
                ('separation_finished', models.BooleanField(default=False)),
            ],
            bases=('analysis.histogram',),
        ),
        migrations.CreateModel(
            name='FullMSVHistogram',
            fields=[
                ('histogram_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='analysis.Histogram')),
                ('amplicon_copy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amplicons.Amplicon')),
            ],
            bases=('analysis.histogram',),
        ),
        migrations.AddField(
            model_name='snpreads',
            name='vcf_read',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.VCFReads'),
        ),
        migrations.AddField(
            model_name='readsalignment',
            name='sample_read',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.SampleReads'),
        ),
        migrations.AddField(
            model_name='histogramentryreads',
            name='histogram',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.Histogram'),
        ),
        migrations.AddField(
            model_name='histogramentryreads',
            name='microsatellite_genotypes',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.MicrosatelliteHistogramGenotypeSet'),
        ),
        migrations.AddField(
            model_name='histogramentryreads',
            name='snp_genotypes',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.SNPHistogramGenotypeSet'),
        ),
        migrations.AddField(
            model_name='histogram',
            name='amplicon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amplicons.Amplicon'),
        ),
        migrations.AddField(
            model_name='histogram',
            name='sample_reads',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.SampleReads'),
        ),
        migrations.AddField(
            model_name='fullmsvmergedreads',
            name='sample_reads',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.SampleReads', unique=True),
        ),
        migrations.AddField(
            model_name='fullmsvassignmentpart',
            name='merged_reads_part',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.FullMSVMergedReadsPart'),
        ),
        migrations.AddField(
            model_name='fullmsvassignmentpart',
            name='ms_variations',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.FullMSVariations'),
        ),
        migrations.AddField(
            model_name='fullmsvassignment',
            name='merged_reads',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.FullMSVMergedReads'),
        ),
        migrations.AddField(
            model_name='fullmsvassignment',
            name='ms_variations',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.FullMSVariations'),
        ),
        migrations.AddField(
            model_name='adammergedreads',
            name='sample_reads',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.SampleReads', unique=True),
        ),
        migrations.AddField(
            model_name='adammarginassignment',
            name='reads_index',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.AdamReadsIndex', unique=True),
        ),
        migrations.AddField(
            model_name='adamampliconreads',
            name='margin_assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.AdamMarginAssignment'),
        ),
        migrations.AlterUniqueTogether(
            name='snpreads',
            unique_together=set([('vcf_read', 'min_cover')]),
        ),
        migrations.AlterUniqueTogether(
            name='snphistogramgenotypeset',
            unique_together=set([('snp_genotype1', 'snp_genotype2', 'snp_genotype3', 'snp_genotype4', 'snp_genotype5', 'snp_genotype6', 'snp_genotype7', 'snp_genotype8')]),
        ),
        migrations.AlterIndexTogether(
            name='snphistogramgenotypeset',
            index_together=set([('snp_genotype1', 'snp_genotype2', 'snp_genotype3', 'snp_genotype4', 'snp_genotype5', 'snp_genotype6', 'snp_genotype7', 'snp_genotype8')]),
        ),
        migrations.AlterUniqueTogether(
            name='snphistogramgenotype',
            unique_together=set([('snp', 'base')]),
        ),
        migrations.AlterIndexTogether(
            name='snphistogramgenotype',
            index_together=set([('snp', 'base')]),
        ),
        migrations.AlterUniqueTogether(
            name='samplereads',
            unique_together=set([('demux', 'barcoded_content')]),
        ),
        migrations.AlterIndexTogether(
            name='samplereads',
            index_together=set([('demux', 'barcoded_content')]),
        ),
        migrations.AlterUniqueTogether(
            name='readsalignment',
            unique_together=set([('sample_read', 'alignment_reference')]),
        ),
        migrations.AlterUniqueTogether(
            name='microsatellitehistogramgenotypeset',
            unique_together=set([('microsatellite_genotype1', 'microsatellite_genotype2', 'microsatellite_genotype3', 'microsatellite_genotype4', 'microsatellite_genotype5', 'microsatellite_genotype6', 'microsatellite_genotype7', 'microsatellite_genotype8')]),
        ),
        migrations.AlterIndexTogether(
            name='microsatellitehistogramgenotypeset',
            index_together=set([('microsatellite_genotype1', 'microsatellite_genotype2', 'microsatellite_genotype3', 'microsatellite_genotype4', 'microsatellite_genotype5', 'microsatellite_genotype6', 'microsatellite_genotype7', 'microsatellite_genotype8')]),
        ),
        migrations.AlterUniqueTogether(
            name='microsatellitehistogramgenotype',
            unique_together=set([('microsatellite', 'repeat_number')]),
        ),
        migrations.AlterIndexTogether(
            name='microsatellitehistogramgenotype',
            index_together=set([('microsatellite', 'repeat_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='histogramentryreads',
            unique_together=set([('histogram', 'microsatellite_genotypes', 'snp_genotypes')]),
        ),
        migrations.AlterUniqueTogether(
            name='fullmsvmergedreadspart',
            unique_together=set([('merged_reads', 'start_row', 'rows')]),
        ),
        migrations.AddField(
            model_name='fullmsvhistogram',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.FullMSVAssignment'),
        ),
        migrations.AlterUniqueTogether(
            name='fullmsvassignmentpart',
            unique_together=set([('merged_reads_part', 'ms_variations')]),
        ),
        migrations.AlterUniqueTogether(
            name='fullmsvassignment',
            unique_together=set([('merged_reads', 'ms_variations')]),
        ),
        migrations.AlterUniqueTogether(
            name='fullmsvariations',
            unique_together=set([('amplicon_collection', 'padding', 'microsatellites_version')]),
        ),
        migrations.AlterIndexTogether(
            name='fullmsvariations',
            index_together=set([('amplicon_collection', 'padding', 'microsatellites_version')]),
        ),
        migrations.AlterUniqueTogether(
            name='adamreadsindex',
            unique_together=set([('merged_reads', 'included_reads', 'padding')]),
        ),
        migrations.AlterIndexTogether(
            name='adamreadsindex',
            index_together=set([('merged_reads', 'included_reads', 'padding')]),
        ),
        migrations.AlterUniqueTogether(
            name='adammsvariations',
            unique_together=set([('amplicon', 'padding', 'microsatellites_version')]),
        ),
        migrations.AlterIndexTogether(
            name='adammsvariations',
            index_together=set([('amplicon', 'padding', 'microsatellites_version')]),
        ),
        migrations.AddField(
            model_name='adamhistogram',
            name='amplicon_reads',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.AdamAmpliconReads'),
        ),
        migrations.AddField(
            model_name='adamhistogram',
            name='ms_variations',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.AdamMSVariations'),
        ),
        migrations.AlterUniqueTogether(
            name='adamampliconreads',
            unique_together=set([('margin_assignment', 'amplicon')]),
        ),
        migrations.AlterIndexTogether(
            name='adamampliconreads',
            index_together=set([('margin_assignment', 'amplicon')]),
        ),
        migrations.AlterUniqueTogether(
            name='fullmsvhistogram',
            unique_together=set([('amplicon_copy', 'assignment')]),
        ),
        migrations.AlterIndexTogether(
            name='fullmsvhistogram',
            index_together=set([('amplicon_copy', 'assignment')]),
        ),
        migrations.AlterUniqueTogether(
            name='adamhistogram',
            unique_together=set([('amplicon_reads', 'ms_variations')]),
        ),
        migrations.AlterIndexTogether(
            name='adamhistogram',
            index_together=set([('amplicon_reads', 'ms_variations')]),
        ),
    ]
