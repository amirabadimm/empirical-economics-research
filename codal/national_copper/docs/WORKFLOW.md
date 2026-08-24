# National Copper Codal Workflow

Last reviewed: 2026-08-24

## Objective and boundary

This project collects Codal disclosures for National Iranian Copper Industries Company (NICICO;
ticker `فملی`). The active scope is the parent company's standalone cumulative 3-, 6-, 9-, and
12-month financial statements and the derived quarterly history. Interim current-period columns
must explicitly state `حسابرسی نشده`; annual inputs used for Q4 must explicitly state
`حسابرسی شده`.

## Planned data architecture

- `data/raw`: immutable disclosure responses and attachments plus a collector-owned canonical raw
  index.
- `data/interim`: reproducible parsing, normalization, and report-level alignment stages.
- `data/processed`: documented analysis-ready issuer datasets.
- `src/national_copper/collectors`: source acquisition and raw persistence.
- `src/national_copper/processing`: deterministic transformations from raw to derived data.
- `src/national_copper/analysis`: reusable analytical logic that never writes raw data.
- `notebooks`: exploration and presentation only.
- `outputs`: generated tables, figures, and reports.

## Source contract

- Official search endpoint: `https://search.codal.ir/api/search/v2/q`.
- Official legacy archive: `https://www.codal.ir/OldLetters/ReportOldList.aspx` and its
  `DownloadFiles.ashx` filing packages.
- Exact identity: symbol `فملی` and company name `ملی صنایع مس ایران`.
- Letter type: `6`; parent filings only; subsidiaries and consolidated titles are excluded.
- Required title scope: financial statements for a three-month period.
- Coverage: `1386/03/31` through `1405/03/31`.
- Canonical raw index: `data/raw/financial_statements/q1_filing_index.csv`.
- Immutable inputs: timestamped compressed API pages and content-addressed Excel exports under
  `data/raw/financial_statements`.

The collector archives 118 qualifying original/corrected filings across 79 cumulative statement
periods. The Q1 subset contains 24 filings across 20 periods. Builders choose the latest source
that passes the required audit-status and standalone-statement validations while preserving every
earlier version in raw storage.

The legacy collector adds two scanned, explicitly unaudited 1386 statements (six and nine
months). Their PDF hashes are pinned, and operating revenue, gross profit, and net profit are
double-checked from page 3. The old archive also contains the 1388 three- and nine-month notices,
but an exhaustive six-month-title search returns no 1388 six-month statement.

## Output schema and availability

`data/processed/national_copper_q1_financials.csv` contains one row per Q1 period. All monetary
amounts are in million IRR, matching the source:

- operating revenue, gross profit, and net profit: 20 periods;
- direct production labor, production-overhead wages, and administrative/general/selling wages:
  values are currently extracted for 7 Q1 periods (`1399/03/31`–`1405/03/31`), but remain
  provisional pending the labor-specific audit described below;
- other production-overhead and other administrative/general/selling expenses: the same 7
  periods, explicitly named as non-wage expenses.

The newer Codal schedule format exposes `دستمزد مستقیم تولید` and separate payroll rows under
production overhead and administrative/general/selling expense. It is consistently available
from 1399 onward, and the 1399 schedule includes a 1398 annual comparative. Searches of older
packages found no equivalent period-level labor table; isolated older references to employee
benefits are narrative disclosures and are not substitutes for labor cost.

### Labor-data checkpoint

The labor fields in the current processed CSV are **provisional and not analysis-ready**:

- Codal changed the number and meaning of schedule columns in later filings, so fixed positional
  extraction can select a prior-year or estimate column instead of the current cumulative value.
- Some reported cumulative direct-labor values decrease between adjacent filings (notably in
  1404), indicating a correction, reclassification, or inconsistent disclosure basis. Blind
  cumulative subtraction can therefore create negative quarterly labor expense.
- A dedicated parser must map values from explicit header dates and section identities, retain
  reported cumulative values, compare corrections, and assign a reliability flag before deriving
  quarterly labor flows.

Until that work is complete, only the core revenue/profit fields are validated for analytical use.
Blank historical labor fields must remain blank, and published zero values must not be converted
to missing values without source-level review. The output exposes this limitation in the
machine-readable `labor_data_status` column: populated rows are labelled
`provisional_pending_header_mapping_and_reconciliation`; absent schedules are labelled
`not_disclosed`.

`data/processed/national_copper_quarterly_financials.csv` contains quarterly—not cumulative—flows:

- Q1 = three-month cumulative statement;
- Q2 = six-month cumulative minus Q1;
- Q3 = nine-month cumulative minus six-month cumulative; and
- Q4 = audited annual cumulative minus unaudited nine-month cumulative.

Q1–Q3 inputs must explicitly be unaudited. The annual input must explicitly be audited. Q4 is
therefore labelled as a mixed-audit residual rather than described as an independently audited
quarter. The 80-row `quarterly_availability.csv` records all expected quarters and the exact reason
for each of the 5 unavailable observations. The valid output has 75 rows; 18 fiscal years are
complete, while 1388 and the still-open 1405 are incomplete.

Modern annual Codal packages are titled consolidated but contain both consolidated and standalone
statements. The parser explicitly selects the standalone income statement and rejects the title
containing `تلفیقی`. Consolidated interim statements remain outside scope.

## Validation

The build stops unless all 20 periods are unique and contiguous at the documented annual Q1
grain, every current column is explicitly unaudited, every snapshot hash matches the raw index,
the expected correction is selected, revenue is positive, gross profit does not exceed revenue,
and detailed-cost fields are either complete or all blank. This structural check does not yet
certify the economic validity of quarterly labor differences; that is the pending labor audit.
Persian/Arabic character and digit variants are normalized only for matching; source files and
labels remain unchanged.

## Integrity rules

Source snapshots and attachments are append-only and are never overwritten or transformed in
place. Only a collector may refresh canonical raw data, after schema, issuer identity, uniqueness,
and provenance validation. Processing and notebooks write only derived locations. Credentials, if
ever required, must come from environment variables.

## Reproduction

```powershell
python .\codal\national_copper\src\national_copper\collectors\financial_statements.py
python .\codal\national_copper\src\national_copper\collectors\legacy_financial_statements.py
python .\codal\national_copper\src\national_copper\processing\build_q1_history.py
python .\codal\national_copper\src\national_copper\processing\build_quarterly_history.py
python -m pytest .\codal\national_copper\tests -q
```
