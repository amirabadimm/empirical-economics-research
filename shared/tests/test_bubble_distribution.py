import pandas as pd

from shared.market_analysis.bubble_distribution import (
    BubbleSeriesSpec,
    empirical_distribution,
    plot_distribution_plotly,
)


SPEC = BubbleSeriesSpec(
    series_id="test",
    bubble_type="certificate_vs_physical",
    comparison="test comparison",
    source_file="test.csv",
    date_column="date",
    bubble_column="bubble",
)


def test_empirical_distribution_handles_both_tails_and_ties() -> None:
    source = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
            "bubble": [-100.0, -10.0, 10.0, 10.0],
        }
    )

    result = empirical_distribution(source, commodity="test", spec=SPEC)
    extreme = result.loc[result["bubble_pct"].eq(-100.0)].iloc[0]
    tied = result.loc[result["bubble_pct"].eq(10.0)]

    assert extreme["empirical_cdf"] == 0.25
    assert extreme["abs_exceedance_probability"] == 0.25
    assert tied["empirical_cdf"].eq(1.0).all()
    assert tied["abs_exceedance_probability"].eq(1.0).all()


def test_empirical_distribution_excludes_estimated_points() -> None:
    filtered_spec = BubbleSeriesSpec(
        series_id="test",
        bubble_type="certificate_vs_physical",
        comparison="test comparison",
        source_file="test.csv",
        date_column="date",
        bubble_column="bubble",
        exact_filter_column="method",
        exact_filter_value="observed",
    )
    source = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02"],
            "bubble": [5.0, 30.0],
            "method": ["observed", "linear_interpolation"],
        }
    )

    result = empirical_distribution(source, commodity="test", spec=filtered_spec)

    assert result["bubble_pct"].tolist() == [5.0]
    assert result["point_type"].tolist() == ["observed"]


def test_empirical_distribution_flags_interpolated_points() -> None:
    method_spec = BubbleSeriesSpec(
        series_id="test",
        bubble_type="certificate_vs_physical",
        comparison="test comparison",
        source_file="test.csv",
        date_column="date",
        bubble_column="bubble",
        point_method_column="method",
    )
    source = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02"],
            "bubble": [5.0, 6.0],
            "method": ["observed", "linear_interpolation"],
        }
    )

    result = empirical_distribution(source, commodity="test", spec=method_spec)

    assert result["point_type"].tolist() == ["observed", "interpolated"]
    assert result["is_interpolated"].tolist() == [False, True]

    figure = plot_distribution_plotly(result, "Test distribution")

    assert len(figure.data) == 3
    assert list(figure.data[1].marker.color) == ["#2F5597", "#ED7D31"]
    assert any("Orange markers" in annotation.text for annotation in figure.layout.annotations)
