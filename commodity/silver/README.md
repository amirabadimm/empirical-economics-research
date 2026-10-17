# Silver research architecture

## First source collection (2026-10-13)

First live certificate collection produced 307 rows through 2026-10-12, including 228 traded rows. The full official physical archive was collected and replayed from 235 immutable monthly snapshots. The corrected filter excludes vehicle colors; it found zero silver-bar or silver-shot physical rows. Consequently the strict physical benchmark and certificate/physical diagnostic cannot be built. This is source coverage, not an approved economic valuation. The combined Silver and Warehouse Fees test run passed 6 tests.

Initially data-free scaffold for Iranian silver research. It keeps the IME 999.9 silver-bar
certificate, broad physical-market observations, and derived analysis independent.
No source data or snapshots are bundled, and local rebuilds never collect data.

The governed certificate identity is IME commodity `21`, legacy code
`CD1SIB0001`, continuous code `SilverBar`. One certificate represents one gram of
999.9 silver, so comparisons explicitly convert certificate IRR/g to IRR/kg.

```powershell
# Explicit network collection, when authorized later:
python commodity/silver/src/silver/collectors/certificate.py
python commodity/silver/src/silver/collectors/physical.py

# Offline derived rebuild from existing canonical inputs:
python commodity/silver/refresh.py
```

The initial comparison uses only same-date positive-volume certificate observations
and cash 999.9 silver-bar physical trades. It is a diagnostic pending tax, fee,
delivery, and product-comparability review. See `docs/WORKFLOW.md` and
`docs/STATUS.md`.
