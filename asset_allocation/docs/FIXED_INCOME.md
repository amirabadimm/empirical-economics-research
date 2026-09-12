# Fixed-income source decision

## Selected asset

The project uses only the exchange-traded fixed-income fund اعتمادآفرین پارسیان
(ticker `اعتماد`, TSETMC instrument `66818022341772870`) for the research window
1395/01 through 1405/05.

The canonical raw table is `data/raw/fixed_income/etf/etemad.csv`. The collector is
`src/asset_allocation/collectors/tsetmc_fixed_income.py`; immutable API responses are
stored by SHA-256 under `data/raw/fixed_income/etf/tsetmc_snapshots/`.

## Data and monthly construction

TSETMC supplies daily reference and trading observations. The canonical table retains
the Gregorian source date, closing, last, previous, first, low and high prices in IRR,
trade count, volume, value, and `has_trade`. Zero-volume reference rows remain in raw
evidence but are excluded when selecting investable month-end observations.

For each Jalali month, select the final row satisfying `has_trade=true`. The monthly
price return is:

```text
monthly_return_t = closing_price_t / closing_price_(t-1) - 1
```

The first return in 1395 requires the final traded close from Esfand 1394 as its
opening observation. All twelve months of 1395 contain traded observations. The raw
history begins on 2015-03-14 and extends beyond the research cutoff, so the collector
must filter derived outputs to 1395/01–1405/05 without truncating raw evidence.

## Alternatives evaluated and removed

Earlier work separately evaluated CBI one-year deposit rates, World Bank deposit-rate
data, Iranian announced deposit-policy schedules, and اخزا as possible proxies. They
were rejected from the active project because the revised research window is fully
covered by اعتماد and mixing deposits, debt instruments, and a traded fund would create
instrument and return-definition changes inside one asset series.

On 2026-09-09, the CBI deposit collector and all active configuration and workflow
references to alternative proxies were removed with user authorization. Workspace policy
requires immutable raw source evidence to remain unchanged, so the historical
`data/raw/fixed_income/bank_deposits/` branch is frozen in place. No deposit or اخزا
observation participates in the active dataset, configuration, or future analysis.

## Return treatment and remaining audit

The issuer states that اعتماد has no periodic distribution and that earnings accumulate in unit
value. The canonical panel therefore calculates investor market-price returns from adjacent final
traded monthly closes. Because the available statement does not independently prove that this
policy was unchanged throughout 1395–1405/05, every اعتماد observation remains flagged
`provisional_distribution_policy_audit` until the full historical policy and corporate-action
record are verified.
