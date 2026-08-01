from genomic_surveillance.metadata import load_metadata


def test_load_metadata() -> None:
    metadata = load_metadata("tests/fixtures/metadata.tsv")

    assert list(metadata["accession"]) == ["TEST_001"]
    assert metadata.iloc[0]["country"] == "Bangladesh"
    assert metadata.iloc[0]["collection_date_parsed"].year == 2024

