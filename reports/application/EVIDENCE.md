# Application evidence checkpoint

Prepared for the 2026-10-17 portfolio review from existing local outputs.
Copper maintenance reconciled 2026-10-18; its primary sample is unchanged.
This is a file and formula verification, not a source refresh, independent
source audit, server check, or new execution of the allocation notebook.

## Commodity certificate research

Means and medians are unweighted across modeled certificate-trading days.
The direct international comparison below uses exactly the primary sample dates.

| Project | Primary dates | Rows | Observed anchors | Interpolated | Mean premium | Median premium | Same-sample certificate/LME–FX mean |
|---|---|---:|---:|---:|---:|---:|---:|
| Copper | 2025-10-26–2026-10-11 | 223 | 39 | 184 | 6.09% | 6.96% | -10.35% |
| Zinc | 2025-10-26–2026-10-11 | 223 | 54 | 169 | 1.88% | 2.73% | -20.58% |

- Copper: direct certificate/intrinsic output has 232 rows through 2026-10-17 (full-sample mean -10.28%); physical/intrinsic output has 802 rows through 2026-10-11.
- Zinc: direct certificate/intrinsic output has 228 rows through 2026-10-12 (full-sample mean -20.43%); physical/intrinsic output has 567 rows through 2026-10-11.

Interpolated observations may use later physical anchors. These are descriptive
valuation estimates; neither predictive accuracy nor executable arbitrage is established.

## Gold ETF research

| Fund | Full-history matched fund-days | First matched date | Last matched date | Two-year candidate days | Exact NAV matches |
|---|---:|---|---|---:|---:|
| Ayar | 1,939 | 2018-07-22 | 2026-10-11 | 462 | 444 |
| Tala | 2,184 | 2017-07-30 | 2026-10-12 | 462 | 460 |
| Kahroba | 1,224 | 2021-08-02 | 2026-10-12 | 462 | 459 |
| Ganj | 874 | 2023-01-09 | 2026-10-12 | 462 | 456 |
| Gohar | 2,032 | 2018-03-12 | 2026-10-13 | 461 | 460 |

Total: **8,253 matched fund-day observations**, not 8,253 distinct calendar days.
Counts refer to local CSVs. The server database and provider discrepancies were not
re-audited for this review. Exact valuation-date matching does not prove NAV was
available when the market price was observed.

## Allocation and REIT scope

- Level grid: 508 asset-month rows; 127 calendar months, 1394/12–1405/06 (Solar Hijri).
- Return grid: 504 asset-month rows; 126 calendar months, 1395/01–1405/06 (Solar Hijri).
  Missing return cells: 1; complete four-asset months: 125. Grid size is not the number of complete observations.
- REIT scenario summary: 8 funds, 13 identified events; latest close dates 2026-10-07–2026-10-07.
- All eight REIT histories remain labelled incomplete or unverified for dividends.
- Historical portfolio optimization is an ex-post pilot. Expert-survey allocation
  and an investable out-of-sample strategy are not delivered results.

## Input fingerprints

SHA-256 fingerprints pin the exact local derived files used for these claims.
Raw third-party datasets are not included in the application package.

| Local input (relative to repository root) | SHA-256 |
|---|---|
| `commodity/copper/data/processed/bubble/copper_certificate_bubble.csv` | `94ce3b02490a0eeeca6814c6ba39a3867de062be62cb2fd30c6c52596f9aff8e` |
| `commodity/copper/data/processed/bubble/certificate_vs_intrinsic_bubble.csv` | `d26e4b996e28068a1585cc7ebb7206e5098d51a4c40a52e22a73913b1abfaca4` |
| `commodity/copper/data/processed/bubble/physical_vs_intrinsic_bubble.csv` | `d4692c14c91f79b6b45cef8426cdd5088c5610d9b056c2229f62481236f92eb0` |
| `commodity/zinc/data/processed/bubble/zinc_certificate_bubble.csv` | `806cb0ac53abeb4349ab2eb47c6e27031b17fcf325863019821aab291579fbca` |
| `commodity/zinc/data/processed/bubble/certificate_vs_intrinsic_bubble.csv` | `1ef86c93096d19d534e8ec94556ae564acceb0a98662ce1b44a1c384ddccf529` |
| `commodity/zinc/data/processed/bubble/physical_vs_intrinsic_bubble.csv` | `13bdb09d1acd8fbee58e8649ec12a76ff0cc4ca4654f44a65612430a1c0f39b8` |
| `commodity/gold/data/processed/bubble/ayar_nav_bubble.csv` | `ba61ef5db01e1dd2be2128088343fdb7f9fddcc5ced1ffe620101a5985ca0d17` |
| `commodity/gold/data/processed/analysis/ayar_daily_price_nav_2y.csv` | `852c055d7914b20be07cce6b5e6c5d269d96dc31663b9d5a597716fc464d9882` |
| `commodity/gold/data/processed/bubble/tala_nav_bubble.csv` | `87f3e0372b7edfc91f36856dee3d652b79430c1f25ae661915497913cae9ec16` |
| `commodity/gold/data/processed/analysis/tala_daily_price_nav_2y.csv` | `c783c4ce718027377bb30dcc4a3ed1af591b8bc64f62e0cf6c15eb151138aea2` |
| `commodity/gold/data/processed/bubble/kahroba_nav_bubble.csv` | `d5827873c8b5b68c0d1bf09acd1fde20ec129d60741b83bc633e66b98e5eb0d5` |
| `commodity/gold/data/processed/analysis/kahroba_daily_price_nav_2y.csv` | `0b34dc3b16aa4755c246c88bdcc1e4b18e5ac90539f53f63e534dfe2a4e49866` |
| `commodity/gold/data/processed/bubble/ganj_nav_bubble.csv` | `34e559152e08871197a90a534cc7dfeaa1ccab1a6833e5b551a92b01a2f0683e` |
| `commodity/gold/data/processed/analysis/ganj_daily_price_nav_2y.csv` | `95bfe8ab88a8092106fd1bbe39b6caac9a301a1f22685e9e11d0eec57c85235c` |
| `commodity/gold/data/processed/bubble/gohar_nav_bubble.csv` | `904e3a60cd6ecb5050fb0c2421dbdac090e9f943d748069b1b30ec05bb4fa6e9` |
| `commodity/gold/data/processed/analysis/gohar_daily_price_nav_2y.csv` | `763724cb2fe49634b2e5624469c742fe3d18d5e698924d554f41bfe8270bf3d7` |
| `asset_allocation/data/processed/analysis/monthly_asset_levels.csv` | `8d06b1e2f486ccc492b1e3709bf8eebb093535c8d2f7ddc767f93f1eb56873c3` |
| `asset_allocation/data/processed/analysis/monthly_asset_returns.csv` | `021dd872838c8ebbc4f32985104e44be1d459ecea173bc27481d89e45fb8d280` |
| `asset_allocation/data/processed/analysis/reit_eight_fund_comparison.csv` | `31a3cb3179427869e786db239c1bc4c62cc3bf586b9df8e22c6ab34e9a33cd58` |

## Recheck

```powershell
python reports/application/verify_claims.py --check
```

The command fails if a formula, identity, key, alignment, or fingerprint changes.
After an intentional research refresh, review all public claims before regenerating
this report with `--write`. This verifier does not establish source correctness,
re-execute every model, or validate economic comparability.
