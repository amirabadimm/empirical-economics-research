"""Detailed performance interpretation and full active-output report appendices."""
from __future__ import annotations

import pandas as pd


def sections(read, table, escape, funds):
    summary = read("reit_usd_tedpix_two_year_cumulative_summary.csv").set_index("asset")
    housing = read("tehran_housing_two_year_cumulative_summary.csv").iloc[0]
    mix = read("reit_codal_asset_mix_monthly.csv")
    panel = read("reit_usd_tedpix_two_year_cumulative.csv")
    models = read("reit_usd_weekly_predictive_regressions.csv")
    grid = read("reit_requested_correlation_heatmaps.csv")
    pct = lambda x: f"{x:.1%}"
    num = lambda x: "--" if pd.isna(x) else f"{x:+.4f}"
    parts = [r"\section{Performance shortfalls and investor purchasing power}",
             "Positive nominal returns do not by themselves mean successful exposure to property or preservation of dollar purchasing power. The following table reports endpoint return differences in percentage points (pp), and relative ending wealth versus each benchmark. Relative wealth is $(1+R_f)/(1+R_b)-1$; it is not the percentage-point return gap. Housing uses its separately stated monthly endpoints, so its comparison is indicative rather than exactly synchronized. Dollar and TEDPIX share the fund baseline and final weekly date."]
    rows = []
    for fund in funds[:-1]:
        r = summary.loc[fund, "cumulative_return"]
        refs = [housing.cumulative_return, summary.loc["USD/IRR", "cumulative_return"],
                summary.loc["TEDPIX", "cumulative_return"]]
        rows.append([fund, pct(r), *(f"{100*(r-b):+.1f}" for b in refs),
                     *(pct((1+r)/(1+b)-1) for b in refs)])
    parts += [table(["Fund", "Return", "Housing gap pp", "USD gap pp", "TEDPIX gap pp",
                     "Housing-relative wealth", "USD-relative wealth", "TEDPIX-relative wealth"], rows),
              "Arzesh Maskan, Kelid, and Danik all lagged the dollar and TEDPIX over the displayed window. The housing comparison is heterogeneous: Arzesh was close to the housing proxy, whereas Kelid and Danik had much larger shortfalls. Calling all three equally poor housing substitutes would conceal this material difference. These results describe the recorded-distribution scenario; an omitted payout can understate a fund's return.",
              r"\subsection{Observed drawdowns and time-scaled returns}",
              "CAGR uses actual calendar days between the displayed baseline and last observation. Drawdown is the largest fall from a prior observed weekly peak, calculated on the cumulative wealth path. Missing weeks remain unobserved; an intraweek or unobserved trough can be deeper. No Sharpe ratio is claimed without a consistent risk-free series."]
    rows = []
    for fund in ("TEDPIX", "USD/IRR", *funds[:-1]):
        s = summary.loc[fund]
        days = (pd.Timestamp(s.latest_observed_week_end)-pd.Timestamp(s.baseline_week_end)).days
        values = panel.loc[panel.asset.eq(fund)].sort_values("week_end_gregorian").cumulative_return.dropna()+1
        rows.append([fund, pct((1+s.cumulative_return)**(365.25/days)-1),
                     pct((values/values.cummax()-1).min()), str(int(s.observed_weeks))])
    parts += [table(["Asset", "Calendar-day CAGR", "Observed weekly max drawdown", "Observed weeks"], rows),
              r"\section{Portfolio composition: how much property exposure was delivered?}",
              "The user-supplied Codal-derived workbook covers Arzesh Maskan and Danik only. Housing means direct real estate; fixed income combines fixed-income funds and direct debt securities. Other combines cash, equity, and other/receivables. Reported asset shares are accounting composition, not measured return sensitivities or independently verified current market values. Monthly means below are equally weighted snapshots, not time-weighted investment exposures."]
    rows = []
    for fund, s in mix.groupby("fund", sort=True):
        s = s.sort_values("jalali_period")
        for label, col in [("Housing", "housing_share"), ("Fixed income", "fixed_income_share"),
                           ("Other incl. cash/equity", "other_including_cash_equity_share")]:
            rows.append([fund, label, pct(s[col].iloc[0]), pct(s[col].iloc[-1]),
                         f"{100*(s[col].iloc[-1]-s[col].iloc[0]):+.2f}",
                         pct(s[col].mean()), pct(s[col].min()), pct(s[col].max())])
    parts += [table(["Fund", "Component", "First", "Latest", "Change pp", "Mean", "Min", "Max"], rows)]
    for fund, s in mix.groupby("fund", sort=True):
        s = s.sort_values("jalali_period")
        last = s.iloc[-1]
        parts.append(escape(f"{fund}: housing exposure fell from {pct(s.housing_share.iloc[0])} to {pct(last.housing_share)}, "
                            f"while fixed income changed from {pct(s.fixed_income_share.iloc[0])} to {pct(last.fixed_income_share)}. "
                            f"Across all 24 snapshots, average housing exposure was {pct(s.housing_share.mean())}, "
                            f"with a low of {pct(s.housing_share.min())}; fixed income reached {pct(s.fixed_income_share.max())}. "
                            f"The first-to-last comparison therefore does not capture the entire allocation path. "
                            f"At the latest month end, cash was {pct(last.cash_share)}, equity {pct(last.equity_share)}, "
                            f"and other/receivables {pct(last.receivables_share)}. Total reported assets were "
                            f"{last.total_assets_bn_irr:,.1f} billion IRR. Changes in total assets are not investment returns: subscriptions, redemptions, distributions, and valuation changes can all affect the total."))
    parts += ["Both observed portfolios held substantial non-property assets, and direct housing weights declined over the sample. This supports the narrower conclusion that their shares did not deliver pure residential-property exposure. It does not quantify how much of the shareholder return shortfall was caused by the allocation: that requires dated holdings, component total returns, flows, fees, and valuation reconciliations. Kelid and Kakh have no asset-mix observations in this workbook, so their composition cannot be inferred from these two funds.",
              r"\subsection{Source reconstruction and quality exceptions}",
              "Property weights are partly reconstructed from accounting buckets. In particular, a residual classified as receivables is not automatically a liquid fixed-income investment. Three flagged source rows are retained below; they are not silently corrected or removed."]
    for row in mix.loc[mix.data_quality_flag.notna()].itertuples():
        parts.append(escape(f"{row.fund}, {row.jalali_period}: {row.data_quality_flag}. Method: {row.reconstruction_method}."))
    parts += [r"\section{Housing tracking and assessment of management}",
              "A property-oriented fund can fail to track housing in two distinct ways: its cumulative shareholder wealth can grow more slowly, and its monthly returns can have little co-movement with the housing benchmark. Correlation measures the second, not the first. A fund could have high correlation but a persistent return shortfall, or similar endpoint appreciation with low correlation. The six complete correlation tables must therefore be read alongside the endpoint and composition tables.",
              "The near-zero or negative 24-month housing correlations support weak contemporaneous tracking of this particular monthly listing-price proxy. They do not establish that the underlying properties failed to appreciate. Exchange share prices also reflect changes in discounts or premiums to NAV, liquidity, investor demand, distributions, and expectations; property valuations may adjust more slowly. Citywide residential listings may be a poor match for a fund's locations, property types, and rental exposure.",
              "The supplied evidence raises a concrete management-review question: why did direct-property weights decline while the intended property exposure was not closely replicated in monthly share returns? It does not identify mismanagement as the cause. A defensible attribution must distinguish allocation decisions, property selection and operation, fees, financing, valuation timing, and share-price discounts. A pure housing mandate, a diversified property mandate, and a liquidity reserve mandate would imply different appropriate benchmarks; no regulatory or mandate breach is asserted here.",
              table(["Question", "Evidence needed"], [
                  ["Allocation decision quality", "Mandate, dated holdings, component returns and cash flows"],
                  ["Property operating quality", "Occupancy, rents, expenses, acquisitions and sale prices"],
                  ["Share-price discount effect", "Comparable historical NAV and distribution-adjusted share prices"],
                  ["Fee and financing drag", "Expense ratios, debt terms, interest and related-party charges"],
                  ["Complete investor return", "All approved payouts, actual payment dates and corporate actions"]]),
              "The strongest supported conclusion is substantial benchmark underperformance for Kelid and Danik in the current scenario, weak monthly housing co-movement across the longer-history funds, and declining property allocation in the two observed portfolios. Arzesh's endpoint housing shortfall is comparatively small. Management quality remains an attribution question rather than an identified causal result.",
              r"\section{Full conditional-regression diagnostics}",
              "The earlier model table emphasizes USD coefficients. This table adds the own-return and TEDPIX controls, full-model fit, and identical-sample baseline fit. The unadjusted joint USD test concerns one- and two-week lags, not the 4/13/26-week correlations. Statistical significance with low explained variation does not imply a strong trading forecast."]
    parts += [table(["Fund", "Own lag beta", "TEDPIX lag beta", "Full R2", "Baseline R2", "First pair", "Last pair"],
                    [[r.fund, num(r.beta_reit_l1), num(r.beta_tedpix_l1), num(r.r_squared),
                      num(r.baseline_r_squared), r.first_pair_week, r.last_pair_week] for r in models.itertuples()]),
              r"\section{Fund-by-fund assessment}"]
    for fund in funds[:-1]:
        r = summary.loc[fund, "cumulative_return"]
        h = grid.loc[grid.fund.eq(fund) & grid.benchmark.eq("Tehran housing") & grid.window_months.eq(24)].iloc[0]
        m = models.loc[models.fund.eq(fund)].iloc[0]
        parts.append(escape(f"{fund}: cumulative return {pct(r)}; housing correlation {h.correlation:+.3f} "
                            f"from {int(h.paired_observations)} monthly pairs; conditional model R-squared {m.r_squared:.3f}, "
                            f"incremental R-squared {m.incremental_r_squared:.3f}, joint USD p-value {m.joint_usd_pvalue:.4f}. "
                            + ("Asset-composition history is available in the appendix." if fund != "Kelid" else "No asset-composition history is supplied for this fund.")))
    parts += ["Kakh is an exploratory short-history comparison. It remains in qualifying daily and weekly correlation cells, but is excluded from the two-year cumulative ranking. Its 18 complete predictive-regression weeks do not meet the 52-week threshold. Suppressed coefficients are unavailable evidence, not evidence of zero sensitivity.",
              r"\appendix", r"\section{Complete monthly allocation observations}",
              "All 48 supplied fund-month allocations are retained. Percentages are rounded for presentation; unrounded components reconcile to 100 percent. The Other column includes the separately displayed cash and equity shares, so those columns must not be added again."]
    for fund, s in mix.groupby("fund", sort=True):
        parts += [rf"\subsection{{{escape(fund)}}}", table(
            ["Jalali month", "Housing", "Fixed income", "Other", "Cash", "Equity", "Assets bn IRR"],
            [[r.jalali_period, pct(r.housing_share), pct(r.fixed_income_share), pct(r.other_including_cash_equity_share),
              pct(r.cash_share), pct(r.equity_share), f"{r.total_assets_bn_irr:,.1f}"] for r in s.itertuples()])]
    parts += [r"\section{Complete return observations in the two-year review window}",
              "These appendices extend the latest-eight-period tables to the entire review window. Missing entries remain dashes. Earlier fund observations used by 36-month correlation cells remain represented by those cells and their explicit windows."]
    for frequency, name in [("Monthly", "reit_reinvested_monthly_returns.csv"), ("Weekly", "reit_reinvested_weekly_returns.csv")]:
        frame = read(name)
        cutoff = "1403/07" if frequency == "Monthly" else str(summary.baseline_week_end.min())
        wide = frame.loc[frame.period.ge(cutoff)].pivot(index="period", columns="fund", values="reinvested_return").reindex(columns=funds)
        parts += [rf"\subsection{{{frequency} fund returns}}", longtable(
            ["Period", *funds], [[p, *("--" if pd.isna(v) else f"{v:+.2%}" for v in row)] for p, row in wide.iterrows()], escape)]
    parts += [r"\section{Correlation window and suppression audit}",
              "All 80 active cells are listed with actual paired counts and required minimum counts. Benchmark D means USD/IRR; L means USD/IRR leading REIT; H means Tehran housing; T means TEDPIX. The column W/L gives lookback months and dollar lead weeks. Status OK means reported; omit means insufficient paired observations or variation.",
              longtable(["B", "Freq", "Fund", "W/L", "Start", "End", "n/min", "Status"],
                        [[{"TEDPIX":"T", "USD/IRR":"D", "USD/IRR leads REIT":"L", "Tehran housing":"H"}[r.benchmark],
                          r.frequency, r.fund, f"{int(r.window_months)}/{int(r.lag_weeks)}", r.window_start, r.window_end,
                          f"{int(r.paired_observations)}/{int(r.minimum_pairs)}", "OK" if r.status == "reported" else "omit"] for r in grid.itertuples()], escape),
              r"\section{Output inventory and translation guidance}",
              "This single English source consolidates the active notebook's cumulative comparison, traded-versus-reinvested comparison, recent return tables, six heatmaps as full numerical grids, and conditional-regression results. The allocation dropdown is represented by both complete fund allocation histories. Numerical tables provide the exact values behind the interactive visuals; separate chart files are not required to interpret this document. Earlier exchange-adjusted, payment-date, and superseded lag analyses are historical methods and are not mixed into the active conclusions.",
              "Input lineage: the report reads the processed two-year cumulative panels and summaries, assembly reinvestment daily path and event ledger, reinvested weekly and monthly return panels, requested correlation heatmaps, weekly predictive regressions, and Codal asset-mix monthly panel. The allocation workbook snapshot has SHA-256 " + r"\texttt{a2592e41fee12f28db32566224794d3a8129}" + r"\allowbreak\texttt{69f1405845e852270d58f73506a1}" + ". The workbook is user-supplied; its accounting reconstruction and flagged rows have not been independently verified against the original filings. The report generation date is not a source-refresh date.",
              "For Persian translation, preserve all dates, signs, units, observation counts, missing-value markers, formulas, and the distinction between percentage points and relative wealth. Translate the interpretation without strengthening association into causation or treating the recorded-distribution scenario as an audited complete total return."]
    return parts


def longtable(headers, rows, escape):
    head = " & ".join(map(escape, headers)) + r" \\"
    body = "\n".join(" & ".join(map(escape, row)) + r" \\" for row in rows)
    return (r"\begingroup\scriptsize\setlength{\tabcolsep}{3pt}" + "\n"
            + r"\begin{longtable}{" + "l" * len(headers) + "}\n"
            + r"\toprule " + head + r" \midrule\endfirsthead" + "\n"
            + r"\toprule " + head + r" \midrule\endhead" + "\n"
            + body + "\n" + r"\bottomrule\end{longtable}\endgroup")
