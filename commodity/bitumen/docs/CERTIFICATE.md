# Bitumen Certificate and Physical-Market Sources

## Certificate

Official endpoint: `https://dataapi.ime.co.ir/api/CDC/CDCTrades`

The old contract code `CD1BIT0001` and the current code `Bitumen` form one continuous analytical
series. The collector validates identity, schema, nonnegative values, and price/value consistency.

A published secondary market report states that one bitumen certificate represents one kilogram:
`https://atlaseqtesad.ir/86480/commodity-certificate-bourse-trading.html`. This supports the
exploratory conversion of certificate counts to metric tons, but the official IME admission or
market-opening notice remains the required authority for production methodology.

Run from the repository root:

```powershell
python .\commodity\bitumen\src\bitumen\collectors\certificate.py
```

Outputs:

- canonical CSV: `commodity/bitumen/data/raw/certificate/bitumen_certificate_raw.csv`;
- immutable responses: `commodity/bitumen/data/raw/certificate/api_snapshots`.

The default run refreshes the trailing 14 days and merges validated observations atomically.
`--full-refresh` reconstructs the complete period from 2025-10-20 but is unnecessary for routine
updates. Both Gregorian `DT` and Jalali `PersianDate` are retained.

## Physical market

Official endpoint:
`https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList`

Run from the repository root:

```powershell
python .\commodity\bitumen\src\bitumen\collectors\physical.py
```

Outputs:

- canonical CSV: `commodity/bitumen/data/raw/physical/bitumen_physical_raw.csv`;
- immutable monthly responses: `commodity/bitumen/data/raw/physical/api_snapshots`.

The collector retains every source row whose normalized product name contains the Persian word
for bitumen, including all grades, producers, symbols, contract forms, market segments, and
zero-quantity offers. The default run refreshes the current and two prior Jalali months. Product
selection and benchmark eligibility are downstream research decisions.

See `WORKFLOW.md` for the current 60/70 scope, empirical findings, and decision gates.
