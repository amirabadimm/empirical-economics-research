import numpy as np
import pandas as pd
import pytest
from shared.market_analysis.bubble_percentiles import expanding_percentiles, figures


def sample():
    return pd.DataFrame({'observation_date':pd.to_datetime(['2026-01-01','2026-04-01','2026-06-30']), 'bubble_pct':[-10,10,0]})


def test_signed_equal_and_calendar_weighted_ranks():
    result = expanding_percentiles(sample(), half_life_days=90)
    np.testing.assert_allclose(result.expanding_percentile, [100,100,200/3])
    assert result.recent_weighted_percentile.iloc[-1] == pytest.approx(100*1.25/1.75)
    assert result.effective_weighted_count.iloc[-1] == pytest.approx(1.75**2/(1+.25+.0625))


def test_future_rows_cannot_change_past_ranks():
    before = expanding_percentiles(sample().iloc[:2])
    after = expanding_percentiles(sample())
    pd.testing.assert_frame_equal(before, after.iloc[:2].reset_index(drop=True))


def test_ties_include_current_and_all_equal_points():
    frame = sample(); frame['bubble_pct'] = 4
    result = expanding_percentiles(frame)
    assert (result.expanding_percentile == 100).all()
    np.testing.assert_allclose(result.recent_weighted_percentile, 100)


@pytest.mark.parametrize('half_life', [0,-1,np.inf,np.nan])
def test_invalid_half_life(half_life):
    with pytest.raises(ValueError): expanding_percentiles(sample(), half_life_days=half_life)


def test_invalid_inputs():
    duplicate = sample(); duplicate.loc[1,'observation_date'] = duplicate.loc[0,'observation_date']
    with pytest.raises(ValueError): expanding_percentiles(duplicate)
    bad = sample().astype({'bubble_pct':float}); bad.loc[0,'bubble_pct'] = np.inf
    with pytest.raises(ValueError): expanding_percentiles(bad)


def test_two_separate_figures_and_two_rank_series():
    hist, timeline = figures(expanding_percentiles(sample()), 'Test')
    assert hist.data[0].type == 'histogram'
    assert len(timeline.data) == 2
    assert list(hist.data[0].x) == [-10,10,0]
