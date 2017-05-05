import pytest
import decimal
import itertools
import functools
from sequencing.calling.hist import Histogram
from sequencing.calling.simcor.models_common import BestCorrelationCalledAlleles, \
    BestCorrelationProportionalCalledAlleles, BestCorrelationProportionalHighestPeakCalledAlleles
from sequencing.calling.simcor.range import contains_excluded_proportions_wrapper


@pytest.mark.django_db
def test_mono_schema(minimalsimcormonoschema):
    assert set(minimalsimcormonoschema.alleles_and_cycles) == set([
        (15, 20), (16, 20), (15, 21), (16, 21),
        (15, 22), (16, 22), (15, 23), (16, 23)
    ])


@pytest.mark.django_db
def test_bi_schema(minimalsimcorbischema):
    assert minimalsimcorbischema.allele_number == 2
    assert set(minimalsimcorbischema.alleles_and_cycles) == set([
        (frozenset([15, 16]), 20), (frozenset([15, ]), 20), (frozenset([16, ]), 20),
        (frozenset([15, 16]), 21), (frozenset([15, ]), 21), (frozenset([16, ]), 21),
        (frozenset([15, 16]), 22), (frozenset([15, ]), 22), (frozenset([16, ]), 22),
        (frozenset([15, 16]), 23), (frozenset([15, ]), 23), (frozenset([16, ]), 23),
    ])


@pytest.mark.django_db
def test_proportional_bi_schema(minimalsimcorbipropschema):
    assert minimalsimcorbipropschema.allele_number == 2
    assert set(minimalsimcorbipropschema.alleles_and_cycles) == set([
        (frozenset([(15, decimal.Decimal('0.1')), (16, decimal.Decimal('0.9'))]), 20),
        (frozenset([(15, decimal.Decimal('0.2')), (16, decimal.Decimal('0.8'))]), 20),
        (frozenset([(15, decimal.Decimal('0.3')), (16, decimal.Decimal('0.7'))]), 20),
        (frozenset([(15, decimal.Decimal('0.4')), (16, decimal.Decimal('0.6'))]), 20),
        (frozenset([(15, decimal.Decimal('0.5')), (16, decimal.Decimal('0.5'))]), 20),
        (frozenset([(15, decimal.Decimal('0.6')), (16, decimal.Decimal('0.4'))]), 20),
        (frozenset([(15, decimal.Decimal('0.7')), (16, decimal.Decimal('0.3'))]), 20),
        (frozenset([(15, decimal.Decimal('0.8')), (16, decimal.Decimal('0.2'))]), 20),
        (frozenset([(15, decimal.Decimal('0.9')), (16, decimal.Decimal('0.1'))]), 20),
        (frozenset([(15, decimal.Decimal('0.0')), (16, decimal.Decimal('1.0'))]), 20),
        (frozenset([(15, decimal.Decimal('1.0')), (16, decimal.Decimal('0.0'))]), 20),
    ])
    assert len(set(minimalsimcorbipropschema.sim_hists_space)) > 1  # TODO: expand this


@pytest.mark.django_db
def test_bound_proportional_bi_schema(minimalsimcorbiboundpropschema):
    assert minimalsimcorbiboundpropschema.allele_number == 2
    assert set(minimalsimcorbiboundpropschema.alleles_and_cycles) == set([
        (frozenset([(15, decimal.Decimal('0.4')), (16, decimal.Decimal('0.6'))]), 20),
        (frozenset([(15, decimal.Decimal('0.5')), (16, decimal.Decimal('0.5'))]), 20),
        (frozenset([(15, decimal.Decimal('0.6')), (16, decimal.Decimal('0.4'))]), 20),
        (frozenset([(15, decimal.Decimal('0.0')), (16, decimal.Decimal('1.0'))]), 20),
        (frozenset([(15, decimal.Decimal('1.0')), (16, decimal.Decimal('0.0'))]), 20),
    ])
    assert len(set(minimalsimcorbiboundpropschema.sim_hists_space)) > 1  # TODO: expand this


@pytest.mark.django_db
def test_prf_exclusion_function(minimal_prf_simcorbiboundpropschema):
    length_sensitivity = minimal_prf_simcorbiboundpropschema.length_sensitivity
    diff_sensetivity = minimal_prf_simcorbiboundpropschema.diff_sensetivity
    pre_filter_alleles_and_cycles = set([
        (frozenset([(15, decimal.Decimal('0.3')), (16, decimal.Decimal('0.7'))]), 20),
        (frozenset([(15, decimal.Decimal('0.4')), (16, decimal.Decimal('0.6'))]), 20),
        (frozenset([(15, decimal.Decimal('0.5')), (16, decimal.Decimal('0.5'))]), 20),
        (frozenset([(15, decimal.Decimal('0.6')), (16, decimal.Decimal('0.4'))]), 20),
        (frozenset([(15, decimal.Decimal('0.7')), (16, decimal.Decimal('0.3'))]), 20),
        (frozenset([(15, decimal.Decimal('0.0')), (16, decimal.Decimal('1.0'))]), 20),
        (frozenset([(15, decimal.Decimal('1.0')), (16, decimal.Decimal('0.0'))]), 20),
    ])
    post_filter_alleles_and_cycles = set(itertools.filterfalse(
        functools.partial(
            contains_excluded_proportions_wrapper,
            length_sensitivity=length_sensitivity,
            diff_sensetivity=diff_sensetivity
        ),
        pre_filter_alleles_and_cycles,
    ))
    assert post_filter_alleles_and_cycles == set([
        (frozenset([(15, decimal.Decimal('0.4')), (16, decimal.Decimal('0.6'))]), 20),
        (frozenset([(15, decimal.Decimal('0.5')), (16, decimal.Decimal('0.5'))]), 20),
        (frozenset([(15, decimal.Decimal('0.6')), (16, decimal.Decimal('0.4'))]), 20),
        (frozenset([(15, decimal.Decimal('0.0')), (16, decimal.Decimal('1.0'))]), 20),
        (frozenset([(15, decimal.Decimal('1.0')), (16, decimal.Decimal('0.0'))]), 20),
    ])


@pytest.mark.django_db
def test_prf_bound_proportional_bi_schema(minimal_prf_simcorbiboundpropschema):
    assert minimal_prf_simcorbiboundpropschema.allele_number == 2
    ac_set = set(minimal_prf_simcorbiboundpropschema.alleles_and_cycles)
    assert len(ac_set) == 5
    assert ac_set == set([
        (frozenset([(15, decimal.Decimal('0.4')), (16, decimal.Decimal('0.6'))]), 20),
        (frozenset([(15, decimal.Decimal('0.5')), (16, decimal.Decimal('0.5'))]), 20),
        (frozenset([(15, decimal.Decimal('0.6')), (16, decimal.Decimal('0.4'))]), 20),
        (frozenset([(15, decimal.Decimal('0.0')), (16, decimal.Decimal('1.0'))]), 20),
        (frozenset([(15, decimal.Decimal('1.0')), (16, decimal.Decimal('0.0'))]), 20),
    ])
    # {(frozenset({(16, Decimal('1.00')), (15, Decimal('0.00'))}), 20),
    #  (frozenset({(16, Decimal('0.00')), (15, Decimal('1.00'))}), 20),
    #  (frozenset({(16, Decimal('0.50')), (15, Decimal('0.50'))}), 20)}
    assert len(set(minimal_prf_simcorbiboundpropschema.sim_hists_space)) > 1  # TODO: expand this


@pytest.mark.django_db
def test_mono_schema_called_allele_class(minimalsimcormonoschema):
    assert minimalsimcormonoschema.called_allele_class == BestCorrelationCalledAlleles


@pytest.mark.django_db
def test_proportional_bi_schema_called_allele_class(minimalsimcorbipropschema):
    assert minimalsimcorbipropschema.called_allele_class == BestCorrelationProportionalCalledAlleles


@pytest.mark.django_db
def test_prf_proportional_bi_schema_called_allele_class(prf_simcorbipropschema):
    assert prf_simcorbipropschema.called_allele_class == BestCorrelationProportionalCalledAlleles


@pytest.mark.django_db
def test_highest_peaks_bi_sim_cor_class(simcorbiprophighpeakschema):
    assert simcorbiprophighpeakschema.called_allele_class == BestCorrelationProportionalHighestPeakCalledAlleles
    assert simcorbiprophighpeakschema.allele_number == 2
    assert len(set(simcorbiprophighpeakschema.sim_hists_space)) > 1  # TODO: expand this
    sample_hist = Histogram(
            {5: 10,
             6: 1,
             7: 1,
             8: 1,
             9: 1,
             10: 11})
    assert set(simcorbiprophighpeakschema.alleles_by_hist(sample_hist)) == {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
    assert len(set(simcorbiprophighpeakschema.filtered_sim_hists_space(sample_hist))) > 1  # TODO: expand this


@pytest.mark.django_db
def test_prf_highest_peaks_bi_sim_cor_class(prf_simcorbiprophighpeakschema):
    assert prf_simcorbiprophighpeakschema.called_allele_class == BestCorrelationProportionalHighestPeakCalledAlleles
    assert prf_simcorbiprophighpeakschema.allele_number == 2
    assert len(set(prf_simcorbiprophighpeakschema.sim_hists_space)) > 1  # TODO: expand this
    sample_hist = Histogram(
            {5: 10,
             6: 1,
             7: 1,
             8: 1,
             9: 1,
             10: 11})
    assert set(prf_simcorbiprophighpeakschema.alleles_by_hist(sample_hist)) == {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
    assert len(set(prf_simcorbiprophighpeakschema.filtered_sim_hists_space(sample_hist))) > 1  # TODO: expand this