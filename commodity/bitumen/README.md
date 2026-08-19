# Bitumen Certificate Research

## Research question

Which bitumen grade, market segment, contract structure, and delivery terms are economically
comparable with the Iranian bitumen certificate?

## Current checkpoint

- Data checkpoint: 2026-08-16
- Certificate: 257 calendar observations, 185 positive-trading days, through 2026-08-15
- Physical market: 47,085 rows, including 24,163 positive trades, through 1405/05/24
- Stage: domestic 60/70 standard-cash/observed-cash specification fixed for the conservative
  diagnostic; production deliverability and price-basis approval remain pending
- Processed benchmark and certificate bubble: not yet produced

The physical market is heterogeneous across grades, producers, domestic/export markets, and
cash, forward, and credit contracts. Raw data therefore retain the broad source scope. No
benchmark will be created until the certificate specification is matched explicitly to grade,
delivery market, settlement type, and eligible contract terms.

## Current exploratory findings

- The focused conventional domestic 60/70 scope contains 12,155 positive rows and approximately
  13.46 million tons from 1387/06/02 through 1405/05/20.
- The source contains 104 positively traded historical symbols in this scope; 17 have traded from
  1405 onward.
- Concurrent producer prices commonly differ by about 5%, with economically important tail cases.
- Missing settlement values are confined to the legacy period through 1392/05/20 and remain
  labeled `Not reported`; they are not silently converted to cash.
- Observed cash and cash/credit settlement within the cash contract group show no significant
  adjusted difference and may be pooled provisionally under a 3% tolerance, with the settlement
  flag preserved and an observed-cash-only sensitivity series.
- Standard cash and cash-matching contracts are price-equivalent in 1,855 exact symbol/day pairs;
  they may be pooled while retaining the contract flag and a cash-only sensitivity series.
- Credit contracts carry an adjusted premium of approximately 3.2%–3.5% over cash contracts;
  exact same-symbol/day pairs have a median premium of approximately 5.25%.
- Cash and credit contracts are therefore not interchangeable in an unadjusted spot benchmark.
- The certificate dataset begins on 2025-10-20 (`1404/07/28`). After that date, the current
  eligible physical candidate has only 51 trading dates, 18 symbols, and 25,410 tons; 50 dates
  overlap positive certificate trading days. Bubble construction therefore requires an explicit
  temporal-alignment rule rather than silent daily carry-forward.
- A stricter standard-cash/observed-cash specification has 29 positive certificate overlaps. Its
  median certificate-to-physical diagnostic changes from about -5% in 1404 to +157% in 1405, so
  unit and specification comparability must be verified before interpreting it as a bubble.
- A published secondary market report identifies one certificate as one kilogram; the notebook
  uses that documented conversion for volume comparison while retaining official IME contract
  documentation as a production-approval requirement.
- Every one of the 14 strict common-date observations in 1405 has a positive diagnostic spread;
  the mean is approximately 149% and the median approximately 157%. These statistics remain
  descriptive until price quotation, tax, fee, warehouse, packaging, and delivery bases are
  reconciled.

## Reproduction from the repository root

```powershell
python .\commodity\bitumen\src\bitumen\collectors\certificate.py
python .\commodity\bitumen\src\bitumen\collectors\physical.py
```

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for collection rules, validation, and the pending
eligibility decisions.

The exploratory producer, grade, continuity, and price-homogeneity analysis is in
[`notebooks/01_bitumen_physical_analysis.ipynb`](notebooks/01_bitumen_physical_analysis.ipynb).
It reads raw data without writing derived files. The product taxonomy, symbol mapping,
delivery conditions, and producer aliases remain provisional until the official
certificate specification is documented and the candidate basket is approved.
