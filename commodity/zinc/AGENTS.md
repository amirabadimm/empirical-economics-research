# Agent Instructions — Zinc Project

- Keep raw data only in `data/raw` and derived data only in `data/processed`.
- Route physical derivatives to `data/processed/physical`, certificate-only derivatives to
  `data/processed/certificate`, and all bubble/model outputs to `data/processed/bubble`.
- Do not delete or manipulate API and CSV canonical snapshots.
- Zinc ingot certificate includes both `CD1ZNI0001` and `ZincIngot` codes; They are a continuous series.
- Do not guess the price unit, volume and value without documents and do not avoid validation.
- Any physical market or bubble method requires separate examination of grade, producer and warehouse.
- The global source of zinc is Westmetall with `field=LME_Zn_cash`; HTML is immutable and annual
  CSV canonical should remain incremental, unique, ordered and atomic.
- LME raw cash price is USD per ton; Intrinsic price conversion only by dividing by 1000 and then
  The multiplication is done in the free dollar Riyal/Dollar and the `-` values of the source are kept in raw.
- Update `docs/WORKFLOW.md` after any source, schema or observation count changes.
- USD/IRR is owned once by `shared/market_data/fx.py` at
  `shared/data/raw/fx/usd_to_rial.csv`; Zinc must read it directly and keep no local copy.
