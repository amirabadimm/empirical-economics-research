# Shared Market Analysis

This package contains only commodity-invariant analytical mechanics:

- validated numeric conversion, CSV reads, and atomic derived writes;
- backward as-of matching for market observations;
- time-series cross-validation and intrinsic-value regression model selection.

Commodity identity, eligible grades, symbols, units, benchmark construction, and interpretation
remain in `commodity/<commodity>`. Shared code must not silently introduce a product filter or
replace the separate physical, certificate, and bubble datasets.
