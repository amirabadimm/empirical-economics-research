# Data Availability

## Summary

This repository versions research code, tests, methodological documentation, report sources,
and selected reproducible figures. It does not redistribute the complete raw market datasets
or source-response archives used in the local research environment.

## Why raw data are not committed

The local workspace contains official exchange responses, vendor-derived international market
tables, FX history, and immutable source snapshots. Public availability of a webpage or endpoint
does not necessarily grant republication rights for a complete historical dataset. Excluding raw
data also prevents Git history from accumulating frequently refreshed bulk files and preserves a
clear separation between third-party evidence and original research code.

The MIT licence in this repository applies only to original code and documentation. It does not
license IME, LME, Westmetall, TGJU, or other third-party data.

## Local data layout

```text
<project>/data/raw/physical/       Canonical physical records and snapshots
<project>/data/raw/certificate/    Canonical certificate records and snapshots
<project>/data/interim/            Temporary derived stages
<project>/data/processed/physical/ Physical benchmarks and diagnostics
<project>/data/processed/certificate/ Certificate-only derivatives
<project>/data/processed/bubble/   Bubble and model outputs
<project>/data/processed/analysis/ Other analytical tables
```

These directories are excluded from Git except for placeholder files.

## Reconstruction

Project READMEs list collector and processing commands. A reconstruction requires lawful access
to the documented sources, a Python environment built from `pyproject.toml`, execution of the
collectors, and then execution of processing scripts in the stated order. Collectors preserve
source URLs and retrieval timestamps and validate schema, identity, uniqueness, units, and dates.

## Verification without local data

Clean clones can run parser, calendar, scope, atomic-write, and synthetic snapshot tests. Tests
that require unversioned canonical or processed datasets skip explicitly when those files are
absent. Research reports contain observation counts, date coverage, formulas, and limitations for
the stated checkpoints.

## Future dataset releases

If a dataset is cleared for redistribution, it should be released separately with a stable
version, data dictionary, source and licence metadata, checksums, construction script, and a DOI
through an appropriate research repository such as Zenodo, OSF, or an institutional archive.
