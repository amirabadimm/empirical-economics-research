# Workspace Instructions

These instructions define the repository's data-governance and maintenance conventions.

- Keep commodity-specific research inside `commodity/<commodity>`.
- Treat source snapshots as immutable evidence. Do not delete, overwrite, or silently transform them.
- Refresh canonical raw CSVs only through documented collectors that are incremental, idempotent, validated, and atomic.
- Analysis code and notebooks must never modify canonical raw data.
- Write derived data only to `data/interim` or `data/processed`.
- Within commodity projects, route physical-market derivatives to `data/processed/physical`, certificate-only derivatives to `data/processed/certificate`, bubble/model outputs to `data/processed/bubble`, and other analytical tables to `data/processed/analysis`.
- Keep canonical physical and certificate datasets independent under `data/raw/{physical,certificate}`. A derived comparison file never replaces either source dataset.
- Place reusable Iran Mercantile Exchange collection logic in `shared/ime_data`, while keeping product-specific filters, units, and eligibility rules explicit in each project.
- Keep cross-project market inputs such as USD/IRR under `shared/market_data` with one canonical owner under `shared/data/raw`. Commodity projects should reference shared inputs rather than maintain duplicate copies.
- Store complete IME physical responses once in the content-addressed `shared/data/raw/ime` archive. Historical project-local snapshots remain frozen evidence.
- Keep Iran Energy Exchange logic separate from `shared/ime_data`.
- Store notebooks in `notebooks`, logs in `logs`, and presentation artifacts in `outputs` or `reports`.
- After a change to a source, schema, path, formula, observation count, view, or research stage, update the affected README, `docs/WORKFLOW.md`, and `docs/STATUS.md` where applicable.
- Read credentials only from environment variables or private runtime configuration. Never commit secrets or place them in documentation or command examples.
- Do not commit raw datasets, snapshots, logs, caches, local environments, or bulk generated outputs unless a project-specific policy explicitly allows it.

## Project continuity and completion checks

- Treat the workspace as a connected research portfolio. Before changing a project, read its README, workflow, status, and applicable project instructions. Inspect relevant code and Git history when context is missing.
- Identify shared inputs, reusable code, and downstream consumers before changing common infrastructure.
- Before declaring a task complete, reconcile documentation for the affected project and update root-level summaries when architecture, status, or execution instructions have changed.
- Keep active, exploratory, planned, and closed research clearly distinguished.
- Record source coverage separately from derived-output coverage. Distinguish documentation-review dates from data-refresh and validation dates.
- Mark superseded checkpoints explicitly so older counts or methods cannot be mistaken for current results.
- Verify completion claims against files, commands, tests, and outputs actually inspected. State unresolved context or verification limits rather than inferring success.
- Preserve project continuity in repository documentation instead of relying on conversational memory.
