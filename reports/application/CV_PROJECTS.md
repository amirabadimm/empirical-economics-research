# CV-ready research project descriptions

Final portfolio edition: **2026-10-25**. Portfolio link:
[Empirical Economics Research](https://github.com/amirabadimm/empirical-economics-research).
This repository is a closed research notebook; Housing is a separate ongoing project.

Evidence checkpoint: 2026-10-17. These entries describe projects, not an employment
title, publication, or degree. Add actual project dates and institutional affiliation
in the CV; those biographical details are not inferred from repository activity.

## Research Projects

**Commodity Certificate Valuation and Domestic Price Formation — Iran**

- Built reproducible copper and zinc valuation pipelines combining exchange-traded warehouse receipts, eligible physical transactions, LME prices, and USD/IRR; analyzed 223 modeled trading days per commodity.
- Distinguished domestic physical-market bases from certificate premiums, estimating mean domestic premiums of 6.09% for copper and 1.88% for zinc while explicitly separating observed anchors from bounded interpolations.

**Gold ETF Price–NAV Premiums and Data Reliability**

- Constructed exact-date price–NAV histories for five Iranian gold ETFs, yielding 8,253 matched fund-day observations with explicit missing-data and provider-disagreement flags.
- Implemented empirical premium distributions and a PostgreSQL research workflow separating permanent daily history from disposable intraday monitoring.

**Iranian Cross-Asset Allocation — Historical Research Pilot**

- Assembled a four-asset monthly panel spanning 126 return-grid months across gold, equities, Tehran housing, and fixed income; preserved missing observations and documented housing-source corrections and proxy transitions.
- Implemented long-only historical portfolio optimization and risk-aversion sensitivity analysis, examining how allocation results change across periods and covariance specifications.

## Compact alternative

**Empirical Financial Economics Research | Python, pandas, NumPy, SQL/PostgreSQL, Git**

- Analyzed Iranian commodity certificate valuation using product-specific physical benchmarks, LME prices, and exchange rates; separated observed transactions from interpolated estimates across two 223-day samples.
- Built five-fund gold ETF price–NAV histories with 8,253 matched fund-days and audited source reliability; developed a four-asset monthly panel and historical portfolio-allocation framework.

Use either the three detailed entries or the compact version, depending on available
space. The [portfolio](README.md) supplies the research narrative and the
[evidence report](EVIDENCE.md) supports the numerical claims.

## Interview notes

- Explain why certificate/LME discounts differ from certificate/domestic-physical premiums. The international reference omits domestic frictions and is not a complete import-parity price.
- Explain the interpolation limit: later physical anchors enter historical estimates, so the series cannot establish look-ahead-free trading performance.
- Distinguish a fund-day from a calendar day and a same-date NAV from information available in real time.
- Explain the housing audit, proxy transition, and the difference between a hindsight optimum and an implementable allocation.
- Present REIT reinvestment as a scenario with incomplete dividend history. Do not describe it as certified total return or claim causal management effects.

Do not add claims of publication, causal identification, forecast accuracy, investment
profits, employer impact, or sole authorship beyond the contribution you can document.
