"""Validation and normalization of isolate metadata."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "accession",
    "organism",
    "collection_date",
    "country",
    "source",
}

NCBI_COLUMN_ALIASES = {
    "Assembly Accession": "accession",
    "Organism Name": "organism",
    "Assembly BioSample Collection date": "collection_date",
    "Assembly BioSample Geographic location": "country",
    "Assembly BioSample Isolation source": "source",
}


def load_metadata(path: str | Path) -> pd.DataFrame:
    """Load TSV metadata, validate its schema, and normalize text fields."""
    metadata_path = Path(path)
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    frame = pd.read_csv(metadata_path, sep="\t", dtype=str).fillna("")
    applicable_aliases = {
        source: destination
        for source, destination in NCBI_COLUMN_ALIASES.items()
        if source in frame.columns and destination not in frame.columns
    }
    frame = frame.rename(columns=applicable_aliases)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing metadata columns: {sorted(missing)}")

    frame = frame.copy()
    missing_tokens = {
        "missing",
        "not collected",
        "not provided",
        "not applicable",
        "n/a",
        "na",
        "unknown",
    }

    for column in frame.columns:
        frame[column] = frame[column].str.strip()
        frame[column] = frame[column].mask(
            frame[column].str.lower().isin(missing_tokens),
            "",
        )

    if frame["accession"].eq("").any():
        raise ValueError("Metadata contains an empty accession")
    if frame["accession"].duplicated().any():
        duplicates = sorted(frame.loc[frame["accession"].duplicated(), "accession"])
        raise ValueError(f"Duplicate accessions found: {duplicates}")

    frame["collection_date_parsed"] = pd.to_datetime(
        frame["collection_date"].replace("", pd.NA),
        format="mixed",
        errors="coerce",
    )
    return frame
