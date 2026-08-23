# Documentation Integration Prompt

Use the following prompt when asking another model to incorporate this reconnaissance into a
larger project document:

> Update the Iran Energy Exchange research documentation using the attached market-access
> inventory as the authoritative evidence for the 2026-08-22 reconnaissance checkpoint. Write in
> formal academic English. Preserve the distinction between legal market classifications and the
> four engineering data domains: physical auctions, electricity markets, certificates, and
> derivatives. Report 21 certificate symbols (8 commodity deposits, 2 renewable-electricity
> production certificates, 10 energy-saving certificates, and 1 cash capacity certificate) and
> 71 observed derivative symbols (50 salaf/standard parallel-salaf and 21 futures). State that the
> resulting observed listed-instrument inventory is 92 symbols, but qualify the derivative count
> as an observed minimum because public search results may be capped. Report certificate coverage
> from 2019-04-17 through 2026-08-19, salaf coverage from 2016-02-09, futures coverage from
> 2023-05-31, and individually addressable physical auctions from 2013-07-31 through current
> August 2026 offers. Explain that daily-history rows are not necessarily positive-trading days.
> Document the seven deposit-certificate underlyings: heavy crude oil, gas condensate, naphtha,
> full-range naphtha, LHC, ethanol, and renewable-electricity production. Preserve the observed
> `صگاز04او` versus `0512` metadata inconsistency as a validation issue. Describe the public
> access routes conceptually without inventing undocumented guarantees. Emphasize immutable raw
> payloads, separate auction/specification/trade tables, ID-based historical auction backfill,
> conservative rate limiting, retries, schema validation, provenance, and atomic incremental
> updates. Do not claim complete option-market coverage; state only that no Energy Exchange option
> instrument was discovered. Do not fabricate observations, dates, endpoints, or market rules.
