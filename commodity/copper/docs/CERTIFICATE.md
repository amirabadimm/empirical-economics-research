# Copper Warehouse-Receipt Certificate: Source and Identity Record

Last reviewed: 2026-08-15

## Purpose

This document records the certificate identity, official source contract, canonical fields, and
collection safeguards used by the copper project. Analytical methodology is documented in
`WORKFLOW.md`; governance requirements are documented in `CERTIFICATE_POLICY.md`.

## Official source

The certificate series is collected from the Iran Mercantile Exchange CDC API through the shared
collector in `shared/ime_data/certificate_collector.py` and the copper-specific wrapper in
`src/copper/collectors/certificate.py`.

The continuous analytical history joins:

- historical code `CD1COP0001`;
- current contract identity `CopperCthd`.

The wrapper validates that overlapping identities do not create conflicting observations.

## Canonical fields

- `DT`: Gregorian trade date.
- `PersianDate`: official Jalali trade date.
- `ContractCode`: source contract identity.
- `ContractDescription`: official description.
- `TradesVolume`: traded certificate quantity.
- `TradesValue`: total traded value in IRR.
- `TodaySettlementPrice`: official analytical settlement price.
- `LastSettlementPrice`: previous settlement where available.
- `fetched_at_utc`: retrieval timestamp.
- `source_url`: official source endpoint.

`TodaySettlementPrice` is the analytical price. The ratio `TradesValue / TradesVolume` is used only
to validate settlement-price consistency within source rounding tolerance.

## Positive-trade rule

A certificate date enters price analysis only when `TradesVolume > 0` and the settlement price is
positive. Zero-volume dates remain in the canonical raw file because they document the complete
market calendar and may be relevant to liquidity analysis.

## Incremental collection contract

The collector:

1. reads the existing canonical file when present;
2. refreshes a documented trailing date window;
3. archives complete source JSON responses before canonical merge;
4. validates schema, identity, date uniqueness, and overlap consistency;
5. merges by trade date;
6. writes atomically only after all validations pass.

Repeated execution over unchanged source data must produce the same canonical result.

## Current checkpoint

- Canonical certificate rows: 256.
- Positive-trading days: 184.
- Latest certificate date: 2026-08-13.
- Primary valuation coverage: 178 dates through 2026-08-09.
- Exact physical/certificate anchors: 28.

Counts are documentation checkpoints, not hard-coded pipeline assumptions.

## Relationship to the physical market

The certificate is compared with the approved National Iranian Copper Industries Company cathode
cash benchmark. Physical eligibility, daily weighting, anchor interpolation, intrinsic-price
alignment, and regression sensitivities are defined in `WORKFLOW.md`.

No TSETMC subscription or inferred `InsCode` is required for the official CDC collector. A failed
third-party probe must not be interpreted as absence of an official certificate series.

## Reproduction

From the repository root:

```powershell
python .\commodity\copper\src\copper\collectors\certificate.py
```

Raw certificate data and immutable response snapshots remain local and are excluded from Git.
