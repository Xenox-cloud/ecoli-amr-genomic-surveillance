# Analytical workflow

```mermaid
flowchart TD
    A["NCBI assemblies and metadata"] --> B["Schema and FASTA validation"]
    B --> C["SQLite genomic database"]
    B --> D["AMRFinderPlus"]
    D --> E["AMR summaries and features"]
    C --> E
    B --> F["Homologous sequence selection"]
    F --> G["MAFFT alignment"]
    G --> H["IQ-TREE phylogeny"]
    C --> I["Metadata-aware interpretation"]
    H --> I
    E --> I
```

## Quality principles

1. Keep raw inputs unchanged.
2. Validate accessions and required metadata before analysis.
3. Record missingness rather than silently imputing biological metadata.
4. Split modelling data at isolate level and check class balance.
5. Prevent closely related isolates from leaking across evaluation partitions.
6. Report uncertainty and avoid causal or clinical claims.

