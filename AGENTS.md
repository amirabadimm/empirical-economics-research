# Workspace Instructions

- Keep the domain of each product in `commodity/<commodity>`.
- Source snapshots are immutable: deletion, overwriting or implicit transformation is prohibited.
- Raw canonical CSV only by documented, incremental, idempotent and atomic collector
  it is refreshed; Analysis and notebook do not have the right to change raw.
- Write the derived file only in `data/interim` or `data/processed`.
- Within each commodity, route physical derivatives to `data/processed/physical`,
  certificate-only derivatives to `data/processed/certificate`, bubble/model outputs to
  `data/processed/bubble`, and other analytical tables to `data/processed/analysis`.
- Canonical physical and certificate CSVs remain independent under `data/raw/{physical,certificate}`;
  a bubble file never replaces either source dataset.
- The general logic of the commodity exchange is placed in `shared/ime_data`; Each product must have a wrapper
  Keep the settings and filters of the same project explicit.
- Cross-commodity external inputs such as USD/IRR belong to `shared/market_data` with one canonical
  dataset under `shared/data/raw`; commodity projects must reference it rather than copy it.
- Complete IME physical responses belong in the content-addressed `shared/data/raw/ime` archive.
  Historical project-local snapshots are frozen evidence; never delete, overwrite, or extend them.
- The energy exchange logic is placed in a separate joint package and is not mixed with `ime_data`.
- notebooks in `notebooks`, logs in `logs` and presentation output in `outputs` or
  `reports` are placed.
- After changing the source, schema, path, formula, view count or stage status, README,
  Update project `docs/WORKFLOW.md` and `docs/STATUS.md`.
- Credentials are only received from the environment and should not be in the file, code or documentation
  be registered
- raw, snapshot, log, cache, environment and bulk output should not be entered into Git.

## Project continuity and completion checks

- Maintain the workspace as a connected research portfolio. Before changing a project,
  read its applicable instructions, README, workflow, and status; inspect relevant code
  and Git history when context is missing. Identify shared inputs, shared code, and
  downstream consumers affected by the task.
- Before declaring work complete, check the impact on shared code and dependent projects,
  reconcile the affected project's README, `docs/WORKFLOW.md`, and `docs/STATUS.md`, and
  update the root `README.md`, `docs/STATUS.md`, `docs/WORKSPACE.md`, or `docs/WORKFLOW.md`
  wherever the workspace summary or execution instructions have changed. Documentation
  maintenance is part of the task, not a separate reminder required from the user.
- Keep active, exploratory, planned, and closed work distinct. Record source coverage
  separately from derived-output coverage, and distinguish documentation review dates
  from data-refresh and validation dates. Clearly label superseded checkpoints so old
  counts and stages cannot be mistaken for current status.
- Verify completion claims against the files, commands, and outputs actually inspected.
  State unresolved context and verification limits explicitly; do not claim a whole-project
  review, successful refresh, or test run that was not performed.
- Preserve continuity through repository documentation rather than relying on conversation
  memory or asking the user to reconstruct previously documented project decisions.
