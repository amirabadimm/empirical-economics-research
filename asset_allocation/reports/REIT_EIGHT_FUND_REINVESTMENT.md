# Eight Iranian REITs: hypothetical dividend reinvestment

Generated from the canonical raw traded-close CSVs and the user-supplied event ledger. Market data end 2026-10-07 for all eight funds. The latest common valid traded date is 2026-10-07.

This is a hypothetical first-traded-session-after-event model. Cash is assumed immediately available; fractional units are allowed. There are no fees, spread, taxes, or slippage. The results are provisional because historical dividend coverage is not complete.

## Since-inception comparison

| Fund | First trade | Last trade | Last close IRR | Price return | Holding return | Hypothetical reinvested return | Events | Identified IRR/unit | Status |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Arzesh Maskan | 2022-10-18 | 2026-10-07 | 40,986 | 309.9% | 313.0% | 313.9% | 1 | 310 | dividend history incomplete |
| Danik | 2023-08-01 | 2026-10-07 | 17,235 | 72.4% | 108.1% | 127.1% | 2 | 3,574 | dividend history incomplete |
| Amin Shahr | 2023-12-18 | 2026-10-07 | 20,920 | 109.2% | 117.3% | 119.7% | 5 | 805 | provisional dates and history incomplete |
| Malek Atiyeh | 2024-04-23 | 2026-10-07 | 13,355 | 33.5% | 59.0% | 62.7% | 3 | 2,548 | dividend history incomplete |
| Kelid | 2024-09-28 | 2026-10-07 | 18,338 | 83.4% | 101.1% | 109.9% | 2 | 1,771 | dividend history incomplete |
| Kashaneh | 2025-05-12 | 2026-10-07 | 14,750 | 47.5% | 47.5% | 47.5% | 0 | 0 | unverified dividend history |
| Kakh | 2026-02-22 | 2026-10-07 | 13,565 | 35.6% | 35.6% | 35.6% | 0 | 0 | unverified dividend history |
| Emarat Dey | 2026-05-13 | 2026-10-07 | 14,609 | 46.1% | 46.1% | 46.1% | 0 | 0 | unverified dividend history |

Returns use each fund's own first valid traded close and are therefore not common-period rankings. The processed comparison CSV also contains three-month, one-year, two-year, and annualized estimates where enough history exists.

## Included dividend events

| Fund | Event | Jalali model date | First later trade | IRR/eligible unit | Eligible units | Assumed cash IRR | Date status |
|---|---|---|---|---:|---:|---:|---|
| Arzesh Maskan | arzesh_1405 | 1405/03/03 | 2026-05-25 | 310 | 1.000000 | 310.00 | verified |
| Danik | danik_1404 | 1404/05/28 | 2025-08-20 | 1,800 | 1.000000 | 1,800.00 | verified |
| Danik | danik_1405 | 1405/05/31 | 2026-08-24 | 1,774 | 1.161827 | 2,061.08 | verified |
| Amin Shahr | amin_1403_10 | 1403/10/08 | 2024-12-29 | 65 | 1.000000 | 65.00 | provisional_date |
| Amin Shahr | amin_1404_05 | 1404/05/01 | 2025-07-26 | 126 | 1.005176 | 126.65 | provisional_date |
| Amin Shahr | amin_1404_08 | 1404/08/21 | 2025-11-15 | 100 | 1.013882 | 101.39 | provisional_date |
| Amin Shahr | amin_1404_10 | 1404/10/06 | 2025-12-28 | 203 | 1.020261 | 207.11 | provisional_date |
| Amin Shahr | amin_1405_03 | 1405/03/27 | 2026-06-20 | 311 | 1.032867 | 321.22 | provisional_date |
| Malek Atiyeh | malek_1404 | 1404/02/31 | 2025-05-24 | 1,176 | 1.000000 | 1,176.00 | verified |
| Malek Atiyeh | malek_1405 | 1405/03/05 | 2026-05-30 | 1,283 | 1.098468 | 1,409.33 | verified |
| Malek Atiyeh | malek_1405_supp | 1405/05/14 | 2026-08-08 | 89 | 1.098468 | 97.76 | provisional_date |
| Kelid | kelid_1404 | 1404/07/16 | 2025-10-11 | 907 | 1.000000 | 907.00 | verified |
| Kelid | kelid_1405 | 1405/06/25 | 2026-09-19 | 864 | 1.087380 | 939.50 | verified |

The Danik 1404 event date is 1404/05/28 as supplied here; it supersedes the earlier project entry of 1404/05/27. Amin Shahr's five dates are reported distribution dates, not verified assembly dates. The zero entry on 1404/08/20 was excluded. Malek Atiyeh's supplementary 89 IRR uses the quantity eligible at its 1405 annual assembly; it is not a fresh entitlement for units acquired later. The 1403/12/08 Arzesh, 1405/04/28 and 1405/06/02 Kakh, and 1405/05/17 Emarat Dey decisions did not document a cash dividend. Kashaneh's 1404 and 1405 distribution history remains unverified. No missing dividend is treated as a confirmed zero.

Source status: amounts and event descriptions are supplied in the user's project instructions; original source documents were not attached here. The positive amounts enter the hypothetical model as instructed, while independent source verification and historical completeness remain open. Actual payment dates are deliberately unused.

## Market data checks

| Fund | Raw rows | Traded rows | Nontrading rows | Gaps over 14 days | Absolute price jumps over 30% |
|---|---:|---:|---:|---:|---:|
| Arzesh Maskan | 955 | 874 | 81 | 3 | 0 |
| Danik | 767 | 664 | 103 | 3 | 0 |
| Amin Shahr | 670 | 573 | 97 | 4 | 0 |
| Malek Atiyeh | 587 | 483 | 104 | 3 | 0 |
| Kelid | 493 | 419 | 74 | 2 | 0 |
| Kashaneh | 339 | 265 | 74 | 2 | 0 |
| Kakh | 148 | 107 | 41 | 1 | 0 |
| Emarat Dey | 98 | 56 | 42 | 1 | 0 |

All raw series had zero duplicate dates and zero nonpositive closes. Gaps and jumps are review flags, not automatic errors or filled observations. Market charts break lines at gaps exceeding 14 days. The exchange-adjusted price archive ends 2026-10-04, three calendar days before the raw price archive. Its separate since-reference-start returns and dates appear in the comparison CSV; it was not used to calculate dividend-reinvested returns.

Weekly correlations use Friday-ending observed weeks, require at least 12 paired returns, and do not fill missing weeks. Risk uses the sample standard deviation of observed weekly returns times the square root of 52; short histories need caution. See the processed correlation and risk CSVs.

The earlier four-fund notebook and English/Persian report sources contain fixed narrative or layout assumptions and are superseded for current eight-fund dividend results. They must be revised before reuse. The eight PNG charts in outputs/reit_dividend_comparison are the current slide assets.
