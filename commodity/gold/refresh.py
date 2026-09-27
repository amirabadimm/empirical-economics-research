"""Gold research entry point: configured funds and a shared statistical engine."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from gold.collectors.fund_history import collect
from gold.processing.build_nav_bubble import build

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fund',default='ayar')
    parser.add_argument('--collect',action='store_true')
    parser.add_argument('--full',action='store_true',help='Reconcile complete NAV history when collecting')
    args = parser.parse_args()
    if args.collect: collect(args.fund,args.full)
    build(args.fund)
