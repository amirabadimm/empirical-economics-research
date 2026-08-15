# Agent Instructions — Copper Certificate Project

## Scope

این فایل برای تمام کارهای داخل `commodity/copper/` اعمال می‌شود. فایل‌های پروژه LME
در پوشه والد را تغییر نده، مگر اینکه کاربر مشخصاً چنین درخواستی کند.

## Collaboration rule

پروژه باید مرحله‌به‌مرحله پیش برود. بدون تأیید صریح کاربر وارد مرحله بعد نشو.
تحقیق هر مرحله، نتایج، فرض‌ها و محدودیت‌ها را پیش از پیاده‌سازی مرحله بعد گزارش
کن. تأیید یک مرحله، مجوز تغییر دامنه یا اجرای مراحل بعدی نیست.

## Current status

- مراحل ۲ تا ۴ برای گواهی جدید کامل شده‌اند.
- منبع تأییدشده گواهی API رسمی عمومی CDC بورس کالا و کد قرارداد تأییدشده
  `CopperCthd` است؛ جزئیات در `README.md` ثبت شده‌اند.
- مرحله ۵ نمونه‌گیری بازار فیزیکی کامل شده است.
- مرحله ۶ کامل شده است: collector افزایشی بازار فیزیکی و تاریخچه کامل raw موجود است.
- مرحله ۷ کامل شده است: benchmark فیزیکی، نسبت فیزیکی به قیمت ذاتی، درون‌یابی خطی
  نسبت و حباب گواهی ساخته شده‌اند.
- مرحله بعدی پیشنهادی: مرحله ۸، کنترل کیفیت تحلیلی و زمان‌بندی اجرای زنجیره کامل.
- `WORKFLOW.md` مرجع منسجم گزارش و ارائه است. پس از هر تغییر روش، تعداد مشاهده،
  فرمول یا خروجی production، آن را همراه README و این status به‌روز کن.
- TSETMC اشتراکی برای collector گواهی لازم نیست و `InsCode` تعیین نشده است.
- ابزار خواندنی `src/copper/tools/probe_sources.py` ساخته و از نظر syntax تأیید شده است. اجرای
  آن در ۱۰ مرداد ۱۴۰۵ برای همه منابع در TLS handshake timeout شد. این وضعیت را
  به‌عنوان نبود داده، نبود نماد یا نیاز به API key تفسیر نکن.
- `src/copper/collectors/certificate.py` wrapper collector مشترک رسمی و افزایشی گواهی است و
  هر دو کد تاریخی `CD1COP0001` و `CopperCthd` را به یک سری متصل می‌کند. CSV خام و
  snapshotهای JSON آن را حفظ کن. اجرای دوم باید فقط بازه refresh را بخواند.

## Data rules

1. داده خام گواهی را فقط در `data/raw/certificate/` ذخیره کن.
2. داده خام بازار فیزیکی را فقط در `data/raw/physical/` ذخیره کن.
3. داده خام را پاک، بازنویسی یا به‌صورت ضمنی تبدیل نکن؛ snapshot یا پاسخ منبع را
   همراه زمان دریافت و نشانی منبع نگه دار.
4. داده مشتق‌شده را فقط در `data/processed/` ذخیره کن.
5. قیمت‌ها باید همراه واحد صریح ذخیره شوند؛ به‌ویژه ریال/تومان و کیلوگرم/تن.
6. تاریخ منبع، تاریخ معامله، و زمان دریافت را در ستون‌های جدا نگه دار.
7. اسکریپت‌ها باید افزایشی، idempotent و دارای کنترل تکرار باشند.
8. شکست دانلود یا validation نباید دیتاست سالم قبلی را خراب کند.

## Source hierarchy

1. بورس کالای ایران؛
2. TSETMC، فقط پس از اثبات پوشش نماد موردنظر؛
3. منبع ثالث صرفاً برای تطبیق و تشخیص اختلاف.

هر اختلاف میان منابع باید ثبت و گزارش شود، نه اینکه بدون توضیح یکی انتخاب شود.

## Certificate discovery requirements

پیش از نوشتن collector گواهی باید موارد زیر تأیید شود:

- نام دقیق نماد و شناسه ابزار؛
- وجود یا نبود `InsCode` معتبر در TSETMC؛
- اولین و آخرین تاریخ موجود در هر منبع؛
- تعریف فیلدهای قیمت، حجم، ارزش و تعداد معامله؛
- واحد هر فیلد؛
- رفتار روزهای بدون معامله و اصلاحات تاریخی.

## Physical-market requirements

تمام ردیف‌های عرضه و معامله خام را حفظ کن. فیلتر محصول، تولیدکننده، بازار، نوع
قرارداد، تاریخ تحویل، قیمت پایه، قیمت معامله و مقدار معامله را پیش از محاسبه
قیمت موزون بررسی کن. فقط ردیف‌های واقعاً قابل مقایسه با دارایی پشتوانه گواهی
باید وارد معیار حباب شوند.

### Confirmed physical candidate

- Primary symbol candidate: `NCI-OACCAA-00`
- Goods: `مس کاتد`
- Producer: `ملی صنایع مس ایران`
- Observed contract types: `نقدی` and `نقدی (مچینگ)`
- Preserve but exclude zero-quantity offers from weighted traded price.
- Do not combine `مس کاتد 2` or other producers without explicit equivalence
  evidence and user approval.
- By the user's later explicit decision, the canonical physical CSV must retain
  only normalized `GoodsName == مس کاتد`, symbols `NCI-CCAA-00` and
  `NCI-OACCAA-00`, and contract types `نقدی` or `نقدی (مچینگ)`. Discard other
  goods groups, producers, symbols, forward, forward-matching, and credit rows
  from that CSV. Retain zero-quantity offers within the selected scope. Keep full
  compressed API snapshots so excluded rows remain recoverable.
- The source reports `Unit=تن`, while `Price` is on the same apparent scale as
  certificate IRR/kg and `TotalPrice=Price*Quantity`. Preserve all raw units and
  do not silently infer or rescale `TotalPrice`.

### Physical collector status

- Script: `src/copper/collectors/physical.py`
- Canonical raw table: `data/raw/physical/copper_cathode_physical_raw.csv`
- Full-response archives: `data/raw/physical/api_snapshots/*.json.gz`
- Search coverage: `1386/01` through the current Jalali month.
- Initial broad collection found 1,993 cathode-related rows. After the user's
  staged filtering decisions, the canonical table contains 1,163 National Iranian
  Copper Industries cash/cash-matching rows; verify current coverage and counts
  after each collector run.
- On the current history, cash and cash-matching daily weighted prices are exactly
  equal on all 362 paired trading days, while matching adds 9 matching-only dates.
  The proposed primary benchmark combines both using Quantity weights, while
  retaining contract-type diagnostics for sensitivity analysis.
- `src/copper/processing/build_physical_benchmark.py` implements the approved combined benchmark and
  writes `data/processed/nci_copper_cash_daily.csv`. Its current output has 789
  positive-trade days. Do not treat stage 7 as complete until date matching and
  bubble calculations have been explicitly approved and implemented.
- The processed daily benchmark must expose only one numeric price column,
  `physical_weighted_price`. Keep cash/matching quantity diagnostics, and fail
  validation if their daily weighted prices ever diverge in future source data.
- `src/copper/processing/build_certificate_bubble.py` implements the approved ratio interpolation:
  physical/LME-FX ratios at the currently available 26 exact anchors are linearly interpolated by calendar
  day, multiplied by each day's intrinsic LME-FX price, and compared with the
  certificate VWAP. It writes `data/processed/copper_certificate_bubble.csv`.
  Never extrapolate outside the first/last anchor without new explicit approval.
- `src/copper/processing/build_intrinsic_bubbles.py` writes the two direct comparison datasets:
  `physical_vs_intrinsic_bubble.csv` (789 physical observations) and
  `certificate_vs_intrinsic_bubble.csv` (178 certificate observations). These do
  not use the interpolated physical benchmark.
- Incremental runs refresh recent complete Jalali months and replace those
  months atomically rather than attempting to infer a source primary key.

## Bubble calculation safeguards

تا پیش از تأیید کاربر، هیچ روش اتصال تاریخی را نهایی نکن. در خروجی آینده باید
حداقل `physical_trade_date` و `physical_price_age_days` وجود داشته باشد تا قیمت
قدیمی بازار فیزیکی به‌صورت پنهان به روز گواهی نسبت داده نشود.

## Documentation

پس از تأیید و تکمیل هر مرحله، وضعیت checklist در `README.md` و بخش Current
status این فایل را در همان تغییر به‌روزرسانی کن.
