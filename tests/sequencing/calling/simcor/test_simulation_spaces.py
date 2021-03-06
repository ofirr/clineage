import pytest

from sequencing.calling.hist import Histogram as dHist
from tests.sequencing.calling.simcor.conftest import histogram_dicts
from sequencing.calling.simcor.hist_analysis import get_far_apart_highest_peaks


def test_highest_peaks(histogram_dicts):
    for hp in histogram_dicts:
        hist = histogram_dicts[hp]['histogram']
        result = histogram_dicts[hp]['result']
        allele = 2
        distance = 3
        peaks = get_far_apart_highest_peaks(hist, allele_number=allele, minimal_distance_between_peaks=distance)
        assert peaks[0] == result[0] or peaks[0] == result[1]
        assert peaks[1] == result[0] or peaks[1] == result[1]


def test_proportional_highest_peaks(histogram_dicts):
    for hp in histogram_dicts:
        hist = histogram_dicts[hp]['histogram']
        result = histogram_dicts[hp]['result']
        allele = 2
        distance = 3
        min_prop = 0.1
        peaks = get_far_apart_highest_peaks(hist, allele_number=allele,
                                            minimal_distance_between_peaks=distance, min_prop=min_prop)
        assert peaks[0] == result[0] or peaks[0] == result[1]
        assert peaks[1] == result[0] or peaks[1] == result[1]
        assert peaks[0] != peaks[1]


