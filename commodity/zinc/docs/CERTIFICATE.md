# گواهی سپرده شمش روی

منبع رسمی: `https://dataapi.ime.co.ir/api/CDC/CDCTrades`

کدهای یک سری پیوسته: `CD1ZNI0001` (قدیم) و `ZincIngot` (جدید).

```powershell
python .\src\zinc\collectors\certificate.py
```

خروجی خام: `data/raw/certificate/zinc_certificate_raw.csv`؛ پاسخ‌های کامل در
`data/raw/certificate/api_snapshots` نگه‌داری می‌شوند. اجرای عادی ۱۴ روز اخیر
را refresh می‌کند؛ `--full-refresh` کل دوره را از 2025-10-20 بازسازی می‌کند.

## بازار فیزیکی — جمع‌آوری خام گسترده

```powershell
python .\src\zinc\collectors\physical.py
```

خروجی `data/raw/physical/zinc_physical_raw.csv` است. collector عمداً تمام نام‌های
کالای شامل «روی»، از جمله شمش با عیارهای مختلف و خاک روی، همه تولیدکنندگان، نمادها،
قراردادها و عرضه‌های مقدار صفر را حفظ می‌کند. این raw گسترده تغییر نمی‌کند؛ فیلتر
underlying فقط در processing اعمال می‌شود.

## benchmark و حباب

underlying مصوب تحلیل، سبد موزون حجمی شمش‌های 99.97 و 99.98 در قراردادهای نقدی و
نقدی مچینگ است. سه خروجی حباب شامل فیزیکی نسبت به LME–دلار، گواهی نسبت به
LME–دلار و گواهی نسبت به قیمت فیزیکی برآوردی با درون‌یابی نسبت است. معیار قیمت
گواهی `TodaySettlementPrice` و روش اصلی پروژه حباب سوم است. جزئیات کامل فرمول،
آمار و محدودیت‌ها در `docs/WORKFLOW.md` ثبت شده است.
