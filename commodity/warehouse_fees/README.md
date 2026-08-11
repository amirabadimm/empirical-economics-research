# IME warehouse and assessment fees

Reproducible daily panel of storage and assessment tariffs for commodity deposit
certificates listed by the Iran Mercantile Exchange (IME).

## Canonical output

`data/processed/warehouse_fees_daily.csv` is the **only analysis-ready output**.
It contains one unique row per calendar date and commodity. Do not use files in
`data/raw` or `data/interim` directly for analysis.

Current coverage: 21 commodities from 2016-10-29 through the build date. Coverage
starts independently for each commodity at its first recoverable official record.

Important quality fields:

- `exact_effective_date`: an official notice establishes the effective date.
- `first_observed`: the tariff was visible in an archived official page; its true
  effective date may be earlier.
- `current_table`: confirmed in the current IME table.
- `not_recovered`: no reliable historical assessment tariff was recovered; the
  amount is intentionally blank, not zero.

See [docs/WORKFLOW.md](docs/WORKFLOW.md) for lineage and [docs/STATUS.md](docs/STATUS.md)
for current coverage.

## Commands

Run from the workspace root using its Python environment:

```powershell
# Optional network refreshes; each creates an immutable raw snapshot.
.\Finenv\Scripts\python.exe commodity\warehouse_fees\src\warehouse_fees\collect_current.py
.\Finenv\Scripts\python.exe commodity\warehouse_fees\src\warehouse_fees\collect_wayback.py

# Rebuild the single canonical output from documented inputs.
.\Finenv\Scripts\python.exe commodity\warehouse_fees\src\warehouse_fees\build_daily.py

# Validate schema, uniqueness, coverage, and known tariff transitions.
.\Finenv\Scripts\python.exe -m pytest commodity\warehouse_fees\tests -q
```

Primary source: <https://www.ime.co.ir/WarehousesFee.html>. Row-level source URLs
are retained in the canonical output.
