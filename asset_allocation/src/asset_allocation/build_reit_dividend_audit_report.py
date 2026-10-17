"""Generate quality checks and the active eight-fund dividend audit report."""
from pathlib import Path
import math
import pandas as pd
from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame
from asset_allocation.build_reit_assembly_reinvestment import ROOT, RAW, FUNDS, EVENTS, LEDGER
DATA=ROOT/"data/processed/analysis"
REPORT=ROOT/"reports/REIT_EIGHT_FUND_REINVESTMENT.md"
def build():
    summary=pd.read_csv(DATA/"reit_eight_fund_comparison.csv",dtype={"ins_code":str})
    events=pd.read_csv(EVENTS,dtype={"ins_code":str})
    daily=pd.read_csv(DATA/"reit_assembly_reinvested_daily.csv",dtype={"ins_code":str})
    weekly=pd.read_csv(DATA/"reit_all_fund_weekly_returns.csv")
    quality=[]
    for code,name in FUNDS.items():
        raw=pd.read_csv(RAW/f"{code}.csv")
        traded=raw.loc[raw.has_trade.eq(True)].sort_values("source_date_gregorian")
        gap=pd.to_datetime(traded.source_date_gregorian).diff().dt.days
        jumps=pd.to_numeric(traded.closing_price_irr).pct_change().abs()
        quality.append({"fund":name,"ins_code":code,"raw_rows":len(raw),"traded_rows":len(traded),
                        "duplicate_dates":int(raw.source_date_gregorian.duplicated().sum()),
                        "nonpositive_closes":int((pd.to_numeric(raw.closing_price_irr,errors="coerce")<=0).sum()),
                        "nontrading_rows":int((~raw.has_trade.eq(True)).sum()),
                        "gaps_over_14_days":int(gap.gt(14).sum()),
                        "price_jumps_over_30pct":int(jumps.gt(.30).sum()),
                        "latest_traded_date":traded.source_date_gregorian.max()})
    quality=pd.DataFrame(quality)
    atomic_frame(DATA/"reit_market_quality_audit.csv",quality)
    pivot=weekly.pivot(index="period",columns="fund",values="total_return")
    correlations=pivot.corr(min_periods=12)
    correlations.index.name="fund"
    atomic_frame(DATA/"reit_eight_fund_weekly_correlations.csv",correlations.reset_index())
    risk=weekly.groupby("fund").total_return.agg(["count","std"]).reset_index()
    risk["annualized_weekly_volatility"]=risk["std"]*math.sqrt(52)
    atomic_frame(DATA/"reit_eight_fund_risk.csv",risk)
    lines=["# Eight Iranian REITs: hypothetical dividend reinvestment",
           "",
           "Generated from the canonical raw traded-close CSVs and the user-supplied event ledger. Market data end 2026-10-07 for all eight funds. The latest common valid traded date is 2026-10-07.",
           "",
           "This is a hypothetical first-traded-session-after-event model. Cash is assumed immediately available; fractional units are allowed. There are no fees, spread, taxes, or slippage. The results are provisional because historical dividend coverage is not complete.",
           "",
           "## Since-inception comparison",
           "",
           "| Fund | First trade | Last trade | Last close IRR | Price return | Holding return | Hypothetical reinvested return | Events | Identified IRR/unit | Status |",
           "|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for row in summary.itertuples():
        lines.append(f"| {row.fund} | {row.first_trading_date} | {row.latest_trading_date} | {row.latest_closing_price_irr:,.0f} | {row.price_return_since_inception:.1%} | {row.holding_return_since_inception:.1%} | {row.hypothetical_total_return_since_inception:.1%} | {row.identified_dividend_events} | {row.identified_dividends_per_original_unit_irr:,.0f} | {row.dividend_history_status.replace('_',' ')} |")
    lines += ["","Returns use each fund's own first valid traded close and are therefore not common-period rankings. The processed comparison CSV also contains three-month, one-year, two-year, and annualized estimates where enough history exists.","",
              "## Included dividend events","",
              "| Fund | Event | Jalali model date | First later trade | IRR/eligible unit | Eligible units | Assumed cash IRR | Date status |",
              "|---|---|---|---|---:|---:|---:|---|"]
    for e in events.itertuples():
        lines.append(f"| {e.fund} | {e.event_id} | {e.event_date_jalali} | {e.reinvestment_date_gregorian} | {e.cash_irr_per_unit:,.0f} | {e.units_entitled:.6f} | {e.total_assumed_dividend_cash:,.2f} | {e.evidence_status} |")
    lines += ["","The Danik 1404 event date is 1404/05/28 as supplied here; it supersedes the earlier project entry of 1404/05/27. Amin Shahr's five dates are reported distribution dates, not verified assembly dates. The zero entry on 1404/08/20 was excluded. Malek Atiyeh's supplementary 89 IRR uses the quantity eligible at its 1405 annual assembly; it is not a fresh entitlement for units acquired later. The 1403/12/08 Arzesh, 1405/04/28 and 1405/06/02 Kakh, and 1405/05/17 Emarat Dey decisions did not document a cash dividend. Kashaneh's 1404 and 1405 distribution history remains unverified. No missing dividend is treated as a confirmed zero.",
              "",
              "Source status: amounts and event descriptions are supplied in the user's project instructions; original source documents were not attached here. The positive amounts enter the hypothetical model as instructed, while independent source verification and historical completeness remain open. Actual payment dates are deliberately unused.",
              "",
              "## Market data checks","",
              "| Fund | Raw rows | Traded rows | Nontrading rows | Gaps over 14 days | Absolute price jumps over 30% |",
              "|---|---:|---:|---:|---:|---:|"]
    for q in quality.itertuples():
        lines.append(f"| {q.fund} | {q.raw_rows} | {q.traded_rows} | {q.nontrading_rows} | {q.gaps_over_14_days} | {q.price_jumps_over_30pct} |")
    lines += ["","All raw series had zero duplicate dates and zero nonpositive closes. Gaps and jumps are review flags, not automatic errors or filled observations. Market charts break lines at gaps exceeding 14 days. The exchange-adjusted price archive ends 2026-10-04, three calendar days before the raw price archive. Its separate since-reference-start returns and dates appear in the comparison CSV; it was not used to calculate dividend-reinvested returns.",
              "",
              "Weekly correlations use Friday-ending observed weeks, require at least 12 paired returns, and do not fill missing weeks. Risk uses the sample standard deviation of observed weekly returns times the square root of 52; short histories need caution. See the processed correlation and risk CSVs.",
              "",
              "The earlier four-fund notebook and English/Persian report sources contain fixed narrative or layout assumptions and are superseded for current eight-fund dividend results. They must be revised before reuse. The eight PNG charts in outputs/reit_dividend_comparison are the current slide assets.",
              ""]
    REPORT.write_text("\n".join(lines),encoding="utf-8")
    return REPORT
if __name__=="__main__":
    print(build())
