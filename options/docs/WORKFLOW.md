# Workflow

`scripts/run_pipeline.py discover` searches TSETMC for both Ahrom option symbol families.
The search API caps broad results at 40, so a capped numeric prefix is divided into ten
longer searches until each branch is uncapped. The current option market watch supplies
additional InsCodes with a direct `uaInsCode` relationship. Every candidate is checked
against TSETMC instrument identity: symbol family, option description, and issuer code
`AHRM`. For expired contracts, that issuer code and description establish Ahrom association;
the available identity response does not expose a direct underlying InsCode. Discovery
queries, market watch, and identity responses are archived separately by content hash.

The contract master has one row per InsCode. Expiration is parsed from the official TSETMC
description and converted from Jalali to Gregorian. Active/expired status is based on that
expiration date. The `availability` stage archives TSETMC daily history and fills the first
and last official available dates. OptionBaaz observation dates are separate columns.
The discovery audit records capped search queries and any metadata rejections.

`collect` uses a persistent session with retries for 429 and server errors, timeout, and
a delay between requests. Each successful JSON response is archived at
`data/raw/optionbaaz/contracts/<ins_code>/<sha256>.json`. The processed manifest points
to the selected version. HTTP 404 JSON bodies are archived separately under
`data/raw/optionbaaz/errors`; known 404s are skipped on ordinary reruns and retried
with `--refresh`. Existing archive hashes are checked before reuse. Invalid identity
or metadata responses remain archived for audit
but are excluded from the panel. The access token comes only from the environment and is
sent as the `access_token` cookie.

`build` merges `underlyingPoints` by exact date without filling gaps, keeps `close` and
`endPrice` separate, adds conservative quality flags, and writes a long CSV and quality
report. Source values are never changed. It writes Parquet only if `pyarrow` is installed.
The panel may have gaps because OptionBaaz's tested daily endpoint offers a rolling maximum
period of `1y`; no claim of full lifetime coverage is made from that response.
The `probe-periods` stage tests two known contracts against the nine candidate period
values and archives each response and the compact result table.
