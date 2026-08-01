"""FASTA parsing and transparent sequence-quality feature extraction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from Bio import SeqIO


@dataclass(frozen=True)
class FastaQuality:
    """Summary statistics for one FASTA file."""

    file_name: str
    sequence_count: int
    total_length: int
    minimum_length: int
    maximum_length: int
    mean_length: float
    gc_percent: float
    n50: int
    ambiguous_bases: int
    ambiguous_fraction: float

    def to_dict(self) -> dict[str, int | float | str]:
        return asdict(self)


def calculate_n50(lengths: list[int]) -> int:
    """Return the contig length at which cumulative length reaches 50%."""
    if not lengths:
        return 0

    ordered = sorted(lengths, reverse=True)
    halfway = sum(ordered) / 2
    cumulative = 0

    for length in ordered:
        cumulative += length
        if cumulative >= halfway:
            return length

    return 0


def summarize_fasta(path: str | Path) -> FastaQuality:
    """Parse a nucleotide FASTA file and calculate basic QC features."""
    fasta_path = Path(path)
    if not fasta_path.exists():
        raise FileNotFoundError(f"FASTA file not found: {fasta_path}")

    sequences = [str(record.seq).upper() for record in SeqIO.parse(fasta_path, "fasta")]
    if not sequences:
        raise ValueError(f"No FASTA records found in: {fasta_path}")

    lengths = [len(sequence) for sequence in sequences]
    total_length = sum(lengths)
    gc_bases = sum(sequence.count("G") + sequence.count("C") for sequence in sequences)
    canonical_bases = sum(
        sequence.count(base) for sequence in sequences for base in "ACGT"
    )
    ambiguous_bases = total_length - canonical_bases

    return FastaQuality(
        file_name=fasta_path.name,
        sequence_count=len(sequences),
        total_length=total_length,
        minimum_length=min(lengths),
        maximum_length=max(lengths),
        mean_length=round(total_length / len(lengths), 2),
        gc_percent=round((gc_bases / total_length) * 100, 4),
        n50=calculate_n50(lengths),
        ambiguous_bases=ambiguous_bases,
        ambiguous_fraction=round(ambiguous_bases / total_length, 6),
    )

