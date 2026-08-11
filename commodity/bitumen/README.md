# Bitumen Certificate Research

## Research question

Which bitumen grade, market segment, contract structure, and delivery terms are economically
comparable with the Iranian bitumen warehouse receipt?

## Current checkpoint

- Data checkpoint: 2026-08-03
- Certificate: 246 calendar observations, 178 positive-trading days, through 2026-08-02
- Physical market: 47,035 rows, including 24,154 positive trades, through 1405/05/12
- Stage: broad raw collection complete; underlying not yet approved
- Notebook, processed benchmark, and certificate bubble: not yet produced

The physical market is heterogeneous across grades, producers, domestic/export markets, and
cash, forward, and credit contracts. Raw data therefore retain the broad source scope. No
benchmark will be created until the certificate specification is matched explicitly to grade,
delivery market, settlement type, and eligible contract terms.

## Reproduction from the repository root

```powershell
python .\commodity\bitumen\src\bitumen\collectors\certificate.py
python .\commodity\bitumen\src\bitumen\collectors\physical.py
```

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for collection rules, validation, and the pending
eligibility decisions.
