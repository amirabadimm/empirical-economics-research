"""Exact-date official closing-price / redemption-NAV premium; no carry-forward."""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[3]
ROOT = PROJECT.parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from shared.market_analysis.bubble_distribution import _atomic_csv, BubbleSeriesSpec
from shared.market_analysis.bubble_percentiles import build_project_distributions


def calculate(prices, nav):
    if prices.date.duplicated().any() or nav.date.duplicated().any():
        raise ValueError('Duplicate dates')
    traded = prices.loc[(prices.trade_volume > 0) & (prices.trade_count > 0)].copy()
    result = traded.merge(nav,on='date',how='inner',validate='one_to_one',suffixes=('_price','_nav'))
    if result.empty: raise ValueError('No exact-date price/NAV overlap')
    for c in ['closing_price_irr','redemption_nav_irr']:
        if not np.isfinite(result[c]).all() or (result[c]<=0).any(): raise ValueError(f'Invalid {c}')
    result['bubble_pct'] = 100 * (result.closing_price_irr / result.redemption_nav_irr - 1)
    result['spread_irr'] = result.closing_price_irr - result.redemption_nav_irr
    result['alignment_method'] = 'exact_date_close_to_raw_redemption_nav'
    return result.sort_values('date')


def build(fund='ayar'):
    raw = PROJECT/'data/raw/funds'/fund
    prices = pd.read_csv(raw/'price.csv',parse_dates=['date'])
    nav = pd.read_csv(raw/'nav.csv',parse_dates=['date'])
    result = calculate(prices,nav)
    result['fund'] = fund
    _atomic_csv(result,PROJECT/f'data/processed/bubble/{fund}_nav_bubble.csv')
    cfg = json.loads((PROJECT/'config/funds.json').read_text())[fund]
    ranks = build_project_distributions(project_dir=PROJECT,commodity=fund,
        specs=(BubbleSeriesSpec(f'{fund}_nav','price_vs_redemption_nav',f'{fund.title()}: close vs redemption NAV',
                   f'{fund}_nav_bubble.csv','date','bubble_pct'),),half_life_days=cfg['half_life_days'])
    _atomic_csv(ranks,PROJECT/f'outputs/{fund}_nav_monitor.csv')
    print(f'{fund}: {len(result)} exact-date bubbles; '
          f'{result.date.min().date()} through {result.date.max().date()}')
    print(ranks[['observation_date','bubble_pct','expanding_percentile','recent_weighted_percentile']].tail(1).to_string(index=False))
    return result
