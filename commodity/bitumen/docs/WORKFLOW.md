# Bitumen Certificate Research Workflow

Last reviewed: 2026-08-29

## Research objective

The project evaluates which physical bitumen product can serve as an economically defensible
underlying for the Iranian bitumen certificate. A production benchmark requires agreement
on grade, specification, producer eligibility, delivery location, unit, market segment, contract
type, settlement conditions, and temporal coverage.

Statistical liquidity alone does not establish deliverability or technical comparability.

## Current status

| Source | Current coverage |
|---|---|
| Certificate | 257 calendar observations through 2026-08-15; 185 positive-trading days |
| Broad physical market | 47,085 rows through 1405/05/24; 24,163 positive trades |
| Exploratory notebook | Executed successfully; 34 cells, no external analytical outputs |
| Working analytical underlying | Conventional domestic penetration-grade 60/70 |
| Conservative physical specification | Standard cash contract and observed cash settlement |
| Approved physical benchmark | Not yet approved |
| Certificate premium/discount series | Not yet produced |

Broad raw collection is complete and current. Exploratory work is performed in
`notebooks/01_bitumen_physical_analysis.ipynb`. The notebook reads canonical raw data without
writing interim or processed files.

The research specification is now fixed for the current diagnostic: certificate observations are
compared with conventional domestic 60/70 physical trades executed under standard cash contracts
and observed cash settlement. “Not yet approved” refers to production use and legal deliverability,
not to uncertainty about the working analytical filter.

## Workflow state and decisions

| Component | Current decision | Status |
|---|---|---|
| Product | Conventional domestic penetration-grade 60/70 | Fixed for the current research specification |
| Physical contract | Standard cash (`ContractType`) | Fixed for the conservative diagnostic |
| Settlement | Observed cash (`Tasvieh`) | Fixed for the conservative diagnostic |
| Cash matching | Economically close to standard cash | Excluded from the conservative series; retained for sensitivity work |
| Cash/credit settlement | No significant adjusted difference under a 3% tolerance | Excluded from the conservative series; retained for sensitivity work |
| Credit contracts | Positive financing premium | Excluded without financing and maturity adjustment |
| Forward contracts | Different maturity basis | Excluded |
| Missing settlement | Source value retained as unknown | Excluded from the primary specification |
| Date alignment | Exact common positive-trading dates | Approved for the diagnostic only |
| Daily physical price | Physical value divided by physical volume | Approved for the diagnostic; symbol median is a robustness check |
| Certificate volume conversion | One certificate equals one kilogram | Supported by secondary documentation; official IME notice still required |
| Price comparability | Certificate settlement divided by physical VWAP | Diagnostic only pending quotation- and delivery-basis reconciliation |
| Processed benchmark | None | Blocked by the production decision gates below |

## Data architecture

### Certificate

- Official endpoint: `https://dataapi.ime.co.ir/api/CDC/CDCTrades`
- Continuous instrument identities: `CD1BIT0001` and `Bitumen`
- Canonical CSV: `data/raw/certificate/bitumen_certificate_raw.csv`
- Immutable responses: `data/raw/certificate/api_snapshots`
- Default refresh: trailing 14 days

### Physical market

- Official endpoint:
  `https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList`
- Canonical CSV: `data/raw/physical/bitumen_physical_raw.csv`
- Shared immutable monthly responses: `shared/data/raw/ime/physical`
- Frozen pre-consolidation responses: `data/raw/physical/api_snapshots`
- Default refresh: current month plus two prior Jalali months
- Raw scope: every source row whose normalized `GoodsName` contains the Persian word for bitumen

The collectors are incremental, idempotent, validated, and atomic. Raw rows include untraded
offers and the full heterogeneous product universe. Analytical exclusions occur only in memory or
in an explicitly approved derived layer.

## Exploratory market taxonomy

The current provisional taxonomy distinguishes:

- conventional penetration/numeric grades;
- performance grades (`PG`);
- cutback grades (`MC`, `RC`, and `SC`);
- emulsions;
- polymer-modified products;
- anode material and unresolved labels;
- domestic/unspecified and export market segments.

The taxonomy is a research aid, not an approved technical specification. Source product labels
remain visible for manual review.

## Current focus: conventional domestic 60/70

The active exploratory scope is conventional domestic penetration-grade 60/70:

- family: `penetration_or_numeric`;
- grade: `6070`;
- market: `domestic_or_unspecified`;
- currency: rial;
- unit: ton;
- positive traded quantity, price, and value;
- exports, emulsions, and polymer-modified products excluded.

This scope contains 12,155 positive rows, approximately 13.46 million tons, 3,140 trading days,
and 92 normalized producer labels from 1387/06/02 through 1405/05/20.

The historical source contains 142 symbols in this scope, of which 104 have positive trades.
There are 35 positively traded symbols from 1404 onward and 17 from 1405 onward. Historical symbol
counts must not be interpreted as distinct product grades because symbols can encode producer,
plant, legacy naming, packaging, or other offer details.

## Price dispersion within 60/70

Nominal prices are not compared across the full history because inflation dominates the raw
range. The notebook calculates a volume-weighted producer price on each date and compares
concurrent producers.

Across 2,332 dates with at least two producers:

- median same-day high-low range relative to the daily mean: about 5%;
- 90th percentile: about 10%;
- 95th percentile: about 12%.

From 1404 onward, only 67 dates have at least two producers. The median range is about 4.5%, the
90th percentile is about 11.7%, and the maximum is about 18.4%. These differences are economically
relevant but do not by themselves identify quality differences; producer, delivery, contract,
settlement, and lot-size effects may contribute.

## Contract and settlement definitions

`ContractType` and `Tasvieh` are distinct source fields:

- `ContractType` identifies the contract form, including cash, cash matching, credit, credit
  matching, forward, and forward matching.
- `Tasvieh` records a settlement condition: cash, credit, cash/credit, or not reported.

A cash contract must not automatically be described as observed cash settlement when `Tasvieh`
is credit, mixed, or missing.

### Missing settlement values

Within cash-contract 60/70 observations, missing `Tasvieh` values are concentrated entirely in the
legacy period 1387/06/02 through 1392/05/20. Missing settlement accounts for 100% of cash-contract
volume in 1387–1391, 29% in 1392, and zero from 1393 onward.

Policy:

- never overwrite the raw value;
- retain `Not reported` as the primary analytical label;
- permit `imputed cash` only as a separately reported sensitivity scenario;
- never present imputed cash as observed cash settlement.

Observed cash and missing settlement overlap on only one date, and there are no exact same-symbol,
same-day cash-versus-missing pairs. A missing-versus-cash fixed-effects coefficient is therefore
not estimated.

### Cash versus cash/credit settlement within the cash contract group

This comparison includes both standard cash and cash-matching contracts and controls for contract
subtype. Observed cash settlement contains 867 rows and 215,106 tons; the cash/credit category
contains 3,598 rows and 2,271,868 tons.

There are no exact same-symbol, same-day, same-contract-subtype pairs. Across 361 common dates, the
pooled median cash/credit premium is approximately 0.68% and the mean is approximately 1.32%.
After date, symbol, and cash-contract-subtype controls:

- unweighted estimate: approximately +0.72%, with a 95% interval of -0.81% to +2.27%;
- volume-weighted estimate: approximately -0.73%, with a 95% interval of -2.54% to +1.11%;
- neither estimate is statistically significant.

Decision: observed cash and cash/credit settlement may be pooled provisionally for exploratory
price construction under a 3% materiality tolerance. Preserve the source settlement flag and
report an observed-cash-only sensitivity series. The evidence does not establish equivalence under
a stricter 2% tolerance, and the cash/credit label may describe an option rather than realized
settlement.

### Cash versus credit contracts

The contract-level comparison groups:

- cash: cash plus cash-matching contracts;
- credit: credit plus credit-matching contracts;
- forward contracts: excluded.

Coverage:

| Contract group | Rows | Volume | Symbols | Trading days |
|---|---:|---:|---:|---:|
| Cash | 11,031 | 12,447,569.5 | 92 | 2,921 |
| Credit | 919 | 570,391.0 | 46 | 416 |

Empirical findings:

- 45 exact same-symbol, same-day pairs across 8 symbols and 42 dates;
- median exact-pair credit premium: approximately 5.25%;
- mean exact-pair credit premium: approximately 5.47%;
- pooled same-day median premium across 230 dates: approximately 2.84%;
- date/symbol fixed-effects premium: approximately 3.20%;
- volume-weighted fixed-effects premium: approximately 3.45%;
- both adjusted estimates are positive and highly statistically significant.

Decision: cash and credit contracts are not interchangeable. The primary spot benchmark should
use cash and eligible cash-matching contracts. Credit contracts require an explicit financing and
maturity adjustment before inclusion.

### Standard cash versus cash matching

Standard cash and cash-matching contracts have substantial exact-pair overlap:

- 1,855 exact same-symbol, same-day pairs across 33 symbols and 1,215 dates;
- 1,786 pairs have exactly equal prices;
- 1,815 pairs are within 10 basis points;
- 1,841 pairs are within 50 basis points;
- 1,846 pairs are within 1%;
- all 14 exact pairs from 1404 onward have identical prices.

The date/symbol fixed-effects estimate is approximately -0.08% without volume weights and +0.02%
with volume weights. Both confidence intervals include zero and are economically narrow.

Decision: standard cash and cash matching may be pooled for price construction. The original
`ContractType` must remain available as an audit field, and a standard-cash-only sensitivity series
must be reported before production approval.

## Post-certificate-inception physical market

The certificate dataset begins with a positive observation on 2025-10-20, corresponding to
1404/07/28. This is the current analytical inception date for bubble research. It is not yet
described as the legally verified issuance date because an official issuance document has not been
obtained. The physical window is inclusive of 1404/07/28.

All conventional domestic 60/70 positive trades from inception contain:

- 158 rows and 153,075 tons;
- 83 physical trading days;
- 29 symbols and 30 producer labels;
- coverage through 1405/05/20.

The current benchmark candidate—standard cash plus cash matching, with observed cash plus
cash/credit settlement—contains:

- 79 rows and 25,410 tons;
- 51 physical trading days;
- 18 symbols and 19 producer labels;
- first eligible physical trade on 1404/08/04;
- last eligible physical trade on 1405/05/20.

Liquidity is sparse: the median eligible day has one symbol and 300 tons; only 13 dates have at
least two eligible symbols. Across those 13 dates, the median within-day high-low price range is
approximately 5.35% of the daily mean.

Date alignment is also sparse:

- 257 certificate calendar observations;
- 185 positive certificate days;
- 51 eligible physical dates;
- 51 exact overlaps with certificate calendar observations;
- 50 exact overlaps with positive certificate days.

Decision: do not construct a nominally daily bubble by silently carrying physical prices forward.
The temporal-alignment rule—exact date, bounded carry-forward, nearest prior trade, or lower-frequency
aggregation—must be defined explicitly and compared through sensitivity analysis.

### Strict cash–cash exact-date diagnostic

The conservative specification requires standard cash `ContractType` and observed cash `Tasvieh`
for conventional domestic 60/70 after certificate inception. It contains:

- 32 physical rows and 6,480 tons;
- 30 physical trading dates;
- 10 symbols and 11 producer labels;
- 29 dates with positive certificate trades.

The physical daily price is calculated as traded value divided by traded volume; a symbol-median
alternative is also reported. Following the copper convention:

- absolute bubble = certificate settlement price minus physical VWAP;
- percentage bubble = `100 × (certificate settlement price / physical VWAP − 1)`.

Every exact-date row reports physical traded volume, certificate traded volume, supplier count,
physical VWAP, certificate settlement price, and both bubble measures.

For volume comparison, one certificate is converted to one kilogram and then to metric tons. This
conversion is supported by a published secondary market report
(`https://atlaseqtesad.ir/86480/commodity-certificate-bourse-trading.html`) and remains subject to
confirmation against the official IME admission or market-opening notice. The notebook retains
both the raw certificate count and converted metric-ton volume.

The volume conversion does not alter the price diagnostic and does not prove that the two quoted
prices share the same tax, fee, delivery, or quotation basis. Internally, physical
`TotalPrice = Quantity × Price` and certificate
`TradesValue = TradesVolume × TodaySettlementPrice` within rounding tolerance. These identities
validate each source internally but do not, by themselves, establish cross-market economic
equivalence.

Results show a structural discontinuity:

| Jalali year | Exact overlap days | Median certificate price | Median physical VWAP | Median diagnostic |
|---|---:|---:|---:|---:|
| 1404 | 15 | 271,439 | 294,851 | approximately -5% |
| 1405 | 14 | 1,118,781.5 | 415,500 | approximately +157% |

Across all 29 overlaps, the diagnostic ranges from approximately -25% to +242%. The discontinuity
does not coincide with the certificate code transition, which occurred earlier in 1404/08.

Within the 14 exact overlaps in 1405, every diagnostic spread is positive; the mean is approximately
149% and the median approximately 157%. A two-sided sign test rejects an equal probability of
positive and negative spreads (`p ≈ 0.00012`). A Mann–Whitney comparison of the 1404 and 1405
samples gives `p ≈ 0.000005`. These are exploratory statistics: the year split is descriptive,
daily observations may be serially dependent, and statistical significance does not resolve unit,
tax, packaging, storage, delivery, or eligibility differences.

Two overlap dates contain two physical suppliers. Their maximum-to-minimum symbol price differences
are 3.39% and 2.50%. The daily physical VWAP differs from the symbol median by -0.56% and +0.53%,
respectively, changing the calculated bubble by only +0.47 and -1.03 percentage points. Supplier
dispersion is therefore visible but has limited influence on these two daily aggregate bubbles.

Decision: retain this series as a diagnostic only. Do not label it a production certificate bubble
until price units, deliverable specification, packaging, delivery basis, and fees are verified.

## Notebook methodology

The exploratory notebook currently performs:

1. schema and data-quality validation;
2. reversible Persian text normalization;
3. positive-trade analytical filtering;
4. provisional product-family and grade classification;
5. producer and supplier profiling;
6. producer continuity and market-share analysis;
7. producer-grade matrices;
8. within-grade price-dispersion diagnostics;
9. domestic 60/70 symbol analysis;
10. cash-settlement symbol comparisons;
11. legacy settlement-missingness analysis;
12. settlement fixed-effects comparisons;
13. standard-cash versus cash-matching contract comparisons;
14. cash-versus-credit contract comparisons;
15. post-certificate-inception liquidity and overlap profiling;
16. strict standard-cash/observed-cash exact-date price construction;
17. certificate-to-physical diagnostic spread calculation and supplier-aggregation sensitivity;
18. source-unit identity checks and certificate-volume conversion to metric tons;
19. descriptive 1404/1405 regime inference and common-day volume visualization.

Fixed-effects models use log price with date and symbol effects and date-clustered standard errors.
Estimation is restricted to dates with overlapping observed comparison groups. Volume-weighted
and unweighted specifications are reported.

The exact-date diagnostic is intentionally not extrapolated to nonphysical trading days. The
regime tests are exploratory rather than confirmatory: the sample is small, the calendar split is
descriptive, and daily observations may be serially dependent. Statistical significance therefore
does not supersede contract-specification validation.

## Reproducibility and analytical outputs

Run the notebook from the repository root with the project environment:

```powershell
.\Finenv\Scripts\python.exe -m nbconvert --to notebook --execute --inplace `
  .\commodity\bitumen\notebooks\01_bitumen_physical_analysis.ipynb `
  --ExecutePreprocessor.timeout=600
```

The executed notebook contains no error outputs and writes no analytical files. Its principal
in-memory objects are:

- `focus`: conventional domestic 60/70 positive physical trades;
- `post_candidate`: broader post-inception cash-group candidate retained for sensitivity work;
- `strict_cash`: standard-cash and observed-cash physical observations after inception;
- `strict_common_records`: record-level physical observations on positive certificate dates;
- `strict_overlap`: exact-date daily physical/certificate comparison;
- `regime_inference`: exploratory year-specific inference table;
- `volume_plot`: common-date physical and certificate volumes in metric tons.

## Benchmark eligibility rules

No production benchmark is approved. The current candidate rules are:

- conventional domestic penetration-grade 60/70 only;
- rial and ton observations only;
- positive quantity, price, and traded value;
- exports, emulsions, polymer-modified products, cutbacks, PG grades, and anode material excluded;
- cash and eligible cash-matching contracts as the primary spot-price candidates;
- credit and credit-matching contracts excluded unless financing-adjusted;
- forward contracts excluded unless maturity-adjusted;
- missing settlement retained as unknown in the primary specification;
- producer aliases and eligible symbols require documented review;
- warehouse, delivery, packaging, and technical-specification comparability remain unresolved.

## Decision gates before processed output

A processed benchmark may be created only after all of the following are documented and approved:

1. official certificate technical specification;
2. exact deliverable grade and permitted tolerances;
3. eligible producers, warehouses, and delivery locations;
4. unit and packaging consistency;
5. approved symbol and producer alias mapping;
6. missing-settlement treatment and observed-cash-only sensitivity specification;
7. minimum liquidity and temporal-coverage requirements;
8. price aggregation and outlier policy;
9. benchmark sensitivity to exclusions;
10. certificate-to-physical date alignment.

## Governance

- Preserve canonical raw CSVs and all API snapshots unchanged.
- Do not write exploratory derived files from the notebook.
- Record every future exclusion through stable source fields or documented symbol mappings.
- Store physical derivatives in `data/processed/physical`, certificate-only derivatives in
  `data/processed/certificate`, and any approved bubble in `data/processed/bubble`.
- Stop on schema or validation failure.
- Update the README, this workflow, and repository status after changes to source, schema, paths,
  formulas, observation counts, or research stage.

## Next actions

1. Obtain and archive the official IME certificate admission or market-opening notice, including
   grade, certificate mass, quotation unit, eligible warehouse, delivery lot, fees, and taxes.
2. Reconcile the sharp 1405 price discontinuity against quotation conventions, VAT, storage,
   packaging, delivery location, and any contract-rule changes.
3. Review the strict 60/70 symbol universe and document producer, plant, packaging, and delivery
   attributes without collapsing unsupported aliases.
4. Test whether the 1405 diagnostic survives tax/fee harmonization and any required quality or
   delivery-basis adjustment.
5. Report exact-date results as the conservative primary diagnostic; evaluate bounded prior-trade
   and lower-frequency alignment only as explicitly labeled sensitivity analyses.
6. Estimate uncertainty with methods appropriate for short, potentially dependent time series
   once the economic basis is validated.
7. Keep cash-matching and cash/credit-settlement extensions as secondary sensitivity specifications;
   do not use them to replace observed standard-cash prices silently.
8. Approve an auditable symbol/producer basket and methodology before writing any processed
   benchmark or production certificate premium/discount series.

## Interpretation boundary

The current result supports the statement that a large, persistent recorded certificate-to-physical
price spread appears on the strict exact-date sample in 1405. It does not yet support claims of a
risk-free arbitrage opportunity, market mispricing, or a production-ready bubble. Those stronger
claims require completion of the documentary and economic reconciliation steps above.
