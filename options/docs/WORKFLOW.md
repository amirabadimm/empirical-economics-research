# Workflow

Root: E:\Work\options (explicit user exception to commodity/<commodity> layout).

- data/raw/optionbaaz/<hash>: immutable captured source files and manifest.
- data/processed/analysis/<hash>: normalized tables and validation metadata.
- data/processed/analysis/latest.json: pointers to the current local snapshot.
- scripts/import_capture.py: imports completed captures into content-addressed archives.

The importer resolves its project root from its own file location by default.
No collector was run during the move. Source files must never be overwritten.
Data, outputs, logs and caches are excluded from the existing parent Git repository
by this project's .gitignore. Code and documentation remain eligible for version control.
No separate nested Git repository is needed.

Collection remains paused. Upon resumption, validate source coverage and exact field
semantics before a historical backfill; distinguish observed IV/Greeks from calculated
values and record missing data explicitly.

Validation: `python -m pytest options/tests` from E:\Work tests numeric parsing, missing values, and immutable/idempotent imports. CLI JSON output uses ASCII escapes for Windows console compatibility.
