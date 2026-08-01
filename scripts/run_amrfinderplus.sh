#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <ncbi-data-directory> <output-directory>" >&2
  exit 2
fi

input_directory="$1"
output_directory="$2"
mkdir -p "$output_directory"

if ! command -v amrfinder >/dev/null 2>&1; then
  echo "amrfinder is not installed or is not on PATH." >&2
  exit 1
fi

find "$input_directory" -type f -name "*_genomic.fna" -print0 |
while IFS= read -r -d '' genome_path; do
  accession="$(basename "$(dirname "$genome_path")")"
  output_path="$output_directory/${accession}_amrfinder.tsv"
  echo "Processing $accession"
  amrfinder \
    --nucleotide "$genome_path" \
    --organism Escherichia \
    --plus \
    --output "$output_path"
done

