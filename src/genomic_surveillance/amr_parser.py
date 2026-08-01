"""Validation and normalization of NCBI AMRFinderPlus output."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


COLUMN_CANDIDATES = {
    "gene_symbol": (
        "Element symbol",
        "Gene symbol",
    ),
    "sequence_name": (
        "Element name",
        "Sequence name",
    ),
    "element_type": (
        "Type",
        "Element type",
    ),
    "drug_class": (
        "Class",
    ),
    "method": (
        "Method",
    ),
}


def _resolve_columns(columns: pd.Index) -> dict[str, str]:
    """Map available AMRFinderPlus headers to stable project headers."""
    available = set(columns)
    aliases: dict[str, str] = {}
    missing: list[str] = []

    for normalized_name, candidates in COLUMN_CANDIDATES.items():
        matched_column = next(
            (
                candidate
                for candidate in candidates
                if candidate in available
            ),
            None,
        )

        if matched_column is None:
            missing.append(
                f"{normalized_name}: one of {list(candidates)}"
            )
        else:
            aliases[matched_column] = normalized_name

    if missing:
        raise ValueError(
            "Missing AMRFinderPlus columns: "
            + "; ".join(missing)
        )

    return aliases


def load_amrfinder_results(path: str | Path) -> pd.DataFrame:
    """Load one AMRFinderPlus TSV and normalize its column names."""
    result_path = Path(path)

    if not result_path.exists():
        raise FileNotFoundError(
            f"AMRFinderPlus result not found: {result_path}"
        )

    if result_path.stat().st_size == 0:
        return pd.DataFrame(columns=COLUMN_CANDIDATES)

    frame = pd.read_csv(
        result_path,
        sep="\t",
        dtype=str,
    ).fillna("")

    aliases = _resolve_columns(frame.columns)

    normalized = (
        frame[list(aliases)]
        .rename(columns=aliases)
        .copy()
    )

    for column in normalized.columns:
        normalized[column] = normalized[column].str.strip()

    normalized = normalized.loc[
        normalized["gene_symbol"].ne("")
    ]

    return normalized.drop_duplicates().reset_index(drop=True)


def accession_from_result_path(path: str | Path) -> str:
    """Extract an accession from `<accession>_amrfinder.tsv`."""
    suffix = "_amrfinder.tsv"
    name = Path(path).name

    if not name.endswith(suffix):
        raise ValueError(
            f"Unexpected AMRFinderPlus result filename: {name}"
        )

    return name.removesuffix(suffix)