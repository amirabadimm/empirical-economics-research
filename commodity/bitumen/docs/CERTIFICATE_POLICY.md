# Bitumen Data Policy

- Canonical raw CSVs and API snapshots are immutable research records.
- Collection must remain incremental, idempotent, validated, and atomic.
- The old `CD1BIT0001` and current `Bitumen` codes form one continuous certificate series.
- Both Gregorian and Jalali certificate dates must be retained.
- Zero-volume days and untraded physical offers remain in raw data.
- Analytical filters may exclude nonpositive observations only in memory or approved derived data.
- Missing settlement values must never be overwritten. Any imputation must be explicitly labeled
  and reported as a sensitivity analysis.
- Cash, credit, forward, and matching contracts must remain distinguishable.
- Credit contracts must not enter a cash-price benchmark without a documented financing and
  maturity adjustment.
- Schema changes, identity failures, or validation errors must stop the pipeline.
- Credentials, raw snapshots, logs, caches, and bulk outputs must remain outside Git.
