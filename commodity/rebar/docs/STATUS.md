# Steel Rebar Research Status

Last updated: 2026-08-24
Stage: broad physical-market collection complete; A3 / 12 mm exploratory cash-price pipeline available

## Current state

- Product project created for IME steel rebar physical-market data.
- Broad source filter retains every normalized rebar-labelled row without quality, producer, symbol, contract, settlement, or trade-status exclusions.
- Initial historical collection produced 31,532 source rows from 1387/06/03 through 1405/06/01; the canonical raw file and immutable monthly snapshot archive remain local and excluded from Git.
- The active chart scope is plainly specified straight A3 / 12 mm rebar under cash or cash-matching contracts. A deterministic builder produces its daily VWAP and percentage-difference output; the notebook visualizes it on source Jalali dates.
- The notebook now includes a reproducible initial screen that ranks plainly specified, single-diameter/single-grade straight rebar groups by cash-trade frequency. This screening does not approve a benchmark or resolve producer and delivery comparability.

## Next action

Audit A3 / 12 mm producer, standard, delivery, and quotation-basis comparability before treating the exploratory daily output as a benchmark or economically interpreted price series.
