# Ahrom options data

This project discovers Ahrom ETF calls and puts from TSETMC and collects available daily
option history from OptionBaaz. TSETMC `InsCode` is passed directly as OptionBaaz `symbolId`.
Raw responses are immutable, content addressed JSON files under `data/raw` and are excluded
from Git. Derived tables are under `data/processed`.

Use the Python environment described in the workspace README. Set
`OPTIONBAAZ_ACCESS_TOKEN` in the process environment before collection. The collector
does not read token files. From `E:\Work`:

```powershell
..\Finenv\Scripts\python.exe options\scripts\run_pipeline.py discover
..\Finenv\Scripts\python.exe options\scripts\run_pipeline.py availability
..\Finenv\Scripts\python.exe options\scripts\run_pipeline.py collect
..\Finenv\Scripts\python.exe options\scripts\run_pipeline.py build
..\Finenv\Scripts\python.exe options\scripts\run_pipeline.py verify
```

`collect` skips previously archived valid responses. `--refresh` captures a new immutable
version. `--limit N` permits a small trial. Retry, timeout, and inter-request delay are
built in. A failed contract does not stop the run. Period `1y` is used because live probes
on 2026-09-20 found only `3m`, `6m`, and `1y` accepted and `1y` returned the most rows.

Main outputs:

- `data/processed/ahrom_option_contracts.csv`
- `data/processed/ahrom_options_history.csv`
- `data/processed/quality_report.json`
- `data/processed/validation_errors.csv`
- `data/processed/discovery_audit.json` and `download_audit.json`
- `data/processed/period_probe.json` with the live parameter probe

Parquet is written when `pyarrow` is installed. The initial run found 996 contracts
and produced 8,903 historical rows; see [workflow](docs/WORKFLOW.md) and
[status](docs/STATUS.md) for coverage and limitations.
