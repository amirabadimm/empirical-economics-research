# Source register

## CBI Tehran housing reports

| Dataset | Reference | What it supports |
|---|---|---|
| 87 official monthly housing-market reports | [CBI archive](https://www.cbi.ir/category/16994.aspx) | Tehran-wide average residential transaction price per square metre; reconstructed monthly coverage 1395/01–1403/05 with observation-level PDF provenance. |
| Kilid housing-price history | [Kilid](https://kilid.com/house-prices/tehran) | Collector-validated canonical raw CSV contains 37 complete monthly Tehran listing-price observations from 1402/06–1405/06, backed by immutable page snapshots; incomplete 1405/07 is excluded. Used only after 1403/05 as a chain-linked secondary proxy; common-period similarity to CBI is weak and explicitly flagged. Last source refresh: 2026-10-06. |

## Fixed income — selected source

| Dataset | Reference | What it supports |
|---|---|---|
| اعتماد ETF daily closing-price history | [TSETMC closing-price API](https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/66818022341772870/0) | Sole fixed-income source for 1395/01–1405/05; distribution treatment remains subject to audit. |

Deposit-rate and اخزا alternatives were evaluated and retired. The decision history is
preserved in [FIXED_INCOME.md](FIXED_INCOME.md). Their immutable raw evidence is frozen,
but the sources are absent from active configuration and processing.

## Market source updates

The TEDPIX collector was refreshed on 2026-10-05: 4,298 daily observations through 2026-10-04. The real estate fund comparison uses the same index raw file but has a separately built monthly panel.

## Real estate funds

The independent weekly USD comparison reads the workspace-owned [shared USD/IRR canonical series](../../shared/market_data/README.md) in IRR per USD. Its 2026-10-05 refresh reached 1405/07/12 (2026-10-04). The last complete weekly return ends 2026-10-02. The 24-month source window contains both legacy high/low midpoint and TGJU close observations; the analysis records method counts and excludes the boundary return.

The [TSETMC instrument search](https://cdn.tsetmc.com/api/Instrument/GetInstrumentSearch/) identifies eight funds in the current research universe; the [TSETMC daily closing-price API](https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/67717913151786055/0) supplies daily history (linked example: Danik). The eight identities and coverage are recorded in `data/raw/real_estate_funds/instruments.csv`. Raw instrument histories and immutable search/history response snapshots are stored under `data/raw/real_estate_funds/`. The market-category list was cross-checked against [Fundbase's real estate fund list](https://app.fundbase.ir/categories/%D8%A7%D9%85%D9%84%D8%A7%DA%A9). Distributions and corporate actions have not been audited.

The cumulative chart now uses the TSETMC [adjusted](https://members.tsetmc.com/tsev2/chart/data/Financial.aspx?i=45292762906823004&t=ph&a=1) and [unadjusted](https://members.tsetmc.com/tsev2/chart/data/Financial.aspx?i=45292762906823004&t=ph&a=0) member-chart histories (linked example: Kelid). Eight pairs of exact responses are content-addressed in the project raw archive. Each unadjusted chart history was compared with the canonical daily fund close before its adjusted counterpart entered the derived cumulative series. Kelid, Danik, and Malek Atiyeh have historical adjustments in the current window; a fund with no exchange adjustment is not proof that it made no cash distribution. Fund-level payout records and the exchange's adjustment rules remain to be audited before claiming complete dividend-reinvested total returns.

Payout-record discovery is incomplete. [Agah Group's Kelid announcement](https://www.t.me/s/agahcom?before=8279) states 907 IRR per unit payable from 1404/08/05 (2025-10-27). [Bank Maskan's fund communication](https://t.me/s/abadmaskan?before=647) states 1,283 IRR per Malek Atiyeh unit payable from 1405/03/17 (2026-06-07). Both are entered into the verified payout ledger. A further [Kelid announcement](https://www.t.me/s/agahcom?after=8531) approves 864 IRR per unit for 1405/06, but its [reported 1405/07/14 payment](https://telegram.me/s/bourseiness?q=%23%D8%B5%D9%86%D8%AF%D9%88%D9%82_%D8%A7%D9%85%D9%84%D8%A7%DA%A9) falls after the 2026-10-05 research date and is not realized in this chart. [Arzesh Maskan's disclosure list](https://www.shakhesban.com/markets/fund/%D8%A7%D8%B1%D8%B2%D8%B4%20%D9%85%D8%B3%DA%A9%D9%86) points to a Codal payment schedule, but its attachment was not retrievable in this environment. [Danik's exchange reopening notice](https://www.shakhesban.com/stocks/messages/261692) confirms a cash distribution before 1405/06/02, without a per-unit amount or payment date. These notices establish that adjusted-price equality is insufficient to infer zero payouts. No event is entered without both payment date and cash per unit; the ledger does not yet cover all annual payments.

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
Source-verified extraction adjudications are recorded in `config/housing_cbi_overrides.csv`.
They preserve the original workbook value and cite both the primary report and adjacent official
verification where available. The processed series is regenerated from this layer; the notebook
does not contain housing corrections.
