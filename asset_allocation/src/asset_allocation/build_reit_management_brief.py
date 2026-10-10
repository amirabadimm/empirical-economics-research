"""Create a concise management brief with all supporting tables at the end."""
from datetime import datetime
from zoneinfo import ZoneInfo

from asset_allocation.build_reit_latex_report import ROOT, read, tabular

REPORT = ROOT / "reports/REIT_MANAGEMENT_BRIEF.tex"
FUNDS = ("Arzesh Maskan", "Kelid", "Danik")


def build():
    returns = read("reit_usd_tedpix_two_year_cumulative_summary.csv").set_index("asset")
    housing = read("tehran_housing_two_year_cumulative_summary.csv").iloc[0]
    mix = read("reit_codal_asset_mix_monthly.csv")
    grid = read("reit_requested_correlation_heatmaps.csv")
    # This concise narrative is an editorial snapshot. Fail on changed inputs rather
    # than silently publishing old conclusions alongside refreshed tables.
    expected_returns = {"Arzesh Maskan": 177.2, "Kelid": 108.2, "Danik": 98.8,
                        "TEDPIX": 287.2, "USD/IRR": 320.9}
    if any(round(100*returns.loc[a, "cumulative_return"], 1) != v
           for a, v in expected_returns.items()) or round(100*housing.cumulative_return, 1) != 160.7:
        raise ValueError("Performance inputs changed; revise the management narrative before rebuilding")
    pct = lambda x: f"{x:+.1%}"
    performance = []
    for fund in FUNDS:
        r = returns.loc[fund, "cumulative_return"]
        performance.append([fund, pct(r), f"{100*(r-housing.cumulative_return):+.1f}",
                            pct((1+r)/(1+returns.loc['USD/IRR', 'cumulative_return'])-1)])
    performance += [["Tehran housing", pct(housing.cumulative_return), "--", "--"],
                    ["TEDPIX", pct(returns.loc['TEDPIX', 'cumulative_return']), "--", "--"],
                    ["USD/IRR", pct(returns.loc['USD/IRR', 'cumulative_return']), "--", "--"]]
    allocations = []
    for fund, frame in mix.groupby("fund"):
        frame = frame.sort_values("jalali_period")
        first, last = frame.iloc[0], frame.iloc[-1]
        allocations.append([fund, f"{first.housing_share:.1%}", f"{last.housing_share:.1%}",
                            f"{frame.housing_share.mean():.1%}", f"{last.fixed_income_share:.1%}",
                            f"{last.other_including_cash_equity_share:.1%}"])
    correlations = []
    for fund in FUNDS:
        row = grid.loc[grid.fund.eq(fund) & grid.benchmark.eq("Tehran housing")
                       & grid.frequency.eq("monthly") & grid.window_months.eq(24)].iloc[0]
        correlations.append([fund, f"{row.correlation:+.3f}", str(int(row.paired_observations))])
    p = [r"\documentclass[11pt,a4paper]{article}", r"\usepackage[margin=2.2cm]{geometry}",
         r"\usepackage[T1]{fontenc}\usepackage{lmodern,booktabs,graphicx,microtype}",
         r"\setlength{\parindent}{0pt}\setlength{\parskip}{0.65em}",
         r"\begin{document}", r"{\LARGE\bfseries Iranian REIT Management Brief}\par",
         "Prepared " + datetime.now(ZoneInfo("Asia/Tehran")).strftime("%d %B %Y") + r"\par",
         r"\textbf{Purpose.} Assess whether the observed REIT returns delivered useful housing exposure and preserved purchasing power over the two-year review period.",
         r"\textbf{Main finding.} Kelid and Danik substantially underperformed the housing proxy. Arzesh Maskan finished above it. All three underperformed USD/IRR and TEDPIX. Monthly share returns showed little co-movement with the housing proxy, and the two portfolios with allocation data held substantial non-property assets.",
         r"\textbf{Investor performance.} Arzesh Maskan returned 177.2\%, Kelid 108.2\%, and Danik 98.8\%, compared with 160.7\% for housing, 287.2\% for TEDPIX, and 320.9\% for USD/IRR. The indicative housing gaps were +16.5, -52.5, and -61.9 percentage points, respectively. Measured against USD/IRR, ending purchasing power fell by 34.1\%, 50.5\%, and 52.8\% respectively. Table 1 distinguishes nominal gains from benchmark gaps.",
         r"\textbf{Housing exposure.} Arzesh's direct-property allocation declined from 83.3\% to 68.7\%; its latest fixed-income share was 26.7\%. Danik's direct-property allocation declined from 89.6\% to 60.2\%, but averaged only 43.1\% across the 24 snapshots and reached a low of 23.9\%. Its fixed-income share reached 75.4\% during the period. At the latest month end, Danik held 12.9\% in fixed income and 26.9\% in other assets, primarily other/receivables. These portfolios did not provide pure direct-property exposure. Table 2 summarizes the observed composition.",
         r"\textbf{Housing tracking.} Over 24 months, housing-return correlations were $-0.064$ for Arzesh, $+0.094$ for Kelid, and $-0.178$ for Danik, based on 21--22 paired monthly returns. These coefficients indicate weak contemporaneous co-movement with this benchmark. They do not measure cumulative underperformance or prove that the underlying properties failed to appreciate. Table 3 reports the sample sizes.",
         r"\textbf{Management implication.} The evidence warrants a review of portfolio composition and shareholder-return delivery. It does not establish mismanagement as the cause. Attribution requires complete distributions, historical NAV and share-price discounts, property operating results, fees, financing costs, and a holdings-based return bridge. No allocation conclusion can be drawn for Kelid from the supplied workbook, which covers Arzesh and Danik only.",
         r"\textbf{Essential qualifications.} Market comparisons use asset-specific first observations in the two-year window ending 9 October 2026. Housing runs from 21 October 2024 to 22 September 2026 and is a monthly Kilid listing-price proxy excluding rental income and ownership costs; its return gap is therefore indicative. REIT returns assume immediate reinvestment of only three recorded approved distributions; payout completeness remains unresolved and assembly-date reinvestment differs from actual cash timing. The allocation workbook is user-supplied and contains three flagged reconstructed observations. Kakh is excluded from this two-year performance assessment because its history is too short.",
         r"\newpage", r"{\Large\bfseries Supporting tables}\par",
         r"\textbf{Table 1 Investor performance and benchmark gaps}",
         tabular(["Asset", "Cumulative return", "Housing gap pp", "USD-relative wealth"], performance),
         r"{\small pp means percentage points. USD-relative wealth equals $(1+R_{fund})/(1+R_{USD})-1$. It measures the change in dollar purchasing power, not the arithmetic return difference. Housing uses the different monthly dates stated above.}\par",
         r"\textbf{Table 2 Arzesh and Danik portfolio composition}",
         tabular(["Fund", "First housing", "Latest housing", "Mean housing", "Latest fixed income", "Latest other"], allocations),
         r"{\small Coverage is 1403/07--1405/06, with 24 snapshots per fund. Mean housing is the equally weighted mean of month-end accounting shares. Other includes cash, equity, and other/receivables. Latest housing, fixed income, and other sum to 100\% before rounding.}\par",
         r"\textbf{Table 3 Monthly housing return correlation over 24 months}",
         tabular(["Fund", "Pearson correlation", "Paired months"], correlations),
         r"{\small Same-month comparisons use reconstructed REIT returns and the housing proxy. Missing returns are not filled. All three rows meet the minimum coverage rule.}\par",
         r"\textbf{Source.} Refreshed processed research inputs underlying \texttt{REIT\_CROSS\_ASSET\_ANALYSIS.tex}, including the user-supplied Codal-derived asset-mix workbook. This brief is a summary of that report.",
         r"\end{document}"]
    REPORT.write_text("\n\n".join(p)+"\n", encoding="utf-8")
    return REPORT


if __name__ == "__main__":
    print(build())
