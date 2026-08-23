# Iran Energy Exchange Document Taxonomy

Last reviewed: 2026-08-23

## Purpose and scope

This catalog classifies the 66 source documents currently held in `../documents/` by their
analytical role in understanding the Iran Energy Exchange (IRENEX). It is a conceptual research
taxonomy, not a classification by file format, website section, or issuing institution.

The source contents are unchanged. Each document has a normalized, lowercase English filename and
is stored under the directory for its primary analytical role. The authoritative mapping from the
original acquired filename to the professional filename and current relative path is maintained in
[`../references/DOCUMENT_FILE_MANIFEST.tsv`](../references/DOCUMENT_FILE_MANIFEST.tsv). Secondary
relationships are expressed through tags rather than duplicate source copies. The companion
`documents.zip` is stored in `documents/_archive/` and is excluded from the 66-document count.

Titles supplied for opaque filenames are provisional descriptions derived from the intake notes.
They are not substitutes for title-page verification. Issuer, publication date, version, source
URL, and access date must be verified separately in `../references/SOURCE_REGISTER.md`.

## Taxonomy at a glance

| Code | Analytical role | Documents | Reading focus |
|---|---|---:|---|
| GOV | Exchange foundations and market operations | 12 | Institutional basis, admission, trading, clearing, access, and fees |
| PHY | Physical market and trade finance | 6 | Warehousing, deposit certificates, commodity finance, oil, and bunkering |
| DER | Derivatives | 5 | Futures, options, governance, default management, and accounting |
| ELE | Electricity market and bilateral supply | 15 | Electricity boards, supply rules, generators, industry, storage, and exports |
| CER | Electricity-related certificates | 9 | Capacity, renewable generation, legal origin, and aggregation |
| EFF | Energy-efficiency and environmental market | 9 | Savings certificates, measurement and verification, settlement, and ESCOs |
| STR | National energy strategy and policy context | 7 | The Exchange's place in the national energy system |
| CMP | Adjacent compliance and electricity-use regulation | 3 | AML, anti-smuggling, and crypto-asset mining provisions |
| **Total** |  | **66** |  |

## Physical directory layout

| Code | Directory under `documents/` |
|---|---|
| GOV | `01-corporate-and-market-rules/` |
| PHY | `02-physical-market-and-financing/` |
| DER | `03-derivatives-market/` |
| ELE | `04-electricity-market/` |
| CER | `05-capacity-renewables-and-industrial-generation/` |
| EFF | `06-energy-efficiency-and-optimization/` |
| STR | `07-national-energy-strategy/` |
| CMP | `08-compliance-and-related-regulations/` |

The catalog tables retain the original acquired basename for provenance. Resolve the current file
path through `DOCUMENT_FILE_MANIFEST.tsv`; do not reconstruct it from the original basename.

## Reading-priority convention

- **Core:** read in full and extract article-level rules, actors, inputs, outputs, deadlines,
  exceptions, amendments, and cross-references.
- **Supporting:** read selectively after the relevant core documents; extract the provisions that
  explain implementation, legal authority, accounting, or a specialist product.
- **Contextual:** index first and extract only passages that directly affect IRENEX, energy trades,
  market participants, or regulated electricity consumption.

Priority is a research sequencing aid, not a statement about legal hierarchy or validity.

## GOV — Exchange foundations and market operations (12)

These documents define the institution and the common lifecycle shared across markets.

| ID | Original filename | Working subject | Priority |
|---|---|---|---|
| GOV-01 | `اساسنامه نهایی (2).pdf` | Exchange articles of association | Core |
| GOV-02 | `دستورالعمل معاملات كالا و اوراق بهادار قابل معامله در بورس انرژي ايران (1).pdf` | General trading rules | Core |
| GOV-03 | `دستورالعمل پذیرش کالا و اوراق بهادار قابل معامله در بورس انرژی.pdf` | Admission of commodities and tradable securities | Core |
| GOV-04 | `دستورالعمل ثبت و سپرده_گذاری کالا و اوراق بهادار قابل معامله و تسویه و پایاپای معاملات در بورس انرژی.pdf` | Registration, depository, clearing, and settlement | Core |
| GOV-05 | `59682f71-87eb-11e8-9753-40a8f031c933.pdf` | Trading-symbol definition and assignment rules | Core |
| GOV-06 | `1b6e377b-d788-11ed-b5ae-005056b98203.xlsx` | Symbol, power-plant, and electricity-offer reference data | Core |
| GOV-07 | `b8174b3e-57ad-11ea-a608-40a8f031c930.pdf` | Online-trading procedure | Supporting |
| GOV-08 | `دستورالعمل نحوه انجام امور وکالتی در بورس کالای ایران و بورس انرژی ایران.pdf` | Agency transactions | Supporting |
| GOV-09 | `ضوابط مجوز دسترسی شرکت_های کارگزاری و کارکنان شرکت_های کارگزاری به سامانه معاملاتی بورس انرژی ایران.docx` | Broker and employee trading-system access | Supporting |
| GOV-10 | `کارمزدها 14020715.pdf` | Fee schedule | Supporting |
| GOV-11 | `efdf2f2d-0524-11ee-b5b2-005056b98203.pdf` | Block trading in securities | Supporting |
| GOV-12 | `رویه بلوک- 14050230.pdf` | Block-trade procedure | Supporting |

## PHY — Physical market and trade finance (6)

| ID | Original filename | Working subject | Priority |
|---|---|---|---|
| PHY-01 | `دستورالعمل پذیرش انبار و صدور، معامله و تسویه گواهی سپرده کالایی.pdf` | Warehouse admission and commodity deposit certificates | Core |
| PHY-02 | `ثبتهای_حسابداری_معاملات_گواهی_سپرده_کالایی_در_بورس_انرژی.pdf` | Accounting for commodity deposit certificates | Supporting |
| PHY-03 | `دستورالعمل انتشار اوراق خريد دين كالايي در بورس كالاي ايران و بورس انرژي ايران.pdf` | Commodity purchase-debt securities | Supporting |
| PHY-04 | `001_d4aff401-f795-4459-8bd8-ff7814cec737..pdf` | Supply-chain finance backed by credit instruments | Supporting |
| PHY-05 | `بانکرینگ (سوخت دریایی).pdf` | Marine-fuel bunkering | Supporting |
| PHY-06 | `11zon_JPEG-to-PDF (2).pdf` | Domestic refinery purchases of crude oil and gas condensate through IRENEX | Supporting |

## DER — Derivatives (5)

| ID | Original filename | Working subject | Priority |
|---|---|---|---|
| DER-01 | `5f6e6a57-9d2c-11ec-b5a0-005056b98203.pdf` | Futures trading procedure | Core |
| DER-02 | `22ce2cfa-b028-11ed-b5ad-005056b98203.pdf` | Options trading procedure | Core |
| DER-03 | `193993d7-b499-11ec-b5a1-005056b98203.pdf` | Futures committee rules | Supporting |
| DER-04 | `3da78c2f-9d26-11ec-b5a0-005056b98203.pdf` | Futures default market | Supporting |
| DER-05 | `003_sabt ati bourse energy.PDF` | Futures accounting entries | Supporting |

No standalone forward/salaf instruction was identified in this intake set. Until additional
evidence is collected, the relevant rules should be traced through GOV-02 and any instrument-level
notices; this absence is an inventory observation, not proof that no such rule exists.

## ELE — Electricity market and bilateral supply (15)

This is the primary research domain for the next document-analysis stage.

| ID | Original filename | Working subject | Priority |
|---|---|---|---|
| ELE-01 | `آیین نامه اجرایی بند ب ماده 43.pdf` | Increasing exchange-based electricity trading and competition | Core |
| ELE-02 | `ویرایش پاییز 1404  دستورالعمل برق.pdf` | Electricity-market instruction, autumn 1404 edition | Core |
| ELE-03 | `اصلاحیه دستورالعمل توسعه مبادلات برق تابستان 1403.pdf` | Amendment on electricity-trade development | Core |
| ELE-04 | `مقررات حاکم بر تابلو برق آزاد در بورس انرژی.pdf` | Free Electricity Board rules | Core |
| ELE-05 | `«رویه اجرایی عرضه برق تولیدی نیروگاه_های مقیاس کوچک در تابلو برق آزاد بورس انرژی».pdf` | Small-scale generation offers on the Free Electricity Board | Core |
| ELE-06 | `رویه اجرائی فروش برق نیروگاههای مقیاس کوچک در بورس انرژی.pdf` | Small-scale power-plant electricity sales | Core |
| ELE-07 | `اصلاحیه مقررات نرخ و ضوابط عرضه برق نیروگاه های مقیاس کوچک.pdf` | Small-scale generator pricing and offer amendment | Core |
| ELE-08 | `ضوابط انعقاد قرارداد دوجانبه نیروگاه های دارای قرارداد خرید تضمینی برق.pdf` | Bilateral contracts for generators with guaranteed-purchase contracts | Supporting |
| ELE-09 | `ضوابط عرضه برق نیروگاه های حرارتی جديد الاحداث.pdf` | Offers by newly commissioned thermal power plants | Supporting |
| ELE-10 | `ضوابط عرضه برق سیستم های ذخیره ساز انرژی متصل به شبکه سراسری.pdf` | Grid-connected energy-storage offers | Supporting |
| ELE-11 | `مصوبه وزارت نيرو درخصوص روش اجرايي خريد برق مازاد، محدوديت در مصرف و قرارداد دو جانبه برق توليدي نيروگاه هاي احداث شده توسط صنايع.pdf` | Surplus purchases, consumption constraints, and industrial-generator bilateral contracts | Supporting |
| ELE-12 | `اصلاحیه سند تأمین برق مصارف بیشتر از الگوی مصرف مشترکان.pdf` | Supply above the regulated consumption pattern | Supporting |
| ELE-13 | `11zon_JPEG-to-PDF.pdf` | Supply obligation for industrial consumers above five megawatts | Supporting |
| ELE-14 | `11351_orig.pdf` | Electricity exports and a regional exchange-based market | Supporting |
| ELE-15 | `قانون مانع زدایی.pdf` | Financing and development of the electricity industry | Supporting |

## CER — Electricity-related certificates (9)

| ID | Original filename | Working subject | Priority |
|---|---|---|---|
| CER-01 | `دستورالعمل نحوه تدارک خرید و فروش گواهی ظرفیت.pdf` | Capacity-certificate procurement and sale | Core |
| CER-02 | `Renawable Energy Certificate.pdf` | Renewable electricity production-certificate settlement | Core |
| CER-03 | `171542620625419600.pdf` | Article 10 program and power-plant fuel-related certificates | Supporting |
| CER-04 | `444444.pdf` | Article 4 implementation: industrial generation, electricity sale, and capacity certificates | Core |
| CER-05 | `روش اجرایی ماده ۹ آیین نامه اجرایی ماده ۴ قانون مانع زدایی.pdf` | Implementation of Article 9 under the Article 4 regulation | Supporting |
| CER-06 | `_1405.02.05 ضوابط معافیت مشترکین دارای نیروگاه خورشیدی از برنامه مدیریت مصرف برق.pdf` | Demand-management exemption for customers with solar generation | Supporting |
| CER-07 | `ضوابط ایجاد نهاد تجمیع کننده برق تجدیدپذیر (1).pdf` | Renewable-electricity aggregators | Supporting |
| CER-08 | `آيين نامه اجرايي ماده (16) قانون جهش توليد دانش بنيان.pdf` | Implementation of Article 16 of the Knowledge-Based Production Leap Act | Supporting |
| CER-09 | `شیوه نامه اجرایی مواد 8 و 9 موضوع ماده 10 قانون مانع زدایی از صنعت برق.PDF` | Articles 8 and 9 procedure under Article 10 | Core |

## EFF — Energy-efficiency and environmental market (9)

| ID | Original filename | Working subject | Priority |
|---|---|---|---|
| EFF-01 | `دستورالعمل اجرایی آیین نامه بازار بهینه سازی انرژی و محیط زیست.pdf` | Energy-efficiency and environment market implementation | Core |
| EFF-02 | `دستورالعمل صدور، گواهی صرفه جویی- آبانماه 1404.pdf` | Issuance, application, and settlement of natural-gas savings certificates | Core |
| EFF-03 | `Sabtahye hesabdari - Govahi Sarfe Juyee Energy.pdf` | Energy-savings certificate accounting | Core |
| EFF-04 | `نظام نامه ثبت، اندازه گیری، راستی آزمایی و تایید صرفه جویی انرژی و کاهش تولید آلاینده ها و انتشار گازهای گلخانه ای.pdf` | Registration, measurement, verification, and approval | Core |
| EFF-05 | `مصوبه شورای عالی انرژی درخصوص اجرای آیین نامه بازار بهینه سازی انرژی و محیط زیست.pdf` | High Council decision implementing the market regulation | Supporting |
| EFF-06 | `آیین نامه اجرایی بند الف ماده 46 قانون برنامه پنجساله پیشرفت جمهوری اسلامی ایران.pdf` | Legal and financial basis under Article 46(a) | Supporting |
| EFF-07 | `نسخه چاپی آئين نامه اجرايي بند (س) ماده واحده تبصره (1) قانون بودجه سال 1402 كل كشور (1).pdf` | Budget-law implementation relevant to efficiency financing | Supporting |
| EFF-08 | `نسخه چاپی آيين نامه اجرايي ماده (14) قانون مانع زدايي از توسعه صنعت برق (1).pdf` | Article 14 implementation for electricity-industry development | Supporting |
| EFF-09 | `آیین نامه نحوه فعالیت شرکت های کارور برق و نصب شمارشگرهای هوشمند.pdf` | Electricity ESCOs and smart meters | Supporting |

## STR — National energy strategy and policy context (7)

| ID | Original filename | Working subject | Priority |
|---|---|---|---|
| STR-01 | `سند ملي راهبرد انرژي كشور.pdf` | National energy strategy | Contextual |
| STR-02 | `سند تامین انرژی بخش حمل و نقل کشور تا افق ۱۴۲۰.pdf` | Transport-sector energy supply to horizon 1420 | Contextual |
| STR-03 | `سند تراز تولید و مصرف گاز طبیعی در کشور تا افق ۱۴۲۰.pdf` | Natural-gas production and consumption balance to horizon 1420 | Contextual |
| STR-04 | `سند چشم انداز تولید نفت خام تا افق سال ۱۴۲۰.pdf` | Crude-oil production outlook to horizon 1420 | Contextual |
| STR-05 | `مصوبه شورای عالی انرژی درخصوص طرح جامع انرژی کشور.pdf` | Comprehensive national energy plan | Contextual |
| STR-06 | `مصوبه شورای عالی انرژی درخصوص الگوی مصرف برق و گاز طبیعی.pdf` | Electricity and natural-gas consumption patterns | Contextual |
| STR-07 | `shora-1402-08-01_opt-2-.pdf` | Energy mix, investment, and macro-level programs | Contextual |

## CMP — Adjacent compliance and electricity-use regulation (3)

| ID | Original filename | Working subject | Priority |
|---|---|---|---|
| CMP-01 | `آيين نامه اجرايي ماده (14) الحاقي قانون مبارزه با پولشويي-کامل.pdf` | Anti-money-laundering implementation | Contextual |
| CMP-02 | `آيين نامه اجرايي مواد (55) و (56) قانون مبارزه با قاچاق كالا و ارز.pdf` | Anti-smuggling implementation | Contextual |
| CMP-03 | `آيين نامه استخراج رمز دارايي ها با اصلاحات بعدی.pdf` | Crypto-asset mining and regulated electricity use | Contextual |

For CMP documents, extract only provisions directly concerning an exchange, broker, customer
identification, energy transactions, or electricity consumption for crypto-asset mining.

## Cross-cutting analytical tags

The eight categories answer *why a document matters*. During article-level extraction, apply
additional tags for *what the provision governs*: `legal-authority`, `institution`, `participant`,
`admission`, `instrument`, `board`, `order-and-trade`, `price`, `fee`, `clearing`, `settlement`,
`delivery`, `collateral`, `default`, `metering`, `verification`, `reporting`, `accounting`,
`bilateral-contract`, `export`, `amendment`, and `effective-date`.

## Intake expansion beyond IRENEX

Future collection should preserve issuer provenance and use the same analytical taxonomy. The
next source map should cover, at minimum, the Ministry of Energy, Ministry of Petroleum, Tavanir,
Iran Grid Management Company, SATBA, the Securities and Exchange Organization, Central Securities
Depository of Iran, the Supreme Council of Energy, and other legally competent upstream bodies.
SATBA should be treated as the renewable-energy and energy-efficiency authority; electricity
distribution responsibilities must be attributed to the relevant distribution companies and
sector institutions based on each source, rather than assumed from the publisher name.

Each new source must be stored unchanged, registered with provenance, mapped to one primary role
and any cross-cutting tags, linked to documents it amends or implements, and assigned a reading
priority. A document may be marked superseded only with explicit evidence; a newer-looking date or
filename is insufficient.
