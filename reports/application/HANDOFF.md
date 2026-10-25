# Project closeout and handoff

## Final closure — 2026-10-25

The owner has ended active work in this repository and preserved it as a closed
research notebook for CV and application use. The portfolio, CV descriptions,
evidence checkpoint, and project inventory are the entry points for readers.
The stages in the inventory below record what was delivered at closure; references
to ongoing maintenance or planned extensions describe prior intentions. Unfinished
work remains unfinished and is not an active commitment of this repository.

The separate [Housing repository](https://github.com/amirabadimm/iran-housing-data)
remains open for future development. Its continuation checkpoint is maintained
there. Closing this notebook does not stop or transfer deployed services, and
does not create a backup of ignored source data, secrets, or local environments.
Those operational boundaries and the data-availability policy remain applicable.

Closure validation on October 25: the root suite passed **86 tests and 233
subtests**; the Pista and two allocation collector suites used by CI passed
**10 tests**. Ruff, changed Python files' 3.11 syntax, changed-document local
links, notebook source preservation, and the evidence fingerprint verifier passed.
Saved copper notebook outputs were cleared without changing any cell source.
The final 18-file reader packet passed its manifest, link, and ZIP checks.
Tests used the existing local Python 3.14 research environment with isolated
temporary directories; allocation collector imports used `asset_allocation/src`.
This is local validation, not a new full notebook run or a remote CI result.

## Subsequent copper maintenance — 2026-10-18

Copper sources and production/research outputs were refreshed, both notebooks
executed in memory, and 23 targeted tests passed. Certificate/intrinsic now has
232 dates through October 17; the 223-date primary sample and its headline
statistics remain unchanged through October 11. Figures and evidence fingerprints
were updated. The October 17 portfolio review below remains a dated checkpoint;
this maintenance does not re-audit other projects or change their research scope.

Review date: **2026-10-17**. This review reconciles presentation and validates local
code/output claims. It does not refresh market sources, transfer an employer's
systems, or change the existing research stages listed below.

## Application snapshot

The application-facing deliverables are the portfolio, CV project section,
file-fingerprinted evidence report, refreshed copper/zinc Markdown reports and
figures, and gold/allocation research summaries. These define a bounded research
snapshot; continued market collection is maintenance rather than a condition
for describing the completed work.

Copper and zinc use the October 11 bounded primary sample. Their source-refresh
dates are October 18 and October 13, respectively. Gold's local sources were
refreshed October 17, with prices through October 14 and NAV/matched coverage
varying by fund. Allocation source and model checkpoints differ; its panel ends
at 1405/06 and REIT closes at October 7. Verification dates must not be substituted
for source or observation dates.

## Portfolio inventory

For projects outside the four featured areas, the entries below summarize inspected
project status documentation. They are not new source audits or model executions.

| Project | Delivered component / recorded stage | Application treatment and unresolved boundary |
|---|---|---|
| [Copper](../../commodity/copper/README.md) | Product-specific physical benchmark and bounded certificate valuation | Featured; 223 modeled days, 39 observed anchors. Sparse anchoring and future-anchor interpolation limit inference. Global/COCHILCO research remains cancelled. |
| [Zinc](../../commodity/zinc/README.md) | Grade-filtered physical basket and three valuation comparisons | Featured alongside copper; 223 modeled days, 54 anchors. Basket heterogeneity and omitted domestic costs remain limitations. |
| [Gold](../../commodity/gold/README.md) | Five-fund research checkpoint closed; ongoing maintenance | Featured; 8,253 local matched fund-days. Provider disagreements and NAV publication timing remain explicit; live server state unverified here. |
| [Asset allocation](../../asset_allocation/README.md) | Historical four-asset pilot implemented; expert-informed allocation planned | Featured as a historical pilot. Survey evidence and trailing information-set risk model are required for forward-looking claims. |
| [REIT extension](../../asset_allocation/reports/REIT_EIGHT_FUND_REINVESTMENT.md) | Eight-fund scenario analysis with 13 identified events | Supporting work. Full dividends, provisional dates, adjustment semantics, and historical same-date capitalization remain unresolved. Older four-fund narratives are superseded. |
| [National Copper / Codal](../../codal/national_copper/README.md) | Core quarterly financial reconstruction validated; labor audit pending | Supporting accounting-data research. Do not extend validated revenue/profit claims to provisional labor schedules. |
| [Ahrom options](../../options/README.md) | Contract discovery and historical-data pipeline | Supporting infrastructure. Documented 996 discovered contracts and initial 8,903 history rows are dated checkpoints, not a complete historical option market. |
| [Economic USD/IRR](../../economic_usd/README.md) | Macroeconomic input preparation implemented; valuation pending | Describe data preparation only. PPP anchor windows and liquidity valuation formula are unresolved; no fair-value estimate is delivered. |
| [Energy Exchange](../../energy_exchange/README.md) | Closed feasibility assessment | Completed feasibility study. Sparse, concentrated activity prevented the intended empirical design; retain that decision as the result. |
| [Pellet](../../commodity/pellet/README.md) | Exploratory exact-date comparison; 26 rows at October 13 checkpoint | Supporting exploratory work; product quality and delivery comparability remain provisional. |
| [Rebar](../../commodity/rebar/README.md) | Separate A3/18 and cross-diameter A3/12 diagnostics | Exploratory; 5 and 52 rows respectively. The combined 57 rows are not a homogeneous approved sample. |
| [Bitumen](../../commodity/bitumen/README.md) | 32-row exploratory cash comparison | Units, specification, and price discontinuity require resolution before economic valuation claims. |
| [Silver](../../commodity/silver/README.md) | Certificate collection and physical-source search | Source feasibility/infrastructure only. No eligible silver-metal physical rows were found; no physical valuation is available. |
| [Pistachio](../../goods/pista/README.md) | Certificate collection and 16-row bounded weekly-price proxy | Exploratory; manual workbook, units, product matching, and flagged source observations remain unresolved. |
| [Warehouse fees](../../commodity/warehouse_fees/README.md) | Tariff reconstruction across 21 commodities | Supporting measurement infrastructure. Distinguish observed archive dates from legally effective dates; unknown assessment fees remain blank. |

## Validation performed

- Root suite: **86 tests and 233 subtests passed** on 2026-10-17.
- Allocation and pistachio suites together: **50 tests passed** on 2026-10-17.
- Ruff correctness checks passed against the configured Python 3.11 target.
- The application verifier checked unique keys, selected formulas, positive inputs,
  no future as-of quotes, bounded anchor dates, fund identities, coverage, and
  SHA-256 fingerprints of 19 existing derived files.
- Copper and zinc figures were regenerated from the inspected outputs.
- The two main commodity figures were visually inspected; local Markdown links
  were checked. A deterministic reader-packet builder verifies its explicit file
  allowlist, manifest, internal links, ZIP integrity, and packaged bytes.

The tests ran under the local Python 3.14 environment. This is not evidence of a
fresh remote CI run or a complete Python 3.11 execution. No new live source audit,
database inspection, full notebook execution, or TeX compilation is claimed.

Two reproducibility issues were repaired: a Python 3.11-incompatible f-string in
the eight-fund figure builder, and a warehouse-fee test that wrote an August-cutoff
panel into the real processed-output path. That test now uses isolated temporary
inputs and output; data-dependent fee tests skip when the unversioned inputs are
absent. The existing current fee panel remains intact.

Initial restricted-shell tests encountered Windows temporary-file permissions.
The passing run used an isolated workspace temporary directory. Ruff was available
in the system interpreter, not the research virtual environment. These environment
issues are separate from research findings.

## Reproduction

From the repository root with the documented dependencies installed:

```powershell
python reports/application/verify_claims.py --check
python reports/application/build_packet.py
python -m ruff check . --no-cache
python -m pytest -q
python -m pytest -q goods/pista/tests
```

From `asset_allocation`, use its environment with the package installed and run
`python -m pytest -q`. Root CI does not substitute for all project-specific tests.
Follow each project's workflow for source collection and model rebuilding; a
newer shared FX file does not prove that every downstream model was rebuilt.

## Operational handoff boundaries

Shared USD/IRR has one owner under `shared/market_data` and one canonical dataset
under `shared/data/raw`. Full IME physical responses belong in the shared
content-addressed archive. Project-local historical snapshots remain frozen.
Iran Energy Exchange logic remains separate. Transfer code and documentation
separately from any authorized private source-data archive; retain source hashes.

Gold's documented deployment has daily collection/database refresh, weekly
reconciliation, and a disposable five-minute intraday monitor. The operator
should use its [database runbook](../../commodity/gold/db/README.md) to verify
service ownership, environment configuration, last successful jobs, retention,
and restoration. No remote service was stopped, changed, or handed to a recipient
in this review. A handoff recipient and destination have not been specified.

## Remaining work before broader claims

The submitted project descriptions can stay within the delivered scopes above.
Promoting the exploratory projects to valuation research, certifying REIT total
returns, completing PPP/liquidity valuation, or producing a forward-looking
allocation would require the specific missing evidence and model decisions.
Those are substantive research tasks, not editorial cleanup, and are not marked
complete by this packaging pass.

The working tree already contained extensive project changes when this review
began. The initial package described that inspected working state. Subsequent
code and documentation delivery is recorded in Git history; the user requested
commit and push after reviewing the package. Raw datasets and the generated
reader ZIP remain excluded from Git. No external data transfer or remote service
handoff is part of that code publication.
