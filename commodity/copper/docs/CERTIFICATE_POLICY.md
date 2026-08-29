# Copper Certificate Research Policy

Last reviewed: 2026-08-15

## Scope and decision discipline

This policy applies to `commodity/copper`. Methodological decisions must be explicit, documented,
and reproducible. Approval of one stage does not authorize an unrelated change in scope. Any
change in source, schema, unit, eligibility rule, formula, observation count, or research status
must update the project README, `docs/WORKFLOW.md`, and `docs/STATUS.md` in the same change.

## Data governance

1. Store certificate raw data only in `data/raw/certificate`.
2. Store physical-market raw data only in `data/raw/physical`.
3. Preserve source responses and snapshots immutably with retrieval time and source URL.
4. Write physical derivatives to `data/processed/physical`, certificate-only derivatives to
   `data/processed/certificate`, and bubble/model outputs to `data/processed/bubble`.
5. Keep price and quantity units explicit, especially IRR versus toman and kilograms versus tonnes.
6. Keep source date, trade date, and retrieval time in separate fields.
7. Collectors must be incremental, idempotent, schema validated, and atomic.
8. A failed download or validation must not destroy the previous healthy canonical file.
9. Credentials must come from environment variables and must never enter code or documentation.

Raw data, snapshots, logs, caches, environments, and bulk outputs are excluded from Git.

## Source hierarchy

1. Iran Mercantile Exchange official endpoints.
2. TSETMC only after coverage and instrument identity are demonstrated.
3. Third-party sources only for reconciliation or dispute investigation.

Source disagreements must be recorded and explained rather than resolved silently.

## Certificate identity and price

The official certificate collector joins the continuous historical contract identities
`CD1COP0001` and `CopperCthd`. `TodaySettlementPrice` is the analytical certificate price.
`TradesValue / TradesVolume` is a rounding-tolerant validation only. Zero-volume dates remain in
raw data but do not enter price analysis.

The collector must validate instrument identity, date uniqueness, schema, positive-trade logic,
historical overlap, and incremental refresh behavior before replacing the canonical file.

## Physical-market eligibility

The approved comparable underlying is National Iranian Copper Industries Company cathode under
symbols `NCI-CCAA-00` and `NCI-OACCAA-00`. The exact official Persian source labels used by the
collector are intentionally preserved:

- goods: `مس کاتد`;
- producer: `ملی صنایع مس ایران`;
- eligible contract types: `نقدی` and `نقدی (مچینگ)`.

Forward, forward-matching, credit, other producers, and `مس کاتد 2` are excluded from the cash
benchmark unless a later documented decision establishes equivalence. Zero-quantity offers may be
preserved within source scope but never enter a traded-price weight.

The source reports quantity in tonnes while `Price` is on the observed IRR/kg scale used by the
certificate. Raw source units must be preserved; `TotalPrice` must not be silently rescaled.

## Physical benchmark safeguards

`build_physical_benchmark.py` produces `nci_copper_cash_daily.csv`. The output exposes one primary
numeric price, `physical_weighted_price`, and retains cash/matching quantity diagnostics. If
cash and cash-matching weighted prices diverge on the same date, validation must fail rather than
silently combining them.

The current benchmark contains 791 positive-trading days through 2026-08-09.

## Certificate valuation safeguards

The primary method uses the physical/intrinsic ratio at exact physical/certificate anchors and
linearly interpolates that ratio by calendar day. Current coverage contains 28 exact anchors and
150 interpolated dates. Extrapolation outside the first and last anchor is prohibited without a
new explicit methodological decision.

Every valuation output must retain enough information to audit:

- certificate date and price;
- physical anchor dates and observed prices;
- interpolation method;
- LME and FX source dates and ages;
- estimated physical price;
- bubble in IRR/kg and percent.

The regression specification is a sensitivity check only. Certificate price must not be used to
predict physical price.

## Forward-gap diagnostic

Forward trades inside the 102-day cash gap remain separate from the approved cash benchmark.
Their prices may be compared with adjacent cash anchors, but they must not fill the cash series
without explicit maturity and financing adjustments.

## Validation and reporting

- Final analytical prices use IRR/kg.
- Dates are unique and sorted.
- Price and quantity are positive in analytical samples.
- Exact anchors are distinguished from modeled observations.
- Stale as-of inputs remain visible through source date and age fields.
- Observation counts and headline statistics are never hard-coded as validation logic.
- Limitations are reported alongside results.

This repository provides research documentation and reproducible analysis, not investment advice.
