import pandas as pd

from asset_allocation.plot_reit_asset_mix import build_cumulative_figure


def test_asset_mix_dropdown_changes_shading_without_hiding_return_lines():
    months = pd.date_range("2024-10-01", periods=24, freq="MS")
    mix = pd.DataFrame([
        {"fund": fund, "jalali_period": f"1403/{i + 1:02}",
         "source_jalali_date": f"1403/{i + 1:02}/30",
         "observation_date_gregorian": day.date().isoformat(),
         "housing_share": 0.6, "fixed_income_share": 0.3,
         "other_including_cash_equity_share": 0.1,
         "cash_share": 0.04, "equity_share": 0.01, "receivables_share": 0.05,
         "reconstruction_method": "source report", "data_quality_flag": ""}
        for fund in ("Arzesh Maskan", "Danik") for i, day in enumerate(months)
    ])
    cumulative = pd.DataFrame([
        {"asset": asset, "week_end_gregorian": "2024-10-04", "cumulative_return": 0.1,
         "source_observation_date": "2024-10-03", "price_method": "observed"}
        for asset in ("TEDPIX", "USD/IRR", "Arzesh Maskan", "Kelid", "Danik")
    ])
    housing = pd.DataFrame({"observation_date_gregorian": ["2024-10-21"],
                            "cumulative_return": [0.0]})
    fig = build_cumulative_figure(cumulative, housing, mix)
    assert len(fig.data) == 12
    assert all(trace.yaxis == "y2" for trace in fig.data[:6])
    assert [trace.fill for trace in fig.data[:3]] == ["tozeroy", "tonexty", "tonexty"]
    assert all(float(trace.fillcolor.rsplit(",", 1)[1].rstrip(") ")) < 0.07
               for trace in fig.data[:6])
    assert list(fig.data[0].y) == [0.6] * 24
    assert all(abs(value - 0.9) < 1e-12 for value in fig.data[1].y)
    assert all(abs(value - 1) < 1e-12 for value in fig.data[2].y)
    assert fig.layout.yaxis2.range == (0, 1)
    buttons = fig.layout.updatemenus[0].buttons
    assert [button.label for button in buttons] == ["Arzesh Maskan mix", "Danik mix", "No allocation shading"]
    assert list(buttons[1].args[0]["visible"]) == [False] * 3 + [True] * 9
    assert all(button.args[0]["visible"][6:] == [True] * 6 for button in buttons)
