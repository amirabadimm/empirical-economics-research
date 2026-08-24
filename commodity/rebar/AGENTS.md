# Agent Instructions — Steel Rebar Project

- Keep raw data only in `data/raw` and derived data only in `data/interim` or `data/processed`.
- Do not delete, overwrite, or manipulate canonical CSVs or API snapshots.
- The physical raw scope retains every official IME row whose normalized goods name identifies rebar; it includes all grades, producers, symbols, contracts, settlement terms, and zero-quantity offers.
- Do not infer a comparable rebar basket, price unit, quality, diameter, standard, delivery location, producer, or contract/settlement equivalence without documented evidence.
- Update the project README, `docs/WORKFLOW.md`, and `docs/STATUS.md` after a source, schema, path, formula, observation-count, or research-stage change.
