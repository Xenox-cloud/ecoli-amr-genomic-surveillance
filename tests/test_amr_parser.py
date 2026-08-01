from genomic_surveillance.amr_parser import (
    accession_from_result_path,
    load_amrfinder_results,
)


def test_load_amrfinder_results() -> None:
    hits = load_amrfinder_results(
        "tests/fixtures/amrfinder/TEST_001_amrfinder.tsv"
    )

    assert len(hits) == 1
    assert hits.iloc[0]["gene_symbol"] == "blaTEST"
    assert hits.iloc[0]["drug_class"] == "BETA-LACTAM"


def test_accession_from_result_path() -> None:
    assert accession_from_result_path("TEST_001_amrfinder.tsv") == "TEST_001"

