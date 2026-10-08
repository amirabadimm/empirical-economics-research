"""Generate a complete, table-first LaTeX REIT cross-asset research report."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from asset_allocation.reit_performance_review import sections

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/analysis"
REPORT = ROOT / "reports/REIT_CROSS_ASSET_ANALYSIS.tex"
FUNDS = ("Arzesh Maskan", "Kelid", "Danik", "Kakh")
GRID_SPECS = (
    ("TEDPIX", "daily", (1, 3, 6, 12), "window_months", "m",
     "Daily REIT and TEDPIX returns: same-day correlation"),
    ("TEDPIX", "weekly", (1, 3, 6, 12, 24), "window_months", "m",
     "Weekly REIT and TEDPIX returns: same-week correlation"),
    ("TEDPIX", "monthly", (12, 24, 36), "window_months", "m",
     "Monthly REIT and TEDPIX returns: same-month correlation"),
    ("Tehran housing", "monthly", (12, 24, 36), "window_months", "m",
     "Monthly REIT and Tehran housing price returns: same-month correlation"),
    ("USD/IRR", "daily", (1, 3), "window_months", "m",
     "Daily REIT and USD/IRR returns: same-day correlation"),
    ("USD/IRR leads REIT", "weekly", (4, 13, 26), "lag_weeks", "w",
     "Weekly REIT returns and earlier USD/IRR returns: two-year lead correlations"),
)


def read(name: str) -> pd.DataFrame:
    path = DATA / name
    if not path.is_file():
        raise FileNotFoundError(f"Build the documented derivative first: {path}")
    return pd.read_csv(path, dtype={"ins_code": str})


def latex(value: object) -> str:
    """Escape text fields without altering numeric table cells."""
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
                    "$": r"\$", "#": r"\#", "_": r"\_",
                    "{": r"\{", "}": r"\}"}
    return "".join(replacements.get(character, character) for character in str(value))


def tabular(headers: list[str], rows: list[list[str]]) -> str:
    columns = "l" + "r" * (len(headers) - 1)
    header = " & ".join(latex(value) for value in headers) + r" \\"
    body = "\n".join(" & ".join(latex(value) for value in row) + r" \\" for row in rows)
    return (r"\begin{center}" "\n" r"\small" "\n"
            r"\resizebox{\linewidth}{!}{%" "\n"
            rf"\begin{{tabular}}{{{columns}}}" "\n"
            r"\toprule" "\n" + header + "\n" + r"\midrule" + "\n" + body + "\n"
            r"\bottomrule" "\n" r"\end{tabular}%" "\n" r"}" "\n" r"\end{center}")


def grid_rows(grid: pd.DataFrame, spec: tuple) -> tuple[list[str], list[list[str]]]:
    benchmark, frequency, xs, field, suffix, _ = spec
    sample = grid.loc[grid.benchmark.eq(benchmark) & grid.frequency.eq(frequency)]
    rows = []
    for fund in FUNDS:
        row = [fund]
        for x in xs:
            match = sample.loc[sample.fund.eq(fund) & sample[field].eq(x)]
            if len(match) != 1:
                raise ValueError(f"Missing or duplicate {benchmark}/{frequency}/{fund}/{x} grid cell")
            cell = match.iloc[0]
            n = int(cell.paired_observations)
            row.append(f"{cell.correlation:+.3f} (n={n})" if pd.notna(cell.correlation)
                       else f"-- (n={n})")
        rows.append(row)
    return ["REIT", *(f"{x}{suffix}" for x in xs)], rows


def build() -> Path:
    cumulative = read("reit_usd_tedpix_two_year_cumulative_summary.csv")
    housing = read("tehran_housing_two_year_cumulative_summary.csv").iloc[0]
    daily = read("reit_assembly_reinvested_daily.csv")
    weekly_returns = read("reit_reinvested_weekly_returns.csv")
    monthly_returns = read("reit_reinvested_monthly_returns.csv")
    events = read("reit_assembly_reinvestment_events.csv")
    models = read("reit_usd_weekly_predictive_regressions.csv")
    grid = read("reit_requested_correlation_heatmaps.csv")
    if set(FUNDS) - set(daily.fund) or set(FUNDS) - set(models.fund):
        raise ValueError("Incomplete four-fund derived inputs")
    expected = sum(len(spec[2]) * len(FUNDS) for spec in GRID_SPECS)
    if len(grid) != expected:
        raise ValueError(f"Expected {expected} correlation cells, got {len(grid)}")
    generated = datetime.now(ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M Asia/Tehran")
    market_end = str(cumulative.latest_observed_week_end.max())
    housing_end = str(housing.latest_observation_date)

    cumulative_rows = []
    for asset in ("TEDPIX", "USD/IRR", *FUNDS[:-1]):
        row = cumulative.loc[cumulative.asset.eq(asset)].iloc[0]
        cumulative_rows.append([asset, row.baseline_week_end, row.latest_observed_week_end,
                                f"{int(row.observed_weeks)} weeks", f"{row.cumulative_return:+.1%}"])
    cumulative_rows.append(["Tehran housing", housing.baseline_observation_date,
                            housing.latest_observation_date, f"{int(housing.observed_months)} months",
                            f"{housing.cumulative_return:+.1%}"])
    event_rows = [[e.fund, e.assembly_date_gregorian, e.reinvestment_date_gregorian,
                   f"{e.cash_irr_per_unit:,.0f}", f"{e.reinvestment_close_irr:,.0f}",
                   f"{e.units_after:.6f}"] for e in events.itertuples()]
    dividend_rows = []
    for fund in ("Kelid", "Danik"):
        sample = daily.loc[daily.fund.eq(fund)].sort_values("source_date_gregorian")
        traded = sample.traded_close_irr.iloc[-1] / sample.traded_close_irr.iloc[0] - 1
        reinvested = sample.reinvested_value_irr.iloc[-1] / sample.reinvested_value_irr.iloc[0] - 1
        dividend_rows.append([fund, sample.source_date_gregorian.iloc[0],
                              sample.source_date_gregorian.iloc[-1], f"{traded:+.1%}",
                              f"{reinvested:+.1%}", f"{reinvested - traded:+.1%}"])
    def recent_return_rows(frame: pd.DataFrame) -> list[list[str]]:
        wide = frame.pivot(index="period", columns="fund", values="reinvested_return")
        wide = wide.reindex(columns=FUNDS).tail(8)
        return [[period, *(f"{value:+.2%}" if pd.notna(value) else "--" for value in row)]
                for period, row in wide.iterrows()]

    weekly_rows = recent_return_rows(weekly_returns)
    monthly_rows = recent_return_rows(monthly_returns)
    coverage_rows = []
    for benchmark, frequency, xs, _, _, _ in GRID_SPECS:
        subset = grid.loc[grid.benchmark.eq(benchmark) & grid.frequency.eq(frequency)]
        coverage_rows.append([benchmark, frequency, "/".join(map(str, xs)),
                              str(len(subset)), str(int(subset.correlation.notna().sum()))])
    model_rows = []
    for fund in FUNDS:
        row = models.loc[models.fund.eq(fund)].iloc[0]
        fmt = lambda value, spec: format(value, spec) if pd.notna(value) else "--"
        model_rows.append([fund, str(int(row.paired_weeks)), fmt(row.beta_usd_l1, "+.3f"),
                           fmt(row.beta_usd_l2, "+.3f"), fmt(row.joint_usd_pvalue, ".4f"),
                           fmt(row.incremental_r_squared, "+.3f"),
                           "Reported" if row.status == "reported" else "Insufficient history"])

    def percent(value: float) -> str:
        return f"{value:+.1%}".replace("%", r"\%")

    ranked = sorted([(row.asset, float(row.cumulative_return)) for row in cumulative.itertuples()
                     if row.asset in ("TEDPIX", "USD/IRR", *FUNDS[:-1])]
                    + [("Tehran housing", float(housing.cumulative_return))],
                    key=lambda item: item[1], reverse=True)
    reit_returns = [float(cumulative.loc[cumulative.asset.eq(fund), "cumulative_return"].iloc[0])
                    for fund in FUNDS[:-1]]
    tedpix_24 = grid.loc[grid.benchmark.eq("TEDPIX") & grid.frequency.eq("weekly")
                         & grid.window_months.eq(24) & grid.fund.isin(FUNDS[:-1]), "correlation"].dropna()
    home_24 = grid.loc[grid.benchmark.eq("Tehran housing") & grid.frequency.eq("monthly")
                       & grid.window_months.eq(24) & grid.fund.isin(FUNDS[:-1])]
    dollar_3 = grid.loc[grid.benchmark.eq("USD/IRR") & grid.frequency.eq("daily")
                        & grid.window_months.eq(3), "correlation"].dropna()
    dollar_leads = grid.loc[grid.benchmark.eq("USD/IRR leads REIT")
                            & grid.fund.isin(FUNDS[:-1]), "correlation"].dropna()
    significant = int((models.joint_usd_pvalue < 0.05).sum())
    housing_details = ", ".join(
        f"{latex(row.fund)} {row.correlation:+.3f} ({int(row.paired_observations)} pairs)"
        for row in home_24.itertuples() if pd.notna(row.correlation))

    parts = [r"\documentclass[11pt,a4paper]{article}",
             r"\usepackage[margin=2.2cm]{geometry}",
             r"\usepackage[T1]{fontenc}", r"\usepackage{lmodern}",
             r"\usepackage{booktabs,graphicx,amsmath,microtype,xcolor,longtable,hyperref}",
             r"\hypersetup{colorlinks=true,linkcolor=blue!55!black}",
             r"\setlength{\parindent}{0pt}", r"\setlength{\parskip}{0.6em}",
             r"\title{\textbf{Iranian REIT Performance Review}\\\large Investor Returns, Housing Tracking, Portfolio Composition, and Benchmark Shortfalls}",
             r"\author{Asset Allocation research workflow}",
             rf"\date{{{latex(generated)}}}",
             r"\begin{document}", r"\maketitle", r"\tableofcontents", r"\newpage",
             r"\begin{abstract}",
             f"Four Iranian real-estate funds are compared with TEDPIX, USD/IRR, and Tehran housing. The market endpoint is {latex(market_end)} and the monthly housing endpoint is {latex(housing_end)}. Fund returns use raw traded closes and immediate reinvestment of the three recorded approved distributions. Six correlation grids contain {len(grid)} cells; {int(grid.correlation.notna().sum())} pass the observation and coverage rules. The results describe historical association rather than causal effects or investable forecasts.",
             r"\end{abstract}",
             r"\section{Data, return construction, and sample rules}",
             "The fund series values fractional units at raw traded closes. Recorded cash is assumed available on the assembly date and buys units at the first traded close on or afterward. Actual cash dates and complete distribution histories remain unaudited. Arzesh Maskan and Kakh have no approved cash event in the current ledger; equality of their reconstructed and traded-close paths does not establish zero distributions.",
             "Daily comparisons align observed Gregorian dates; weekly comparisons align completed Friday-ending weeks; monthly comparisons align the same Jalali month. A return is missing across a long trading gap or the USD/IRR source-method boundary. No missing return is filled or interpolated. Housing is monthly only: official CBI observations through 1403/05 and a flagged chain-linked Kilid listing-price extension afterward. The 36-month housing window spans both regimes; the 12- and 24-month windows lie entirely in the extension.",
             "Each Pearson coefficient requires at least five paired returns, at least 70\\% nominal-window coverage, and variation in both series. Daily coverage assumes 20 trading sessions per month, weekly coverage 52/12 weeks per month, and monthly coverage one return per month. The two-year dollar-lead sample requires at least 74 pairs. A dash in any table marks an unreported coefficient; the paired count remains visible.",
             r"\section{Two-year cumulative returns}",
             "Each asset is rebased at its own first observed point inside the two-year window; dates and observation counts differ. The REIT rows reflect recorded-dividend reinvestment. Kakh is excluded because its available cumulative history begins much later. Housing is monthly price appreciation only; rent and ownership costs are excluded.",
             tabular(["Asset", "Baseline", "Last observed", "Observed points", "Cumulative return"], cumulative_rows),
             r"\section{Recorded distributions and reinvestment}",
             "The three ledger events are shown below. The purchase date is the first traded close on or after the assembly date; this is a scenario rather than a verified cash-payment schedule.",
             tabular(["Fund", "Assembly date", "Purchase date", "IRR/unit", "Purchase close IRR", "Units after"], event_rows),
             "For funds with recorded events, the following whole-history comparison separates traded-close appreciation from the specified reinvestment scenario. These baselines are each fund's first traded observation, so this table is not a common-period ranking.",
             tabular(["Fund", "First trade", "Last trade", "Traded close", "Reinvested", "Difference"], dividend_rows),
             r"\section{Recent reconstructed fund returns}",
             "The next two tables retain the notebook's latest observed weekly and monthly dividend-reinvested returns. A dash denotes a missing return, not zero. Weekly periods end Friday; monthly periods use Jalali year/month.",
             r"\subsection{Latest eight weekly returns}",
             tabular(["Friday-ending week", *FUNDS], weekly_rows),
             r"\subsection{Latest eight monthly returns}",
             tabular(["Jalali month", *FUNDS], monthly_rows),
             r"\section{Frequency-matched Pearson correlations}",
             "Every cell gives Pearson $r$ and its paired observation count $n$. Columns marked m are trailing Jalali months; columns marked w are prior completed weeks of USD/IRR returns. REITs are rows throughout. Correlations are descriptive and are not causal estimates."]
    for spec in GRID_SPECS:
        headers, rows = grid_rows(grid, spec)
        parts.extend([rf"\subsection{{{latex(spec[5])}}}", tabular(headers, rows)])
        if spec[0] == "Tehran housing":
            parts.append("Only monthly housing observations exist. Daily and weekly housing heatmaps would require a separate observed high-frequency source and are not calculated here.")
        if spec[0] == "USD/IRR leads REIT":
            parts.append("The dollar is observed 4, 13, or 26 completed weeks before the REIT return (approximately 1, 3, or 6 months). All three columns use the last 24 Jalali months of REIT weeks; a coefficient is suppressed if coverage is too short.")
    parts.extend([r"\section{Conditional weekly predictive regression}",
                  r"The separate model is $r^{\mathrm{REIT}}_t=\alpha+\phi r^{\mathrm{REIT}}_{t-1}+\beta_1 r^{\mathrm{USD}}_{t-1}+\beta_2 r^{\mathrm{USD}}_{t-2}+\gamma r^{\mathrm{TEDPIX}}_{t-1}+\varepsilon_t$. The joint USD p-value uses unadjusted HAC/Newey--West standard errors with four lags. Incremental $R^2$ compares the full model with a model using only the REIT and TEDPIX lag terms on identical rows. At least 52 complete weeks are required.",
                  tabular(["Fund", "Weeks", "USD lag 1 beta", "USD lag 2 beta", "Joint p", "Incremental R2", "Status"], model_rows),
                  r"\section{Correlation-grid coverage summary}",
                  "Reported cells satisfy the observation-count, coverage, and variation rules. The complete grid tables above retain paired counts for suppressed cells.",
                  tabular(["Benchmark", "Frequency", "Columns", "Cells", "Reported"], coverage_rows),
                  r"\section{Results and interpretation}",
                  f"In the two-year cumulative comparison, {latex(ranked[0][0])} had the largest nominal change ({percent(ranked[0][1])}), followed by {latex(ranked[1][0])} ({percent(ranked[1][1])}). The three included REIT scenarios ranged from {percent(min(reit_returns))} to {percent(max(reit_returns))}; Tehran housing price appreciation was {percent(float(housing.cumulative_return))}. These values use each asset's stated baseline and are not equal-horizon risk-adjusted returns.",
                  f"The 24-month weekly TEDPIX correlations for the three longer-history funds range from {tedpix_24.min():+.3f} to {tedpix_24.max():+.3f}. Kakh's 12- and 24-month weekly coefficients are suppressed because its history does not cover enough of those windows. Short windows with five weekly pairs should be treated as unstable descriptive estimates even when they pass the formal threshold.",
                  f"The reportable 24-month monthly housing coefficients are {housing_details}. REIT returns are missing in 1405/01--02 for Arzesh Maskan and Danik; Kelid also lacks 1403/07. The housing source is a listing-price proxy in this interval, so these coefficients should not be read as transaction-price or rent-return relationships.",
                  f"The three-month daily USD/IRR coefficients range from {dollar_3.min():+.3f} to {dollar_3.max():+.3f}. The two-year dollar-leading-weekly-return coefficients for the three longer-history funds range from {dollar_leads.min():+.3f} to {dollar_leads.max():+.3f}; Kakh is suppressed for insufficient two-year coverage. These simple correlations do not by themselves establish a stable dollar lead at the specified 4/13/26-week offsets. The separate one- and two-week conditional regression has unadjusted joint p-values below 0.05 for {significant} funds, but it is in-sample, uses different lags, and is not evidence of causation or out-of-sample forecasting skill.",
                  r"\section{Limitations and reproducibility}",
                  "Only three approved distributions are in the current reinvestment ledger. Additional annual payments and actual payment dates need verification before these reconstructed paths can be called complete total returns. The 36-month housing comparison crosses the CBI-to-Kilid source boundary. Daily and weekly housing returns are unavailable. Pair counts vary because source and fund observations are missing; no interpolation or synthetic return is used. Multiple windows are exploratory and their coefficients should not be interpreted as independent confirmations.",
                  r"\textbf{Rebuild order.} Run the documented REIT reinvestment, cumulative-return, weekly/monthly-return, regression, and monthly housing builders; then run \texttt{python -m asset\_allocation.build\_reit\_requested\_heatmaps} and \texttt{python -m asset\_allocation.build\_reit\_latex\_report}. The report reads processed data only and does not alter canonical sources.",
                  r"\end{document}"])
    parts[-1:-1] = sections(read, tabular, latex, FUNDS)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    return REPORT


if __name__ == "__main__":
    print(f"Wrote {build()}")
