"""Build eight-fund return summaries, periodic returns, and slide-ready charts."""
from pathlib import Path
import pandas as pd
import jdatetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame, friday
from asset_allocation.build_reit_assembly_reinvestment import OUTPUT as DAILY, EVENTS, FUNDS
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"data/processed/analysis"
CHARTS=ROOT/"outputs/reit_dividend_comparison"
def period_returns(group,frequency):
    p=group.copy()
    p["date"]=pd.to_datetime(p.source_date_gregorian)
    if frequency=="weekly":
        p["period"]=p.date.dt.date.map(lambda x: friday(x).isoformat())
    else:
        p["period"]=p.date.dt.date.map(lambda d: str(jdatetime.date.fromgregorian(date=d))[:7])
    p=p.groupby("period",sort=True).tail(1).copy()
    previous=p.period.shift(1)
    if frequency=="weekly":
        adjacent=(pd.to_datetime(p.period)-pd.to_datetime(previous)).dt.days.eq(7)
    else:
        adjacent=pd.to_datetime(p.period.str.replace("/","-")+"-01").dt.to_period("M").astype(int).diff().eq(1)
    p["price_return"]=p.traded_close_irr.pct_change().where(adjacent)
    p["holding_return"]=p.holding_value_irr.pct_change().where(adjacent)
    p["total_return"]=p.reinvested_value_irr.pct_change().where(adjacent)
    p["frequency"]=frequency
    return p[["ins_code","fund","period","source_date_gregorian","frequency","price_return","holding_return","total_return"]]
def window_return(group,days,column):
    last=pd.Timestamp(group.source_date_gregorian.iloc[-1])
    cutoff=last-pd.Timedelta(days=days)
    baseline=group.loc[pd.to_datetime(group.source_date_gregorian)>=cutoff]
    if baseline.empty or pd.Timestamp(baseline.source_date_gregorian.iloc[0])>cutoff+pd.Timedelta(days=14):
        return float("nan")
    return group[column].iloc[-1]/baseline[column].iloc[0]-1
def build():
    daily=pd.read_csv(DAILY,dtype={"ins_code":str})
    events=pd.read_csv(EVENTS,dtype={"ins_code":str})
    adjusted=OUT/"reit_adjusted_daily.csv"
    if adjusted.exists():
        ref=pd.read_csv(adjusted,dtype={"ins_code":str})
        daily=daily.merge(ref[["ins_code","source_date_gregorian","adjusted_close_irr"]],on=["ins_code","source_date_gregorian"],how="left",validate="one_to_one")
    rows=[]
    periodic={"weekly":[],"monthly":[]}
    for code,name in FUNDS.items():
        g=daily.loc[daily.ins_code==code].sort_values("source_date_gregorian").copy()
        e=events.loc[events.ins_code==code]
        g["holding_value_irr"]=g.traded_close_irr+g.source_date_gregorian.map(lambda d: e.loc[e.event_date_gregorian<=d,"cash_irr_per_unit"].sum())
        for f in periodic: periodic[f].append(period_returns(g,f))
        first,last=g.iloc[0],g.iloc[-1]
        identified=e.cash_irr_per_unit.sum()
        status="provisional_dates_and_history_incomplete" if name=="Amin Shahr" else "dividend_history_incomplete"
        if name in ("Kashaneh","Kakh","Emarat Dey"): status="unverified_dividend_history"
        length=(pd.Timestamp(last.source_date_gregorian)-pd.Timestamp(first.source_date_gregorian)).days
        row={"fund":name,"ins_code":code,"first_trading_date":first.source_date_gregorian,"latest_trading_date":last.source_date_gregorian,"latest_closing_price_irr":last.traded_close_irr,
             "price_return_since_inception":last.traded_close_irr/first.traded_close_irr-1,
             "holding_return_since_inception":last.holding_value_irr/first.traded_close_irr-1,
             "hypothetical_total_return_since_inception":last.reinvested_value_irr/first.reinvested_value_irr-1,
             "identified_dividend_events":len(e),"identified_dividends_per_original_unit_irr":identified,
             "dividend_history_status":status,
             "annualized_total_return":(last.reinvested_value_irr/first.reinvested_value_irr)**(365.25/length)-1 if length>=365 else float("nan")}
        for label,days in (("three_month",91),("one_year",365),("two_year",730)):
            row[label+"_price_return"]=window_return(g,days,"traded_close_irr") if length>=days else float("nan")
            row[label+"_holding_return"]=window_return(g,days,"holding_value_irr") if length>=days else float("nan")
            row[label+"_total_return"]=window_return(g,days,"reinvested_value_irr") if length>=days else float("nan")
        if "adjusted_close_irr" in g:
            reference=g.dropna(subset=["adjusted_close_irr"]).sort_values("source_date_gregorian")
            if not reference.empty:
                row["exchange_adjusted_reference_first_date"]=reference.source_date_gregorian.iloc[0]
                row["exchange_adjusted_reference_last_date"]=reference.source_date_gregorian.iloc[-1]
                row["exchange_adjusted_reference_return"]=reference.adjusted_close_irr.iloc[-1]/reference.adjusted_close_irr.iloc[0]-1
        rows.append(row)
        # Older funds display the last year; newer ones display all observed history.
        if length>=365:
            shown=g.loc[pd.to_datetime(g.source_date_gregorian)>=pd.Timestamp(last.source_date_gregorian)-pd.Timedelta(days=365)]
        else: shown=g
        dates=pd.to_datetime(shown.source_date_gregorian)
        price=100*shown.traded_close_irr/shown.traded_close_irr.iloc[0]
        total=100*shown.reinvested_value_irr/shown.reinvested_value_irr.iloc[0]
        fig,ax=plt.subplots(figsize=(12,6.75),dpi=200)
        segments=dates.diff().dt.days.gt(14).cumsum()
        for segment in segments.unique():
            mask=segments.eq(segment)
            ax.plot(dates[mask],price[mask],color="#526780",linewidth=2,label="Raw price index" if segment==0 else None)
            ax.plot(dates[mask],total[mask],color="#d17a36",linewidth=2,label="Hypothetical dividend-reinvested index" if segment==0 else None)
        ax.set_title(name+" | price and hypothetical reinvestment",loc="left",fontsize=16)
        ax.set_ylabel("Index (start = 100)")
        ax.grid(axis="y",alpha=.18)
        ax.legend(loc="upper left",frameon=False)
        fig.autofmt_xdate()
        fig.text(.08,.025,f"Normalized {shown.source_date_gregorian.iloc[0]} | Last observation {last.source_date_gregorian} | Dividend history: {status.replace('_', ' ')}",fontsize=9,color="#555")
        fig.tight_layout(rect=(0,.05,1,1))
        CHARTS.mkdir(parents=True,exist_ok=True)
        fig.savefig(CHARTS/(name.lower().replace(" ","_")+".png"),dpi=200)
        plt.close(fig)
    summary=pd.DataFrame(rows)
    atomic_frame(OUT/"reit_eight_fund_comparison.csv",summary)
    if adjusted.exists():
        reference=ref.sort_values(["ins_code","source_date_gregorian"]).copy()
        reference["fund"]=reference.ins_code.map(FUNDS)
        reference["adjusted_daily_return"]=reference.groupby("ins_code").adjusted_close_irr.pct_change()
        reference["frequency"]="daily"
        daily_reference=reference[["ins_code","fund","source_date_gregorian","frequency","adjusted_close_irr","adjusted_daily_return"]]
        atomic_frame(OUT/"reit_exchange_adjusted_reference_daily.csv",daily_reference)
        for frequency in ("weekly","monthly"):
            rows_reference=[]
            for code,group in reference.groupby("ins_code"):
                group=group.sort_values("source_date_gregorian").copy()
                group["date"]=pd.to_datetime(group.source_date_gregorian).dt.date
                group["period"]=group.date.map(lambda d: friday(d).isoformat() if frequency=="weekly" else str(jdatetime.date.fromgregorian(date=d))[:7])
                group=group.groupby("period",sort=True).tail(1).copy()
                if frequency=="weekly":
                    adjacent=pd.to_datetime(group.period).diff().dt.days.eq(7)
                else:
                    adjacent=pd.to_datetime(group.period+"-01").dt.to_period("M").astype(int).diff().eq(1)
                group["adjusted_return"]=group.adjusted_close_irr.pct_change().where(adjacent)
                group["frequency"]=frequency
                rows_reference.append(group[["ins_code","fund","period","source_date_gregorian","frequency","adjusted_close_irr","adjusted_return"]])
            atomic_frame(OUT/("reit_exchange_adjusted_reference_"+frequency+".csv"),pd.concat(rows_reference,ignore_index=True))
    for frequency,frames in periodic.items():
        atomic_frame(OUT/("reit_all_fund_"+frequency+"_returns.csv"),pd.concat(frames,ignore_index=True))
    return summary
if __name__=="__main__":
    print(build().to_string(index=False))
