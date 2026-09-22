# Status

The data-preparation stage is complete: four independent processed inputs and a preliminary monthly join are implemented. Economic valuation remains in progress and has not yet been calculated.

Two valuation methods have been selected for the next stage:

- a dollar-liquidity valuation; and
- a PPP valuation.

The unresolved PPP issue was base-period sensitivity. The agreed direction is to use five anchors instead of one base year. Each anchor must represent the average of a six-to-twelve-month period rather than a single date. Exact anchor periods, the calculation formula, and the presentation of the five estimates still need to be finalized and implemented.

Validated coverage:

- USD/IRR: 1360/07/07–1405/06/21, daily observed trading dates.
- Iranian headline urban CPI: 1361-01–1405-04, monthly with no missing months.
- Iranian liquidity (M2): 1385-01–1404-12, monthly with no missing months.
- U.S. CPIAUCNS: 1913-01–2026-08, monthly with no missing months.

The largest-change diagnostic flags liquidity at 1393-05 and Iranian CPI at 1361-07 for later source review. Values remain unchanged. FRED was retrieved through its official CSV endpoint because `FRED_API_KEY` was not set.

Next actions:

1. define the dollar-liquidity formula and dollar denominator;
2. select and document five economically defensible PPP anchor periods;
3. calculate each anchor from a six-to-twelve-month average;
4. produce the five PPP valuation paths and a transparent comparison; and
5. compare the PPP results with the dollar-liquidity estimate.
