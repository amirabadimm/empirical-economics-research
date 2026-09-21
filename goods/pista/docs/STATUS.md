# Pista status

The 16-row observed weekly-price comparison is included in the project-local Power BI delivery CSV at `outputs/power_bi/pista_certificate_physical_comparison.csv`.

- Stage: certificate collection and reproducible weekly price audit; manual review pending.
- Packaging: self-contained Python project with declared analysis dependencies and no workspace imports.
- Source and identity: official IME CDC API, market 22, commodity 11, `PistaCL`.
- Coverage: 2026-08-25 through 2026-09-17; 21 daily rows, 16 with trades.
- Last collection: 2026-09-19.
- Abtahi workbook: 578 weekly dated rows, Jalali 1393/07/03 to 1405/06/19;
  572 Khandan and 391 Dahan-Bast populated price rows.
- Weekly price units, grade/size, location, and compilation method remain unverified.
- No physical transaction benchmark or certificate valuation has been approved.
- `analysis/` and `report/` are prepared for future code and written findings.
- Weekly audit: 578 rows preserved; 55 product observations flagged, 38 kept,
  17 require manual review, and 0 prices corrected automatically. The source
  also contains the invalid Jalali date `1403/08/31`.
- Interim cleaned and audit CSVs are generated locally; no return, volatility,
  or econometric estimates have been run on unresolved observations.
- Indicative certificate comparison notebook: 16 positive-volume dates matched
  to a Dahan-Bast quote no more than six days old; provisional premium 6.13%
  to 30.96% under an unconfirmed toman/kg physical-price assumption.
- Next: confirm Abtahi price units and grade/size before interpreting the comparison
  premium as a certificate bubble.
# Bubble distribution status

As of 2026-09-21, the standardized pistachio distribution contains all 16 observed
certificate-versus-physical comparisons. The distribution CSV, figure, and notebook section use
these observations without classifying them as proxies.
