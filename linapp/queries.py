__author__ = 'ofirr'

from Bio.SeqUtils.MeltingTemp import Tm_staluc
from linapp.models import Microsatellite, PrimersMultiplex, TargetEnrichment


def get_targets_by_panel(panel):
    for te in panel.targets.select_related('left', 'right', 'left__sequence', 'right__sequence', 'left__referencevalue',
                                           'right__referencevalue', 'primersmultiplex_set__physical_locations',
                                           'primersmultiplex_set__physical_locations__plate'):
        for tgt in te.targets.select_related('chromosome', 'type'):
            for mpx in te.primersmultiplex_set.all():
                for loc in mpx.physical_locations.all():
                    try:
                        ms = tgt.microsatellite
                        repeat_unit_len = str(ms.repeat_unit_len)
                        repeat_number = str(ms.repeat_number)
                        repeat_unit_type = str(ms.repeat_unit_type)
                    except Microsatellite.DoesNotExist:
                        repeat_unit_len = ''
                        repeat_number = ''
                        repeat_unit_type = ''
                    yield [str(tgt.id), # Target ID
                           tgt.name, # Target name
                           str(te.id),  # Target enrichment name
                           tgt.type.name,  # Target: MS/Other Mutation
                           tgt.chromosome.assembly.name, #Assembly name
                           str(repeat_unit_len),  # Basic Unit size
                           str(repeat_number),  # Expected Number of repeats
                           str(repeat_unit_type),  # Basic Unit Type
                           tgt.chromosome.name,  # Chromosome
                           str(tgt.end_pos-tgt.start_pos),  # Length MS
                           te.left.sequence.sequence,  # Primer sequence -  Left
                           str(Tm_staluc(te.left.referencevalue.sequence)),  # Primer Tm -  Left
                           te.right.sequence.sequence,  # Primer sequence -  Right
                           str(Tm_staluc(te.right.referencevalue.sequence)),  # Primer Tm -  Right
                           str(te.passed_validation),
                           str(tgt.start_pos),  # Target location on Chromosome - start
                           str(tgt.end_pos),  # Target location on Chromosome - end
                           str(te.left.start_pos), # left primer location on Chromosome - start
                           str(te.left.end_pos),  # left primer location on Chromosome - end
                           str(te.right.start_pos), # right primer location on Chromosome - start
                           str(te.right.end_pos),  # right primer location on Chromosome - end
                           str(te.left.start_pos),  # Amplicon location on Chromosome - start
                           str(te.right.end_pos),  # Amplicon location on Chromosome - end
                           str(mpx.name),  # Mpx groups names
                           str(len(mpx.primers.all())),
                           str(loc.plate.name),
                           str(loc.well)]

def get_targets_for_aar7(panel): #temporary query 08.06.14 for aar7
    mpxs = []
    mpxs += list(PrimersMultiplex.objects.filter(physical_locations__plate__name='MM_MPX_w/o_LB_P3').filter(name__endswith='40'))
    mpxs += list(PrimersMultiplex.objects.filter(physical_locations__plate__name='MM_MPX_w/o_LB_P4'))
    for mpx in mpxs:
        for te in mpx.primers.all():
            for tgt in te.targets.all():
                try:
                    ms = tgt.microsatellite
                    repeat_unit_len = str(ms.repeat_unit_len)
                    repeat_number = str(ms.repeat_number)
                    repeat_unit_type = str(ms.repeat_unit_type)
                except Microsatellite.DoesNotExist:
                    repeat_unit_len = ''
                    repeat_number = ''
                    repeat_unit_type = ''
                yield [str(tgt.id), # Target ID
                       tgt.name, # Target name
                       str(te.id),  # Target enrichment name
                       tgt.type.name,  # Target: MS/Other Mutation
                       tgt.chromosome.assembly.name, #Assembly name
                       str(repeat_unit_len),  # Basic Unit size
                       str(repeat_number),  # Expected Number of repeats
                       str(repeat_unit_type),  # Basic Unit Type
                       tgt.chromosome.name,  # Chromosome
                       str(tgt.end_pos-tgt.start_pos),  # Length MS
                       te.left.sequence.sequence,  # Primer sequence -  Left
                       str(Tm_staluc(te.left.referencevalue.sequence)),  # Primer Tm -  Left
                       te.right.sequence.sequence,  # Primer sequence -  Right
                       str(Tm_staluc(te.right.referencevalue.sequence)),  # Primer Tm -  Right
                       str(te.passed_validation),
                       str(tgt.start_pos),  # Target location on Chromosome - start
                       str(tgt.end_pos),  # Target location on Chromosome - end
                       str(te.left.start_pos), # left primer location on Chromosome - start
                       str(te.left.end_pos),  # left primer location on Chromosome - end
                       str(te.right.start_pos), # right primer location on Chromosome - start
                       str(te.right.end_pos),  # right primer location on Chromosome - end
                       str(te.left.start_pos),  # Amplicon location on Chromosome - start
                       str(te.right.end_pos),  # Amplicon location on Chromosome - end
                       str(mpx.name),  # Mpx groups names
                       str(len(mpx.primers.all())),
                       '',
                       '']

def get_extra_targets_for_aar7(panel):
    target_enrichment_groups = [m.primers.all() for m in PrimersMultiplex.objects.filter(physical_locations__plate__name='MM_MPX_w/o_LB_P3').exclude(name__endswith='40')]
    target_enrichments = [item for sublist in target_enrichment_groups for item in sublist]
    mpxs = []
    mpxs += list(PrimersMultiplex.objects.filter(physical_locations__plate__name='MM_MPX_w/o_LB_P3').filter(name__endswith='40'))
    mpxs += list(PrimersMultiplex.objects.filter(physical_locations__plate__name='MM_MPX_w/o_LB_P4'))
    panel_tes = TargetEnrichment.objects.filter(primersmultiplex__in=mpxs)
    for te in list(set(target_enrichments)-set(panel_tes)):
        for tgt in te.targets.all():
            try:
                ms = tgt.microsatellite
                repeat_unit_len = str(ms.repeat_unit_len)
                repeat_number = str(ms.repeat_number)
                repeat_unit_type = str(ms.repeat_unit_type)
            except Microsatellite.DoesNotExist:
                repeat_unit_len = ''
                repeat_number = ''
                repeat_unit_type = ''
            yield [str(tgt.id), # Target ID
                   tgt.name, # Target name
                   str(te.id),  # Target enrichment name
                   tgt.type.name,  # Target: MS/Other Mutation
                   tgt.chromosome.assembly.name, #Assembly name
                   str(repeat_unit_len),  # Basic Unit size
                   str(repeat_number),  # Expected Number of repeats
                   str(repeat_unit_type),  # Basic Unit Type
                   tgt.chromosome.name,  # Chromosome
                   str(tgt.end_pos-tgt.start_pos),  # Length MS
                   te.left.sequence.sequence,  # Primer sequence -  Left
                   str(Tm_staluc(te.left.referencevalue.sequence)),  # Primer Tm -  Left
                   te.right.sequence.sequence,  # Primer sequence -  Right
                   str(Tm_staluc(te.right.referencevalue.sequence)),  # Primer Tm -  Right
                   str(te.passed_validation),
                   str(tgt.start_pos),  # Target location on Chromosome - start
                   str(tgt.end_pos),  # Target location on Chromosome - end
                   str(te.left.start_pos), # left primer location on Chromosome - start
                   str(te.left.end_pos),  # left primer location on Chromosome - end
                   str(te.right.start_pos), # right primer location on Chromosome - start
                   str(te.right.end_pos),  # right primer location on Chromosome - end
                   str(te.left.start_pos),  # Amplicon location on Chromosome - start
                   str(te.right.end_pos),  # Amplicon location on Chromosome - end
                   str(None),  # Mpx groups names
                   str(len(list(set(target_enrichments)-set(panel_tes)))),
                   '',
                   '']