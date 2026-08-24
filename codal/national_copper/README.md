# National Iranian Copper Industries Company — Codal Research

## Research objective

Build an auditable issuer-level dataset from disclosures published through Iran's Codal system
for National Iranian Copper Industries Company (NICICO; Tehran Stock Exchange ticker: `فملی`).
The pipeline covers the parent company's standalone cumulative financial statements, preserves
every original and corrected filing returned by Codal, and derives individual quarterly flows
with explicit audit lineage.

## Current stage

The integrated quarterly output contains 75 valid flows from 80 expected fiscal-year quarters,
covering `1386/03/31` through `1405/03/31`. Eighteen years
have all four quarters. The legacy OldLetters archive recovers 1386 completely. Five quarters
remain unavailable: 1388 Q2-Q3 lack a six-month input, and fiscal 1405 currently has only Q1.

Operating revenue, gross profit, and net profit are validated in every published output row.
Labor schedules appear consistently in the newer disclosure format from 1399 onward, with a 1398
annual comparative available in the 1399 filing. The labor columns currently present in the
quarterly CSV are provisional: later Codal schedules change column layout, and some cumulative
values are not monotonic across filings. They must not be used analytically until the
period-aware parser and reconciliation checks are complete. All monetary fields use the source
unit, million IRR.

The output also retains two explicitly non-wage fields—other production-overhead expense and
other administrative/general/selling expense—because Codal reports `سایر هزینه‌ها` but does not
identify it as other wages.

## Project layout

```text
codal/national_copper/
├── src/national_copper/{collectors,processing,analysis}/
├── data/{raw,interim,processed}/
├── notebooks/
├── tests/
├── logs/
├── outputs/{tables,figures,reports}/
└── docs/{WORKFLOW,STATUS}.md
```

Raw disclosures and attachments will be immutable and local-only. A future collector may refresh
a canonical raw index only through a documented incremental, idempotent, validated, and atomic
process. Derived tables belong in `data/interim` or `data/processed`.

See [docs/WORKFLOW.md](docs/WORKFLOW.md) for the source contract and
[docs/STATUS.md](docs/STATUS.md) for the current research stage.

## Reproduction

From the repository root:

```powershell
python .\codal\national_copper\src\national_copper\collectors\financial_statements.py
python .\codal\national_copper\src\national_copper\collectors\legacy_financial_statements.py
python .\codal\national_copper\src\national_copper\processing\build_quarterly_history.py
python -m pytest .\codal\national_copper\tests -q
```
