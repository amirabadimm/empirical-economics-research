# Global Copper Market Research Framework

Last reviewed: 2026-09-01
Stage: architecture and source-contract backlog; no global-market dataset is yet canonical

## Purpose

This document adapts the COCHILCO analytical framework to the existing Copper project. It is a
research and data-governance map, not a replacement filesystem and not a claim that every listed
series is already collected.

The active project already answers a narrower question: valuation of the Iranian copper-cathode
warehouse receipt against a comparable domestic physical benchmark, LME cash copper, and the
free-market USD/IRR rate. That workflow remains authoritative. The global framework adds the
physical and financial context needed to explain when the LME-based intrinsic proxy is supported
by mine, concentrate, refined, regional, demand, and positioning conditions.

## Existing assets and ownership

| Asset | Canonical owner | Role in the global framework |
|---|---|---|
| Iranian cathode physical trades | `commodity/copper/data/raw/physical` | Domestic refined-physical market and local benchmark |
| Copper certificate trades | `commodity/copper/data/raw/certificate` | Domestic certificate market; not a global physical-balance input |
| LME cash, three-month, and stock history | `commodity/copper/data/raw/lme` via `shared/market_data/lme.py` | Benchmark price, nearby curve, and visible inventory |
| Free-market USD/IRR | `shared/data/raw/fx` via `shared/market_data/fx.py` | Shared currency conversion; never copied into Copper |
| Iranian concentrate exports and offers | `commodity/copper/data/raw/concentrate_export` | Iran-specific concentrate trade evidence |
| NICICO financial disclosures | `codal/national_copper` | Issuer fundamentals; joined only through an explicit derived analysis |
| COCHILCO reports | `commodity/copper/articles/chicolo_reports` | Local immutable research evidence; spelling is preserved for compatibility |
| Existing bubbles and valuation models | `commodity/copper/data/processed/bubble` | Domestic valuation outputs, not measures of global physical tightness |

## Analytical modules mapped to this repository

The COCHILCO system is represented as linked modules. New sources remain separate in raw storage;
they are combined only in reproducible interim or processed outputs.

| Module | Already available | Missing canonical inputs | Intended derived location |
|---|---|---|---|
| Benchmark and nearby curve | LME cash, three-month, stock | Official LME warrant detail and longer forward curve | `data/processed/analysis` |
| Iranian refined physical market | IME cathode benchmark | Regional cathode premiums outside Iran | `data/processed/physical` for domestic benchmarks; `analysis` for comparisons |
| Mine supply | None | Mine/country production, grade, recovery, disruptions, project guidance | `data/processed/analysis` |
| Concentrates | Iran export/offer evidence | Global concentrate balance, China imports, spot and benchmark TC/RC | `data/processed/analysis` |
| Smelting and refining | None | Capacity, utilization, outages/cuts, output mix, SX-EW, secondary refining | `data/processed/analysis` |
| Global refined balance | LME visible stock only | Refined production, usage, balance, multi-exchange and regional inventories | `data/processed/analysis` |
| Fabrication and end use | None | Semis/wire-rod activity, grid, construction, EV, renewables, data centers | `data/processed/analysis` |
| Scrap and circularity | None | Secondary production, scrap availability/trade, cathode discount, direct melt | `data/processed/analysis` |
| Cross-market pricing | LME only | COMEX and SHFE normalized prices, FX/tax/freight bases, regional premiums | `data/processed/analysis` |
| Positioning and macro | Shared FX only | COT/positions, open interest, DXY, rates, PMI, industrial production | `data/processed/analysis` |
| China physical demand | None | Refined/concentrate trade, SHFE stock, import premium, grid and semis activity | `data/processed/analysis` |

## Storage and source rules

1. Do not create one monolithic `global_copper.csv`. Mine, concentrate, refined, exchange,
   premium, positioning, and demand sources have different definitions and must remain separate.
2. A new source receives its own documented collector and raw directory only when its source
   contract is known. Empty speculative collectors and placeholder datasets are prohibited.
3. Raw canonical CSVs and source snapshots are immutable except through their documented,
   incremental, idempotent, validated, and atomic collector.
4. Source directories should follow `data/raw/<source_or_market>/`, not the conceptual module name
   when several providers measure the same module. Provider identity must remain visible.
5. Normalized and joined tables belong in `data/interim`; validated KPIs and comparison tables
   belong in `data/processed/analysis` unless they are strictly physical, certificate, or bubble
   outputs under the existing routing rules.
6. Cross-commodity series belong in `shared/market_data` and `shared/data/raw`; Copper references
   them rather than creating local copies.
7. NICICO disclosure data remains in `codal/national_copper`. Copper may consume a validated
   processed output read-only, with source dates and lineage retained.
8. COCHILCO reports support definitions and interpretation. Reported values must not be manually
   transcribed into a canonical time series without a documented extraction and validation path.

## Indicator contract

Every new series must document at least:

- provider, publication, landing page, and access method;
- economic concept and value-chain stage;
- original and canonical units;
- geography, grade/brand, market, and frequency;
- observation date versus publication/retrieval date;
- revision policy and whether history can change;
- missing-value and non-trading-day semantics;
- transformation from source to canonical fields;
- validation bounds and uniqueness key;
- license or access restriction;
- whether the series is a flow, stock, price, spread, ratio, or event.

This contract prevents economically different observations—such as mine copper, concentrate,
smelter copper, refined cathode, exchange inventory, and regional availability—from being joined
under an ambiguous `supply` or `inventory` label.

## Priority sequence

### Phase 0 — reuse and harden what exists

- Treat LME cash, three-month, and stock as three distinct analytical fields.
- Add explicit cash-minus-three-month spread and stock-change tables from the existing raw LME
  data; preserve the sign convention (`cash - 3M`).
- Keep domestic physical, certificate, intrinsic, and bubble measures distinct from global
  tightness indicators.
- Inventory the local COCHILCO archive and record report title, period, language, and provenance
  before extracting observations.

### Phase 1 — physical confirmation

- Add official LME warehouse/warrant documentation and, if reproducibly available, warrant-level
  or regional inventory detail.
- Add COMEX and SHFE contract specifications before computing cross-exchange spreads.
- Add regional cathode-premium sources only with explicit grade, location, quotation, currency,
  tax, and freight bases.
- Build inventory changes, inventory coverage where consumption is available, and premium-stock
  confirmation diagnostics.

### Phase 2 — upstream transmission

- Add mine production and disruption data.
- Add global concentrate balance and spot/benchmark TC/RC.
- Add smelter/refinery capacity, utilization, cuts, output, SX-EW, and secondary-refined supply.
- Test the chain from mine disruption to TC/RC, smelter stress, refined output, inventories, and
  nearby spreads without assuming fixed lags.

### Phase 3 — demand and geography

- Add China refined/concentrate trade, SHFE inventory, import premium, grid, and semis activity.
- Add broader fabrication and end-use proxies.
- Normalize COMEX-LME and SHFE-LME comparisons for units, FX, tax, freight, eligibility, and timing
  before interpreting them as arbitrage.

### Phase 4 — models and composites

- Align frequencies and retain release-time information to prevent look-ahead bias.
- Run lead/lag tests, event studies, regime checks, and out-of-sample validation.
- Build composite tightness or financial-impulse scores only after individual signals have stable
  definitions and demonstrated behavior.
- Keep any price forecast or multivariate model in `data/processed/bubble` when it estimates the
  domestic valuation bubble; other global-market analytical models belong in
  `data/processed/analysis`.

## First derived tables to build from existing data

No new external source is needed for these candidates:

1. `lme_curve_and_stock_daily.csv`: date, cash, three-month, cash-minus-three-month spread,
   contango/backwardation regime, stock, and 1/5/20-observation stock changes.
2. `domestic_global_basis_daily.csv`: the existing NCI physical benchmark aligned to LME and FX,
   with source dates and ages preserved. This should reuse current intrinsic logic rather than
   duplicate it.
3. `copper_market_event_timeline.csv`: a governed extension of the existing presentation event
   timeline, with event type, affected module, geography, source, publication time, and whether
   the event is observed or analyst-interpreted.

These are implementation candidates, not existing canonical outputs. Their schemas and tests
must be approved in code before production.

## Interpretation guardrails

- “Tight” must identify the layer: mine, concentrate, smelter, refined global, regional cathode,
  or prompt exchange availability.
- Supply and demand are flows; inventory is a stock. Never combine them without an explicit
  normalization or accounting identity.
- Visible exchange inventory is not total commercial inventory.
- A positive refined balance does not prove regional abundance; inventory location and delivery
  eligibility matter.
- Negative TC/RC signals concentrate-feed competition, not a negative engineering processing cost.
- An exchange benchmark is not a physical invoice; premiums, grade, location, freight, tax, and
  quotation period remain separate.
- Bullish positioning without falling stocks, stronger premiums, or backwardation is financial
  impulse, not confirmed physical tightness.
- Composite scores and forecasts are downstream products. They must never replace their source
  tables or obscure conflicting signals.

## Definition of completion

The global-market layer is complete only when each active module has a documented source contract,
canonical immutable raw input, validated derived table, update procedure, tests, coverage record,
and known limitations. The COCHILCO framework defines what to investigate; this repository's
source contracts and validation evidence determine what can be claimed.
