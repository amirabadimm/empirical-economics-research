# Contributing

This repository is primarily an individual empirical-research portfolio, but reproducibility
fixes, methodological critiques, tests, and documentation improvements are welcome.

## Before proposing a change

1. Open an issue describing the economic or technical motivation.
2. Keep commodity-specific logic inside its project and reusable IME logic under `shared/ime_data`.
3. Never commit credentials, raw datasets, snapshots, local environments, logs, or bulk outputs.
4. Preserve source identity, units, date provenance, and immutable snapshot behavior.
5. Document any change to source, schema, formula, sample size, or research stage.

## Validation

Install development dependencies and run:

```bash
python -m pytest -q
python -m ruff check .
```

Data-dependent tests should skip clearly when licensed local inputs are unavailable; they must not
silently weaken validations when the data are present.

The current CI lint gate covers syntax and correctness-critical Pyflakes rules. Broader formatting
and modernization changes should be proposed separately from economic-methodology changes so that
review remains auditable.

## Research standards

Distinguish descriptive evidence, measurement assumptions, and causal claims. Do not present
interpolated values as observed transactions. State sample limitations, source ages, and scope
decisions explicitly. New benchmark rules require economic justification, not only statistical fit.
