# Iranian asset allocation and real estate funds

**Mohammad Mahdi Amirabadi** · Portfolio review: 2026-10-17

## Historical allocation pilot

How stable are hindsight-efficient allocations across gold, equities, Tehran
housing, and fixed income? The project constructs monthly series for TGJU
18-karat gold, TEDPIX, Tehran housing, and the Etemad ETF, with explicit calendar,
unit, source-transition, and missing-value rules.

The current level grid has 508 asset-month rows across 127 months (1394/12–1405/06).
The return grid has 504 cells across 126 months (1395/01–1405/06), including one
missing initial housing return. Thus 125 months have complete four-asset returns;
the optimization pilot begins later, in 1396. These are Solar Hijri dates.

The analysis separates long-only risky-sleeve composition from the amount of
risky exposure chosen under explicit risk-aversion parameters. Year-specific
and full-sample covariance specifications expose sensitivity to the risk model.
Saved notebook results show sharply changing dominant assets and five corner
solutions among ten Stage-I periods. The notebook was inspected, not re-executed,
in this application review.

Housing source review is a substantive contribution. Source-adjudicated corrections
are versioned separately from preserved evidence. Official CBI transaction prices
end at 1403/05; later observations use a flagged chain-linked Kilid listing-price
proxy. Housing excludes rent and ownership costs, and Etemad's historical
distribution policy remains an audit limitation. The asset proxies are not
equivalent total-return investments.

The delivered research component is an **ex-post historical pilot**. The expert
survey and trailing-risk model required for forward-looking allocation remain
planned. Full-sample covariance uses future observations relative to earlier
years and cannot support an investable backtest claim.

## Separate REIT extension

Eight fund histories end at 2026-10-07. The current model compares raw-price,
cash-holding, and hypothetical reinvestment paths using 13 identified events.
Reinvestment occurs at the first valid traded close strictly after the modeled
event. Some dates are provisional and complete dividend histories remain unverified.
These are scenario returns, not certified total returns.

The current [eight-fund report](REIT_EIGHT_FUND_REINVESTMENT.md) is the entry point.
Older four-fund notebook and LaTeX performance narratives are superseded for
current dividend results and should not be submitted as current findings.
Same-date historical unit counts and market capitalization for 2026-10-07 remain
unresolved; later unit counts support only an indicative capitalization.

## Evidence and reproduction

Use the [workflow](../docs/WORKFLOW.md), [housing audit](../docs/HOUSING.md),
[dividend audit](../docs/REIT_DIVIDEND_AUDIT.md), and
[application evidence checkpoint](../../reports/application/EVIDENCE.md).
The September historical pilot report remains an earlier numerical vintage;
this summary reconciles scope and current panel coverage without silently
replacing its original result tables.
