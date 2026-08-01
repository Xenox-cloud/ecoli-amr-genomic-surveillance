"""Create the project database and load one FASTA quality record."""

from __future__ import annotations

import argparse

from genomic_surveillance.database import (
    connect_database,
    initialize_schema,
    upsert_fasta_quality,
    upsert_isolates,
)
from genomic_surveillance.fasta_qc import summarize_fasta
from genomic_surveillance.metadata import load_metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--fasta", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument(
        "--accession",
        help="Accession associated with the FASTA; defaults to the first metadata row.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = load_metadata(args.metadata)
    accession = args.accession or metadata.iloc[0]["accession"]

    if accession not in set(metadata["accession"]):
        raise ValueError(f"Accession {accession!r} is absent from metadata")

    quality = summarize_fasta(args.fasta)
    with connect_database(args.database) as connection:
        initialize_schema(connection)
        upsert_isolates(connection, metadata)
        upsert_fasta_quality(connection, accession, quality)

    print(f"Loaded {len(metadata)} isolate(s)")
    print(f"Stored FASTA QC for {accession}: {quality.to_dict()}")


if __name__ == "__main__":
    main()

