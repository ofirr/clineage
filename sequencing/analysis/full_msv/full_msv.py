
import os
import itertools
import contextlib
import plumbum
import math
import resource
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from django.db import IntegrityError, connection

from utils.groups import grouper
from misc.utils import unique_file_cm, unique_dir_cm, unlink, \
    get_get_or_create
from sequencing.analysis.full_msv.models import FullMSVariations, \
    FullMSVHistogram, FullMSVMergedReads, FullMSVAssignment, \
    FullMSVMergedReadsPart, FullMSVAssignmentPart
from sequencing.analysis.models import MicrosatelliteHistogramGenotype, \
    MicrosatelliteHistogramGenotypeSet, HistogramEntryReads, \
    SNPHistogramGenotypeSet, SNPHistogramGenotype
from sequencing.analysis.models_common import BowtieIndexMixin, \
    PearOutputMixin, ms_genotypes_to_name, split_ms_genotypes_name, \
    get_ms_genotypes_from_strings_tuple
from targeted_enrichment.planning.models import Microsatellite
from targeted_enrichment.amplicons.models import AmpliconCollection


pear = plumbum.local["pear"]
pear_with_defaults = pear["-v", "40",
                          "-m", "300"]


bowtie2build = plumbum.local["bowtie2-build"]
bowtie2build_fixed_seed = bowtie2build["--seed", "1"]


bowtie2 = plumbum.local["bowtie2"]
bowtie2_fixed_seed = bowtie2["--seed", "1"]
bowtie2_with_defaults = bowtie2_fixed_seed["-p", "1",
    "--very-sensitive"]
bowtie2_with_defaults2 = bowtie2_fixed_seed["-p", "1"]


samtools = plumbum.local["samtools"]
samtools_sort = samtools["sort"]
samtools_view = samtools["view"]
samtools_merge = samtools["merge"]


bwa = plumbum.local["bwa"]
bwa_mem_paramed = bwa["mem", "-M", "-t", "20"]


def merge(sample_reads):
    def inner(raise_or_create_with_defaults):
        with unique_dir_cm() as pear_dir:
            pear_output = PearOutputMixin(
                pear_dump_dir=pear_dir,
            )
            pear_with_defaults("-f", sample_reads.fastq1,
                               "-r", sample_reads.fastq2,
                               "-o", pear_output.pear_files_prefix)
            from django.db import connection
            connection.close()
            return raise_or_create_with_defaults(
                pear_dump_dir=pear_dir,
            )
    return get_get_or_create(inner, FullMSVMergedReads,
        sample_reads=sample_reads,
    )


def _collect_mappings_from_sam(margin_assignment):
    reads_matches = {}
    for read_id, amplicon_margin in margin_assignment.read_sam():
        reads_matches.setdefault(read_id, set()).add(amplicon_margin)
    return reads_matches


@contextlib.contextmanager
def _extract_reads_by_id(indexed_reads, read_ids):
    amplicon_reads = (indexed_reads[read_id] for read_id in read_ids)
    with unique_file_cm("fastq") as amplicon_reads_fastq_name:
        SeqIO.write(amplicon_reads, amplicon_reads_fastq_name, "fastq")
        yield amplicon_reads_fastq_name


def _get_ms_length_range(ms):
    #if (Rep>3)
            #Xcomb{ti} = 3:(Rep*2-3);
    #else
            #Xcomb{ti} = 1:5;
    #end
    # TODO: put better boundries
    n = int(ms.repeat_number)
    if n > 3:
        return range(3,2*n-2)
    else:
        return range(1,6)


def _get_ms_variations(ms):
    for i in _get_ms_length_range(ms):
        yield MicrosatelliteHistogramGenotype.get_for_genotype(ms,i)


def _get_mss_variations_seqrecords(mss, seq_fmt, prefix):
    for mult in itertools.product(*[_get_ms_variations(ms) for ms in mss]):
        seqs = [mhg.sequence for mhg in mult]
        # name='', description='' are workarounds for the '<unknown
        # description>' that is being outputted otherwise
        yield SeqRecord(
            Seq(seq_fmt.format(*seqs)),
            id=ms_genotypes_to_name(mult, prefix),
            name='',
            description=''
        )


def _get_amplicon_variations_seqrecords(amplicon, padding, mss_version):
    amplicon = amplicon.subclass
    mss = Microsatellite.objects.filter(
        slice__start_pos__gte=amplicon.slice.start_pos,
        slice__end_pos__lte=amplicon.slice.end_pos,
        slice__chromosome_id=amplicon.slice.chromosome_id,
        planning_version=mss_version,
    )
    # This is so they are ordered properly for the format string.
    mss = sorted(mss, key=lambda ms: ms.slice.start_pos)
    # FIXME: kill this +-1 when we move to 0-based.
    points = [amplicon.slice.start_pos-1]
    for ms in mss:
        # FIXME: kill this +-1 when we move to 0-based.
        points.append(ms.slice.start_pos-1)
        points.append(ms.slice.end_pos)
    points.append(amplicon.slice.end_pos)
    if points != sorted(points):
        raise IntegrityError("Amplicon {} has interlocking MSs or MSs "
            "outside its boundaries".format(amplicon.id))
    # FIXME: kill this +-1 when we move to 0-based.
    fmt = "{}".join([
        amplicon.slice.chromosome.getdna(points[2*i]+1, points[2*i+1])
            if points[2*i] < points[2*i+1] else ""
        for i in range(len(points)//2)
    ])
    full_fmt = "{pad}{left}{slice}{right}{pad}".format(
        pad="N"*padding,
        left=amplicon.left_margin,
        slice=fmt,
        right=amplicon.right_margin
    )
    prefix = "{}".format(amplicon.id)
    return _get_mss_variations_seqrecords(mss, full_fmt, prefix)


def _get_panel_variations_seqrecords(amplicon_collection, padding, mss_version):
    for amp in amplicon_collection.amplicons.all():
        yield from _get_amplicon_variations_seqrecords(
            amp, padding, mss_version
        )


def _build_ms_variations(amplicon_collection, padding, mss_version):
    with unique_file_cm("fa") as fasta:
        SeqIO.write(
            _get_panel_variations_seqrecords(
                amplicon_collection, padding, mss_version
            ), fasta, "fasta")
        return fasta


def get_full_ms_variations(amplicon_collection, padding, mss_version):
    def inner(raise_or_create_with_defaults):
        with unique_dir_cm() as index_dir:
            bowtie_index = BowtieIndexMixin(index_dump_dir=index_dir)
            with unlink(_build_ms_variations(amplicon_collection, padding, mss_version)) as fasta:
                bowtie2build(fasta, bowtie_index.index_files_prefix)
            return raise_or_create_with_defaults(
                index_dump_dir=index_dir,
            )
    return get_get_or_create(inner, FullMSVariations,
        amplicon_collection=amplicon_collection,
        padding=padding,
        microsatellites_version=mss_version,
    )


def split_merged_reads(merged_reads, reads_chunk_size=10**5, included_reads='M'):
    num_reads = merged_reads.num_reads(included_reads)
    if merged_reads.fullmsvmergedreadspart_set.count() == math.ceil(num_reads/reads_chunk_size):
        yield from merged_reads.fullmsvmergedreadspart_set.filter(rows=reads_chunk_size)
    else:
        reads_chunk_gen = grouper(
            reads_chunk_size,
            merged_reads.included_reads_generator(included_reads)
        )
        try:
            peek = next(reads_chunk_gen)
        except StopIteration:
            peek = ([])  # No reads, continue on with empty fastq
        for i, reads_chunk in enumerate(itertools.chain([peek], reads_chunk_gen)):
            def inner(raise_or_create_with_defaults):
                with unique_file_cm("fastq") as fastq_part:
                    SeqIO.write(reads_chunk, fastq_part, "fastq")
                    return raise_or_create_with_defaults(
                        fastq_part=fastq_part,
                        merged_reads=merged_reads,
                        start_row=i * reads_chunk_size,
                        rows=reads_chunk_size,
                    )
            yield get_get_or_create(inner, FullMSVMergedReadsPart,
                                    merged_reads=merged_reads,
                                    start_row=i*reads_chunk_size,
                                    rows=reads_chunk_size,
                                    )
        else:
            merged_reads.separation_finished = True
            merged_reads.save()


def split_merged_reads_as_list(merged_reads, reads_chunk_size=10**5, included_reads='M'):
    return list(split_merged_reads(merged_reads, reads_chunk_size, included_reads=included_reads))


def align_reads_to_ms_variations_original(merged_reads, padding, mss_version):
    amplicon_collection = merged_reads.sample_reads.library.subclass.panel.amplicon_collection
    msv = get_full_ms_variations(amplicon_collection, padding, mss_version)
    def inner(raise_or_create_with_defaults):
        with unique_file_cm("bam") as sorted_assignment_bam:
            bowtie_to_sorted_bam = bowtie2_with_defaults2[
                '-x', msv.index_files_prefix,
                '-U', merged_reads.assembled_fastq,  # TODO: reconsider 'F'/'M' reads collections
            ] | samtools_view[
                '-bS',
                '-'
            ] | samtools_sort[
                '-o',
                sorted_assignment_bam
            ]
            bowtie_to_sorted_bam & plumbum.FG
            return raise_or_create_with_defaults(
                sorted_assignment_bam=sorted_assignment_bam,
                merged_reads=merged_reads,
                ms_variations=msv,
            )
    return get_get_or_create(inner, FullMSVAssignment,
        merged_reads=merged_reads,
        ms_variations=msv,
    )


def align_reads_to_ms_variations(merged_reads, padding, mss_version, chunk_size=15000):
    total_amplicon_collection = merged_reads.sample_reads.library.subclass.panel.amplicon_collection
    all_amplicons = total_amplicon_collection.amplicons.order_by('id')
    amplicons_splitted = grouper(chunk_size, all_amplicons)  # split the amplicons to create smaller amplicon collections
    for amplicon_subgroup in amplicons_splitted:
        amplicon_collection = AmpliconCollection.custom_get_or_create(amplicons=amplicon_subgroup)
        msv = get_full_ms_variations(amplicon_collection, padding, mss_version)
        def inner(raise_or_create_with_defaults):
            with unique_file_cm("bam") as sorted_assignment_bam:
                bowtie_to_sorted_bam = bowtie2_with_defaults2[
                    '-x', msv.index_files_prefix,
                    '-U', merged_reads.assembled_fastq,  # TODO: reconsider 'F'/'M' reads collections
                ] | samtools_view[
                    '-bS',
                    '-'
                ] | samtools_sort[
                    '-o',
                    sorted_assignment_bam
                ]
                bowtie_to_sorted_bam & plumbum.FG
                return raise_or_create_with_defaults(
                    sorted_assignment_bam=sorted_assignment_bam,
                    merged_reads=merged_reads,
                    ms_variations=msv,
                )
        yield get_get_or_create(inner, FullMSVAssignment,
            merged_reads=merged_reads,
            ms_variations=msv,
        )


def align_reads_to_ms_variations_as_list(merged_reads, padding, mss_version, chunk_size=15000):
    return list(align_reads_to_ms_variations(merged_reads, padding, mss_version, chunk_size))


def align_reads_to_ms_variations_part(merged_reads_part, padding, mss_version, chunk_size=15000):
    assert isinstance(merged_reads_part, FullMSVMergedReadsPart)
    total_amplicon_collection = merged_reads_part.merged_reads.sample_reads.library.subclass.panel.amplicon_collection
    all_amplicons = total_amplicon_collection.amplicons.order_by('id')
    amplicons_splitted = grouper(chunk_size,
                                 all_amplicons)  # split the amplicons to create smaller amplicon collections
    for amplicon_subgroup in amplicons_splitted:
        amplicon_collection = AmpliconCollection.custom_get_or_create(amplicons=amplicon_subgroup)
        msv = get_full_ms_variations(amplicon_collection, padding, mss_version)
        def inner(raise_or_create_with_defaults):
            with unique_file_cm("bam") as assignment_bam:
                rstring = '@RG\tID:test_sample\tPL:illumina\tPU:1\tLB:test_sample\tSM:test_sample'
                # fasta_path = '/net/192.168.107.11/export/dc_temp/PROD_STORAGE/52/bf/b4/73-1278-4456-bf1d-8bc12552f75a.fa'  # OM6
                fasta_path = '/net/192.168.107.11/export/dc_temp/PROD_STORAGE/4d/c5/b4/a7-66fa-4a96-892d-94c5c4679973.fa'  # OM9
                bwa_mem_to_bam = bwa_mem_paramed[
                    '-R',
                    rstring,
                    fasta_path,
                    merged_reads_part.fastq_part
                ] | samtools_view[
                    '-bS',
                    '-'
                ] > assignment_bam
                # bowtie_to_bam = bowtie2_with_defaults2[
                #     '-x', msv.index_files_prefix,
                #     '-U', merged_reads_part.fastq_part,  # TODO: reconsider 'F'/'M' reads collections
                # ] | samtools_view[
                #     '-bS',
                #     '-'
                # ] > assignment_bam
                bwa_mem_to_bam & plumbum.FG
                return raise_or_create_with_defaults(
                    assignment_bam=assignment_bam,
                    merged_reads_part=merged_reads_part,
                    ms_variations=msv,
                )
        yield get_get_or_create(inner, FullMSVAssignmentPart,
            merged_reads_part=merged_reads_part,
            ms_variations=msv,
        )


def align_reads_to_ms_variations_part_as_list(merged_reads_part, padding, mss_version, chunk_size=15000):
    return list(align_reads_to_ms_variations_part(merged_reads_part, padding, mss_version, chunk_size=chunk_size))


def merge_fmsva_parts(fmsva_parts, reads_chunk_size=10**5, included_reads='M'):
    by_msv = dict()
    for fmsva_part in [f for fs in fmsva_parts for f in fs]:
        by_msv.setdefault(fmsva_part.ms_variations, []).append(fmsva_part)
    for msv, fmsva_parts_by_msv in by_msv.items():
        for fmsva_part in fmsva_parts_by_msv:
            assert isinstance(fmsva_part, FullMSVAssignmentPart)
        merged_reads_set = set(fmsvap.merged_reads_part.merged_reads for fmsvap in fmsva_parts_by_msv)
        assert len(merged_reads_set) == 1
        merged_reads = merged_reads_set.pop()
        ms_variations_set = set(fmsvap.ms_variations for fmsvap in fmsva_parts_by_msv)
        assert len(ms_variations_set) == 1
        msv = ms_variations_set.pop()
        assert set(
            (merged_reads.id, i * reads_chunk_size, reads_chunk_size) for i, reads_chunk in enumerate(grouper(
                reads_chunk_size,
                merged_reads.included_reads_generator(included_reads)
            ))) == set(
            (mrp.merged_reads_id, mrp.start_row, mrp.rows) for mrp in merged_reads.fullmsvmergedreadspart_set.filter(
                rows=reads_chunk_size,
            )
        )
        partial_bams = [fmsvap.assignment_bam for fmsvap in fmsva_parts_by_msv]

        def inner(raise_or_create_with_defaults):
            resource.setrlimit(resource.RLIMIT_OFILE, (4096, 4096))
            with unique_file_cm("bam") as sorted_assignment_bam:
                with unique_file_cm("bam") as temp_merged_bam:
                    if len(partial_bams) == 1:
                        samtools_sort(
                            '-o',
                            sorted_assignment_bam,
                            partial_bams[0]
                        )
                    else:
                        with unique_file_cm("csv") as bams_list_path:
                            with open(bams_list_path, 'w') as f:
                                f.writelines(('\n').join(partial_bams))
                            samtools_merge(
                                '-b',
                                bams_list_path,
                                temp_merged_bam,
                            )
                            samtools_sort(
                                '-o',
                                sorted_assignment_bam,
                                temp_merged_bam
                            )
                            os.unlink(temp_merged_bam)
                            os.unlink(bams_list_path)
                    connection.close()
                return raise_or_create_with_defaults(
                    sorted_assignment_bam=sorted_assignment_bam,
                    merged_reads=merged_reads,
                    ms_variations=msv,
                )
        yield get_get_or_create(inner, FullMSVAssignment,
                                merged_reads=merged_reads,
                                ms_variations=msv,
                                )


def merge_fmsva_parts_as_list(fmsva_parts, reads_chunk_size=10**5, included_reads='M'):
    return list(merge_fmsva_parts(fmsva_parts, reads_chunk_size, included_reads))


def index_fastqs(fmsva):
    reads1 = SeqIO.index(fmsva.merged_reads.sample_reads.fastq1, "fastq")
    reads2 = SeqIO.index(fmsva.merged_reads.sample_reads.fastq2, "fastq")
    readsm = SeqIO.index(fmsva.merged_reads.assembled_fastq, "fastq")
    return reads1, reads2, readsm


def stream_group_alignemnts(fmsva):
    histogram_reads = {}
    # genotyped_reads = set()
    cur_amp_id = None
    for read_id, ms_genotypes_name in fmsva.read_bam():
        # assert read_id not in genotyped_reads  # TODO: consider removal
        prefix, ms_genotype_strings = split_ms_genotypes_name(ms_genotypes_name)
        amp_id = int(prefix)
        if amp_id != cur_amp_id:
            if cur_amp_id is not None:
                yield cur_amp_id, histogram_reads
                histogram_reads = {}
            cur_amp_id = amp_id
        histogram_reads.setdefault(ms_genotype_strings, list()).append(read_id)
        # genotyped_reads.add(read_id)
    else:
        if cur_amp_id is not None:
            yield cur_amp_id, histogram_reads


def separate_reads_by_genotypes(fmsva):
    if type(fmsva) == list:
        assert len(fmsva) == 1
        fmsva = fmsva[0]
    if type(fmsva) != FullMSVAssignment:
        fmsva = next(fmsva)
    if fmsva.separation_finished:
        fmsva_hists = FullMSVHistogram.objects.filter(
                assignment=fmsva,
        )
        for her in HistogramEntryReads.objects.filter(
                    histogram__in=fmsva_hists,
        ):
            yield her
    else:
        if fmsva.merged_reads.sample_reads.write_her_files:
            reads1, reads2, readsm = index_fastqs(fmsva)
        none_snp_genotype = SNPHistogramGenotype.objects.get(snp=None)
        snp_histogram_genotypes, c = SNPHistogramGenotypeSet.objects.get_or_create(
            **{fn: none_snp_genotype for fn in SNPHistogramGenotypeSet.genotype_field_names()})
        group_alignments_generator = stream_group_alignemnts(fmsva)
        try:
            peek = next(group_alignments_generator)
        except StopIteration:
            raise  # Alignments file contains no valid alignments
        for amp_id, histogram_reads in itertools.chain([peek], group_alignments_generator):
            histogram, created = FullMSVHistogram.objects.get_or_create(
                amplicon_id=amp_id,
                amplicon_copy_id=amp_id,
                assignment=fmsva,
                defaults=dict(
                    sample_reads_id=fmsva.merged_reads.sample_reads_id,
                    microsatellites_version=fmsva.ms_variations.microsatellites_version,
                )
            )
            for msg, read_ids in histogram_reads.items():
                try:
                    ms_histogram_genotypes = MicrosatelliteHistogramGenotypeSet.get_for_msgs(
                        get_ms_genotypes_from_strings_tuple(msg)
                    )
                except Microsatellite.DoesNotExist:
                    continue  # This happens when the database has changed but the indexed panel has not

                def inner(raise_or_create_with_defaults):
                    if histogram.sample_reads.write_her_files:
                        with _extract_reads_by_id(readsm, read_ids) as genotypes_readsm_fastq_name, \
                                _extract_reads_by_id(reads1, read_ids) as genotypes_reads1_fastq_name, \
                                _extract_reads_by_id(reads2, read_ids) as genotypes_reads2_fastq_name:
                            return raise_or_create_with_defaults(  # *
                                num_reads=len(read_ids),
                                fastq1=genotypes_reads1_fastq_name,
                                fastq2=genotypes_reads2_fastq_name,
                                fastqm=genotypes_readsm_fastq_name,
                            )
                    else:
                        return raise_or_create_with_defaults(  # *
                            num_reads=len(read_ids),
                            fastq1='N/A',
                            fastq2='N/A',
                            fastqm='N/A',
                        )
                yield get_get_or_create(inner, HistogramEntryReads,
                                        histogram=histogram,
                                        microsatellite_genotypes=ms_histogram_genotypes,
                                        snp_genotypes=snp_histogram_genotypes,
                                        )
        else:  # when the loop terminates through exhaustion of the list
            yield get_get_or_create(inner, HistogramEntryReads,
                                    histogram=histogram,
                                    microsatellite_genotypes=ms_histogram_genotypes,
                                    snp_genotypes=snp_histogram_genotypes,
                                    )
            fmsva.separation_finished = True
            fmsva.save()


def seek_histogram(hist, verbose=False):
    fmsva = hist.subclass.assignment
    if verbose:
        print('indexing fastqs')
    reads1, reads2, readsm = index_fastqs(fmsva)
    if verbose:
        print('seeking')
    for amp_id, histogram_reads in stream_group_alignemnts(fmsva):
        if amp_id != hist.amplicon_id:
            continue
        for msg, read_ids in histogram_reads.items():
            ms_histogram_genotypes = MicrosatelliteHistogramGenotypeSet.get_for_msgs(
                get_ms_genotypes_from_strings_tuple(msg)
            )
            yield ms_histogram_genotypes, ({'M': readsm[read_id], 'R1': reads1[read_id], 'R2': reads2[read_id]} for
                                           read_id in read_ids)
