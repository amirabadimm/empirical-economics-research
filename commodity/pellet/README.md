# Iron-Ore Pellet Certificate Research

## Research question

Which domestic physical-market basket is sufficiently comparable with the Iranian iron-ore
pellet warehouse receipt to support a defensible daily benchmark and certificate valuation?

## Current checkpoint

- Data checkpoint: 2026-08-10
- Certificate: 252 calendar observations, 182 positive-trading days, through 2026-08-09
- Physical market: 3,467 rows, including 1,606 positive trades, through 1405/05/18
- Stage: complete raw collection and exploratory analysis; underlying not yet approved
- Processed benchmark and certificate bubble: not yet produced

The physical raw scope retains all rows whose normalized goods name is exactly iron-ore pellet,
without silently choosing a producer, symbol, contract type, or delivery condition. The exploratory
notebook compares producers and cash/cash-matching transactions. A formal benchmark will be built
only after quality specifications and certificate delivery terms are matched to eligible physical rows.

## Reproduction from the repository root

```powershell
python .\commodity\pellet\src\pellet\collectors\certificate.py
python .\commodity\pellet\src\pellet\collectors\physical.py
```

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for provenance, validation, and the unresolved
underlying-selection decision.
