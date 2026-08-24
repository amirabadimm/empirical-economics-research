# Agent Instructions — National Iranian Copper Industries Company

- Keep this issuer project under `codal/national_copper`; do not mix Codal disclosure logic with
  `shared/ime_data` or the Iran Energy Exchange package.
- Treat downloaded disclosures, attachments, and source responses as immutable snapshots.
- Refresh canonical raw tables only through a documented incremental, idempotent, and atomic
  collector.
- Write derived files only to `data/interim` or `data/processed`; notebooks and analysis code
  must never modify raw data.
- Keep the issuer identity, ticker, Codal identifiers, report types, and filters explicit. Do not
  infer or silently broaden them.
- Read credentials only from environment variables and never record them in code, data, logs, or
  documentation.
- Update `README.md`, `docs/WORKFLOW.md`, and `docs/STATUS.md` after a source, schema, path,
  formula, observation count, or project-stage change.
