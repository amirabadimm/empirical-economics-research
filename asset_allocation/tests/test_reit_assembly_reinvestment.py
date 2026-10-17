import pandas as pd
import pytest
from asset_allocation.build_reit_assembly_reinvestment import FUNDS, reinvest_fund

def prices():
    return pd.DataFrame({"source_date_gregorian":["2025-01-01","2025-01-02","2025-01-04","2025-02-01","2025-02-03"],"traded_close_irr":[100.,80.,80.,90.,75.]})
def event(event_id,day,cash,reference=""):
    return {"event_id":event_id,"event_date_gregorian":day,"cash_irr_per_unit":cash,"evidence_status":"verified","eligibility_reference_event":reference}
def test_strict_next_session_and_receivable():
    panel,audit=reinvest_fund(prices(),pd.DataFrame([event("annual","2025-01-02",20.)]))
    assert audit.reinvestment_date_gregorian.iloc[0]=="2025-01-04"
    assert panel.dividend_receivable_irr.iloc[1]==20
    assert panel.reinvested_value_irr.iloc[1]==100
    assert panel.reinvested_units.iloc[2]==1.25
    assert panel.reinvested_value_irr.iloc[2]==100
def test_without_events_matches_raw_price():
    panel,_=reinvest_fund(prices(),pd.DataFrame())
    assert panel.reinvested_value_irr.tolist()==panel.traded_close_irr.tolist()
def test_supplement_uses_original_eligible_units():
    events=pd.DataFrame([event("annual","2025-01-02",20.),event("supplement","2025-02-01",10.,"annual")])
    panel,audit=reinvest_fund(prices(),events)
    assert audit.units_entitled.tolist()==[1.,1.]
    assert audit.total_assumed_dividend_cash.tolist()==[20.,10.]
    assert panel.reinvested_units.iloc[-1]==pytest.approx(1.25+10/75)
def test_invalid_or_duplicate_events_rejected():
    with pytest.raises(ValueError): reinvest_fund(prices(),pd.DataFrame([event("x","2025-01-02",0.)]))
    with pytest.raises(ValueError): reinvest_fund(prices(),pd.DataFrame([event("x","2025-01-02",20.),event("x","2025-02-01",10.)]))
def test_eight_instruments():
    assert len(FUNDS)==8
    assert set(FUNDS)=={"71945594172117613","67717913151786055","70814244102598215","37118058361762279","45292762906823004","34322849244939912","71595553356620707","41480981133648877"}

def test_supplied_ledger_totals_and_raw_mapping():
    from asset_allocation.build_reit_assembly_reinvestment import LEDGER, RAW, gregorian
    ledger=pd.read_csv(LEDGER,dtype={"ins_code":str})
    manifest=pd.read_csv(RAW/"instruments.csv",dtype={"ins_code":str})
    assert set(manifest.ins_code)==set(FUNDS)
    totals=ledger.groupby("ins_code").cash_irr_per_unit.sum()
    assert totals["67717913151786055"]==3574
    assert totals["70814244102598215"]==805
    assert totals["37118058361762279"]==2548
    assert totals["45292762906823004"]==1771
    assert ledger.event_id.is_unique
    assert ledger.loc[ledger.event_id.eq("malek_1405_supp"),"eligibility_reference_event"].iloc[0]=="malek_1405"
    assert gregorian("1405/03/03")=="2026-05-24"
