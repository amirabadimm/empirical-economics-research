# Bitumen Warehouse-Receipt Certificate: Research Workflow

Last reviewed: 2026-08-15

## Research objective

The bitumen project is an underlying-selection study. Its purpose is to identify the physical
grade, market, producer, delivery conditions, and settlement terms that are economically
comparable with the warehouse-receipt certificate before any valuation benchmark is approved.

## Current stage

| Source | Coverage |
|---|---|
| Certificate | Through 2026-08-02 |
| Broad physical bitumen market | Through 1405/05/12 |

Broad raw collection is complete, but the comparable physical underlying remains unresolved. No
processed benchmark or certificate bubble is approved.

## Architecture and collection

The certificate wrapper uses the shared CDC collector with explicit bitumen identities. The
physical collector archives complete official IME monthly responses before filtering and retains
the broad bitumen source scope. Collectors are incremental, idempotent, and atomic. Raw files and
immutable snapshots are never changed by notebooks or processing scripts.

## Required comparability decision

Before benchmark construction, research must establish:

- the certificate's exact deliverable grade and specification;
- eligible physical-market grade labels and symbols;
- producer and delivery-location comparability;
- contract and settlement eligibility;
- unit consistency and any required quality adjustment;
- sufficient exact-date or defensible temporal coverage.

Cash and cash-matching transactions are the default candidates. Credit, forward, and cash/credit
observations must not be mixed with cash prices without an explicit financing and maturity model.
Positive price and quantity are required for every analytical observation.

## Governance rules

- Preserve all broad source rows in raw data.
- Apply grade and contract decisions only in derived layers.
- Record every exclusion with a stable source field or symbol.
- Keep source snapshots immutable and outside Git.
- Do not create a production benchmark until the delivery specification is matched explicitly.
- Update the README, workflow, and repository status after any approved scope change.

## Next step

Obtain and document the official certificate specification, map it to physical-market grades and
delivery terms, quantify eligible liquidity, and submit the candidate basket for approval. Only
then should the project build a daily processed benchmark and certificate premium/discount series.
