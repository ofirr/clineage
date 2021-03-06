import pytest
from genomes.models import DNASlice, Chromosome, Assembly

@pytest.mark.django_db
def test_assembly(hg19_assembly):
    assert str(hg19_assembly) == "hg19"


@pytest.mark.django_db
def test_chromosome(hg19_chromosome):
    assert str(hg19_chromosome) == "hg19:X"


@pytest.mark.django_db
def test_dnaslice(slice_28727_left):
    assert str(slice_28727_left) == "X:81316094-81316116"


@pytest.mark.skipif(pytest.config.getoption("nomigrations"), reason="No migrations, no view.")
@pytest.mark.django_db
def test_dnaslice_contains(slice_28727_target_a, slice_28727_target_b, slice_28727_amplicon, slice_28727_overlaps_some):
    assert set(slice_28727_amplicon.contains.all()) == set([slice_28727_target_a, slice_28727_target_b])
    assert set(slice_28727_amplicon.contained.all()) == set()
    assert set(slice_28727_target_a.contains.all()) == set()
    assert set(slice_28727_target_a.contained.all()) == set([slice_28727_amplicon])
    assert set(slice_28727_target_b.contains.all()) == set()
    assert set(slice_28727_target_b.contained.all()) == set([slice_28727_amplicon])
    assert set(slice_28727_overlaps_some.contains.all()) == set()
    assert set(slice_28727_overlaps_some.contained.all()) == set()


@pytest.mark.skipif(pytest.config.getoption("nomigrations"), reason="No migrations, no view.")
@pytest.mark.django_db
def test_dnaslice_contains_overlaps_trigger(slice_28734_target_a,hg19_chromosome):

    dnas_to_contain = DNASlice.objects.create(
        chromosome=hg19_chromosome,
        start_pos=54384789,
        end_pos=54384804,
    )

    dnas_to_overlap = DNASlice.objects.create(
        chromosome=hg19_chromosome,
        start_pos=54384789,
        end_pos=54384807,
    )

    assert dnas_to_contain in set(slice_28734_target_a.contains.all())

    assert set(slice_28734_target_a.contains.all()) == set([dnas_to_contain])
    assert dnas_to_overlap in set(slice_28734_target_a.overlaps.all())

    # check that the objects are deleted from the table - fk works
    dnas_to_contain.delete()
    dnas_to_overlap.delete()

    assert set(slice_28734_target_a.contains.all()) == set()
    assert set(slice_28734_target_a.overlaps.all()) == set()


@pytest.mark.skipif(pytest.config.getoption("nomigrations"), reason="No migrations, no view.")
@pytest.mark.django_db
def test_dnaslice_overlaps(slice_28727_target_a, slice_28727_target_b, slice_28727_amplicon, slice_28727_overlaps_some):
    assert set(slice_28727_amplicon.overlaps.all()) == set([slice_28727_target_a, slice_28727_target_b, slice_28727_overlaps_some])
    assert set(slice_28727_target_a.overlaps.all()) == set([slice_28727_amplicon, slice_28727_overlaps_some])
    assert set(slice_28727_target_b.overlaps.all()) == set([slice_28727_amplicon])
    assert set(slice_28727_overlaps_some.overlaps.all()) == set([slice_28727_target_a, slice_28727_amplicon])
