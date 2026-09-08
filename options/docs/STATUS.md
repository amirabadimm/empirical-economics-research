# Status - 2026-09-08

PAUSED at the user's request. Do not restart full collection until asked.

Intended research scope: every discoverable option, including expired contracts,
from Jalali 1401 onward; market history, specifications, open interest where available,
historical volatility (HV), implied volatility (IV), and Greeks.
Complete coverage is not yet established.

Existing capture: 324 Ahrom contracts (162 calls, 162 puts); 230 detail snapshots;
94 catalogue-only entries; 191 underlying IV days, 1404/06/16 through 1405/06/16.
The full per-contract historical panel has NOT been collected.

Direct TSETMC data used by fima matched last/closing prices, volume and trade count
for two Optionbaaz samples dated 1405/06/16 (eight fields matched).
This is a small sample, not whole-history validation. Some requests returned 502.
The tse-option legacy history endpoint returned 403.
Fima calculates IV and Greeks; these are not archived Optionbaaz values.
Its IV function suppresses results below 10 days to expiry; Optionbaaz showed IV
4.06 for a saved contract with 9 days remaining. Exact IV/Greek/HV parity is unverified.

Next research: verify expired-contract discovery and earliest available dates;
identify bulk archived IV/Greeks/OI access; document calculation conventions before
reconstruction. Preserve source-provided and calculated fields separately.

Project moved to E:\Work\options. All existing files were hash-verified after moving;
only derived location pointers were updated. No raw snapshot content was changed.

Validation: `python -m pytest options/tests` from E:\Work tests numeric parsing, missing values, and immutable/idempotent imports. CLI JSON output uses ASCII escapes for Windows console compatibility.
