# Gold ETF NAV Premiums in Iran

## Research question

How do liquid Iranian gold ETFs trade relative to same-date redemption NAV, and how unusual is a given premium or discount relative to each fund's own historical distribution?

The project separates three layers that are often mixed together in market-data work: source reliability, the permanent daily research sample, and disposable intraday monitoring. Historical results use daily observations only; live readings are compared with those distributions but are never appended to the historical sample.

## Active universe

The current five-fund research universe is Ayar (`ayar`), Lotus Gold (`tala`), Kahroba (`kahroba`), Ganj (`ganj`), and Gohar (`gohar`). Zarvan does not cover the full two-year research window, and Mesghal is excluded because a validated historical NAV series could not be established.

Fund identity, provider settings, and statistical parameters are versioned in [`config/funds.json`](config/funds.json). Raw histories are isolated by fund under `data/raw/funds/<fund>` and are excluded from Git.

## Data

Daily market prices come from TSETMC. The selected historical redemption NAV series comes from Fipiran for all five active funds. Source responses are archived as immutable, content-addressed evidence before parsing, and canonical CSVs are updated only by validated collectors.

The September 29 two-year rebuild produced the following exact-date price/NAV matches:

| Fund | Matched trading dates | Candidate trading dates |
|---|---:|---:|
| Ayar | 448 | 465 |
| Tala | 465 | 465 |
| Kahroba | 464 | 465 |
| Ganj | 462 | 465 |
| Gohar | 464 | 464 |

The server-side daily refresh subsequently expanded the full historical PostgreSQL store to more than 8,000 matched bubble observations across the five ETFs. Current operational counts and coverage belong in [`docs/STATUS.md`](docs/STATUS.md), not in the headline research claim.

## Method

For fund \(i\) on date \(t\), the daily premium or discount is

```text
bubble_pct = 100 * (unadjusted_close_irr / redemption_nav_irr - 1)
```

Positive values are premiums and negative values are discounts. Both inputs are per-unit IRR values. The research sample uses only positive-volume, positive-trade-count sessions with an exact same-date redemption NAV. There is no NAV interpolation, carry-forward, smoothing, or adjusted-price substitution.

The project reports historical ranks in several forms:

- expanding equal-weight percentile and decile;
- recent-weighted percentile using a 90-calendar-day half-life;
- rolling one-year equal-weight percentile and decile;
- rolling six-month equal-weight percentile and decile;
- rolling two-year equal-weight percentile and decile, bounded no earlier than 2024-01-01.

Percentile ties use `<=`. These are empirical historical ranks, not probabilities of mean reversion or trading signals.

## Data-quality findings

The NAV-reliability audit is part of the empirical result rather than a preprocessing footnote. Saved Tala, Kahroba, and Ganj Fipiran observations are corroborated on shared two-year dates by the available manager records. Kahroba has one missing trading NAV and Ganj has three. Gohar has three manager disagreements, including a material September 9 conflict and a large unit-count change on September 27.

Ayar's selected Fipiran history contains gaps but agrees with the saved TSETMC comparison on all 337 shared traded dates in the audited two-year window. That provider agreement is evidence about consistency, not an independent portfolio valuation.

Detailed validation is documented in [`docs/NAV_RELIABILITY.md`](docs/NAV_RELIABILITY.md). The unsuccessful Mesghal historical-NAV investigation is documented separately in [`docs/MESGHAL_NAV_VALIDATION.md`](docs/MESGHAL_NAV_VALIDATION.md).

## Interpretation and limitations

This is an ex-post price-versus-NAV comparison. Historical NAV publication timestamps are not available, so the daily series should not be interpreted as a vintage-safe intraday trading signal. A same-date match establishes valuation-date alignment, not simultaneous observability.

Provider timing and valuation basis can differ. For that reason, the five funds are not collapsed into a single pooled premium series without preserving fund and provider identity. Missing NAV dates remain missing rather than being silently filled.

## Reproduction

From the repository root:

```bash
python commodity/gold/collect_daily.py
python commodity/gold/collect_fipiran_nav.py
python commodity/gold/build_two_years.py --as-of 2026-09-28
python commodity/gold/refresh.py
```

Use `--fund <key>` to restrict collection to one ETF and `--full` when a complete source-history refresh is required. Successful source responses are archived before parsing, and collectors alone modify canonical raw CSVs.

## Outputs

Key research and presentation outputs include:

- `data/processed/bubble/ayar_nav_bubble.csv` — exact-date Ayar price/NAV premium history;
- `data/processed/bubble/ayar_bubble_distribution.csv` — signed bubbles with chronological empirical ranks;
- `notebooks/01_ayar_nav.ipynb` — read-only interactive analysis;
- PostgreSQL tables and views for five-fund daily history, current disposable readings, and daily reference distributions.

The database schema, loader, Docker environment, retention rules, and scheduled monitoring are documented in [`db/README.md`](db/README.md). Those deployment details are intentionally separated from the empirical research summary.

## Operational status

The PostgreSQL workflow is deployed on Ubuntu with scheduled daily refresh, weekly reconciliation, and a five-minute disposable monitor during the configured Tehran trading window. Runtime state, secrets, logs, collected raw evidence, and database volumes remain outside Git by design.

For the exact current data checkpoint and verification history, see [`docs/STATUS.md`](docs/STATUS.md) and [`docs/WORKFLOW.md`](docs/WORKFLOW.md).
