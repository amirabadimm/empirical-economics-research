# Steel Rebar Research Status

Last updated: 2026-08-29
Stage: unfiltered physical and certificate collection complete; no rebar bubble

## Current state

- Product project created for IME steel rebar physical-market data.
- Broad source filter retains every normalized rebar-labelled row without quality, producer, symbol, contract, settlement, or trade-status exclusions.
- The refreshed physical collection contains 31,641 source rows from 1387/06/03 through 1405/06/07; the canonical raw file remains local, the former monthly archive is frozen, and future complete responses use the shared content-addressed IME archive. All remain excluded from Git.
- The standardized notebook dashboard counts 630 distinct `GoodsName` labels across all 31,641
  physical records and adds separate physical/certificate activity and price views. Its bubble
  panel correctly reports that no validated Rebar bubble exists.
- The active chart scope is plainly specified straight A3 / 12 mm rebar under cash or cash-matching contracts. A deterministic builder produces its daily VWAP and percentage-difference output; the notebook visualizes it on source Jalali dates.
- The notebook now includes a reproducible initial screen that ranks plainly specified, single-diameter/single-grade straight rebar groups by cash-trade frequency. This screening does not approve a benchmark or resolve producer and delivery comparability.
- Continuous-certificate collection covers commodity ID 29 across `CD1RBR0001` and `SteelRebar`: 268 records from 2025-10-20 through 2026-08-27, including 194 traded days.
- No rebar bubble is computed. Historical launch notices describe A3 / 18 mm as the certificate deliverable; current official contract and warehouse documentation is still required before comparison.
- Network-free tests cover certificate identity and the separate A3 / 12 mm physical exploration.

## Next action

Obtain and archive the current official certificate and warehouse specification, then define and
test an A3 / 18 mm physical analytical scope. Do not build the rebar bubble before that gate.
