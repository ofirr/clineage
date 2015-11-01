from django.contrib.contenttypes import fields
from django.db import models
from targeted_enrichment.planning.models import TargetEnrichment
from targeted_enrichment.reagents.models import TargetedEnrichmentReagent, PCR1PrimerPairTER, \
    PCR1PrimerPairTERDeprecated
from wet_storage.models import SampleLocation

__author__ = 'ofirr'

### -------------------------------------------------------------------------------------
### Primers Multiplex
### -------------------------------------------------------------------------------------


#TODO : notail?


class TERMultiplex(models.Model): # TODO: move to primers, m2m to TER.
    name = models.CharField(max_length=20)
    primers = models.ManyToManyField(TargetedEnrichmentReagent)
    physical_locations = fields.GenericRelation(SampleLocation,
                               content_type_field='content_type',
                               object_id_field='object_id')

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class PCR1Multiplex(TERMultiplex):
    primers = models.ManyToManyField(PCR1PrimerPairTER)
    #TODO: physical_locations(MPXPlate)


class PCR1DeprecatedMultiplex(TERMultiplex):
    primers = models.ManyToManyField(PCR1PrimerPairTERDeprecated)
    #TODO: physical_locations(MPXPlate)


class Panel(models.Model):#collection of targets
                                                # TODO: m2m pri_mux, well on the m2m table.
    name = models.CharField(max_length=50)
    targets = models.ManyToManyField(TargetEnrichment, related_name='panels')
    def __unicode__(self):
        return self.name
