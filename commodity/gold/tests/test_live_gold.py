import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "db"))
from live_gold import evaluate, months_before, reference_ranks


def test_daily_windows_exclude_intraday_and_weight_recent_days():
    today = date(2026, 10, 3)
    history = [(today - timedelta(days=d), v) for d, v in [(400, 1), (200, 3), (10, 5), (0, -100)]]
    ranks = reference_ranks(history, 4, today)
    assert ranks[:6] == (50, 5, 2, 0, 1, 1)
    assert ranks[8] == 3
    assert 0 < ranks[6] < 50
    assert months_before(date(2024, 8, 31), 6) == date(2024, 2, 29)


def test_latest_price_nav_freshness_and_identity():
    now = datetime(2026, 10, 3, 9, 0, tzinfo=timezone.utc)
    price = dict(insCode="0", pDrCotVal=110, dEven=20261003, hEven=122900, zTotTran=1)
    nav = dict(insCode="123", pRedTran=100, deven=20261003, hEven=122800)
    assert evaluate(price, nav, "123", now)["bubble"] == pytest.approx(10)
    assert evaluate(price, nav, "123", now + timedelta(hours=1))["bubble"] is None
    with pytest.raises(ValueError, match="identity"):
        evaluate(price, nav, "999", now)
