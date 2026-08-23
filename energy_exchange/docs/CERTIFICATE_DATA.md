# Certificate Data Contract and Activity Checkpoint

Last collected: 2026-08-23 UTC

## Source and scope

The collector uses the public, unauthenticated TSETMC instrument-search and closing-price-history
interfaces at `https://cdn.tsetmc.com/api`. Certificate discovery is the union of explicit Persian
queries for savings, capacity, renewable production, and energy-carrier deposit certificates.
Only Energy Exchange (`flow == 6`) records whose official name identifies a certificate are kept.
The observed registry contains 21 symbols: eight commodity deposits, ten energy-saving
certificates, two renewable-production certificates, and one cash capacity certificate.

For every instrument, the complete `ClosingPriceDaily` response is archived unchanged in a
timestamped raw snapshot. TSETMC is an undocumented interface: field names and response shape must
be validated on every run, and the raw response is authoritative when derived data disagree.

## Fields and activity definition

The processed activity check uses these raw fields:

| Raw field | Interpretation used here |
|---|---|
| `dEven` | Gregorian trading date as `YYYYMMDD` |
| `zTotTran` | transaction count |
| `qTotTran5J` | traded quantity/volume |
| `qTotCap` | reported transaction value in rials |
| `pClosing` | closing price |
| `pDrCotVal` | last traded price |

A row is a **traded day** only when both `zTotTran > 0` and `qTotTran5J > 0`. A published daily row
with carried prices but zero transactions or volume is not evidence of market activity. Units are
instrument-specific, so volumes must not be summed across families as an economically homogeneous
quantity. Reported values for several commodity-deposit records appear inconsistent with price
times volume and require source-level reconciliation before valuation analysis.

## 2026-08-23 result

The snapshot contains 7,070 daily rows, of which 1,432 (20.25%) meet the traded-day definition.

| Family | Symbols | Published rows | Traded rows | Traded-row rate | Latest trade |
|---|---:|---:|---:|---:|---:|
| Commodity deposits | 8 | 2,556 | 144 | 5.63% | 2026-08-15 |
| Energy saving | 10 | 2,475 | 468 | 18.91% | 2026-08-22 |
| Renewable production | 2 | 281 | 218 | 77.58% | 2026-08-22 |
| Capacity | 1 | 1,758 | 602 | 34.24% | 2026-08-19 |

During the final 30 calendar days of the snapshot, both renewable-production symbols traded on 19
days each. The capacity certificate traded on nine days. Six energy-saving symbols traded at
least once, while only one commodity-deposit symbol traded. The two observed diesel-saving
symbols had no trades anywhere in their returned histories.

Historical reported value is concentrated: the capacity certificate and the larger gas-saving
symbol account for 73.1% of reported value across all certificate histories. This concentration,
the family-level differences, and the high zero-trade rate mean the 21-symbol registry must not be
described as one uniformly liquid market.

## Outputs

- `data/raw/certificates/<UTC timestamp>/`: immutable search, registry, and per-symbol responses.
- `data/interim/certificate_daily.csv`: normalized daily observations.
- `data/processed/certificate_activity_by_symbol.csv`: symbol-level activity summary.
- `src/energy_exchange/collect_certificates.py`: reproducible collector and processor.
