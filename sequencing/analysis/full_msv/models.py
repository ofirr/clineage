
from Bio import SeqIO
import itertools
import re

from django.db import models

from lib_prep.multiplexes.models import OM6Panel
from sequencing.analysis.models_common import Histogram, PearOutputMixin, \
    BowtieIndexMixin, post_delete_files, SampleReads, _read_bam
from targeted_enrichment.amplicons.models import Amplicon, AmpliconCollection


class FullMSVMergedReads(PearOutputMixin):
    sample_reads = models.ForeignKey(SampleReads, unique=True)

    INCLUDED_READS_OPTIONS = (('M', 'Only merged'),
                              ('F', 'Merged and unassembled_forward'),)

    def included_reads_generator(self, included_reads):
        if included_reads == 'M':
            it = SeqIO.parse(self.assembled_fastq, "fastq")
        elif included_reads == 'F':
            it = itertools.chain(
                SeqIO.parse(self.assembled_fastq, "fastq"),
                SeqIO.parse(self.unassembled_forward_fastq, "fastq")
            )
        else:
            raise ValueError("included_reads should be one of {}".format(
                FullMSVMergedReads.INCLUDED_READS_OPTIONS))
        return itertools.filterfalse(
            lambda rec: re.fullmatch("N*", str(rec.seq)), it
        )

    def __str__(self):
        return "{}".format(self.sample_reads)

post_delete_files(FullMSVMergedReads)


class FullMSVariations(BowtieIndexMixin):
    amplicon_collection = models.ForeignKey(AmpliconCollection)
    padding = models.PositiveIntegerField()
    microsatellites_version = models.IntegerField()

    class Meta:
        index_together = (
            ("amplicon_collection", "padding", "microsatellites_version"),
        )
        unique_together = (
            ("amplicon_collection", "padding", "microsatellites_version"),
        )

    def __str__(self):
        return "{} v. {}".format(self.amplicon_collection, self.microsatellites_version)

post_delete_files(FullMSVariations)


class FullMSVAssignment(models.Model):
    merged_reads = models.ForeignKey(FullMSVMergedReads, unique=True)
    sorted_assignment_bam = models.FilePathField(max_length=200)
    ms_variations = models.ForeignKey(FullMSVariations)
    separation_finished = models.BooleanField(default=False)

    def read_bam(self):
        for ms_genotypes_name, read_id in _read_bam(self.sorted_assignment_bam):
            yield read_id, ms_genotypes_name

    @property
    def files(self):
        yield self.sorted_assignment_bam

    def __str__(self):
        return "{}@{}".format(self.merged_reads, self.ms_variations.amplicon_collection)

post_delete_files(FullMSVAssignment)


class FullMSVHistogram(Histogram):
    assignment = models.ForeignKey(FullMSVAssignment)
    amplicon_copy = models.ForeignKey(Amplicon)  # to allow unique and index together, amplicon field and assignment field must reside on the same table

    def __str__(self):
        return "{}".format(self.assignment)

    class Meta:
        index_together = (
            ("amplicon_copy", "assignment"),
        )
        unique_together = (
            ("amplicon_copy", "assignment"),
        )

post_delete_files(FullMSVHistogram)
