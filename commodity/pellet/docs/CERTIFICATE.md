# Iron ore pellet deposit certificate
Official source: `https://dataapi.ime.co.ir/api/CDC/CDCTrades`
Codes in a continuous series: `CD1IOP0001` (old) and `IronOrePlt` (new).
```powershell
python .\src\pellet\collectors\certificate.py
```

raw output: `data/raw/certificate/pellet_certificate_raw.csv`; Complete answers in
`data/raw/certificate/api_snapshots` are kept. The normal performance of the last 14 days
refreshes `--full-refresh` restores the entire period from 2025-10-20.
## Physical market — raw collection stage
Wide collector physical market:
```powershell
python .\src\pellet\collectors\physical.py
```

The programmed output is `data/raw/physical/pellet_physical_raw.csv` and the complete response
Archived monthly at `data/raw/physical/api_snapshots`. This step is all rows
Precisely named "iron ore cart", including all manufacturers, symbols, contract types and
Maintains non-traded supplies. Still no benchmark or final underlying filter
not defined The first performance is from 1386/01 and the subsequent performances are with a refresh of the last two months.