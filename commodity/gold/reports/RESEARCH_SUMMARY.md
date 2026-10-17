# Gold ETF price–NAV premiums in Iran

**Mohammad Mahdi Amirabadi** · Portfolio review: 2026-10-17

## Question and contribution

How do Iranian gold ETF closing prices differ from same-date redemption NAV?
This project builds an auditable comparison for Ayar, Tala, Kahroba, Ganj, and
Gohar, separating differences in market valuation from gaps and disagreements
in the NAV sources. It combines empirical asset-pricing measurement with a
reproducible daily research pipeline.

## Data and method

TSETMC supplies unadjusted closing prices; selected Fipiran histories supply
redemption NAV. Both are measured in IRR per fund unit. Positive-volume,
positive-trade-count sessions are joined on the exact valuation date, and the
premium is `100 × (close / redemption NAV − 1)`. Missing NAV remains missing.

The five local historical outputs contain **8,253 matched fund-day observations**.
Their last matched dates range from 2026-10-11 to 2026-10-13. The distinct
two-year presentation window contains 2,279 matches across 2,309 candidate
fund-days; unequal fund coverage remains visible. The local source refresh
was performed on October 17; the current review checks formulas and output
fingerprints without rerunning collectors.

Expanding, rolling, and recency-weighted empirical ranks describe each fund's
own history. A PostgreSQL implementation and disposable intraday cache support
maintenance; live readings never extend the permanent daily sample.

## What the evidence supports

The project establishes a reproducible price–NAV measurement framework and
documents why provider selection matters. The September 29 reliability audit
found provider agreement on overlapping dates for several funds, missing NAV,
and unresolved Gohar disagreements. Those exceptions remain part of the result.
The October refresh does not establish that every newly added NAV is independently
corroborated. Mesghal is excluded because validated historical NAV was unavailable.

Same-date matching establishes valuation-date alignment. Historical NAV publication
timestamps are unavailable, so premiums and historical ranks do not establish
an implementable intraday strategy, forecast, or arbitrage profit.

## Reproduction and evidence

Follow the [project workflow](../docs/WORKFLOW.md) for collection and rebuilding.
The [NAV audit](../docs/NAV_RELIABILITY.md) records provider-specific limitations.
The [application evidence report](../../../reports/application/EVIDENCE.md) pins
the local files and can be rechecked using its read-only verifier. The deployed
server was not inspected in the October 17 application review.
