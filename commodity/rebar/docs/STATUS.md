# Steel Rebar Research Status

Last updated: 2026-08-29
Stage: exploratory exact-date A3 / 18 mm bubble built; specification QA remains open

## Current state

- Product project created for IME steel rebar physical-market data.
- Broad source filter retains every normalized rebar-labelled row without quality, producer, symbol, contract, settlement, or trade-status exclusions.
- The refreshed physical collection contains 31,641 source rows from 1387/06/03 through 1405/06/07; the canonical raw file remains local, the former monthly archive is frozen, and future complete responses use the shared content-addressed IME archive. All remain excluded from Git.
- The standardized notebook dashboard counts 630 distinct `GoodsName` labels across all 31,641
  physical records and adds separate physical/certificate activity and price views. Its bubble
  panel reads the reproducible processed exact-date comparison.
- The active chart scope is plainly specified straight A3 / 12 mm rebar under cash or cash-matching contracts. A deterministic builder produces its daily VWAP and percentage-difference output; the notebook visualizes it on source Jalali dates.
- The notebook now includes a reproducible initial screen that ranks plainly specified, single-diameter/single-grade straight rebar groups by cash-trade frequency. This screening does not approve a benchmark or resolve producer and delivery comparability.
- Continuous-certificate collection covers commodity ID 29 across `CD1RBR0001` and `SteelRebar`: 268 records from 2025-10-20 through 2026-08-27, including 194 traded days.
- A strict A3 / 18 mm cash-only, exact-Gregorian-date builder produces 5 gross quoted-price bubble
  observations from 2026-03-15 through 2026-05-26. All physical anchors are Isfahan Steel trades;
  no interpolation, forward pooling, or cost adjustment is used.
- A separate requested A3 / 12 mm cash-only exact-date sensitivity contains 46 observations from
  2025-11-12 through 2026-08-26. Its schema explicitly marks the diameter mismatch and prevents it
  from being presented as the certificate-underlying comparison.
- Network-free tests cover certificate identity, both strict product scopes, cash filtering,
  exact-date alignment, VWAP, bubble arithmetic, and the mandatory cross-diameter warning.

## Next action

Obtain and archive the current official certificate and warehouse specification; verify lot and
quotation units, producer/warehouse eligibility, delivery timing, taxes, storage and transaction
fees; then decide whether the exploratory exact-date diagnostic can become an approved benchmark.
