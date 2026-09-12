# Source register

## CBI Tehran housing reports

| Dataset | Reference | What it supports |
|---|---|---|
| 87 official monthly housing-market reports | [CBI archive](https://www.cbi.ir/category/16994.aspx) | Tehran-wide average residential transaction price per square metre; reconstructed monthly coverage 1395/01–1403/05 with observation-level PDF provenance. |
| Kilid housing-price history | [Kilid](https://kilid.com/house-prices/tehran) | Monthly Tehran values from 1402/06–1405/05 in the preserved page snapshot. Used only after 1403/05 as a chain-linked secondary proxy; common-period similarity to CBI is weak and explicitly flagged. |

## Fixed income — selected source

| Dataset | Reference | What it supports |
|---|---|---|
| اعتماد ETF daily closing-price history | [TSETMC closing-price API](https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/66818022341772870/0) | Sole fixed-income source for 1395/01–1405/05; distribution treatment remains subject to audit. |

Deposit-rate and اخزا alternatives were evaluated and retired. The decision history is
preserved in [FIXED_INCOME.md](FIXED_INCOME.md). Their immutable raw evidence is frozen,
but the sources are absent from active configuration and processing.

## TSE total-return index

| Dataset | Reference | What it supports |
|---|---|---|
| TEDPIX daily history | [TSETMC index API](https://cdn.tsetmc.com/api/Index/GetIndexB2History/32097828799138957) | Official daily closing, opening, and high index levels. The active derivative selects the final valid daily close in every Jalali month from 1394/12 through 1405/05. |

Historical annual and TGJU stock-index files remain frozen as inactive source evidence under
`data/raw/tse_total_index/`; they do not support the active monthly table.

## Gold

| Dataset | Reference | What it supports |
|---|---|---|
| TGJU 18-karat gold / gram daily history | [TGJU public history API](https://api.tgju.org/v1/market/indicator/summary-table-data/geram18?lang=fa&order_dir=asc) | Daily open, low, high, and close in IRR per gram. The 2026-09-08 collection covers 1392/04/31–1405/06/16. The active derivative selects the final valid daily close in each Jalali month. |
## Active Tehran housing sources

The official CBI monthly report corpus is primary. Its 87 PDFs support a 101-row citywide
extraction covering 1395/01–1403/05. The processed panel retains CBI through that endpoint and
uses chain-linked Kilid afterward, with source-specific provenance and quality flags. See
[HOUSING.md](HOUSING.md).
