# Agent Instructions — Zinc Certificate

داده خام immutable است، snapshot کامل باید حفظ شود، collector باید incremental،
idempotent و atomic بماند. هر دو کد قدیم و جدید یک ابزار پیوسته هستند. روزهای حجم
صفر در raw حفظ و فقط در تحلیل قیمت حذف شوند. تغییر schema یا شکست validation باید
اجرای pipeline را متوقف کند.

underlying تحلیلی فقط سبد عیارهای 99.97 و 99.98 با قرارداد نقدی/نقدی مچینگ است؛
raw گسترده نباید برای رسیدن به این scope حذف یا بازنویسی شود. قیمت روزانه فیزیکی
با وزن `Quantity`، قیمت گواهی با `TodaySettlementPrice` و قیمت ذاتی با
`LME cash / 1000 × USD/IRR` ساخته می‌شود. در روش اصلی فقط بین anchorهای واقعی
درون‌یابی و هرگونه extrapolation ممنوع است.
