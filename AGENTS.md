# Workspace Instructions

- Keep the domain of each product in `commodity/<commodity>`.
- Source snapshots are immutable: deletion, overwriting or implicit transformation is prohibited.
- Raw canonical CSV only by documented, incremental, idempotent and atomic collector
  it is refreshed; Analysis and notebook do not have the right to change raw.
- Write the derived file only in `data/interim` or `data/processed`.
- The general logic of the commodity exchange is placed in `shared/ime_data`; Each product must have a wrapper
  Keep the settings and filters of the same project explicit.
- The energy exchange logic is placed in a separate joint package and is not mixed with `ime_data`.
- notebooks in `notebooks`, logs in `logs` and presentation output in `outputs` or
  `reports` are placed.
- After changing the source, schema, path, formula, view count or stage status, README,
  Update project `docs/WORKFLOW.md` and `docs/STATUS.md`.
- Credentials are only received from the environment and should not be in the file, code or documentation
  be registered
- raw, snapshot, log, cache, environment and bulk output should not be entered into Git.