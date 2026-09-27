"""Rebuild silver-derived products from existing canonical raw inputs only."""
from pathlib import Path
import subprocess
import sys

PROJECT = Path(__file__).resolve().parent
STEPS = ("src/silver/processing/build_physical_benchmark.py",
         "src/silver/processing/build_certificate_bubble.py",
         "src/silver/processing/build_bubble_distribution.py")

if __name__ == "__main__":
    for relative in STEPS:
        print(f"silver: {relative}", flush=True)
        subprocess.run([sys.executable, str(PROJECT / relative)], cwd=PROJECT, check=True)
