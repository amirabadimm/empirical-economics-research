# گواهی سپرده گندله سنگ‌آهن

منبع رسمی: `https://dataapi.ime.co.ir/api/CDC/CDCTrades`

کدهای یک سری پیوسته: `CD1IOP0001` (قدیم) و `IronOrePlt` (جدید).

```powershell
python .\src\pellet\collectors\certificate.py
```

خروجی خام: `data/raw/certificate/pellet_certificate_raw.csv`؛ پاسخ‌های کامل در
`data/raw/certificate/api_snapshots` نگه‌داری می‌شوند. اجرای عادی ۱۴ روز اخیر
را refresh می‌کند؛ `--full-refresh` کل دوره را از 2025-10-20 بازسازی می‌کند.

## بازار فیزیکی — مرحله جمع‌آوری خام

collector گسترده بازار فیزیکی:

```powershell
python .\src\pellet\collectors\physical.py
```

خروجی برنامه‌ریزی‌شده `data/raw/physical/pellet_physical_raw.csv` است و پاسخ کامل
هر ماه در `data/raw/physical/api_snapshots` آرشیو می‌شود. این مرحله همه ردیف‌های
دقیقاً با نام «گندله سنگ آهن»، شامل تمام تولیدکنندگان، نمادها، انواع قرارداد و
عرضه‌های بدون معامله را حفظ می‌کند. هنوز هیچ benchmark یا فیلتر underlying نهایی
تعریف نشده است. اجرای اول از 1386/01 و اجراهای بعدی با refresh دو ماه انتهایی است.
