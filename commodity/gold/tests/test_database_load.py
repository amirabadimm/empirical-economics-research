import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "db"))
from load_gold import decile_from_percentile


def test_decile_boundaries_and_ties():
    percentiles = pd.Series([1, 10, 10.000000000000002, 10.1, 50, 90, 100])
    assert decile_from_percentile(percentiles).tolist() == [1, 1, 1, 2, 5, 9, 10]
