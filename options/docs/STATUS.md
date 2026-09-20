# Status — 2026-09-20

TSETMC discovery verified 996 unique Ahrom option InsCodes: 84 active and 912 expired
as of 2026-09-20. The earliest expiration found is 2022-09-21. The broad TSETMC search
returns at most 40 rows; targeted searches can retrieve an expired contract. Recursive
numeric-prefix search and current option market watch are used for discovery. All 996
candidates passed TSETMC identity, issuer, name, and option-type checks. The verified
underlying InsCode is `17914401175772326`. This is the discovered universe, not proof
that TSETMC indexes every contract ever listed.
The exact-byte discovery archive contains 142 search responses, the option market watch,
and 996 instrument-identity responses, with no recapture failures. The final archive
integrity check verified 3,076 referenced snapshots with no hash mismatch.

OptionBaaz period probes on an expired and an active contract returned HTTP 200 for
`3m`, `6m`, and `1y`. Parameters `1m`, `2y`, `3y`, `5y`, `max`, and `all` returned HTTP 400
with the API message listing those three allowed values. For the expired sample
`طهرم3029`, `1y` returned 12 points from 2026-02-25 to 2026-06-17; `6m` returned 11;
`3m` returned zero. For active `ضهرم7051`, all accepted periods returned 38 points from
2026-07-25 to 2026-09-20. Full earlier history remains unverified.
Adding `endDate=2026-03-01` or `page=2` to the expired sample's `1y` request did not
change its 12 returned points; those parameters are not established pagination routes.

The 2026-09-20 bulk run attempted all 996 OptionBaaz contracts. It obtained 374 valid
responses, of which 335 contain daily points; 622 contracts returned HTTP 404. No
identity, symbol, strike, or type mismatch entered the panel. TSETMC daily histories
provide first/last dates for 990 contracts; six returned empty histories. The earliest
TSETMC available date is 2022-05-21 for `ضهرم6000`; the earliest expiration is
2022-09-21 for `ضهرم6011`.

The OptionBaaz panel contains 8,903 contract-date rows from 2025-12-17 through
2026-09-20. It has no duplicate `(ins_code, date)` keys. CSV and Parquet have equal
row counts. There are no OptionBaaz observations for contracts expiring in 2022,
2023, or 2024, although TSETMC discovered 346 such contracts. Of the 2025 expiries,
only 23 contracts have OptionBaaz rows. Earlier OptionBaaz history remains a material
coverage gap; the `1y` parameter did not yield full contract lifetimes.

The quality report flags, without dropping observations, 1,413 zero-IV rows (15.87%),
733 rows with IV above 2 (8.23%), 59 zero-volume rows (0.66%), 280 close/end-price
gaps above 50% (3.15%), 31 conservative intrinsic-value violations (0.35%), and
25 inconsistent OHLC rows (0.28%). No panel row lacks an exact-date underlying
price. These are diagnostic flags, not corrected prices.
