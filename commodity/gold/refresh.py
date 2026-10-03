"""Gold research entry point: configured funds and a shared statistical engine."""
import argparse
import sys
import subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from gold.processing.build_nav_bubble import build
from collect_daily import collect_price
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fund',default='ayar')
    parser.add_argument('--collect',action='store_true')
    parser.add_argument('--full',action='store_true',help='Fetch complete price and Fipiran NAV histories')
    args = parser.parse_args()
    if args.collect:
        config = json.loads((Path(__file__).resolve().parent/'config/funds.json').read_text(encoding='utf-8'))[args.fund]
        session = requests.Session()
        session.mount('https://', HTTPAdapter(max_retries=Retry(
            total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
        )))
        collect_price(session,args.fund,config,full=args.full)
        cmd = [sys.executable, '-B', str(Path(__file__).resolve().parent / 'collect_fipiran_nav.py'), '--fund', args.fund]
        if args.full:
            cmd.append('--full')
        subprocess.run(cmd, check=True)
    build(args.fund)
