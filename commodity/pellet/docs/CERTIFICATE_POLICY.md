# Agent Instructions — Pellet Certificate

داده خام immutable است، snapshot کامل باید حفظ شود، collector باید incremental،
idempotent و atomic بماند. هر دو کد قدیم و جدید یک ابزار پیوسته هستند. روزهای حجم
صفر در raw حفظ و فقط در تحلیل قیمت حذف شوند. تغییر schema یا شکست validation باید
اجرای pipeline را متوقف کند.
