
from django.db import models, IntegrityError
from django.db.models import Count
from model_utils.managers import InheritanceManager

from genomes.models import DNASlice
from misc.dna import DNA
from targeted_enrichment.planning.models import UGSPlus, UGSMinus


class Amplicon(models.Model):
    slice = models.ForeignKey(DNASlice)

    objects = InheritanceManager()

    # FIXME
    @property
    def subclass(self):
        return Amplicon.objects.get_subclass(id=self.id)

    @property
    def left_margin(self):
        raise NotImplementedError()

    @property
    def right_margin(self):
        raise NotImplementedError()

    @property
    def sequence(self):
        return self.left_margin + self.slice.sequence + self.right_margin

    def __str__(self):
        return "{}".format(self.slice)


def get_ampliconcollection_by_amplicons(amps):
    for ac in AmpliconCollection.objects.annotate(amp_num=Count('amplicons')).filter(amp_num=len(amps)):
        if set(amp.id for amp in ac.amplicons.all()) == set(amp.id for amp in amps):
            return ac
    raise AmpliconCollection.DoesNotExist()


class AmpliconCollection(models.Model):
    amplicons = models.ManyToManyField(Amplicon)

    @classmethod
    def custom_get_or_create(cls, amplicons):
        try:
            ac = get_ampliconcollection_by_amplicons(amplicons)
        except cls.DoesNotExist:
            ac = cls.objects.create()
            ac.amplicons = amplicons
            ac.save()
        return ac


class RawAmplicon(Amplicon):

    @property
    def left_margin(self):
        return DNA()

    @property
    def right_margin(self):
        return DNA()


class TargetedAmplicon(Amplicon):
    left_ugs = models.ForeignKey(UGSPlus)
    right_ugs = models.ForeignKey(UGSMinus)

    def infer_slice(self):
        c = self.left_ugs.slice.chromosome
        if self.right_ugs.slice.chromosome != c:
            raise IntegrityError("Both UGSs should be of the same chromosome.")
        # FIXME: this is only true for 1-based,inclusive indexing!
        left = self.left_ugs.slice.end_pos + 1
        right = self.right_ugs.slice.start_pos - 1
        s, created = DNASlice.objects.get_or_create(
            chromosome=c,
            start_pos=left,
            end_pos=right,
        )
        self.slice = s

    class Meta:
        abstract = True


class PlainTargetedAmplicon(TargetedAmplicon):

    @property
    def left_margin(self):
        return self.left_ugs.ref_sequence

    @property
    def right_margin(self):
        return self.right_ugs.ref_sequence


class TargetedAmpliconWithCompanyTag(TargetedAmplicon):
    left_tag = models.CharField(max_length=1) # DNAField
    right_tag = models.CharField(max_length=1) # DNAField
    
    @property
    def left_margin(self):
        return DNA(self.left_tag) + self.ter.te.left.ref_sequence

    @property
    def right_margin(self):
        return self.ter.te.right.ref_sequence + DNA(self.right_tag)


class UMITargetedAmplicon(TargetedAmplicon):
    umi_length = models.PositiveSmallIntegerField()

    @property
    def left_margin(self):
        return DNA.umi(self.umi_length) + self.left_ugs.ref_sequence

    @property
    def right_margin(self):
        return self.right_ugs.ref_sequence + DNA.umi(self.umi_length)
