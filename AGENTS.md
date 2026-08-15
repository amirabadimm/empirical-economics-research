# Workspace Instructions

- دامنه هر کالا را در `commodity/<commodity>` نگه دار.
- snapshotهای منبع immutable هستند: حذف، بازنویسی یا تبدیل ضمنی ممنوع است.
- CSV canonical خام فقط توسط collector مستند، incremental، idempotent و atomic
  refresh می‌شود؛ تحلیل و notebook حق تغییر raw را ندارند.
- فایل مشتق‌شده را فقط در `data/interim` یا `data/processed` بنویس.
- منطق عمومی بورس کالا در `shared/ime_data` قرار می‌گیرد؛ wrapper هر کالا باید
  تنظیمات و فیلترهای همان پروژه را صریح نگه دارد.
- منطق بورس انرژی در پکیج مشترک جداگانه قرار می‌گیرد و با `ime_data` مخلوط نمی‌شود.
- notebookها در `notebooks`، logها در `logs` و خروجی ارائه در `outputs` یا
  `reports` قرار می‌گیرند.
- پس از تغییر منبع، schema، مسیر، فرمول، تعداد مشاهده یا وضعیت مرحله، README،
  `docs/WORKFLOW.md` پروژه و `docs/STATUS.md` را به‌روزرسانی کن.
- credentialها فقط از environment دریافت می‌شوند و نباید در فایل، کد یا مستندات
  ثبت شوند.
- raw، snapshot، log، cache، environment و خروجی حجیم نباید وارد Git شوند.
