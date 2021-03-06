from django.db import models
from sequencing.calling.models import CallingScheme
from sequencing.calling.simcor.simulation_spaces import mono_sim_hists_space_generator, bi_sim_hists_space_generator,\
    proportional_bi_sim_hists_space_generator, vec_proportional_bi_sim_hists_space_generator
from sequencing.calling.hist_dist import pop_dist_corr_numpy, derived_proportions_dot, dotv
from sequencing.calling.simcor.calling import call_microsatellite_histogram, get_closest, get_closest_vec_opt, \
    get_closest_vec_opt_mms
from sequencing.calling.simcor.models_common import CyclesModelMixin, SimulationsByCycles, MSLengthBoundsModelMixin, \
    ProportionsBoundsModelMixin, ProportionStepModelMixin, BestCorrelationCalledAlleles, \
    BestCorrelationProportionalCalledAlleles, \
    BestCorrelationProportionalHighestPeakCalledAlleles, \
    AlleleDistanceProportionBoundsModelMixin
from sequencing.calling.simcor.range import AllelesCyclesRangeMixin, FullRangeBiMixin, \
    ProportionalAllelesCyclesRangeMixin, BoundProportionalAllelesCyclesRangeMixin, \
    HighestPeaksRangeModelMixin, ProximityRatioFilteredBoundProportionalAllelesCyclesRangeMixin, \
    ProximityRatioFilteredProportionalAllelesCyclesRangeMixin, HighestPeaksModelMixin
from itertools import filterfalse, repeat


class BestCorrelationCalledAlleleMixin(object):
    @property
    def called_allele_class(self):
        return BestCorrelationCalledAlleles


class BestCorrelationProportionalCalledAlleleMixin(object):
    @property
    def called_allele_class(self):
        return BestCorrelationProportionalCalledAlleles


class BestCorrelationProportionalHighestPeakCalledAlleleMIxin(object):
    @property
    def called_allele_class(self):
        return BestCorrelationProportionalHighestPeakCalledAlleles


class DynamicFilteredHistSpaceMixin(object):
    """
    Filters sim_hists_space by a live histogram object
    """

    def filtered_sim_hists_space(self, hist):
        raise NotImplemented

    def find_best_in_space(self, hist):
        return get_closest(hist, self.filtered_sim_hists_space(hist), self.distance_metric)


class FilterByHistMixin(DynamicFilteredHistSpaceMixin):

    def filtered_sim_hists_seeds(self, hist):
        """cuts the simulations based on the hist"""
        alleles_by_hist = set(self.alleles_by_hist(hist))
        def allele_in_seed_space(alleles_and_cycles):
            alleles, cycles = alleles_and_cycles
            if not isinstance(self, ProportionStepModelMixin):
                alleles = zip(alleles, repeat(None))  # make it look like proportional
            for allele, p in alleles:
                if allele not in alleles_by_hist:
                    return True
            return False
        yield from filterfalse(allele_in_seed_space, self.alleles_and_cycles)

    def filtered_sim_hists_space(self, hist):
        """cuts the simulations based on the hist"""
        yield from self.sim_hists_space_generator(
            self.simulations.get_simulations_dict(),
            self.filtered_sim_hists_seeds(hist))


class BaseSimCallingScheme(BestCorrelationCalledAlleleMixin, CallingScheme, MSLengthBoundsModelMixin, CyclesModelMixin):
    """
    Base calling for calling against simulated histograms
    """
    simulations = models.ForeignKey(SimulationsByCycles)

    class Meta:
        abstract = True

    @property
    def distance_metric(self):
        return pop_dist_corr_numpy

    @property
    def sim_hists_space_generator(self):
        raise NotImplemented

    @property
    def sim_hists_space(self):
        yield from self.sim_hists_space_generator(
            self.simulations.get_simulations_dict(),
            self.alleles_and_cycles)

    def find_best_in_space(self, hist):
        return get_closest(hist, self.sim_hists_space, self.distance_metric)

    def call_ms_hist(self, dbhist, microsatellite):
        return call_microsatellite_histogram(self, dbhist, microsatellite)


class BaseMonoAllelicMixin(object):

    @property
    def allele_number(self):
        return 1

    @property
    def sim_hists_space_generator(self):
        return mono_sim_hists_space_generator


class BaseBiAllelicMixin(object):

    @property
    def allele_number(self):
        return 2


class FullMonoSimCorScheme(BaseMonoAllelicMixin, BaseSimCallingScheme, AllelesCyclesRangeMixin):
    """
    Calling schema for calling against simulated histograms
    """
    pass


class FullBiSimCorScheme(BaseSimCallingScheme, BaseBiAllelicMixin, FullRangeBiMixin):
    """
    Calling schema for calling against combinations of two simulated histograms
    """

    @property
    def sim_hists_space_generator(self):
        return bi_sim_hists_space_generator


class ProportionalSimCorSchemeMixin(object):
    @property
    def sim_hists_space_generator(self):
        return proportional_bi_sim_hists_space_generator


class ProportionalSimCorScheme(BestCorrelationProportionalCalledAlleleMixin, BaseBiAllelicMixin,
                               ProportionStepModelMixin, ProportionalAllelesCyclesRangeMixin,
                               ProportionalSimCorSchemeMixin, BaseSimCallingScheme):
    """
    Calling schema for calling against multi-allelic simulated histograms at differential proportions
    """
    pass


class ProximityRatioFilteredProportionalSimCorScheme(BestCorrelationProportionalCalledAlleleMixin, BaseBiAllelicMixin,
                               ProportionStepModelMixin, AlleleDistanceProportionBoundsModelMixin,
                               ProximityRatioFilteredProportionalAllelesCyclesRangeMixin,
                               ProportionalSimCorSchemeMixin, BaseSimCallingScheme):
    """
    Calling schema for calling against multi-allelic simulated histograms at differential proportions
    """

    @property
    def alleles_and_cycles(self):
        yield from self.prf_filtered(
            super().alleles_and_cycles,
        )


class BoundProportionalSimCorScheme(BestCorrelationProportionalCalledAlleleMixin, ProportionStepModelMixin,
                                    ProportionsBoundsModelMixin, BaseBiAllelicMixin,
                                    BoundProportionalAllelesCyclesRangeMixin, ProportionalSimCorSchemeMixin,
                                    BaseSimCallingScheme):
    """
    Calling schema for calling against multi-allelic simulated histograms at differential proportions
    """

    pass


class ProximityRatioFilteredBoundProportionalSimCorScheme(BestCorrelationProportionalCalledAlleleMixin, ProportionStepModelMixin,
                                    ProportionsBoundsModelMixin, AlleleDistanceProportionBoundsModelMixin, BaseBiAllelicMixin,
                                    ProximityRatioFilteredBoundProportionalAllelesCyclesRangeMixin, ProportionalSimCorSchemeMixin,
                                    BaseSimCallingScheme):
    """
    Calling schema for calling against multi-allelic simulated histograms at differential proportions
    """

    @property
    def alleles_and_cycles(self):
        yield from self.prf_filtered(
            super().alleles_and_cycles,
        )


class HighestPeaksProportionalBiSimCorSchemeModel(BoundProportionalAllelesCyclesRangeMixin, FilterByHistMixin,
                                                  BestCorrelationProportionalHighestPeakCalledAlleleMIxin, ProportionStepModelMixin,
                                                  ProportionsBoundsModelMixin, HighestPeaksRangeModelMixin, BaseBiAllelicMixin,
                                                  ProportionalSimCorSchemeMixin, BaseSimCallingScheme):
    pass


class HighestPeaksProximityRatioFilteredBiSimCorSchemeModel(HighestPeaksRangeModelMixin, FilterByHistMixin,
                                                            BestCorrelationProportionalHighestPeakCalledAlleleMIxin,
                                                            ProportionStepModelMixin, ProportionsBoundsModelMixin,
                                                            AlleleDistanceProportionBoundsModelMixin, BaseBiAllelicMixin,
                                    ProximityRatioFilteredBoundProportionalAllelesCyclesRangeMixin, ProportionalSimCorSchemeMixin,
                                    BaseSimCallingScheme):
    @property
    def alleles_and_cycles(self):
        yield from self.prf_filtered(
            super().alleles_and_cycles,
        )


class HighestPeaksMonoSimCorSchemeModel(HighestPeaksModelMixin, BaseMonoAllelicMixin,
                                        BaseSimCallingScheme, FilterByHistMixin,
                                        AllelesCyclesRangeMixin):
    pass


class HighestPeaksMonoSimCorSchemeModelDot(HighestPeaksMonoSimCorSchemeModel):
    @property
    def distance_metric(self):
        return dotv


class HighestPeaksProximityRatioFilteredBiSimCorSchemeModelDot(HighestPeaksProximityRatioFilteredBiSimCorSchemeModel):
    @property
    def distance_metric(self):
        return dotv

from decimal import Decimal
class HighestPeaksProximityRatioFilteredBiSimCorSchemeModelDotBA(
    HighestPeaksRangeModelMixin, FilterByHistMixin, BestCorrelationProportionalHighestPeakCalledAlleleMIxin,
    ProportionStepModelMixin, ProportionsBoundsModelMixin, AlleleDistanceProportionBoundsModelMixin, BaseBiAllelicMixin,
    ProximityRatioFilteredBoundProportionalAllelesCyclesRangeMixin, ProportionalSimCorSchemeMixin, BaseSimCallingScheme):

    is_prf = models.BooleanField(default=True)

    @property
    def distance_metric(self):
        return derived_proportions_dot

    @property
    def alleles_and_cycles(self):
        alleles_set = set()
        for alleles_and_cycles in self.prf_filtered(
            super().alleles_and_cycles,
        ):
            alleles_and_proportions, cycle = alleles_and_cycles
            alleles_and_proportions = frozenset({(a, Decimal('0.5')) for a, p in alleles_and_proportions})
            if (alleles_and_proportions, cycle) not in alleles_set:
                yield alleles_and_proportions, cycle
            alleles_set.add((alleles_and_proportions, cycle))

    def find_best_in_space(self, hist):
        return get_closest_vec_opt(hist, self.filtered_sim_hists_space(hist), self.distance_metric, is_prf=self.is_prf,
                                   length_sensitivity=self.length_sensitivity, diff_sensetivity=self.diff_sensetivity,
                                   eps=self.proportion_bounds[0])

    @property
    def sim_hists_space_generator(self):
        return vec_proportional_bi_sim_hists_space_generator


class HighestPeaksProximityRatioFilteredBiSimCorSchemeModelDotBAMMS(
    HighestPeaksRangeModelMixin, FilterByHistMixin, BestCorrelationProportionalHighestPeakCalledAlleleMIxin,
    ProportionStepModelMixin, ProportionsBoundsModelMixin, AlleleDistanceProportionBoundsModelMixin, BaseBiAllelicMixin,
    ProximityRatioFilteredBoundProportionalAllelesCyclesRangeMixin, ProportionalSimCorSchemeMixin, BaseSimCallingScheme):

    @property
    def distance_metric(self):
        return derived_proportions_dot

    @property
    def alleles_and_cycles(self):
        alleles_set = set()
        for alleles_and_cycles in self.prf_filtered(
            super().alleles_and_cycles,
        ):
            alleles_and_proportions, cycle = alleles_and_cycles
            alleles_and_proportions = frozenset({(a, Decimal('0.5')) for a, p in alleles_and_proportions})
            if (alleles_and_proportions, cycle) not in alleles_set:
                yield alleles_and_proportions, cycle
            alleles_set.add((alleles_and_proportions, cycle))

    def find_best_in_space(self, hist):
        best, second_best = get_closest_vec_opt_mms(hist, self.filtered_sim_hists_space(hist), self.distance_metric,
                                                    length_sensitivity=self.length_sensitivity,
                                                    diff_sensetivity=self.diff_sensetivity,
                                                    eps=self.proportion_bounds[0])
        (best_sim_hist, min_dist) = best
        (second_best_sim_hist, second_min_dist) = second_best
        return best_sim_hist, second_min_dist - min_dist

    @property
    def sim_hists_space_generator(self):
        return vec_proportional_bi_sim_hists_space_generator
