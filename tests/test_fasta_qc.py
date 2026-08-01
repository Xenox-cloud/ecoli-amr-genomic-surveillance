from genomic_surveillance.fasta_qc import calculate_n50, summarize_fasta


def test_calculate_n50() -> None:
    assert calculate_n50([10, 6, 4]) == 10
    assert calculate_n50([]) == 0


def test_summarize_fasta() -> None:
    quality = summarize_fasta("tests/fixtures/sample.fna")

    assert quality.sequence_count == 2
    assert quality.total_length == 30
    assert quality.minimum_length == 12
    assert quality.maximum_length == 18
    assert quality.n50 == 18
    assert quality.ambiguous_bases == 2
    assert quality.ambiguous_fraction == 0.066667

