# Decision 0001 — Close the Energy Exchange Certificate Project

Date: 2026-08-23

## Decision

Stop active research and do not extend the Iran Energy Exchange project into a valuation,
liquidity, trading, or investment-analysis pipeline. Preserve the source corpus, public-access
inventory, certificate collector, immutable local snapshot, and derived feasibility results so
the decision remains reproducible. No recurring collection is approved or scheduled.

## Evidence

The complete observed certificate registry contains 21 symbols and 7,070 returned daily records
through 2026-08-22. Only 1,432 records (20.25%) contain both positive transaction count and positive
volume. Activity is not uniform:

- commodity-deposit certificates traded on 144 of 2,556 returned rows (5.63%);
- energy-saving certificates traded on 468 of 2,475 rows (18.91%), and both observed diesel-saving
  symbols had no trades;
- the cash capacity certificate traded on 602 of 1,758 rows (34.24%);
- renewable-production certificates traded on 218 of 281 rows (77.58%).

Historical reported value is also concentrated: the capacity certificate and the largest
gas-saving symbol account for 73.1% of total reported value. Several commodity-deposit value
fields require unresolved unit reconciliation. The active renewable niche does not offset the
limited breadth, concentration, and data-quality work required for the broader research question.

## Consequences

- The feasibility question is considered answered: there is real activity in selected niches,
  but the overall certificate market is unsuitable for the intended broad empirical project.
- The project status is **closed after feasibility assessment**, not “failed” and not “no market.”
- Existing raw snapshots remain immutable and local under the repository data policy.
- Derived CSV files remain local and reproducible from the versioned collector.
- Restarting the project requires a new decision that defines a narrower question—most plausibly
  renewable-production certificates—and a fresh data-quality and source-stability review.
