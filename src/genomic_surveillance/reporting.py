"""Generate a concise, limitation-aware Markdown analytical report."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def _top_rows(frame: pd.DataFrame, label: str, limit: int = 10) -> str:
    if frame.empty:
        return "No AMR detections were available."
    rows = [
        f"- {row[label]}: {int(row['isolate_count'])} isolate(s)"
        for _, row in frame.head(limit).iterrows()
    ]
    return "\n".join(rows)


def write_report(
    tables: dict[str, pd.DataFrame],
    output_path: str | Path,
) -> None:
    isolates = tables["isolate_amr_summary"]
    genes = tables["gene_frequency"]
    classes = tables["drug_class_frequency"]
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    isolate_count = len(isolates)
    isolates_with_hits = (
        int((isolates["unique_amr_genes"] > 0).sum()) if isolate_count else 0
    )
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    report = f"""# Microbial AMR Genomics Analysis Report

Generated: {generated_at}

## Objective

Describe AMR genes and drug classes detected by NCBI AMRFinderPlus in the
selected public *Escherichia coli* assemblies and connect those results with
basic assembly-quality and isolate metadata.

## Dataset summary

- Isolates loaded: {isolate_count}
- Isolates with one or more detected AMR genes: {isolates_with_hits}
- Distinct detected gene symbols: {len(genes)}
- Represented drug-class labels: {len(classes)}

## Most frequent gene detections

{_top_rows(genes, "gene_symbol")}

## Most frequent drug-class labels

{_top_rows(classes, "drug_class")}

## Interpretation boundaries

- AMRFinderPlus detects genetic determinants using curated references; a
  detected determinant does not by itself prove phenotypic resistance.
- Absence of a reported hit must not be interpreted as susceptibility.
- Public metadata may be incomplete, inconsistent, or affected by sampling
  bias.
- Reference/complete assemblies are convenient for development but are not a
  representative epidemiological sample.
- This educational analysis does not support clinical treatment decisions.

## Reproducibility

The database, summary tables, figures, source-accession metadata, and execution
commands should be retained with the tool and database versions used for the
analysis.
"""
    output.write_text(report, encoding="utf-8")

