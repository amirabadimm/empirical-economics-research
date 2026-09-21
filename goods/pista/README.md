# Pista

Double-click `refresh_powerbi.cmd` in this project to rebuild the observed weekly-quote comparison and `outputs/power_bi/pista_certificate_physical_comparison.csv` from existing raw inputs.

The refresh invokes `analysis/build_certificate_bubble.py`, a command-line version of the notebook's six-day backward-match calculation. The physical-price unit assumption remains unverified.

Independent Python project for collecting pistachio certificate trades from the
Iran Mercantile Exchange (IME). It covers the continuous `PistaCL` certificate opened on 2026-08-25
(1405/06/03). Earlier, expiring pistachio certificates are a separate historical
market and are not merged into this series.

The first collection has 21 daily records through 2026-09-17, including 16
days with trades.

A separate weekly pistachio price workbook was provided directly by Abtahi
Pistachio after outreach to several companies. It contains 578 Jalali-dated
rows through `1405/06/19` for Khandan and Dahan-Bast prices. This company
series is preserved under `data/raw/physical` and has not yet been validated
as a comparable benchmark for the certificate.

From this directory, with Python 3.11+ and `curl` on `PATH`:

```powershell
python -m pip install -e .
python .\src\pista\collectors\certificate.py
python .\analysis\audit_physical.py
python -m unittest discover -s tests -v
```

The collector writes `data/raw/certificate/pista_certificate_raw.csv` and keeps
complete API responses in `data/raw/certificate/api_snapshots`. Both are local,
untracked data. See [workflow](docs/WORKFLOW.md) and [status](docs/STATUS.md).

The collector uses only the Python standard library and `curl`. It can be copied
or published as its own repository without importing any workspace package.

Project work is organized in `analysis/` for analysis code and `report/` for
written findings. Derived data belongs under `data/interim` or `data/processed`.
The physical audit writes `data/interim/pistachio_physical_cleaned.csv` and
`data/interim/pistachio_physical_audit.csv`. Its [report](report/PHYSICAL_DATA_AUDIT.md)
records unresolved cases. The cleaned CSV retains flagged values, so review
`quality_flag` before calculating returns or other statistics.

The [certificate analysis notebook](analysis/pista_certificate_analysis.ipynb)
plots an indicative premium to the latest Dahan-Bast weekly price for 16
positive-volume certificate days. It uses a maximum six-day backward match and
an explicit, unconfirmed assumption that Abtahi prices are toman per kilogram.
Its table is written to `data/processed/bubble/pista_certificate_bubble.csv`.

## Resume summary

Built a standalone, reproducible data collection pipeline for IME pistachio
warehouse certificates. It pages the official API, validates contract identity
and trade arithmetic, archives complete source responses, and atomically updates
an incremental daily CSV. The initial dataset covers 21 observations, including
16 trading days. Also sourced a separate 578-row weekly price series through
direct company outreach; documented its provenance and comparability limits.
The current scope is source collection and assessment, not a price model.
# Historical bubble distribution

`data/processed/bubble/pistachio_bubble_distribution.csv` is the standardized Power BI table for the 16
observed certificate-versus-physical comparisons. It contains signed bubble percentages,
empirical `F(x)`, and `P(|Bubble| >= |x|)`. The figure is written to
`data/processed/analysis`.
