"""Project entry point for the shared certificate pipeline."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from shared.certificate_pipeline.refresh import main

if __name__ == "__main__":
    main("copper")
