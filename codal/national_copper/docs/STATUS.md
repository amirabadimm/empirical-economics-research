# National Copper Codal Research Status

Last updated: 2026-08-24
Stage: core financial history validated; labor-cost audit pending

## Current state

- The canonical index contains 24 original/corrected filings covering 20 Q1 periods from
  `1386/03/31` through `1405/03/31`.
- Every selected current-period column explicitly reports `حسابرسی نشده`.
- Operating revenue, gross profit, and net profit have complete 20-period coverage.
- Labor schedules are consistently present from 1399 onward, with a 1398 annual comparative in
  the 1399 filing. Older packages do not provide an equivalent period-level labor table.
- Corrections are selected for 1400, 1402, and 1405; superseded filings remain immutable.
- The processed output is `data/processed/national_copper_q1_financials.csv`.
- The expanded raw index contains 118 filings across 79 cumulative statement periods.
- The legacy OldLetters collector recovers explicitly unaudited 1386 six- and nine-month scanned
  statements with pinned hashes and page-level transcription provenance.
- The quarterly output contains 75 valid observations; 18 years are complete.
- The 5 unavailable quarters are recorded explicitly: 1388 Q2-Q3 and 1405 Q2-Q4.
- The CSV currently contains 22 derived quarterly labor observations, but these fields are
  provisional and must not yet be used analytically. Codal column-layout changes and
  non-monotonic cumulative values can produce misaligned or negative quarterly labor amounts.
- Q1–Q3 use unaudited cumulative statements; Q4 is an audited-annual-minus-unaudited-nine-month
  residual and is labelled accordingly.

## Resume checkpoint

1. Build a labor-specific, header-aware parser for the `بهای تمام شده` and
   `هزینه‌های سربار و هزینه‌های عمومی و اداری` schedules.
2. Preserve reported cumulative labor values separately from derived quarterly values.
3. Reconcile corrections and non-monotonic periods, especially 1404, and attach a reliability
   status and reason to every labor observation.
4. Recover the 1398 annual comparative explicitly; leave 1386–1397 blank unless a genuine labor
   schedule is found in another official filing package.
5. Decide whether `سایر هزینه‌ها` belongs in the final analytical view. It must never be labelled
   “other wages” without explicit source evidence.

The validated revenue/profit history and legacy 1386 recovery are safe to resume from as-is.
