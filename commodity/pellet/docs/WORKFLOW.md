# Iron-Ore Pellet Warehouse-Receipt Certificate: Research Workflow

Last reviewed: 2026-08-15

## Research objective

The pellet project estimates the warehouse-receipt premium or discount relative to comparable
domestic physical pellet transactions. It is currently an exploratory exact-date study. Global
prices, exchange rates, and external intrinsic-value models are outside scope.

## Data checkpoint

| Source | Coverage |
|---|---|
| Certificate | 252 calendar rows; 182 positive-trading days through 2026-08-09 |
| Broad physical pellet market | 3,467 rows; 1,606 positive trades through 1405/05/18 |
| Exploratory exact-date bubble | 22 observations |

Raw data and immutable monthly snapshots remain unchanged. No production processed benchmark has
yet been approved.

## Architecture and collection

The certificate wrapper uses the shared CDC collector and explicit pellet contract identities.
The physical collector archives complete official IME monthly responses before filtering and
retains every exact normalized iron-ore-pellet row in canonical raw data. Collection is
incremental, idempotent, and atomic. Analysis never writes to raw paths.

## Producer selection

Producer selection uses all positive physical trades since certificate inception, independent of
contract or settlement type. This measures market representation before the stricter benchmark
price rules are applied.

| Producer | Symbol | Volume share |
|---|---|---:|
| Gol Gohar | `GOLG-PELL-00` | 30.75% |
| Gohar Zamin | `GHZ-PELL-00` | 23.10% |
| Chadormalu | `CHMI-PELL-00` | 9.81% |
| Sangan Khorasan | `SSMI-PELL-00` | 5.66% |

Gol Gohar and Gohar Zamin jointly represent 53.86% and are retained. Chadormalu and Sangan
Khorasan jointly represent 15.47% and are excluded from the candidate benchmark. This is an
analytical decision only; excluded observations remain in raw data.

## Strict-cash benchmark rule

Eligible physical observations must satisfy all of the following:

- selected producer;
- cash or cash-matching contract;
- explicitly cash settlement;
- positive executed price and quantity.

Cash/credit observations are excluded. A single-producer day uses that producer's observed price;
a two-producer day uses the simple mean. The certificate is joined only on exact dates with
positive volume and settlement price. No interpolation or carry-forward is used.

The exploratory sample contains 16 single-producer dates and six two-producer dates. Mean bubble
is -12.18%, median is -11.55%, minimum is -24.93%, and maximum is +11.03%.

## Cross-producer validation

Only 16 strict-cash common dates exist for Gol Gohar and Gohar Zamin over the full history: nine
before and seven after certificate inception. The mean symmetric price difference declines from
1.53% before inception to 0.88% after inception; both medians are zero. Four of the seven later
dates have identical prices. The evidence does not support increased producer dispersion after
certificate trading began.

On 1401/04/11, the largest valid symmetric difference is 7.67%. Base price, offer quantity,
delivery, warehouse, and settlement terms align. Demand-to-supply is 1.3 for Gol Gohar and 3.0 for
Gohar Zamin, consistent with stronger competition for the latter offer. Available data do not
identify the underlying cause of buyer preference.

## Positive-bubble case: 1404/10/21

The qualifying benchmark is Gol Gohar's cash price of IRR 94,566/kg. The certificate settles at
IRR 104,998/kg, implying a +11.03% bubble. Gohar Zamin's IRR 111,229/kg observation is excluded
because settlement is cash/credit. A sensitivity mean using both same-day producer prices reduces
the bubble to approximately +2.04%, demonstrating material composition risk.

Certificate settlement had already risen from IRR 81,844/kg on 1404/10/10 to IRR 103,483/kg on
1404/10/17. The evidence is consistent with a timing difference in price discovery but does not
establish causality. The observation is retained and labeled as a composition-sensitive,
single-producer benchmark.

## Outputs

- `notebooks/01_physical_analysis.ipynb`: complete reproducible exploratory analysis.
- `docs/STATUS.md`: current decision record and next step.
- `reports/FINAL_REPORT.md`: concise English research report.
- `reports/pellet_certificate_report.tex`: publication-style English LaTeX report.
- `reports/build_report_figures.py`: reproducible report figures.

## Reproduction and next step

From the repository root:

```powershell
python .\commodity\pellet\src\pellet\collectors\certificate.py
python .\commodity\pellet\src\pellet\collectors\physical.py
```

Then execute `notebooks/01_physical_analysis.ipynb` with the project kernel. The next research step
is to extend exact-date coverage and continue separating single- and two-producer results. A
production processed benchmark should be created only after final approval of the selection rule.
