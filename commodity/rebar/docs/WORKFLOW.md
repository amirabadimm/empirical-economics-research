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
  reserved for certificate-only derivatives; `processed/bubble` is reserved for future bubbles.
- `src/rebar/collectors` owns source acquisition; `src/rebar/processing` will own deterministic derived builders when a specification is approved.
- Notebooks may inspect data but must never modify canonical raw data.

The active notebook uses `shared/notebook_tools/commodity_dashboard.py` for the standard read-only,
responsive Plotly presentation pattern with a neutral dashboard background, white plot panels,
consistent typography, and accessible grid contrast. Goods-type counts use all canonical physical rows and no certificate goods
taxonomy is invented. Bubble visualization reads only an existing validated processed bubble CSV;
therefore Rebar currently reports that no bubble is available.

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

No bubble builder is active. Historical launch notices describe A3 / 18 mm rebar, but current
official warehouse and continuous-contract documentation must still establish grade, diameter,
standard, lot conversion, eligible warehouse and producer, delivery timing, taxes, storage and
transaction fees, and quotation units.

The required architecture is three separate datasets: canonical certificate records, canonical
physical records, and—only after analytical approval—a derived bubble table. A bubble table must
never replace or act as the storage location for either source dataset.
