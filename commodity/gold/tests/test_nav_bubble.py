import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from gold.processing.build_nav_bubble import calculate


def inputs():
    prices = pd.DataFrame({'date':['2026-01-01','2026-01-02','2026-01-03'],
        'closing_price_irr':[110.,90.,120.], 'trade_volume':[1,1,0], 'trade_count':[1,1,0]})
    nav = pd.DataFrame({'date':['2026-01-01','2026-01-03'],'redemption_nav_irr':[100.,100.]})
    return prices,nav


def test_exact_dates_no_fill_no_zero_volume():
    result = calculate(*inputs())
    assert result.date.tolist() == ['2026-01-01']
    assert result.bubble_pct.iloc[0] == pytest.approx(10)


def test_negative_bubble_retains_sign():
    prices,nav = inputs(); prices.loc[0,'closing_price_irr']=90
    assert calculate(prices,nav).bubble_pct.iloc[0] == pytest.approx(-10)


def test_invalid_nav_and_duplicates():
    prices,nav = inputs(); nav.loc[0,'redemption_nav_irr']=0
    with pytest.raises(ValueError): calculate(prices,nav)
    prices,nav = inputs()
    with pytest.raises(ValueError): calculate(prices,pd.concat([nav,nav]))
