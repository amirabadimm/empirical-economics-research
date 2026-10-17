# Economics research portfolio

**Mohammad Mahdi Amirabadi** · Application checkpoint: **2026-10-17**

My research examines how asset prices in Iran relate to underlying value,
international benchmarks, and domestic market conditions. The projects combine
economic measurement with reproducible data construction, emphasizing source
quality, comparable products, and the limits of historical inference.

## Selected research

### Commodity certificates and domestic price formation

**Question.** How does the choice of benchmark change the measured premium or
discount on copper and zinc warehouse receipts?

**Approach.** Combine IME certificate and physical trades with LME prices and
USD/IRR. Construct product-specific physical baskets, align international inputs
without using future quotes, and interpolate the domestic physical basis only
between observed anchors.

**Evidence.** Both primary samples cover 223 certificate-trading days through
2026-10-11. Estimated mean domestic premiums are **6.09% for copper** and **1.88%
for zinc**. On the same dates, their direct LME–FX comparisons show discounts
of 10.35% and 20.58%, respectively. The choice of economic comparable materially
changes the valuation interpretation. Copper has 39 observed anchors and zinc 54;
the remaining modeled days are interpolated, not physical observations.

**Research contribution.** A transparent distinction between the domestic physical
basis and certificate valuation. The analysis measures historical relative prices;
it does not identify causal effects or establish executable arbitrage.

Read the [copper report](../copper/research/REPORT.md) and
[zinc report](../zinc/research/REPORT.md).

### Gold ETF price–NAV measurement

**Question.** How do Iranian gold ETF prices compare with same-date redemption NAV,
and how reliably can those differences be measured?

**Approach.** Build exact-date price–NAV histories for five funds, preserve missing
observations and provider discrepancies, and calculate fund-specific empirical
distributions. Daily research history remains separate from intraday monitoring.

**Evidence.** The current local history contains **8,253 matched fund-days**.
The source audit documents gaps and disputed NAV values rather than silently
filling or reconciling them. Historical NAV publication times are unavailable,
so the outputs support ex-post valuation measurement rather than a live strategy.

Read the [gold research summary](../../commodity/gold/reports/RESEARCH_SUMMARY.md).

### Iranian cross-asset allocation: historical pilot

**Question.** How stable are hindsight-efficient allocations across gold,
equities, Tehran housing, and fixed income?

**Approach.** Construct a monthly panel with source-audited housing values and
explicit proxy transitions. Separate long-only risky-sleeve selection from
risk-aversion sensitivity, and compare year-specific and fixed covariance models.

**Evidence.** The current return grid spans **126 months**, with 125 complete
four-asset months. Saved historical optimization results show substantial changes
in the dominant asset across periods. The delivered contribution is the historical
pilot and measurement framework; the expert-informed forward-looking model remains
planned. The separate eight-fund REIT extension retains provisional dividend scenarios.

Read the [allocation research summary](../../asset_allocation/reports/CURRENT_RESEARCH_SUMMARY.md).

## Application and handoff materials

- [CV project descriptions](CV_PROJECTS.md): concise text for a research-projects section.
- [Evidence checkpoint](EVIDENCE.md): reproducible counts, formulas, sample windows, and input fingerprints.
- [Closeout and handoff](HANDOFF.md): all project stages, reproducibility, operational boundaries, and unresolved work.
- [Repository overview](../../README.md): code organization, methods, and additional projects.

A portable reader packet is built locally with
`python reports/application/build_packet.py`. It contains these summaries and
six selected commodity figures, with a file manifest and checked internal links.
The generated ZIP stays under ignored `reports/application/outputs/`; it contains
no datasets or full source archive.

The portfolio emphasizes demonstrated work. Exploratory commodities, the option
dataset, issuer reconstruction, and macroeconomic input preparation remain
supporting projects with their own stated limits. None is relabelled as a completed
econometric paper. Original code and documentation follow the repository licence;
third-party source data remain outside the application materials.
