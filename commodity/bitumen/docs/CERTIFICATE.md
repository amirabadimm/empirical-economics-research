# Bitumen deposit certificate
Official source: `https://dataapi.ime.co.ir/api/CDC/CDCTrades`
Codes in a continuous series: `CD1BIT0001` (old) and `Bitumen` (new).
```powershell
python .\src\bitumen\collectors\certificate.py
```

raw output: `data/raw/certificate/bitumen_certificate_raw.csv`; Complete answers in
`data/raw/certificate/api_snapshots` are kept. The normal performance of the last 14 days
refreshes `--full-refresh` restores the entire period from 2025-10-20.
## Physical Market — Extensive raw collection
```powershell
python .\src\bitumen\collectors\physical.py
```

The output is `data/raw/physical/bitumen_physical_raw.csv` and the full answer every month in
`data/raw/physical/api_snapshots` will be archived. collector All item names included
"bitumen", maintaining all grades, manufacturers, symbols, contracts and supplies of zero value
does At this stage, no final grade or underlying has been selected.