
import os
import pysam
import itertools
import re

from model_utils.managers import InheritanceManager

from django.db import models
from django.db.models.signals import post_delete

from sequencing.runs.models import Demultiplexing
from targeted_enrichment.planning.models import Microsatellite, SNP
from targeted_enrichment.amplicons.models import Amplicon
from lib_prep.workflows.models import Library, BarcodedContent


def _delete_files(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    for filename in getattr(instance, "files", []):
        try:
            os.unlink(filename)
        except FileNotFoundError:
            pass
    for dirname in getattr(instance, "dirs", []):
        try:
            os.rmdir(dirname)
        except FileNotFoundError:
            pass

def post_delete_files(model):
    post_delete.connect(_delete_files, model)


def pear_property(suffix):
    @property
    def inner(self):
        return "{}.{}.fastq".format(self.pear_files_prefix, suffix)
    return inner

class PearOutputMixin(models.Model):
    PEAR_PREFIX = "pear"
    pear_dump_dir = models.FilePathField(max_length=200, allow_files=False, allow_folders=True)

    class Meta:
        abstract = True

    @property
    def pear_files_prefix(self):
        return os.path.join(self.pear_dump_dir, self.PEAR_PREFIX)

    assembled_fastq = pear_property("assembled")
    discarded_fastq = pear_property("discarded")
    unassembled_forward_fastq = pear_property("unassembled.forward")
    unassembled_reverse_fastq = pear_property("unassembled.reverse")

    @property
    def files(self):
        yield self.assembled_fastq
        yield self.discarded_fastq
        yield self.unassembled_forward_fastq
        yield self.unassembled_reverse_fastq

    @property
    def dirs(self):
        yield self.pear_dump_dir


class BowtieIndexMixin(models.Model):
    INDEX_PREFIX = "index"
    index_dump_dir = models.FilePathField(max_length=200, allow_files=False, allow_folders=True)

    class Meta:
        abstract = True

    @property
    def index_files_prefix(self):
        return os.path.join(self.index_dump_dir, self.INDEX_PREFIX)

    @property
    def files(self):
        for i in range(1, 5):
            yield "{}.{}.bt2".format(self.index_files_prefix, i)
        for i in range(1, 3):
            yield "{}.rev.{}.bt2".format(self.index_files_prefix, i)

    @property
    def dirs(self):
        yield self.index_dump_dir


class BWAIndexMixin(models.Model):
    INDEX_PREFIX = "Index_Ext_0"
    fasta_file = models.FilePathField(max_length=200, allow_files=True, allow_folders=True)
    faidx_file = models.FilePathField(max_length=200, allow_files=True, allow_folders=True)
    index_dump_dir = models.FilePathField(max_length=200, allow_files=False, allow_folders=True)

    class Meta:
        abstract = True

    @property
    def index_files_prefix(self):
        return os.path.join(self.index_dump_dir, self.INDEX_PREFIX)

    @property
    def files(self):
        yield self.fasta_file
        yield self.faidx_file
        yield "{}.amb".format(self.index_files_prefix)
        yield "{}.ann".format(self.index_files_prefix)
        yield "{}.bwt".format(self.index_files_prefix)
        yield "{}.pac".format(self.index_files_prefix)
        yield "{}.sa".format(self.index_files_prefix)

    @property
    def dirs(self):
        yield self.index_dump_dir


class SampleReads(models.Model):
    """
    Sample reads are the output of Illumina sequencing and is identified by a barcoded_content and demultiplexing.
    """
    demux = models.ForeignKey(Demultiplexing)
    barcoded_content = models.ForeignKey(BarcodedContent)
    library = models.ForeignKey(Library)
    num_reads = models.PositiveIntegerField()
    fastq1 = models.FilePathField(max_length=200)
    fastq2 = models.FilePathField(max_length=200)
    write_her_files = models.BooleanField(default=False)

    class Meta:
        index_together = (
            ("demux", "barcoded_content"),
        )
        unique_together = (
            ("demux", "barcoded_content"),
        )

    @property
    def files(self):
        yield self.fastq1
        yield self.fastq2

    @property
    def cell(self):
        return self.barcoded_content.subclass.amplified_content.cell

    def __str__(self):
        return "{} @ {}".format(self.barcoded_content.subclass, self.demux)

post_delete_files(SampleReads)


def _read_sam(sam_path):
    with pysam.AlignmentFile(sam_path, "r") as samfile:
        for r in samfile:
            if r.is_unmapped:
                continue  # unmapped TODO: dump in appropriate bin
            yield samfile.getrname(r.reference_id), r.query_name


def _read_bam(bam_path):
    with pysam.AlignmentFile(bam_path, "rb") as bamfile:
        for r in bamfile:
            if r.is_unmapped:
                continue  # unmapped TODO: dump in appropriate bin
            yield bamfile.getrname(r.reference_id), r.query_name


class Histogram(models.Model):
    """
    Identify each amplicon to the correct cell id and gives it a reference point. This reference point is used to
    recover information in order to build a histogram
    """
    sample_reads = models.ForeignKey(SampleReads)
    microsatellites_version = models.IntegerField()
    amplicon = models.ForeignKey(Amplicon)
    num_reads = models.PositiveIntegerField(null=True)

    objects = InheritanceManager()

    # FIXME
    @property
    def subclass(self):
        return Histogram.objects.get_subclass(id=self.id)


def ms_genotypes_to_name(ms_genotypes, prefix):
    names = ["{}".format(mhg) for mhg in ms_genotypes]
    return ":".join([prefix] + names)


def split_ms_genotypes_name(ms_genotypes_name):
    genotypes_plus = ms_genotypes_name.split(":")
    prefix = genotypes_plus[0]  # amplicon
    return prefix, tuple(genotypes_plus[1:])


def get_ms_genotypes_from_strings_tuple(genotype_strings_tuple):
    ms_genotypes = tuple(
        [
            MicrosatelliteHistogramGenotype.get_for_string(s) \
            for s in genotype_strings_tuple
            ]
    )
    return ms_genotypes


def name_to_ms_genotypes(ms_genotypes_name):
    prefix, msgs = split_ms_genotypes_name(ms_genotypes_name)
    ms_genotypes = tuple(
        [
            MicrosatelliteHistogramGenotype.get_for_string(s) \
            for s in msgs
        ]
    )
    return ms_genotypes, prefix


class MicrosatelliteHistogramGenotype(models.Model):
    microsatellite = models.ForeignKey(Microsatellite, null=True)
    repeat_number = models.PositiveIntegerField()

    class Meta:
        index_together = (
            ("microsatellite", "repeat_number"),
        )
        unique_together = (
            ("microsatellite", "repeat_number"),
        )

    def __str__(self):
        return "{}={}".format(self.microsatellite.id, self.repeat_number)

    @classmethod
    def get_for_string(cls, s):
        # py3: m = re.fullmatch("([1-9][0-9]*)=([1-9][0-9]*)", s)
        m = re.match("([1-9][0-9]*)=([1-9][0-9]*)$", s)
        if not m:
            raise ValueError("Bad ms genotype string: {}".format(s))
        msid, rn = m.groups()
        # NOTE: we save a query by not getting the actual MS.
        # This is OK as long as we use a db with FK enforcement.
        ms = Microsatellite.objects.get(pk=int(msid))
        obj, c = cls.objects.get_or_create(
            microsatellite=ms,
            repeat_number=int(rn),
        )
        return obj

    @classmethod
    def get_for_genotype(cls, ms, rn):
        mhg, c = cls.objects.get_or_create(
            microsatellite=ms,
            repeat_number=rn,
        )
        return mhg

    @property
    def sequence(self):
        return self.microsatellite.repeat_unit_ref_seq * self.repeat_number


class MicrosatelliteHistogramGenotypeSet(models.Model):
    microsatellite_genotype1 = models.ForeignKey(MicrosatelliteHistogramGenotype, related_name='+')
    microsatellite_genotype2 = models.ForeignKey(MicrosatelliteHistogramGenotype, related_name='+')
    microsatellite_genotype3 = models.ForeignKey(MicrosatelliteHistogramGenotype, related_name='+')
    microsatellite_genotype4 = models.ForeignKey(MicrosatelliteHistogramGenotype, related_name='+')
    microsatellite_genotype5 = models.ForeignKey(MicrosatelliteHistogramGenotype, related_name='+')
    microsatellite_genotype6 = models.ForeignKey(MicrosatelliteHistogramGenotype, related_name='+')
    microsatellite_genotype7 = models.ForeignKey(MicrosatelliteHistogramGenotype, related_name='+')
    microsatellite_genotype8 = models.ForeignKey(MicrosatelliteHistogramGenotype, related_name='+')

    @staticmethod
    def genotype_field_names():
        for i in range(1,9):
            yield 'microsatellite_genotype{}'.format(i)

    @classmethod
    def get_for_msgs(cls, msgs):
        l = list(msgs)
        names = list(cls.genotype_field_names())
        assert len(names) >= len(l)
        none_ms_genotype = MicrosatelliteHistogramGenotype.objects.get(microsatellite=None)
        ordered_genotypes = dict(itertools.zip_longest(
            names,
            sorted(l, key=lambda g: g.microsatellite.slice),
            fillvalue=none_ms_genotype,
        ))
        obj, c = cls.objects.get_or_create(**ordered_genotypes)
        return obj

    @property
    def genotype_fields(self):
        return [
            self.microsatellite_genotype1,
            self.microsatellite_genotype2,
            self.microsatellite_genotype3,
            self.microsatellite_genotype4,
            self.microsatellite_genotype5,
            self.microsatellite_genotype6,
            self.microsatellite_genotype7,
            self.microsatellite_genotype8,
        ]

    @property
    def genotypes(self):
        return {
            genotype for genotype
            in self.genotype_fields
            if genotype.microsatellite is not None
        }

    class Meta:
        index_together = (
            (
                "microsatellite_genotype1",
                "microsatellite_genotype2",
                "microsatellite_genotype3",
                "microsatellite_genotype4",
                "microsatellite_genotype5",
                "microsatellite_genotype6",
                "microsatellite_genotype7",
                "microsatellite_genotype8",
             ),
        )
        unique_together = (
            (
                "microsatellite_genotype1",
                "microsatellite_genotype2",
                "microsatellite_genotype3",
                "microsatellite_genotype4",
                "microsatellite_genotype5",
                "microsatellite_genotype6",
                "microsatellite_genotype7",
                "microsatellite_genotype8",
            ),
        )


class SNPHistogramGenotype(models.Model):
    snp = models.ForeignKey(SNP, null=True)
    base = models.CharField(max_length=1)

    class Meta:
        index_together = (
            ("snp", "base"),
        )
        unique_together = (
            ("snp", "base"),
        )


class SNPHistogramGenotypeSet(models.Model):
    snp_genotype1 = models.ForeignKey(SNPHistogramGenotype, related_name='+')
    snp_genotype2 = models.ForeignKey(SNPHistogramGenotype, related_name='+')
    snp_genotype3 = models.ForeignKey(SNPHistogramGenotype, related_name='+')
    snp_genotype4 = models.ForeignKey(SNPHistogramGenotype, related_name='+')
    snp_genotype5 = models.ForeignKey(SNPHistogramGenotype, related_name='+')
    snp_genotype6 = models.ForeignKey(SNPHistogramGenotype, related_name='+')
    snp_genotype7 = models.ForeignKey(SNPHistogramGenotype, related_name='+')
    snp_genotype8 = models.ForeignKey(SNPHistogramGenotype, related_name='+')

    @staticmethod
    def genotype_field_names():
        for i in range(1, 9):
            yield 'snp_genotype{}'.format(i)

    @property
    def genotype_fields(self):
        return [
            self.snp_genotype1,
            self.snp_genotype2,
            self.snp_genotype3,
            self.snp_genotype4,
            self.snp_genotype5,
            self.snp_genotype6,
            self.snp_genotype7,
            self.snp_genotype8,
        ]

    @property
    def genotypes(self):
        for genotype in self.genotype_fields:
            if genotype.snp is not None:
                yield genotype

    class Meta:
        index_together = (
            (
                "snp_genotype1",
                "snp_genotype2",
                "snp_genotype3",
                "snp_genotype4",
                "snp_genotype5",
                "snp_genotype6",
                "snp_genotype7",
                "snp_genotype8",
             ),
        )
        unique_together = (
            (
                "snp_genotype1",
                "snp_genotype2",
                "snp_genotype3",
                "snp_genotype4",
                "snp_genotype5",
                "snp_genotype6",
                "snp_genotype7",
                "snp_genotype8",
             ),
        )


class HistogramEntryReads(models.Model):
    """
    Represents the collection of reads that contributed to a single genotype in a Histogram
    """
    histogram = models.ForeignKey(Histogram)
    microsatellite_genotypes = models.ForeignKey(MicrosatelliteHistogramGenotypeSet)
    snp_genotypes = models.ForeignKey(SNPHistogramGenotypeSet)
    num_reads = models.PositiveIntegerField()
    fastq1 = models.FilePathField(max_length=200)
    fastq2 = models.FilePathField(max_length=200)
    fastqm = models.FilePathField(max_length=200, null=True)

    @property
    def files(self):
        if self.fastq1 == 'N/A':
            # no files
            raise StopIteration
        
        yield self.fastq1
        yield self.fastq2
        yield self.fastqm

    def __str__(self):
        return "{}: {}".format(self.histogram.subclass,
            ", ".join([
                "{}".format(msg) for msg in self.microsatellite_genotypes.genotypes
            ] + [
                "{}".format(sng) for sng in self.snp_genotypes.genotypes
            ])
        )

    class Meta:
        unique_together = (
            (
                "histogram",
                "microsatellite_genotypes",
                "snp_genotypes",
             ),
        )
post_delete_files(HistogramEntryReads)
