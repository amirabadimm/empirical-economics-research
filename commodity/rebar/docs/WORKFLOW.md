# Steel Rebar Physical-Market Workflow

Last reviewed: 2026-08-29

## Objective and boundary

This project collects official Iran Mercantile Exchange (IME) physical-market and continuous-
certificate observations for steel rebar. It defines an exploratory A3 / 12 mm physical screen,
but no certificate/physical comparison or approved homogeneous benchmark.

Rebar can vary materially by standard, diameter, grade, producer, bundle/lot terms, warehouse or delivery location, tax and quotation basis, contract type, settlement condition, and currency. None of these characteristics may be silently pooled in a derived series.

## Source contract

- Official landing page: `https://www.ime.co.ir/offer-stat.html`
- Official endpoint: `https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList`
- Request grain: one Jalali calendar month per request.
- Canonical raw CSV: `data/raw/physical/rebar_physical_raw.csv`
- Shared immutable source responses: `shared/data/raw/ime/physical/ime_physical_YYYY-MM_SHA256.json.gz`
- Frozen legacy responses: `data/raw/physical/api_snapshots/physical_YYYY-MM_TIMESTAMP.json.gz`
- Raw selection: every response row for which normalized `GoodsName` identifies rebar.

The collector retains zero-trade offers and all source fields. It never changes the source values or removes a row because of a later analytical preference.

## Collection procedure

`src/rebar/collectors/physical.py` is the commodity-specific wrapper around `shared/ime_data/ime_physical_collector.py`.

1. Each requested month is fetched from the official endpoint after a landing-page session warmup.
2. The complete outer API response is compressed and archived with request payload, source URL, and UTC retrieval timestamp.
3. Only the documented broad rebar rows are copied into the canonical CSV; schema and scope are validated before writing.
4. Refreshes replace only the selected trailing months in the canonical CSV, preserving all older rows. The CSV is written to a sibling temporary file and atomically replaced only after validation succeeds.

The first run begins at 1386/01. Subsequent runs refresh the current month and two prior Jalali months. New full-market responses are content-addressed in the shared archive. `--rebuild-from-snapshots` chooses the newest shared or frozen legacy response for each month and modifies no snapshot.

## Data architecture and validation

- `data/raw` contains the canonical raw CSV and frozen pre-consolidation snapshots; new complete responses belong to the shared archive.
- `data/interim` may hold reproducible temporary cleaning/alignment stages.
- `data/processed/physical` holds approved physical derivatives; `processed/certificate` is
  reserved for certificate-only derivatives; `processed/bubble` holds reproducible comparison tables.
- `src/rebar/collectors` owns source acquisition; `src/rebar/processing` will own deterministic derived builders when a specification is approved.
- Notebooks may inspect data but must never modify canonical raw data.

The active notebook uses `shared/notebook_tools/commodity_dashboard.py` for the standard read-only,
responsive Plotly presentation pattern with a neutral dashboard background, white plot panels,
consistent typography, and accessible grid contrast. Goods-type counts use all canonical physical rows and no certificate goods
taxonomy is invented. Bubble visualization reads only the reproducible processed bubble CSV and
does not calculate or repair a comparison in the notebook.

The shared collector validates the complete expected IME schema and verifies that every canonical row still passes the rebar scope predicate. It preserves source date, unit, price, quantity, value, contract, settlement, and provenance fields. Calendar conversion, numeric-unit validation, and identity/uniqueness requirements must be specified and tested before a benchmark is built.

## Decision gates before analytical pricing

Any future physical benchmark must document and test: (1) exact product/standard, grade, diameter, and packaging comparability; (2) eligible producers, symbols, delivery terms, warehouse/location, and market segment; (3) unit and quotation basis, including tax and other fees where relevant; (4) contract type and settlement treatment, with forward and credit terms handled explicitly; (5) zero-trade treatment, positive quantity/price/value rules, daily aggregation method, and composition diagnostics; and (6) date alignment and any external/certificate source contract, if such a comparison is added.

## Active exploratory A3 / 12 mm chart scope

For the initial homogeneous-product visualization, `build_a3_12_cash_daily.py` retains plainly
specified straight `A3 / 12 mm` rebar labels, whether written as grade-before- or grade-after-
diameter. It excludes baskets, coil, alloy, short-length, mixed-product, simple/industrial, and
multi-diameter labels. Eligible rows additionally require a cash or cash-matching `ContractType`,
and positive `Quantity`, `Price`, and `ArzeBasePrice`.

The builder writes `data/processed/physical/rebar_a3_12_cash_daily.csv` atomically. Each Jalali-date row
contains cash trade and offer-base VWAPs using identical executed-quantity weights **only after**
the strict A3 / 12 mm product and cash-contract filter has been applied. It also retains the
source goods names, contract types, symbols, and producer audit fields. The percentage difference
is `100 × (cash / offer base − 1)`. This is an exploratory visualization scope—not an approved economic benchmark—because
producer, standard, delivery, and quotation-basis comparability have not yet been established.

## Continuous certificate

The certificate source is `https://dataapi.ime.co.ir/api/CDC/CDCTrades`, market ID `22`,
commodity ID `29`, exact description `گواهی سپرده پیوسته میلگرد`, and continuous codes
`CD1RBR0001` then `SteelRebar`. Canonical data is stored at
`data/raw/certificate/rebar_certificate_raw.csv`; immutable responses are archived under
`data/raw/certificate/api_snapshots`. The shared collector validates identity, schema,
nonnegative values, traded-day VWAP, unique dates, and writes atomically. It retains zero-trade
records and does not transform the canonical source fields.

### Exploratory exact-date bubble contract

`src/rebar/processing/build_a3_18_exact_bubble.py` implements the deliberately narrow first
comparison. Physical eligibility requires a label parsed as exactly one grade and diameter—A3 and
18 mm—while excluding baskets, coil, alloy, short-length, mixed, simple/industrial, and other
multi-product labels. It then requires a cash or cash-matching contract, rial currency, tonne unit,
and positive executed quantity and price. Eligible same-day rows are aggregated by executed-
quantity VWAP.

Positive-volume certificate records are joined to physical observations only when their Gregorian
dates are identical. The output formula is
`100 × (certificate TodaySettlementPrice / physical Price VWAP − 1)`. No interpolation, as-of
carry, forward-contract pooling, producer substitution, or delivery/storage/tax/fee adjustment is
applied. The output retains Jalali and Gregorian dates, both prices, both activity measures,
physical goods names, symbols, contracts, producer count and names, certificate code, price
difference, percentage bubble, and alignment method.

The builder writes `data/processed/bubble/rebar_a3_18_exact_date_bubble.csv` atomically. The current
table has 5 observations from 2026-03-15 through 2026-05-26, all anchored by Isfahan Steel cash
physical trades. Historical launch descriptions identify the certificate as A3 / 18 mm; however,
the current official warehouse specification must still establish standard, lot conversion,
eligible producer/warehouse, delivery timing, taxes, storage and transaction fees, and quotation
basis. Consequently this is an exploratory gross quoted-price diagnostic, not an approved economic
benchmark.

### Intentional A3 / 12 mm sensitivity series

`src/rebar/processing/build_a3_12_exact_bubble.py` reuses the exact same validated engine but
changes the physical predicate to strict straight A3 / 12 mm. The output is
`data/processed/bubble/rebar_a3_12_exact_date_bubble.csv`, with 46 exact-date observations from
2025-11-12 through 2026-08-26. Its formula is
`100 × (certificate TodaySettlementPrice / A3/12 physical cash Price VWAP − 1)`.

Because the certificate launch description identifies A3 / 18 mm rather than A3 / 12 mm, every
row carries `comparability_status=intentional_cross_diameter_diagnostic_not_underlying_match` and
`alignment_method=exact_date_observed_cash_a3_12_cross_diameter`. This series is a requested
sensitivity/nearby-product diagnostic, never the primary underlying comparison. No diameter
equivalence is inferred.

The required architecture is three separate datasets: canonical certificate records, canonical
physical records, and a reproducible derived bubble table. A bubble table must
never replace or act as the storage location for either source dataset.
