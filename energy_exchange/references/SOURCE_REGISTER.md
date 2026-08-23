# Source Register

Register each original document when it is added. Use one row per file and keep filenames stable.

The initial 66-document corpus is inventoried by stable research ID, original filename, working
subject, analytical role, and reading priority in
[`../docs/DOCUMENT_TAXONOMY.md`](../docs/DOCUMENT_TAXONOMY.md). The complete mapping between the
original filename and normalized current path is stored in
[`DOCUMENT_FILE_MANIFEST.tsv`](DOCUMENT_FILE_MANIFEST.tsv). The taxonomy and file manifest are
intake inventories, while this register is the authoritative provenance record. Do not copy
unverified working subjects into the Title field as if they were title-page metadata.

| ID | Filename | Title | Issuer / author | Publication date | Access date | Source URL or origin | Language | Version | Notes |
|---|---|---|---|---|---|---|---|---|---|

The register is intentionally awaiting source-level verification. Unknown values must remain
explicitly unknown; do not infer issuer, date, version, or URL from a filename.

Use `YYYY-MM-DD` for Gregorian dates. If a date is Solar Hijri, retain it as published and label
the calendar in the Notes field. Never place credentials or restricted access tokens here.
