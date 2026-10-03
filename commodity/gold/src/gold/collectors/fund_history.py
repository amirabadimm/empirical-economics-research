"""Official unadjusted price and raw fund NAV; incremental canonical merge by date."""
import hashlib
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PROJECT = Path(__file__).resolve().parents[3]
ROOT = PROJECT.parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from shared.market_analysis.bubble_distribution import _atomic_csv


def fetch(session, url, archive, params=None):
    response = session.get(url, params=params, timeout=90)
    response.raise_for_status()
    archive.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(response.content).hexdigest()
    path = archive / f'{digest}.json'
    if not path.exists():
        with path.open('xb') as handle: handle.write(response.content)
    metadata = archive / f'{digest}.metadata.json'
    if not metadata.exists():
        with metadata.open('x', encoding='utf8') as handle:
            json.dump({'url':response.url, 'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),
                       'sha256':digest, 'tls_verified':True}, handle)
    return response.json(), digest


def persist(frame, path):
    if frame.empty: raise ValueError('Empty source response')
    frame['date'] = pd.to_datetime(frame['date'], errors='raise').dt.strftime('%Y-%m-%d')
    if frame.date.isna().any(): raise ValueError('Missing source date')
    if frame.date.duplicated().any(): raise ValueError('Duplicate source dates')
    if path.exists():
        previous = pd.read_csv(path)
        frame = pd.concat([previous,frame]).drop_duplicates('date',keep='last')
    _atomic_csv(frame.sort_values('date'),path)


def collect(fund='ayar', full=False):
    if fund == 'ayar':
        raise RuntimeError('Ayar Mofid collector is retired; use collect_fipiran_nav.py --fund ayar')
    cfg = json.loads((PROJECT/'config/funds.json').read_text())[fund]
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=Retry(total=3,backoff_factor=1,status_forcelist=[429,500,502,503,504])))
    raw = PROJECT/'data/raw/funds'/fund
    payload, digest = fetch(session,
        f"https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{cfg['ins_code']}/0",
        raw/'snapshots/tsetmc')
    rows = []
    for r in payload['closingPriceDaily']:
        rows.append({'date':datetime.strptime(str(r['dEven']),'%Y%m%d').date().isoformat(),
            'ins_code':cfg['ins_code'], 'closing_price_irr':r['pClosing'],
            'last_price_irr':r['pDrCotVal'], 'trade_volume':r['qTotTran5J'],
            'trade_count':r['zTotTran'], 'source_snapshot':digest})
    frame = pd.DataFrame(rows)
    if not np.isfinite(frame[['closing_price_irr','last_price_irr','trade_volume','trade_count']]).all().all():
        raise ValueError('Nonfinite price or activity')
    if (frame[['closing_price_irr','trade_volume','trade_count']] < 0).any().any():
        raise ValueError('Negative price or activity')
    persist(frame,raw/'price.csv')
    start = cfg['start_date']
    nav_path = raw/'nav.csv'
    if nav_path.exists() and not full:
        start = (date.fromisoformat(pd.read_csv(nav_path).date.max())-timedelta(days=30)).isoformat()
    payload, digest = fetch(session,cfg['nav_api'],raw/'snapshots/nav',
        {'FromDate':start,'ToDate':date.today().isoformat(),'BasketId':cfg['nav_basket_id'],
         'FundId':cfg['nav_fund_id'],'NavReportType':cfg['nav_report_type']})
    if not isinstance(payload,list) or not payload: raise ValueError('Empty NAV history')
    frame = pd.DataFrame(payload).rename(columns={'redemptionNav':'redemption_nav_irr',
                           'issuanceNav':'issuance_nav_irr','nominalNav':'nominal_nav_irr'})
    frame = frame[['date','redemption_nav_irr','issuance_nav_irr','nominal_nav_irr']]
    if not np.isfinite(frame[['redemption_nav_irr','issuance_nav_irr','nominal_nav_irr']]).all().all():
        raise ValueError('Nonfinite NAV')
    if (frame[['redemption_nav_irr','issuance_nav_irr']] <= 0).any().any():
        raise ValueError('Nonpositive NAV')
    frame['source_snapshot'] = digest
    persist(frame,nav_path)
    print(f'{fund}: price and NAV histories collected; NAV request from {start}')
