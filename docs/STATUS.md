# Research Status

Documentation review: 2026-08-11
Latest data checkpoint: 2026-08-10

| Project | Current data coverage | Research stage | Next action |
|---|---|---|---|
| Copper | Certificate/FX through 2026-08-02; LME through 2026-07-31; physical through 2026-07-26 | Full valuation pipeline | Expand analytical QA, regression tests, and refresh monitoring |
| Iron-ore pellet | Certificate through 2026-08-09; physical through 1405/05/18 | Exploratory underlying research | Validate quality/delivery comparability and approve a physical basket |
| Zinc | Certificate/physical benchmark through 2026-08-09; LME through 2026-08-07; FX through 1405/05/17 | Full three-bubble pipeline | Interpret notebook results and monitor input freshness |
| Bitumen | Certificate through 2026-08-02; physical through 1405/05/12 | Broad raw collection complete | Identify eligible grade, market, delivery, and contract type |

## Available research outputs

- Copper has seven local processed CSVs and an English LaTeX research report under
  `reports/copper/research`.
- Zinc has six local processed CSVs, two analytical notebooks, fourteen tests, and an English
  LaTeX report under `reports/zinc/research`.
- Iron-ore pellet has an exploratory physical-market notebook but no approved benchmark.
- Bitumen has no analytical notebook or processed benchmark yet.
- No collector is currently scheduled or monitored in the repository.

## Update rule

After any change in source, schema, path, formula, observation count, or research stage, update
this file, the project README, and its `docs/WORKFLOW.md`. Detailed operational histories remain
inside each project.
