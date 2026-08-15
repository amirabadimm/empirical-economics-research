# Zinc-Ingot Warehouse-Receipt Certificate
Official source: `https://dataapi.ime.co.ir/api/CDC/CDCTrades`
Codes in a continuous series: `CD1ZNI0001` (old) and `ZincIngot` (new).
```powershell
python .\src\zinc\collectors\certificate.py
```

raw output: `data/raw/certificate/zinc_certificate_raw.csv`; Complete answers in
`data/raw/certificate/api_snapshots` are kept. The normal performance of the last 14 days
refreshes `--full-refresh` restores the entire period from 2025-10-20.
## Physical Market — Extensive raw collection
```powershell
python .\src\zinc\collectors\physical.py
```

The output is `data/raw/physical/zinc_physical_raw.csv`. collector deliberately all the names
The broad physical collector retains zinc-labelled commodities, including ingots of different grades and zinc dust, across manufacturers and symbols.
Maintains contracts and supplies of zero value. This wide raw does not change; Filter
Underlying applies only to processing.
## benchmark and bubble
The approved analytical underlying is the volume-weighted 99.97/99.98 ingot basket in eligible cash contracts and
Cash is matching. Three bubble exits include physical versus LME–dollar, certificate versus
LME-Dollar and certificate to physical price is an estimate with ratio interpolation. Price criteria
The certificate is `TodaySettlementPrice` and the main method of the third bubble project. Full formula details,
Statistics and limits are recorded in `docs/WORKFLOW.md`.
