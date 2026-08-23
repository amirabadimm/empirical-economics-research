# Iran Energy Exchange Public-Data Access Inventory

Assessment date: 2026-08-22

## Purpose and scope

This note records a read-only reconnaissance of public Iran Energy Exchange data exposed through
the TSETMC interfaces. The exercise tested discoverability, record-level access, historical
coverage, and the principal limitations that must inform collector design. API responses were
held in memory and were not persisted.

The inventory is an empirical access assessment, not a legal classification of Iran Energy
Exchange markets. For data-engineering purposes, the accessible material is organized into four
domains: physical auctions, electricity markets, certificates, and derivatives.

## Summary of accessible domains

| Data domain | Accessible objects | Earliest observed date | Latest observed date | Current assessment |
|---|---|---:|---:|---|
| Physical auctions | Offer lists, auction specifications, auction trades, instrument-level trades | 2013-07-31 | Current offers in August 2026 | Accessible; historical discovery requires ID traversal |
| Electricity markets | Retail/physical, green, and free-electricity offers; overview and selected trade feeds | Not yet fully backfilled | Current offers in August 2026 | Accessible, with segment-specific endpoint behavior |
| Certificates | 21 symbols in four families | 2019-04-17 | 2026-08-19 | All 21 discovered symbols returned history |
| Derivatives | 50 salaf and 21 futures symbols in the observed search inventory | 2016-02-09 | 2026-08-19 | All 71 observed symbols returned history |

The observed listed-instrument inventory therefore contains 92 non-physical symbols: 21
certificates and 71 derivatives. The certificate count is complete under the tested multilingual
name-search contract. The derivative count is an observed minimum because broad TSETMC searches
may be capped and product-specific query expansion may reveal additional expired instruments.

## Certificate market

### Instrument families and coverage

| Family | Symbols | Earliest daily record | Latest daily record | Aggregate daily records |
|---|---:|---:|---:|---:|
| Commodity deposit certificates | 8 | 2023-01-18 | 2026-08-19 | 2,550 |
| Renewable-electricity production certificates | 2 | 2025-11-11 | 2026-08-19 | 279 |
| Energy-saving certificates | 10 | 2024-05-20 | 2026-08-19 | 2,467 |
| Cash capacity certificate | 1 | 2019-04-17 | 2026-08-19 | 1,757 |
| **Total** | **21** | **2019-04-17** | **2026-08-19** | **7,053** |

Daily-record counts describe rows returned by the TSETMC closing-price history endpoint. They do
not imply that every row contains a positive transaction. Trading-day eligibility must be defined
from price, volume, value, and trade-count fields during processing.

### Deposit-certificate underlyings

The ten commodity/production deposit symbols represent seven distinct underlyings:

1. heavy crude oil;
2. gas condensate;
3. naphtha;
4. full-range naphtha;
5. light hydrocarbon cut (LHC);
6. ethanol; and
7. renewable-electricity production.

Heavy crude oil, gas condensate, and renewable electricity each have two observed maturities or
series. The remaining underlyings have one observed symbol each.

### Energy-saving structure

The ten observed energy-saving symbols comprise electricity during peak periods, electricity
during ordinary periods, natural gas during peak and off-peak periods, and gasoil/diesel. Series
or maturity suffixes must remain part of symbol identity. One metadata inconsistency requires
special treatment: symbol `صگاز04او` is paired with a displayed instrument name ending in `0512`.
The collector must preserve both raw fields and must not silently reconcile them.

## Derivatives

| Family | Observed symbols | Earliest daily record | Latest daily record | Aggregate daily records |
|---|---:|---:|---:|---:|
| Salaf and standard parallel-salaf contracts | 50 | 2016-02-09 | 2026-08-19 | 13,469 |
| Futures contracts | 21 | 2023-05-31 | 2026-08-19 | 1,842 |
| Options | 0 discovered | — | — | — |
| **Total observed** | **71** | **2016-02-09** | **2026-08-19** | **15,311** |

Observed derivative products include electricity, crude oil, gas condensate, hydrocarbon cuts,
and methanol. No Energy Exchange option instrument was returned by the tested Persian-name
queries. This is evidence of non-discovery, not proof that options have never been admitted.

## Physical-auction market

The current TSETMC frontend exposes lists for upcoming (`ready`), active (`active`), surplus
(`mazad`), and completed (`ended`) auctions. Separate endpoints expose auction specifications,
auction-level trades, and instrument-level trade events. Tested fields include product and
commercial descriptions, producer and supplier, auction date, domestic/export target market,
delivery and settlement terms, packaging, units, offered volume, base and authorized prices,
discovered price, traded quantity, weighted-average price, delivery location, destination, and
broker information.

Auction ID 1 returned a record dated 2013-07-31, while current discovery returned auction IDs
above 94,000 in August 2026. A current light-naphtha example returned auction metadata, three
auction-trade records, and 588 instrument-trade records. The completed-auction list was empty at
the assessment time even though old records remained individually addressable. A historical
collector should therefore traverse validated auction IDs, tolerate gaps, and checkpoint its
high-water mark rather than depend on a single completed-auction listing.

Some fields require semantic validation. In the tested surplus light-naphtha record,
`tradedQuantity` and `wap` were zero while associated trade endpoints returned rows. Raw auction,
auction-trade, and instrument-trade payloads must therefore be preserved as separate tables until
their event semantics are established.

## Electricity market

The public frontend distinguishes ordinary/retail electricity, green electricity, and free
electricity through separate auction segments. Offer discovery succeeded for all three. The
ordinary power overview endpoint responded, and the standard parallel-salaf electricity trade
feed returned current records. At the assessment time, the free-electricity feed returned an
empty result and the green-electricity summary/feed produced an error on one tested route.

These results support collection through a combination of auction, instrument-history, and trade
feed endpoints. They do not support an assumption that one endpoint behaves uniformly across all
electricity segments. Each segment requires an explicit source contract and an independent
availability test.

## Access and reproducibility assessment

Public access is sufficient to design collectors for all four domains. The service is
unauthenticated in the tested environment, but it is undocumented and should not be treated as a
stable contractual API. A production collector must use conservative request rates, bounded
retries with backoff, schema validation, response archiving, and atomic canonical updates.

The initial collection architecture should comprise:

1. an instrument registry keyed by `insCode`, official symbol, series, and instrument family;
2. a daily instrument-history collector for certificates and derivatives;
3. an auction-list monitor for current physical and electricity offers;
4. an ID-based auction backfill collector for historical physical-market coverage;
5. separate raw tables for auction specifications, auction trades, and instrument trades; and
6. source-health checks for every electricity segment and endpoint family.

No analytical joining should occur in the raw layer. Calendar conversion, normalization of
Persian and Arabic characters, family classification, maturity parsing, and positive-trade
filtering belong in interim processing while original identifiers and text remain available for
audit.
