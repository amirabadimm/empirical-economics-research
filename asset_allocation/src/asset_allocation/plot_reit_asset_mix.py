"""Plotly cumulative-return chart with selectable Codal allocation shading."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

SHADED_FUNDS = ("Arzesh Maskan", "Danik")
COMPONENTS = (
    ("Housing", "housing_share", "rgba(42, 157, 143, 0.055)"),
    ("Fixed income", "fixed_income_share", "rgba(233, 162, 59, 0.065)"),
    ("Other, incl. cash/equity/receivables", "other_including_cash_equity_share", "rgba(117, 129, 187, 0.055)"),
)


def build_cumulative_figure(cumulative: pd.DataFrame, housing: pd.DataFrame,
                            mix: pd.DataFrame) -> go.Figure:
    """Shade one fund's month-end mix on a right-hand 0–100% axis."""
    required = {"fund", "jalali_period", "source_jalali_date", "observation_date_gregorian",
                "housing_share", "fixed_income_share", "other_including_cash_equity_share",
                "equity_share", "cash_share", "receivables_share",
                "reconstruction_method", "data_quality_flag"}
    if required - set(mix.columns):
        raise ValueError("Incomplete asset-mix chart input")
    if mix.duplicated(["fund", "jalali_period"]).any():
        raise ValueError("Duplicate asset-mix fund/month")
    fig = go.Figure()
    for fund_index, fund in enumerate(SHADED_FUNDS):
        sample = mix.loc[mix.fund.eq(fund)].sort_values("observation_date_gregorian")
        if len(sample) != 24 or (sample[[component[1] for component in COMPONENTS]]
                                  .sum(axis=1).sub(1).abs() > 1e-8).any():
            raise ValueError(f"Expected 24 reconciled allocation months for {fund}")
        boundary = np.zeros(len(sample))
        for component_index, (label, column, color) in enumerate(COMPONENTS):
            shares = sample[column].to_numpy(dtype=float)
            boundary = boundary + shares
            custom = np.column_stack((shares, sample.source_jalali_date,
                                      sample.data_quality_flag.fillna("").replace("", "none"),
                                      sample.reconstruction_method.fillna(""),
                                      sample.cash_share, sample.equity_share,
                                      sample.receivables_share))
            fig.add_trace(go.Scatter(
                x=sample.observation_date_gregorian, y=boundary,
                name=f"{fund}: {label}", mode="lines", line_shape="linear",
                line=dict(color=color, width=0.5), fillcolor=color,
                fill="tozeroy" if component_index == 0 else "tonexty", yaxis="y2",
                visible=fund_index == 0,
                hovertemplate=(f"{fund}<br>Month end: %{{customdata[1]}}<br>{label}: %{{customdata[0]:.1%}}"
                               "<br>Cash: %{customdata[4]:.1%}; equity: %{customdata[5]:.1%}; "
                               "receivables: %{customdata[6]:.1%}"
                               "<br>Method: %{customdata[3]}<br>Quality flag: %{customdata[2]}<extra></extra>"),
                customdata=custom))
    line_assets = ("TEDPIX", "USD/IRR", "Arzesh Maskan", "Kelid", "Danik")
    for name in line_assets:
        sample = cumulative.loc[cumulative.asset.eq(name)].sort_values("week_end_gregorian")
        if sample.empty:
            raise ValueError(f"Missing cumulative return for {name}")
        fig.add_trace(go.Scatter(
            x=sample.week_end_gregorian, y=sample.cumulative_return,
            name=name, mode="lines", line=dict(width=2.5), connectgaps=True,
            customdata=sample[["source_observation_date", "price_method"]].to_numpy(),
            hovertemplate="%{fullData.name}<br>Week: %{x}<br>Cumulative return: %{y:.1%}"
                          "<br>Observed: %{customdata[0]}<br>Method: %{customdata[1]}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=housing.observation_date_gregorian, y=housing.cumulative_return,
        name="Tehran housing (monthly)", mode="lines+markers",
        line=dict(dash="dash", width=2.5),
        hovertemplate="Tehran housing month end: %{x}<br>Cumulative return: %{y:.1%}<extra></extra>"))
    line_visibility = [True] * (len(line_assets) + 1)
    buttons = [dict(label=f"{fund} mix", method="update",
                    args=[{"visible": [i == index for i in range(len(SHADED_FUNDS))
                                       for _ in COMPONENTS] + line_visibility}])
               for index, fund in enumerate(SHADED_FUNDS)]
    buttons.append(dict(label="No allocation shading", method="update",
                        args=[{"visible": [False] * (len(SHADED_FUNDS) * len(COMPONENTS))
                                           + line_visibility}]))
    fig.update_layout(
        title="Two-year cumulative returns with selected REIT's month-end asset mix",
        xaxis_title="Gregorian observation date", yaxis_title="Cumulative return",
        yaxis_tickformat=".0%", yaxis2=dict(title="Asset share", overlaying="y",
                                             side="right", range=[0, 1], tickformat=".0%",
                                             showgrid=False, zeroline=False),
        updatemenus=[dict(type="dropdown", buttons=buttons, active=0,
                          x=0.01, y=1.15, xanchor="left", yanchor="top")],
        annotations=[dict(text="Shading connects observed month-end weights for display only",
                          xref="paper", yref="paper", x=0, y=-0.17, showarrow=False,
                          font=dict(size=11, color="#596678"))],
        legend=dict(orientation="h", y=-0.25),
        height=720, hovermode="closest", margin=dict(t=115, b=135, r=75))
    return fig
