# Gold ETF NAV Premiums in Iran

## Trading activity refresh (2026-10-17)

The five configured ETFs' TSETMC prices were refreshed through 2026-10-14. Fipiran redemption NAV ends 2026-10-11 for Ayar, 2026-10-12 for Tala/Kahroba/Ganj, and 2026-10-13 for Gohar. The two-year price/NAV tables and five bubble products were rebuilt. The executed [trading activity notebook](notebooks/02_etf_trading_activity.ipynb) ranks mean daily trade count in the common 2026-07-17 to 2026-10-14 window and plots the ranking and trends. Ayar leads with 110,332 transactions per traded day, followed by Tala 23,442, Kahroba 18,169, Ganj 13,715, and Gohar 8,651. This covers the configured five-fund universe. The server database was not checked.
## Live refresh checkpoint (2026-10-13)

Local live collection refreshed the five active ETF price and Fipiran NAV sources, then rebuilt the two-year analysis through 2026-10-12 and all five daily bubble histories. Exact-date NAV matches: Ayar 449/465, Tala 464/465, Kahroba 464/465, Ganj 461/465, Gohar 463/464. Bubble rows: 1,939, 2,183, 1,224, 874, and 2,030 respectively. This is a local research refresh; the separately scheduled server database was not verified in this run.

## Research question

How do liquid Iranian gold ETFs trade relative to same-date redemption NAV, and how unusual is a given premium or discount relative to each fund's own historical distribution?

The project separates three layers that are often mixed together in market-data work: source reliability, the permanent daily research sample, and disposable intraday monitoring. Historical results use daily observations only; live readings are compared with those distributions but are never appended to the historical sample.

## Active universe

The current five-fund research universe is Ayar (`ayar`), Lotus Gold (`tala`), Kahroba (`kahroba`), Ganj (`ganj`), and Gohar (`gohar`). Zarvan does not cover the full two-year research window, and Mesghal is excluded because a validated historical NAV series could not be established.

Fund identity, provider settings, and statistical parameters are versioned in [`config/funds.json`](config/funds.json). Raw histories are isolated by fund under `data/raw/funds/<fund>` and are excluded from Git.

## Data

Daily market prices come from TSETMC. The selected historical redemption NAV series comes from Fipiran for all five active funds. Source responses are archived as immutable, content-addressed evidence before parsing, and canonical CSVs are updated only by validated collectors.

The local two-year build ending 2026-10-17 has the following exact-date price/NAV matches, independently recounted for the application review:

| Fund | Matched trading dates | Candidate trading dates |
|---|---:|---:|
| Ayar | 444 | 462 |
| Tala | 460 | 462 |
| Kahroba | 459 | 462 |
| Ganj | 456 | 462 |
| Gohar | 460 | 461 |

The five full historical local bubble files contain **8,253 matched fund-day observations**, ending October 11–13 by fund. This is distinct from the two-year window and the separately maintained PostgreSQL store, whose current state was not checked. See the [research summary](reports/RESEARCH_SUMMARY.md) and [`docs/STATUS.md`](docs/STATUS.md).

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

The NAV-reliability audit is part of the empirical result rather than a preprocessing footnote. At the September 29 audit checkpoint, saved Tala, Kahroba, and Ganj Fipiran observations were corroborated on shared two-year dates by the available manager records. That window had one missing Kahroba trading NAV and three missing Ganj NAVs; current window coverage is reported above. Gohar had three manager disagreements, including a material September 9 conflict and a large unit-count change on September 27. The October presentation review did not extend this provider audit.

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
python commodity/gold/build_two_years.py --as-of 2026-10-17
python commodity/gold/refresh.py --fund ayar
python commodity/gold/refresh.py --fund tala
python commodity/gold/refresh.py --fund kahroba
python commodity/gold/refresh.py --fund ganj
python commodity/gold/refresh.py --fund gohar
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
