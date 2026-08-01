param(
    [ValidateRange(1, 100)]
    [int]$GenomeLimit = 20
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RawDirectory = Join-Path $ProjectRoot "data\raw"
$ArchivePath = Join-Path $RawDirectory "ncbi_ecoli.zip"
$MetadataPath = Join-Path $RawDirectory "metadata.tsv"

New-Item -ItemType Directory -Force -Path $RawDirectory | Out-Null

if (-not (Get-Command datasets -ErrorAction SilentlyContinue)) {
    throw "NCBI Datasets CLI is not installed or is not available on PATH."
}

Write-Host "Downloading up to $GenomeLimit reference/representative E. coli genomes..."

datasets download genome taxon "Escherichia coli" `
    --reference `
    --assembly-level complete `
    --include genome,gff3,protein,gbff,seq-report `
    --limit $GenomeLimit `
    --filename $ArchivePath

Expand-Archive -Path $ArchivePath -DestinationPath $RawDirectory -Force

if (-not (Get-Command dataformat -ErrorAction SilentlyContinue)) {
    throw "NCBI dataformat CLI is not installed or is not available on PATH."
}

dataformat tsv genome `
    --package $ArchivePath `
    --fields accession,organism-name,assminfo-biosource-collection-date,assminfo-biosource-geo-loc-name,assminfo-biosource-isolation-source |
    Set-Content -Encoding utf8 $MetadataPath

Write-Host "Dataset extracted to $RawDirectory"
Write-Host "Metadata written to $MetadataPath"
