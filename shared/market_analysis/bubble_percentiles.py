"""Signed bubble distributions and expanding, observation-weighted percentiles.

Ranks include the current observation and all ties (<=). Decay uses calendar days.
Ranking does not remove look-ahead already present in interpolated source bubbles.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from .bubble_distribution import _atomic_csv, _histogram_bins


def expanding_percentiles(source, *, half_life_days=90.0):
    if not np.isfinite(half_life_days) or half_life_days <= 0:
        raise ValueError('half_life_days must be finite and positive')
    frame = source.copy()
    frame['observation_date'] = pd.to_datetime(frame['observation_date'], errors='raise')
    frame['bubble_pct'] = pd.to_numeric(frame['bubble_pct'], errors='raise')
    if frame['observation_date'].isna().any() or not np.isfinite(frame['bubble_pct']).all():
        raise ValueError('Missing dates or nonfinite bubbles')
    if frame['observation_date'].duplicated().any():
        raise ValueError('Duplicate observation dates')
    frame = frame.sort_values('observation_date').reset_index(drop=True)
    values = frame['bubble_pct'].to_numpy()
    dates = frame['observation_date']
    plain, weighted, effective = [], [], []
    for i, value in enumerate(values):
        ages = (dates.iloc[i] - dates.iloc[:i+1]).dt.total_seconds().to_numpy() / 86400
        weights = np.exp2(-ages / half_life_days)
        below = values[:i+1] <= value
        plain.append(100 * below.mean())
        weighted.append(100 * weights[below].sum() / weights.sum())
        effective.append(weights.sum() ** 2 / np.square(weights).sum())
    frame['expanding_percentile'] = plain
    frame['recent_weighted_percentile'] = weighted
    frame['history_count'] = np.arange(1, len(frame)+1)
    frame['effective_weighted_count'] = effective
    frame['half_life_days'] = half_life_days
    return frame


def figures(frame, title):
    """Separate signed histogram and chronological percentile chart."""
    if frame.empty:
        raise ValueError('Cannot plot an empty distribution')
    frame = frame.sort_values('observation_date')
    last = frame.iloc[-1]
    histogram = go.Figure(go.Histogram(x=frame['bubble_pct'], histnorm='probability density',
                                      marker_color='#175A8C', name='Signed bubbles'))
    histogram.add_vline(x=0, line_color='#889099', line_dash='dot')
    histogram.add_vline(x=float(last.bubble_pct), line_color='#B66A16', line_width=2)
    histogram.update_layout(title=f'{title} — signed distribution', template='plotly_white',
                            xaxis_title='Bubble (%)', yaxis_title='Density', height=440,
                            annotations=[dict(x=1, y=1.12, xref='paper', yref='paper',
                            xanchor='right', showarrow=False,
                            text=f'Latest {last.observation_date:%Y-%m-%d}: {last.bubble_pct:.2f}% | '
                                 f'Equal rank {last.expanding_percentile:.1f} | Recent rank {last.recent_weighted_percentile:.1f}')])
    timeline = go.Figure()
    for column, label, color in [('expanding_percentile', 'Equal weight', '#175A8C'),
                                 ('recent_weighted_percentile', f'Recent weight (half-life {last.half_life_days:g} days)', '#B66A16')]:
        timeline.add_trace(go.Scatter(x=frame['observation_date'], y=frame[column],
            name=label, mode='lines', line_color=color,
            customdata=frame[['bubble_pct','history_count','effective_weighted_count']],
            hovertemplate='%{x|%Y-%m-%d}<br>Percentile: %{y:.1f}<br>Bubble: %{customdata[0]:.2f}%'
                          '<br>History: %{customdata[1]}<br>Effective weighted count: %{customdata[2]:.1f}<extra>%{fullData.name}</extra>'))
    for rank in [10, 50, 90]:
        timeline.add_hline(y=rank, line_dash='dot', line_color='#B0B7BF')
    timeline.update_layout(title=f'{title} — expanding historical rank', template='plotly_white',
                           xaxis_title='Date', yaxis_title='Percentile (0–100)',
                           yaxis_range=[0,100], hovermode='x unified', height=460,
                           legend=dict(orientation='h', y=-0.2))
    return histogram, timeline


def build_project_distributions(*, project_dir, commodity, specs, half_life_days=90.0):
    outputs = []
    bubble_dir = project_dir / 'data/processed/bubble'
    analysis_dir = project_dir / 'data/processed/analysis'
    analysis_dir.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        raw = pd.read_csv(bubble_dir / spec.source_file)
        frame = raw[[spec.date_column, spec.bubble_column]].rename(
            columns={spec.date_column:'observation_date', spec.bubble_column:'bubble_pct'})
        frame['point_method'] = raw[spec.point_method_column] if spec.point_method_column else 'observed'
        frame['is_interpolated'] = frame['point_method'].str.contains('interpol', case=False, na=False)
        frame = expanding_percentiles(frame, half_life_days=half_life_days)
        if frame.empty:
            raise ValueError(f'Empty input: {spec.source_file}')
        frame['commodity'] = commodity
        frame['series_id'] = spec.series_id
        frame['comparison'] = spec.comparison
        frame['source_file'] = spec.source_file
        outputs.append(frame)
        fig, axes = plt.subplots(2, 1, figsize=(11,8), constrained_layout=True)
        axes[0].hist(frame.bubble_pct, bins=_histogram_bins(frame.bubble_pct), density=True, color='#175A8C')
        last = frame.iloc[-1]
        axes[0].axvline(last.bubble_pct, color='#B66A16', label=f'Latest: {last.bubble_pct:.2f}%')
        axes[0].set(xlabel='Bubble (%)', ylabel='Density', title='Signed distribution'); axes[0].legend()
        axes[1].plot(frame.observation_date, frame.expanding_percentile, label='Equal weight')
        axes[1].plot(frame.observation_date, frame.recent_weighted_percentile, label=f'Recent weight: {half_life_days:g}-day half-life')
        for rank in [10,50,90]: axes[1].axhline(rank, color='gray', linestyle=':', linewidth=.7)
        axes[1].set(xlabel='Date', ylabel='Percentile', ylim=(0,100)); axes[1].legend()
        fig.suptitle(f'{commodity.title()}: {spec.comparison}')
        destination = analysis_dir / f'{spec.series_id}_distribution.png'
        temporary = destination.with_suffix('.tmp.png')
        fig.savefig(temporary, dpi=160); plt.close(fig); temporary.replace(destination)
    combined = pd.concat(outputs, ignore_index=True)
    _atomic_csv(combined, bubble_dir / f'{commodity}_bubble_distribution.csv')
    return combined
