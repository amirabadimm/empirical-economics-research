# گواهی سپرده قیر

منبع رسمی: `https://dataapi.ime.co.ir/api/CDC/CDCTrades`

کدهای یک سری پیوسته: `CD1BIT0001` (قدیم) و `Bitumen` (جدید).

```powershell
python .\src\bitumen\collectors\certificate.py
```

خروجی خام: `data/raw/certificate/bitumen_certificate_raw.csv`؛ پاسخ‌های کامل در
`data/raw/certificate/api_snapshots` نگه‌داری می‌شوند. اجرای عادی ۱۴ روز اخیر
را refresh می‌کند؛ `--full-refresh` کل دوره را از 2025-10-20 بازسازی می‌کند.

## بازار فیزیکی — جمع‌آوری خام گسترده

```powershell
python .\src\bitumen\collectors\physical.py
```

خروجی `data/raw/physical/bitumen_physical_raw.csv` است و پاسخ کامل هر ماه در
`data/raw/physical/api_snapshots` آرشیو می‌شود. collector همه نام‌های کالای شامل
«قیر»، همه گریدها، تولیدکنندگان، نمادها، قراردادها و عرضه‌های مقدار صفر را حفظ
می‌کند. در این مرحله هیچ گرید یا underlying نهایی انتخاب نشده است.
