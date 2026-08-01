from genomic_surveillance.amr_parser import load_amrfinder_results
from genomic_surveillance.database import (
    connect_database,
    initialize_schema,
    replace_amr_hits,
    upsert_fasta_quality,
    upsert_isolates,
)
from genomic_surveillance.fasta_qc import summarize_fasta
from genomic_surveillance.metadata import load_metadata


def test_database_round_trip(tmp_path) -> None:
    metadata = load_metadata("tests/fixtures/metadata.tsv")
    quality = summarize_fasta("tests/fixtures/sample.fna")
    hits = load_amrfinder_results(
        "tests/fixtures/amrfinder/TEST_001_amrfinder.tsv"
    )

    with connect_database(tmp_path / "test.db") as connection:
        initialize_schema(connection)
        upsert_isolates(connection, metadata)
        upsert_fasta_quality(connection, "TEST_001", quality)
        replace_amr_hits(connection, "TEST_001", hits)

        isolate_count = connection.execute(
            "SELECT COUNT(*) FROM isolates"
        ).fetchone()[0]
        stored_n50 = connection.execute(
            "SELECT n50 FROM fasta_quality WHERE accession = ?",
            ("TEST_001",),
        ).fetchone()[0]
        hit_count = connection.execute("SELECT COUNT(*) FROM amr_hits").fetchone()[0]

    assert isolate_count == 1
    assert stored_n50 == 18
    assert hit_count == 1
