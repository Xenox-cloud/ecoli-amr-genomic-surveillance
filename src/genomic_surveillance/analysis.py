"""Database queries and descriptive AMR surveillance outputs."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def build_summary_tables(
    connection: sqlite3.Connection,
) -> dict[str, pd.DataFrame]:
    isolate_summary = pd.read_sql_query(
        """
        SELECT
            i.accession,
            i.organism,
            i.collection_date,
            i.country,
            i.source,
            q.sequence_count,
            q.total_length,
            q.gc_percent,
            q.n50,
            q.ambiguous_fraction,
            COUNT(
                DISTINCT CASE
                    WHEN a.element_type = 'AMR'
                    THEN a.gene_symbol
                END
            ) AS unique_amr_genes,
            COUNT(
                DISTINCT CASE
                    WHEN a.element_type = 'AMR'
                    THEN NULLIF(a.drug_class, '')
                END
            ) AS represented_drug_classes
        FROM isolates AS i
        LEFT JOIN fasta_quality AS q
            ON q.accession = i.accession
        LEFT JOIN amr_hits AS a
            ON a.accession = i.accession
        GROUP BY i.accession
        ORDER BY i.accession
        """,
        connection,
    )

    gene_frequency = pd.read_sql_query(
        """
        SELECT
            gene_symbol,
            COUNT(DISTINCT accession) AS isolate_count
        FROM amr_hits
        WHERE element_type = 'AMR'
        GROUP BY gene_symbol
        ORDER BY isolate_count DESC, gene_symbol
        """,
        connection,
    )

    drug_class_frequency = pd.read_sql_query(
        """
        SELECT
            drug_class,
            COUNT(DISTINCT accession) AS isolate_count
        FROM amr_hits
        WHERE
            element_type = 'AMR'
            AND drug_class <> ''
        GROUP BY drug_class
        ORDER BY isolate_count DESC, drug_class
        """,
        connection,
    )

    return {
        "isolate_amr_summary": isolate_summary,
        "gene_frequency": gene_frequency,
        "drug_class_frequency": drug_class_frequency,
    }


def save_tables(tables: dict[str, pd.DataFrame], directory: str | Path) -> None:
    table_directory = Path(directory)
    table_directory.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(table_directory / f"{name}.csv", index=False)


def _save_barplot(
    frame: pd.DataFrame,
    category: str,
    value: str,
    title: str,
    output_path: Path,
    limit: int = 15,
) -> None:
    if frame.empty:
        return

    plot_frame = frame.head(limit).sort_values(value)
    height = max(4.5, len(plot_frame) * 0.38)
    figure, axis = plt.subplots(figsize=(9, height))
    sns.barplot(data=plot_frame, x=value, y=category, ax=axis, color="#277da1")
    axis.set_title(title)
    axis.set_xlabel("Number of isolates")
    axis.set_ylabel("")
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def save_figures(tables: dict[str, pd.DataFrame], directory: str | Path) -> None:
    figure_directory = Path(directory)
    figure_directory.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    _save_barplot(
        tables["gene_frequency"],
        "gene_symbol",
        "isolate_count",
        "Most frequently detected AMR genes",
        figure_directory / "top_amr_genes.png",
    )
    _save_barplot(
        tables["drug_class_frequency"],
        "drug_class",
        "isolate_count",
        "Drug classes represented by detected AMR elements",
        figure_directory / "drug_class_frequency.png",
    )

