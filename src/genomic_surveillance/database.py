"""SQLite persistence for isolate metadata and FASTA quality results."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from genomic_surveillance.fasta_qc import FastaQuality


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS isolates (
    accession TEXT PRIMARY KEY,
    organism TEXT NOT NULL,
    collection_date TEXT,
    country TEXT,
    source TEXT
);

CREATE TABLE IF NOT EXISTS fasta_quality (
    accession TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    sequence_count INTEGER NOT NULL CHECK (sequence_count > 0),
    total_length INTEGER NOT NULL CHECK (total_length > 0),
    minimum_length INTEGER NOT NULL,
    maximum_length INTEGER NOT NULL,
    mean_length REAL NOT NULL,
    gc_percent REAL NOT NULL CHECK (gc_percent BETWEEN 0 AND 100),
    n50 INTEGER NOT NULL,
    ambiguous_bases INTEGER NOT NULL,
    ambiguous_fraction REAL NOT NULL CHECK (ambiguous_fraction BETWEEN 0 AND 1),
    FOREIGN KEY (accession) REFERENCES isolates(accession) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS amr_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accession TEXT NOT NULL,
    gene_symbol TEXT NOT NULL,
    sequence_name TEXT,
    element_type TEXT,
    drug_class TEXT,
    method TEXT,
    FOREIGN KEY (accession) REFERENCES isolates(accession) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_amr_accession ON amr_hits(accession);
CREATE INDEX IF NOT EXISTS idx_amr_gene ON amr_hits(gene_symbol);
"""


def connect_database(path: str | Path) -> sqlite3.Connection:
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()


def upsert_isolates(connection: sqlite3.Connection, metadata: pd.DataFrame) -> None:
    rows = metadata[
        ["accession", "organism", "collection_date", "country", "source"]
    ].itertuples(index=False, name=None)
    connection.executemany(
        """
        INSERT INTO isolates (
            accession, organism, collection_date, country, source
        ) VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(accession) DO UPDATE SET
            organism = excluded.organism,
            collection_date = excluded.collection_date,
            country = excluded.country,
            source = excluded.source
        """,
        rows,
    )
    connection.commit()


def upsert_fasta_quality(
    connection: sqlite3.Connection,
    accession: str,
    quality: FastaQuality,
) -> None:
    values = quality.to_dict()
    connection.execute(
        """
        INSERT INTO fasta_quality (
            accession, file_name, sequence_count, total_length, minimum_length,
            maximum_length, mean_length, gc_percent, n50, ambiguous_bases,
            ambiguous_fraction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(accession) DO UPDATE SET
            file_name = excluded.file_name,
            sequence_count = excluded.sequence_count,
            total_length = excluded.total_length,
            minimum_length = excluded.minimum_length,
            maximum_length = excluded.maximum_length,
            mean_length = excluded.mean_length,
            gc_percent = excluded.gc_percent,
            n50 = excluded.n50,
            ambiguous_bases = excluded.ambiguous_bases,
            ambiguous_fraction = excluded.ambiguous_fraction
        """,
        (
            accession,
            values["file_name"],
            values["sequence_count"],
            values["total_length"],
            values["minimum_length"],
            values["maximum_length"],
            values["mean_length"],
            values["gc_percent"],
            values["n50"],
            values["ambiguous_bases"],
            values["ambiguous_fraction"],
        ),
    )
    connection.commit()


def replace_amr_hits(
    connection: sqlite3.Connection,
    accession: str,
    hits: pd.DataFrame,
) -> None:
    """Atomically replace all normalized AMR hits for one isolate."""
    required = {
        "gene_symbol",
        "sequence_name",
        "element_type",
        "drug_class",
        "method",
    }
    missing = required.difference(hits.columns)
    if missing:
        raise ValueError(f"Missing normalized AMR columns: {sorted(missing)}")

    with connection:
        connection.execute("DELETE FROM amr_hits WHERE accession = ?", (accession,))
        rows = (
            (
                accession,
                row.gene_symbol,
                row.sequence_name,
                row.element_type,
                row.drug_class,
                row.method,
            )
            for row in hits[
                [
                    "gene_symbol",
                    "sequence_name",
                    "element_type",
                    "drug_class",
                    "method",
                ]
            ].itertuples(index=False)
        )
        connection.executemany(
            """
            INSERT INTO amr_hits (
                accession, gene_symbol, sequence_name, element_type,
                drug_class, method
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
