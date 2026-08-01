# Data dictionary

## `isolates`

| Field | Meaning |
|---|---|
| `accession` | Public assembly or isolate accession |
| `organism` | Scientific organism name |
| `collection_date` | Collection date as supplied by the public source |
| `country` | Reported collection country |
| `source` | Reported sample or isolation source |

The metadata loader accepts either these normalized project headers or the
corresponding headers produced by NCBI `dataformat`.

## `fasta_quality`

| Field | Meaning |
|---|---|
| `sequence_count` | Number of FASTA records/contigs |
| `total_length` | Sum of sequence lengths |
| `minimum_length` | Shortest record |
| `maximum_length` | Longest record |
| `mean_length` | Mean record length |
| `gc_percent` | Percentage of all bases that are G or C |
| `n50` | Contig length where cumulative assembly length reaches 50% |
| `ambiguous_bases` | Bases outside A, C, G, and T |
| `ambiguous_fraction` | Ambiguous bases divided by total length |

## `amr_hits`

This table is reserved for normalized AMRFinderPlus results and will be populated
in the next analytical milestone.
