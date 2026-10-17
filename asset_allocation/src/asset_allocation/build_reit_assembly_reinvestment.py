"""Build eight-fund hypothetical dividend reinvestment from raw closes."""
from pathlib import Path
import jdatetime
import pandas as pd
from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/"data/raw/real_estate_funds"
LEDGER=ROOT/"config/reit_dividend_events.csv"
OUTPUT=ROOT/"data/processed/analysis/reit_assembly_reinvested_daily.csv"
EVENTS=ROOT/"data/processed/analysis/reit_assembly_reinvestment_events.csv"
CANONICAL=ROOT/"data/processed/analysis/reit_dividend_events_verified.csv"
FUNDS={"71945594172117613":"Arzesh Maskan","67717913151786055":"Danik","70814244102598215":"Amin Shahr","37118058361762279":"Malek Atiyeh","45292762906823004":"Kelid","34322849244939912":"Kashaneh","71595553356620707":"Kakh","41480981133648877":"Emarat Dey"}
def gregorian(value):
    return jdatetime.date(*map(int,value.split("/"))).togregorian().isoformat()
def reinvest_fund(prices,events):
    """Accrue eligible claims and reinvest on the first later traded close."""
    p=prices.sort_values("source_date_gregorian").reset_index(drop=True).copy()
    p.traded_close_irr=pd.to_numeric(p.traded_close_irr,errors="raise")
    if p.empty or p.source_date_gregorian.duplicated().any() or p.traded_close_irr.isna().any() or (p.traded_close_irr<=0).any(): raise ValueError("Invalid traded-price history")
    e=events.sort_values(["event_date_gregorian","event_id"]).to_dict("records") if not events.empty else []
    if len({x["event_id"] for x in e})!=len(e): raise ValueError("Duplicate event")
    for x in e:
        if float(x["cash_irr_per_unit"])<=0: raise ValueError("Invalid cash distribution")
        candidates=p.index[p.source_date_gregorian>x["event_date_gregorian"]]
        if not len(candidates): raise ValueError("No traded close after event")
        x["reinvestment_index"]=int(candidates[0])
    units=1.0
    receivable=0.0
    eligible_by_event={}
    cursor=0
    states=[]
    records=[]
    for ix,row in p.iterrows():
        while cursor<len(e) and e[cursor]["event_date_gregorian"]<=row.source_date_gregorian:
            x=e[cursor]
            ref=x["eligibility_reference_event"]
            eligible=eligible_by_event[ref] if ref else units
            eligible_by_event[x["event_id"]]=eligible
            claim=eligible*float(x["cash_irr_per_unit"])
            receivable+=claim
            x["units_entitled"]=eligible
            x["total_assumed_dividend_cash"]=claim
            cursor+=1
        for x in e:
            if x["reinvestment_index"]==ix:
                claim=x["total_assumed_dividend_cash"]
                price=float(row.traded_close_irr)
                added=claim/price
                units+=added
                receivable-=claim
                x.update(reinvestment_date_gregorian=row.source_date_gregorian,reinvestment_close_irr=price,additional_units_purchased=added,units_after=units)
                records.append(x.copy())
        states.append((units,max(receivable,0.0)))
    p[["reinvested_units","dividend_receivable_irr"]]=pd.DataFrame(states)
    p["uninvested_cash_irr"]=0.0
    p["reinvested_value_irr"]=p.reinvested_units*p.traded_close_irr+p.dividend_receivable_irr
    p["holding_value_irr"]=p.traded_close_irr+p.source_date_gregorian.map(lambda day: sum(float(x["cash_irr_per_unit"]) for x in e if x["event_date_gregorian"]<=day))
    p["holding_daily_return"]=p.holding_value_irr.pct_change()
    p["price_index"]=100*p.traded_close_irr/p.traded_close_irr.iloc[0]
    p["total_return_index"]=100*p.reinvested_value_irr/p.reinvested_value_irr.iloc[0]
    p["price_daily_return"]=p.traded_close_irr.pct_change()
    p["reinvested_daily_return"]=p.reinvested_value_irr.pct_change()
    p["return_definition"]="hypothetical_first_traded_day_after_event_raw_close"
    return p,pd.DataFrame(records)
def build():
    ledger=pd.read_csv(LEDGER,dtype=str).fillna("")
    if ledger.event_id.duplicated().any() or not set(ledger.ins_code).issubset(FUNDS): raise ValueError("Invalid ledger identifiers")
    manifest=pd.read_csv(RAW/"instruments.csv",dtype={"ins_code":str})
    if set(manifest.ins_code)!=set(FUNDS):
        raise ValueError("Collector roster does not match eight configured funds")
    ledger["event_date_gregorian"]=ledger.event_date_jalali.map(gregorian)
    ledger["assembly_date_gregorian"]=ledger.assembly_date_jalali.map(lambda d: gregorian(d) if d else "")
    ledger["reported_distribution_date_gregorian"]=ledger.reported_distribution_date_jalali.map(lambda d: gregorian(d) if d else "")
    ledger["cash_irr_per_unit"]=pd.to_numeric(ledger.cash_irr_per_unit,errors="raise")
    if not ledger.evidence_status.isin(["verified","provisional_date"]).all(): raise ValueError("Invalid evidence status")
    panels=[]
    audits=[]
    for code,name in FUNDS.items():
        raw=pd.read_csv(RAW/f"{code}.csv",dtype={"source_date_gregorian":str})
        if raw.source_date_gregorian.duplicated().any() or (pd.to_numeric(raw.closing_price_irr)<=0).any(): raise ValueError("Invalid raw history")
        raw=raw.loc[raw.has_trade.eq(True),["source_date_gregorian","closing_price_irr"]].rename(columns={"closing_price_irr":"traded_close_irr"})
        panel,audit=reinvest_fund(raw,ledger.loc[ledger.ins_code==code])
        panel.insert(0,"ins_code",code)
        panel.insert(1,"fund",name)
        panels.append(panel)
        if not audit.empty:
            audit["ins_code"]=code
            audit.insert(1,"fund",name)
            audits.append(audit)
    panel=pd.concat(panels,ignore_index=True)
    events=pd.concat(audits,ignore_index=True)
    canonical=events.rename(columns={"event_date_gregorian":"effective_model_event_date_gregorian","reinvestment_close_irr":"reinvestment_price_irr","additional_units_purchased":"additional_units"})
    atomic_frame(OUTPUT,panel)
    atomic_frame(EVENTS,events)
    atomic_frame(CANONICAL,canonical)
    return panel,events
if __name__=="__main__":
    panel,events=build()
    print(f"Wrote {len(panel)} sessions and {len(events)} events")
