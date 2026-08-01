"""Run FASTA QC, load AMR results, and generate analytical outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

from genomic_surveillance.amr_parser import load_amrfinder_results
from genomic_surveillance.analysis import build_summary_tables, save_figures, save_tables
from genomic_surveillance.database import (
    connect_database,
    initialize_schema,
    replace_amr_hits,
    upsert_fasta_quality,
    upsert_isolates,
)
from genomic_surveillance.fasta_qc import summarize_fasta
from genomic_surveillance.metadata import load_metadata
from genomic_surveillance.reporting import write_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--genome-directory", required=True)
    parser.add_argument("--amr-directory", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--output-directory", required=True)
    return parser.parse_args()


def locate_genome(genome_directory: Path, accession: str) -> Path:
    candidates = sorted(genome_directory.glob(f"{accession}/**/*_genomic.fna"))
    if not candidates:
        candidates = sorted(genome_directory.glob(f"{accession}.fna"))
    if len(candidates) != 1:
        raise ValueError(
            f"Expected exactly one genome FASTA for {accession}; found {len(candidates)}"
        )
    return candidates[0]


def main() -> None:
    args = parse_args()
    metadata = load_metadata(args.metadata)
    genome_directory = Path(args.genome_directory)
    amr_directory = Path(args.amr_directory)
    output_directory = Path(args.output_directory)

    with connect_database(args.database) as connection:
        initialize_schema(connection)
        upsert_isolates(connection, metadata)

        for accession in metadata["accession"]:
            genome_path = locate_genome(genome_directory, accession)
            quality = summarize_fasta(genome_path)
            upsert_fasta_quality(connection, accession, quality)

            result_path = amr_directory / f"{accession}_amrfinder.tsv"
            hits = load_amrfinder_results(result_path)
            replace_amr_hits(connection, accession, hits)
            amr_count = int(
                hits["element_type"]
                .eq("AMR")
                .sum()
            )

            print(
                f"{accession}: "
                f"{quality.sequence_count} sequence(s), "
                f"{amr_count} AMR element(s), "
                f"{len(hits)} total detected element(s)"
            )

        tables = build_summary_tables(connection)

    save_tables(tables, output_directory / "tables")
    save_figures(tables, output_directory / "figures")
    write_report(tables, output_directory / "reports" / "amr_analysis_report.md")
    print(f"Analysis completed. Outputs: {output_directory.resolve()}")


if __name__ == "__main__":
    main()

