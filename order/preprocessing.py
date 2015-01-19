from collections import defaultdict, Counter
from binomial_sim import sim, dyn_prob
from frogress import bar as tqdm
from order.hist import Histogram
from itertools import combinations
import numpy as np


def generate_bin_hist(d,
                  cycles,
                  up=lambda x: 0.003,
                  dw=lambda x: 0.022,
                  sample_depth=10000,
                  normalize=True,
                  truncate=False,
                  cut_peak=False,
                  trim_extremes=False,
                  **kwargs):
    up_p = up(d)
    dw_p = dw(d)
    z = sim(cycles, up_p, dw_p)
    return Histogram(
        Counter(z.rand(sample_depth)),
        normalize=normalize,
        nsamples=sample_depth,
        truncate=truncate,
        cut_peak=cut_peak,
        trim_extremes=trim_extremes
    )


def generate_dyn_hist(d,
                  cycles,
                  up=lambda x: 0.003,
                  dw=lambda x: 0.022,
                  sample_depth=10000,
                  normalize=True,
                  truncate=False,
                  cut_peak=False,
                  trim_extremes=False,
                  **kwargs):
    dyn_hist = dyn_prob(cycles,
                        d,
                        up,
                        dw,
                        nsamples=sample_depth,
                        normalize=normalize,
                        truncate=truncate,
                        cut_peak=cut_peak,
                        trim_extremes=trim_extremes)
    dyn_hist.normalize()
    return dyn_hist - d


def get_method(method):
    if method == 'bin':
        return generate_bin_hist
    if method == 'dyn':
        return generate_dyn_hist
    print 'unknown method'
    raise


def generate_hist(d, cycles, method, **kwargs):
    generate_method_hist = get_method(method)
    return generate_method_hist(d, cycles, **kwargs)


def generate_sim_hists(max_ms_length=60,
                       max_cycles=90,
                       method='bin',
                       **kwargs):
    sim_hists = defaultdict(dict)
    for d in tqdm(range(max_ms_length)):
        for cycles in range(max_cycles):
            sim_hists[d][cycles] = generate_hist(d, cycles, method, **kwargs)
    return sim_hists


def generate_duplicate_sim_hist(sim_hists, max_alleles=2):
    dup_sim_hist = defaultdict(lambda: defaultdict(dict))
    for allele_number in range(1, max_alleles+1):
        for seeds in combinations(sim_hists.keys(), allele_number):
            shift = int(np.mean(seeds))
            for cycles in tqdm(sim_hists[0].keys()):#TODO: get sim_hists parameters in call?
                first_seed = seeds[0]
                sum_hist = sim_hists[first_seed][cycles] + first_seed
                for seed in seeds[1:]:
                    sum_hist = sum_hist + (sim_hists[seed][cycles] + seed)
                dup_sim_hist[frozenset(seeds)][cycles] = sum_hist - shift
    return dup_sim_hist


def generate_sim_hists_of_up_to_k_alleles(**kwargs):
    """
        method='bin'
        max_ms_length=60,
        max_cycles=90,
        up=lambda x: 0.003,
        dw=lambda x: 0.022,
        sample_depth=10000,
        normalize=True,
        truncate=False,
        cut_peak=False,
        trim_extremes=False
        max_alleles = 2
    :param kwargs:
    :return:
    """
    sim_hists = generate_sim_hists(**kwargs)
    dup_sim_hist = generate_duplicate_sim_hist(sim_hists, kwargs['max_alleles'])
    return dup_sim_hist


def flatten_index(sim_hists):
    flat_dict = {}
    for root in sim_hists:
        for cycle in sim_hists[root]:
            flat_dict[(root, cycle)] = sim_hists[root][cycle]
    return flat_dict


def inflate_index(sim_hists):
    inflated_dict = defaultdict(lambda: defaultdict(dict))
    for root, cycle in sim_hists:
        inflated_dict[root][cycle] = sim_hists[(root, cycle)]
    return inflated_dict
