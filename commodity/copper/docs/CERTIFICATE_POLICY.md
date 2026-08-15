# Agent Instructions — Copper Certificate Project

## Scope

This file applies to all jobs in `commodity/copper/`. LME project files
Do not change the parent folder unless the user specifically requests it.
## Collaboration rule

The project should proceed step by step. Do not proceed to the next step without the explicit confirmation of the user.
Research each stage, report results, assumptions and limitations before implementing the next stage
do Approval of a step is not authorization to change the scope or execute subsequent steps.
## Current status

- Steps 2 to 4 are completed for the new certificate.
- Verified source of official public CDC API certificate of Commodity Exchange and Verified Contract Code
  is `CopperCthd`; Details are recorded in `README.md`.
- Step 5 of physical market sampling is complete.
- Stage 6 is complete: physical market incremental collector and full raw history are available.
- Step 7 is complete: physical benchmark, physical ratio to intrinsic price, linear interpolation
  Proportion and certificate bubbles are made.
- Proposed next step: step 8, analytical quality control and timing of the complete chain implementation.
- `WORKFLOW.md` is a consistent reference for reporting and presentation. After each method change, the number of observations,
  Formula or production output, update it with README and this status.
- TSETMC subscription is not required for certificate collector and `InsCode` is not specified.
- The `src/copper/tools/probe_sources.py` reading tool has been built and verified in terms of syntax. execution
  It timed out on 10 August 1405 for all sources in TLS handshake. This situation
  Do not interpret as missing data, missing symbols or needing an API key.
- `src/copper/collectors/certificate.py` wrapper collector is the official and incremental certificate collector and
  Connects both historical codes `CD1COP0001` and `CopperCthd` into a series. Raw CSV and
  Save its JSON snapshots. The second run should only read the refresh interval.
## Data rules

1. Store raw certificate data only in `data/raw/certificate/`.
2. Store physical market raw data only in `data/raw/physical/`.
3. Do not delete, overwrite or implicitly transform raw data; snapshot or source response
   along with the time of receipt and the address of the source.
4. Store the derived data in `data/processed/` only.
5. Prices must be stored with the explicit unit; Especially rial/toman and kg/ton.
6. Keep source date, transaction date, and receipt time in separate columns.
7. Scripts should be incremental, idempotent and have replication control.
8. Failure of download or validation should not destroy the previous healthy dataset.
## Source hierarchy

1. Iran Commodity Exchange;
2. TSETMC, only after proving the coverage of the desired symbol;
3. Third party source only for reconciliation and dispute resolution.
Any discrepancies between sources should be recorded and reported, rather than being singled out without explanation.
## Certificate discovery requirements

Before writing the certificate collector, the following must be confirmed:
- exact symbol name and tool ID;
- presence or absence of valid `InsCode` in TSETMC;
- the first and last date available in each source;
- Definition of price, volume, value and transaction number fields;
- unit of each field;
- Behavior of no-deal days and historical corrections.
## Physical-market requirements

Maintain all raw supply and transaction rows. Filter product, manufacturer, market, type
Contract, delivery date, base price, transaction price and transaction amount before calculation
Check the reasonable price. Only rows truly comparable to the certificate's backing property
Must enter bubble criteria.
### Confirmed physical candidate

- Primary symbol candidate: `NCI-OACCAA-00`
- Goods: `مس کاتد`
- Producer: `ملی صنایع مس ایران`
- Observed contract types: `نقدی` and `نقدی (مچینگ)`
- Preserve but exclude zero-quantity offers from weighted traded price.
- Do not combine `مس کاتد 2` or other producers without explicit equivalence
  evidence and user approval.
- By the user's later explicit decision, the canonical physical CSV must be retained
  only normalized `GoodsName == مس کاتد`, symbols `NCI-CCAA-00` and
  `NCI-OACCAA-00`, and contract types `نقدی` or `نقدی (مچینگ)`. Discard other
  goods groups, producers, symbols, forward, forward-matching, and credit rows
  from that CSV. Retain zero-quantity offers within the selected scope. Keep full
  compressed API snapshots so excluded rows remain recoverable.
- The source reports `Unit=تن`, while `Price` is on the same apparent scale as
  certificate IRR/kg and `TotalPrice=Price*Quantity`. Preserve all raw units and
  do not silently infer or rescale `TotalPrice`.
### Physical collector status
- Script: `src/copper/collectors/physical.py`
- Canonical raw table: `data/raw/physical/copper_cathode_physical_raw.csv`
- Full-response archives: `data/raw/physical/api_snapshots/*.json.gz`
- Search coverage: `1386/01` through the current Jalali month.
- Initial broad collection found 1,993 cathode-related rows. After the user's
  staged filtering decisions, the canonical table contains 1,163 national Iranians
  Copper Industries cash/cash-matching rows; verify current coverage and counts
  after each collector run.
- On the current history, cash and cash-matching daily weighted prices are exactly
  equal on all 362 paired trading days, while matching adds 9 matching-only dates.
  The proposed primary benchmark combines both using quantity weights, while
  retaining contract-type diagnostics for sensitivity analysis.
- `src/copper/processing/build_physical_benchmark.py` implements the approved combined benchmark and
  writes `data/processed/nci_copper_cash_daily.csv`. Its current output is 789
  positive-trade days. Do not treat stage 7 as complete until date matching and
  bubble calculations have been explicitly approved and implemented.
- The processed daily benchmark must expose only one numeric price column,
  `physical_weighted_price`. Keep cash/matching quantity diagnostics, and fail
  validation if their daily weighted prices ever diverge in future source data.
- `src/copper/processing/build_certificate_bubble.py` implements the approved ratio interpolation:
  physical/LME-FX ratios at the currently available 26 exact anchors are linearly interpolated by calendar
  day, multiplied by each day's intrinsic LME-FX price, and compared with the
  VWAP certificate. It writes `data/processed/copper_certificate_bubble.csv`.
  Never extrapolate outside the first/last anchor without new explicit approval.
- `src/copper/processing/build_intrinsic_bubbles.py` writes the two direct comparison datasets:
  `physical_vs_intrinsic_bubble.csv` (789 physical observations) and
  `certificate_vs_intrinsic_bubble.csv` (178 certificate observations). These do
  do not use the interpolated physical benchmark.
- Incremental runs refresh recent complete Jalali months and replace those
  months atomically rather than attempting to infer a source primary key.
## Bubble calculation safeguards

Do not finalize any historical connection methods until user approval. In the future output should
At least `physical_trade_date` and `physical_price_age_days` exist to price
The old physical market should not be implicitly attributed to the date of the certificate.
## Documentation

After confirming and completing each step, check list status in `README.md` and Current section
status Update this file on the same change.