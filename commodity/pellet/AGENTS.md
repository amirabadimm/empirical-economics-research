# Agent Instructions — Pellet Project

- Keep raw data only in `data/raw` and derived data only in `data/processed`.
- Route physical derivatives to `data/processed/physical`, certificate-only derivatives to
  `data/processed/certificate`, and all bubble/model outputs to `data/processed/bubble`.
- Do not delete or manipulate API and CSV canonical snapshots.
- The pellet certificate contains both `CD1IOP0001` and `IronOrePlt` codes; They are a continuous series.
- Do not guess the price unit, volume and value without documents and do not avoid validation.
- Any method of physical market or bubble requires separate examination of quality, producer and warehouse.
- Update `docs/WORKFLOW.md` after any source, schema or observation count changes.
