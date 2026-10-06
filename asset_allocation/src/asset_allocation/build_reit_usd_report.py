"""Build a standalone Plotly report from validated, existing REIT derivatives."""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/analysis"
REPORTS = ROOT / "reports"
HTML = REPORTS / "REIT_USD_LEAD_LAG_REPORT.html"
MARKDOWN = REPORTS / "REIT_USD_LEAD_LAG_REPORT.md"
FUNDS = ("Arzesh Maskan", "Kelid", "Danik", "Kakh")


def read(name: str) -> pd.DataFrame:
    path = DATA / name
    if not path.is_file():
        raise FileNotFoundError(f"Build the documented derivative first: {path}")
    return pd.read_csv(path, dtype={"ins_code": str})


def html_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{escape(value)}</th>" for value in headers)
    body = "".join("<tr>" + "".join(f"<td>{escape(value)}</td>" for value in row) + "</tr>" for row in rows)
    return f"<div class='table-wrap'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    def cell(value: str) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(map(cell, headers)) + " |",
             "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(map(cell, row)) + " |" for row in rows)
    return "\n".join(lines)


def figure_html(fig: go.Figure, *, first: bool = False) -> str:
    fig.update_layout(template="plotly_white", paper_bgcolor="white", plot_bgcolor="white",
                      font=dict(family="Arial, sans-serif", color="#203149"),
                      margin=dict(l=65, r=25, t=60, b=75), legend=dict(orientation="h", y=-0.2))
    return fig.to_html(full_html=False, include_plotlyjs="inline" if first else False,
                       config={"responsive": True, "displaylogo": False})


def build() -> tuple[Path, Path]:
    cumulative = read("reit_usd_tedpix_two_year_cumulative.csv")
    summary = read("reit_usd_tedpix_two_year_cumulative_summary.csv")
    housing = read("tehran_housing_two_year_cumulative.csv")
    housing_summary = read("tehran_housing_two_year_cumulative_summary.csv").iloc[0]
    daily = read("reit_assembly_reinvested_daily.csv")
    events = read("reit_assembly_reinvestment_events.csv")
    lags = read("reit_usd_weekly_lag_correlations.csv")
    models = read("reit_usd_weekly_predictive_regressions.csv")
    housing_corr = read("reit_housing_monthly_correlation.csv")
    if set(FUNDS) - set(summary.asset) or set(FUNDS) - set(daily.fund):
        raise ValueError("Current four-fund coverage is absent from the derived inputs")
    if len(lags) != 20 or not set(FUNDS).issubset(models.fund):
        raise ValueError("Lag or regression derivatives do not cover four funds")
    if set(FUNDS) - set(housing_corr.fund) or housing_corr.window_end.nunique() != 1 or housing_corr.window_end.iloc[0] != housing.jalali_period.max():
        raise ValueError("REIT–housing correlation is missing a fund or has a stale housing endpoint")
    if not (lags.window_end.nunique() == models.window_end.nunique() == 1 and
            lags.window_end.iloc[0] == models.window_end.iloc[0]):
        raise ValueError("Lag and regression derivatives have different anchors")
    anchor = lags.window_end.iloc[0]
    generated = datetime.now(ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M Asia/Tehran")
    lag_counts = lags.groupby("fund").paired_weeks.first().to_dict()
    model_counts = models.set_index("fund").paired_weeks.to_dict()
    kakh_lag_note = "is suppressed" if lags.loc[lags.fund.eq("Kakh"), "correlation"].isna().all() else "is reported"
    kakh_model_note = "does not meet" if models.loc[models.fund.eq("Kakh"), "status"].iloc[0] != "reported" else "meets"

    # Distinct monthly housing points share a date axis with observed Friday-ending markets.
    fig_cumulative = go.Figure()
    for asset in ("TEDPIX", "USD/IRR", *FUNDS):
        sample = cumulative.loc[cumulative.asset == asset].sort_values("week_end_gregorian")
        fig_cumulative.add_trace(go.Scatter(
            x=sample.week_end_gregorian, y=sample.cumulative_return, mode="lines", name=asset,
            connectgaps=True, customdata=sample[["source_observation_date", "price_method"]].to_numpy(),
            hovertemplate="%{fullData.name}<br>Week: %{x}<br>Cumulative: %{y:.1%}<br>Observed: %{customdata[0]}<br>Method: %{customdata[1]}<extra></extra>"))
    fig_cumulative.add_trace(go.Scatter(
        x=housing.observation_date_gregorian, y=housing.cumulative_return,
        mode="lines+markers", name="Tehran housing (monthly)", line=dict(dash="dash", width=3),
        hovertemplate="Housing month end: %{x}<br>Cumulative: %{y:.1%}<extra></extra>"))
    fig_cumulative.update_layout(title="Cumulative returns from each asset's first observed point",
                                 xaxis_title="Gregorian observation date", yaxis_title="Cumulative return",
                                 yaxis_tickformat=".0%", height=570)

    summary_rows = []
    for asset in ("TEDPIX", "USD/IRR", *FUNDS):
        row = summary.loc[summary.asset == asset].iloc[0]
        summary_rows.append([asset, str(row.baseline_week_end), str(row.latest_observed_week_end),
                             str(int(row.observed_weeks)) + " weeks", f"{row.cumulative_return:+.1%}"])
    summary_rows.append(["Tehran housing", str(housing_summary.baseline_observation_date),
                         str(housing_summary.latest_observation_date),
                         f"{int(housing_summary.observed_months)} months",
                         f"{housing_summary.cumulative_return:+.1%}"])

    fig_dividends = go.Figure()
    for fund in ("Kelid", "Danik"):
        series = daily.loc[daily.fund == fund].sort_values("source_date_gregorian")
        raw = series.traded_close_irr / series.traded_close_irr.iloc[0] - 1
        custom = series.reinvested_value_irr / series.reinvested_value_irr.iloc[0] - 1
        fig_dividends.add_trace(go.Scatter(x=series.source_date_gregorian, y=custom,
                                           mode="lines", name=f"{fund}: reinvested"))
        fig_dividends.add_trace(go.Scatter(x=series.source_date_gregorian, y=raw,
                                           mode="lines", name=f"{fund}: traded", line=dict(dash="dot")))
    fig_dividends.update_layout(title="Effect of recorded dividends since each fund's first traded close",
                                xaxis_title="Trade date", yaxis_title="Cumulative return",
                                yaxis_tickformat=".0%", height=500)
    event_rows = [[str(e.fund), str(e.assembly_date_gregorian), str(e.reinvestment_date_gregorian),
                   f"{e.cash_irr_per_unit:,.0f}", f"{e.reinvestment_close_irr:,.0f}",
                   f"{e.units_after:.6f}", str(e.evidence_status)] for e in events.itertuples()]

    fig_lags = go.Figure()
    lag_rows = []
    for fund in FUNDS:
        sample = lags.loc[lags.fund == fund].sort_values("usd_lag_weeks")
        n = int(sample.paired_weeks.iloc[0])
        if sample.correlation.notna().all():
            fig_lags.add_trace(go.Scatter(x=sample.usd_lag_weeks, y=sample.correlation,
                                          mode="lines+markers", name=f"{fund} (n={n})",
                                          hovertemplate="%{fullData.name}<br>USD lag: %{x} weeks<br>Pearson r: %{y:+.3f}<extra></extra>"))
            values = [f"{value:+.3f}" for value in sample.correlation]
        else:
            values = ["—"] * 5
        lag_rows.append([fund, str(n), *values])
    fig_lags.add_hline(y=0, line_color="gray", line_width=1)
    fig_lags.update_layout(title="USD/IRR lead-lag correlation on identical weeks per fund",
                           xaxis_title="USD lag in completed weeks (0 = same week)",
                           yaxis_title="Pearson correlation", xaxis=dict(tickmode="linear", dtick=1),
                           yaxis=dict(range=[-1, 1]), height=500)

    model_rows = []
    for fund in FUNDS:
        row = models.loc[models.fund == fund].iloc[0]
        model_rows.append([fund, str(int(row.paired_weeks)),
                           f"{row.beta_usd_l1:+.3f}" if pd.notna(row.beta_usd_l1) else "—",
                           f"{row.beta_usd_l2:+.3f}" if pd.notna(row.beta_usd_l2) else "—",
                           f"{row.joint_usd_pvalue:.4f}" if pd.notna(row.joint_usd_pvalue) else "—",
                           f"{row.joint_usd_fdr_pvalue:.4f}" if pd.notna(row.joint_usd_fdr_pvalue) else "—",
                           f"{row.incremental_r_squared:+.3f}" if pd.notna(row.incremental_r_squared) else "—",
                           "Reported" if row.status == "reported" else "Insufficient history"])

    fig_housing = go.Figure()
    housing_rows = []
    for fund in FUNDS:
        row = housing_corr.loc[housing_corr.fund == fund].iloc[0]
        reported = pd.notna(row.correlation)
        fig_housing.add_trace(go.Bar(x=[fund], y=[row.correlation if reported else None],
                                     marker_color="#227da8" if reported and row.correlation >= 0 else "#c85b5b" if reported else "#cbd5df",
                                     name=fund, showlegend=False,
                                     hovertemplate=f"{fund}<br>Pearson r: %{{y:+.3f}}<br>Paired months: {int(row.paired_months)}<extra></extra>"))
        housing_rows.append([fund, str(int(row.paired_months)),
                             f"{row.correlation:+.3f}" if reported else "—",
                             "Reported" if reported else "Insufficient history"])
    fig_housing.add_hline(y=0, line_color="gray", line_width=1)
    kakh_housing = housing_corr.loc[housing_corr.fund.eq("Kakh")].iloc[0]
    if pd.isna(kakh_housing.correlation):
        fig_housing.add_annotation(x="Kakh", y=0, text=f"Insufficient<br>n={int(kakh_housing.paired_months)}",
                                   showarrow=False, yshift=24)
    fig_housing.update_layout(title="Same-month REIT return correlation with Tehran housing",
                              xaxis_title="Fund", yaxis_title="Pearson correlation",
                              yaxis=dict(range=[-1, 1]), height=480)

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Iranian REITs, USD/IRR, and Tehran Housing</title><style>
body{{font:16px/1.6 Arial,sans-serif;color:#203149;background:#f4f7fb;margin:0}}main{{max-width:1120px;margin:auto;background:white;padding:28px 38px 65px;box-shadow:0 2px 18px #dbe3ed}}h1{{font-size:2rem;line-height:1.2;margin-bottom:8px;color:#143050}}h2{{color:#143050;margin-top:42px;border-bottom:1px solid #dbe3ed;padding-bottom:5px}}h3{{color:#234b75;margin-top:27px}}.meta{{color:#64758a}}.lead{{font-size:1.1rem;max-width:900px}}.callout{{background:#eaf3fb;border-left:4px solid #2376ac;padding:12px 18px;margin:18px 0}}.chart{{width:100%;overflow:hidden}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;margin:12px 0 22px;font-size:.94rem}}th,td{{border-bottom:1px solid #dce4ec;text-align:right;padding:9px 10px;white-space:nowrap}}th:first-child,td:first-child{{text-align:left}}th{{background:#eaf1f8;color:#143050}}tr:nth-child(even){{background:#f8fafc}}small,.foot{{color:#64758a}}code{{background:#f2f5f8;padding:2px 4px}}@media(max-width:700px){{main{{padding:18px}}h1{{font-size:1.55rem}}}}
</style></head><body><main><h1>Iranian REITs, USD/IRR, and Tehran housing</h1><p class="meta">Interactive research report · Market endpoint: {escape(anchor)} · Generated: {escape(generated)}</p>
<p class="lead">Four real-estate funds are compared with the dollar price in rials, TEDPIX, and monthly Tehran housing. Fund returns use raw traded closes and a custom reinvestment of recorded approved distributions; they do not use exchange-adjusted fund prices.</p>
<div class="callout"><strong>Main reading.</strong> Across the 24-Jalali-month weekly window, Arzesh Maskan, Danik, and Kelid have {lag_counts['Arzesh Maskan']}, {lag_counts['Danik']}, and {lag_counts['Kelid']} common weeks for the five USD lag correlations. Kakh has {lag_counts['Kakh']} and {kakh_lag_note} under the current coverage rule. The fund-specific predictive models have {model_counts['Arzesh Maskan']}, {model_counts['Danik']}, and {model_counts['Kelid']} complete weeks, respectively; their FDR-adjusted joint USD p-values are {models.loc[models.fund.eq('Arzesh Maskan'), 'joint_usd_fdr_pvalue'].iloc[0]:.4f}, {models.loc[models.fund.eq('Danik'), 'joint_usd_fdr_pvalue'].iloc[0]:.4f}, and {models.loc[models.fund.eq('Kelid'), 'joint_usd_fdr_pvalue'].iloc[0]:.4f}. These are in-sample associations, not causal or out-of-sample forecasts.</div>
<h2>1. Two-year cumulative comparison</h2><p>Each line starts at its own first available observation; Kakh begins later. Weekly markets use observed Friday-ending points. Housing uses actual month ends and a flagged chain-linked Kilid listing-price proxy. Rent and ownership costs are excluded.</p><div class="chart">{figure_html(fig_cumulative, first=True)}</div>{html_table(['Asset','Baseline','Last observation','Observed points','Cumulative return'],summary_rows)}
<h2>2. Dividend reinvestment</h2><p>The solid Kelid and Danik paths compound fractional units bought at the first traded close on or after each supplied assembly date. Dotted lines are traded-close appreciation. This immediate-cash assumption may precede actual payment. Arzesh Maskan and Kakh have no event in the current ledger; equality with traded-price returns does not establish zero dividends.</p><div class="chart">{figure_html(fig_dividends)}</div>{html_table(['Fund','Assembly date','Purchase date','Cash IRR/unit','Purchase close IRR','Units after','Evidence'],event_rows)}
<h2>3. Weekly dollar lead-lag</h2><p>Lag 0 compares returns ending in the same completed week; lag 1 uses the prior completed week, and so on. All five lags for a fund use exactly the same paired dates. A fund needs at least 74 common weeks; USD returns across its source-method boundary are excluded. Pearson coefficients describe co-movement only.</p><div class="chart">{figure_html(fig_lags)}</div>{html_table(['Fund','Common weeks','Lag 0','Lag 1','Lag 2','Lag 3','Lag 4'],lag_rows)}
<h2>4. Conditional predictive model</h2><p><code>REIT return(t) = intercept + own return(t−1) + USD return(t−1) + USD return(t−2) + TEDPIX return(t−1) + error(t)</code></p><p>The joint p-value tests both USD coefficients using HAC/Newey–West standard errors with four lags. FDR p-values apply Benjamini–Hochberg correction across the {int(models.joint_usd_pvalue.notna().sum())} reportable fund tests. ΔR² is the in-sample improvement over the own-lag and TEDPIX-lag model fitted on the same rows. At least 52 complete weeks are required; Kakh has {model_counts['Kakh']}.</p>{html_table(['Fund','Weeks','USD lag 1 β','USD lag 2 β','Joint p','FDR p','Δ in-sample R²','Status'],model_rows)}
<h2>5. Same-month REIT–housing correlation</h2><p>The last 24 complete Jalali months, {housing_corr.window_start.iloc[0]} through {housing_corr.window_end.iloc[0]}, are matched without a lag. REIT returns use the custom dividend-reinvested value; housing uses observed monthly price appreciation from the flagged chain-linked Kilid listing-price proxy. No missing month is filled. A Pearson estimate requires at least {int(housing_corr.minimum_pairs.iloc[0])} paired months and nonconstant returns; Kakh has {int(kakh_housing.paired_months)} observed pairs and is {'suppressed' if pd.isna(kakh_housing.correlation) else 'reported'}.</p><div class="chart">{figure_html(fig_housing)}</div>{html_table(['Fund','Paired months','Pearson r','Status'],housing_rows)}
<h2>Interpretation and limits</h2><p>The regression adds information within this historical sample, but low p-values do not prove a trading strategy or a causal dollar effect. The USD history spans two collection methods, and returns at that boundary are omitted. Fund dividends beyond the three recorded approved events remain unaudited; the assembly-date cash assumption is optimistic if payment occurred later. Housing is a monthly listing-price proxy; its same-month correlation does not establish a delayed effect. Kakh {kakh_model_note} the regression sample minimum.</p>
<p class="foot">Source derivatives: <code>reit_assembly_reinvested_daily.csv</code>, <code>reit_usd_tedpix_two_year_cumulative.csv</code>, <code>tehran_housing_two_year_cumulative.csv</code>, <code>reit_usd_weekly_lag_correlations.csv</code>, <code>reit_usd_weekly_predictive_regressions.csv</code>, and <code>reit_housing_monthly_correlation.csv</code> under <code>data/processed/analysis</code>. Methods and refresh order: <code>docs/WORKFLOW.md</code>. No canonical raw source was modified to generate this report.</p></main></body></html>"""

    markdown = f"""# Iranian REITs, USD/IRR, and Tehran housing

Data endpoint: {anchor}. Report generated: {generated}. Run `python -m asset_allocation.build_reit_usd_report` from this project to generate the [local interactive Plotly report](REIT_USD_LEAD_LAG_REPORT.html), or open the versioned [analysis notebook](../notebooks/iran_reits_cross_asset_analysis.ipynb) for its charts.

The four funds are Arzesh Maskan, Kelid, Danik, and Kakh. Returns use raw traded closes with fractional-unit reinvestment of the three approved distributions in the current ledger. This assumes immediate cash availability at assembly. Arzesh Maskan and Kakh have no recorded event; their displayed paths do not establish complete total return.

## Two-year cumulative comparison

{markdown_table(['Asset','Baseline','Last observation','Observed points','Cumulative return'], summary_rows)}

Housing is a monthly, chain-linked Kilid listing-price proxy. Kakh starts later than the other market series, so cumulative values do not all cover identical holding periods.

## Recorded reinvestments

{markdown_table(['Fund','Assembly date','Purchase date','Cash IRR/unit','Purchase close IRR','Units after','Evidence'], event_rows)}

## Weekly USD lag correlations

Each fund's lag 0–4 estimates use the same paired weeks. A dash means fewer than 74 common weeks or insufficient variation. USD returns crossing the source-method boundary are excluded.

{markdown_table(['Fund','Common weeks','Lag 0','Lag 1','Lag 2','Lag 3','Lag 4'], lag_rows)}

## Conditional predictive regression

The weekly model includes REIT lag 1, USD lags 1 and 2, and TEDPIX lag 1. The joint USD test uses HAC(4); its FDR p-value adjusts across reportable funds. ΔR² is in-sample against a same-date model without USD. At least 52 complete weeks are required.

{markdown_table(['Fund','Weeks','USD lag 1 beta','USD lag 2 beta','Joint p','FDR p','Delta in-sample R2','Status'], model_rows)}

## Same-month REIT–housing correlation

The last 24 complete Jalali months ({housing_corr.window_start.iloc[0]}–{housing_corr.window_end.iloc[0]}) are aligned without a lag. Fund returns use the custom cash-reinvested value and housing uses the flagged chain-linked Kilid monthly price proxy. A correlation needs at least {int(housing_corr.minimum_pairs.iloc[0])} observed pairs; Kakh is suppressed.

{markdown_table(['Fund','Paired months','Pearson r','Status'], housing_rows)}

These results are descriptive and in-sample. They do not establish causation or out-of-sample forecasting skill. Dividend histories and actual cash dates need further verification. See [the workflow](../docs/WORKFLOW.md) and [dividend audit](../docs/REIT_DIVIDEND_AUDIT.md).
"""
    REPORTS.mkdir(parents=True, exist_ok=True)
    HTML.write_text(html, encoding="utf-8")
    MARKDOWN.write_text(markdown, encoding="utf-8")
    return HTML, MARKDOWN


if __name__ == "__main__":
    html_path, md_path = build()
    print(f"Wrote {html_path} and {md_path}")
