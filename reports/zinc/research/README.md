# Zinc Research Report

For the current visitor-facing research summary, see [`REPORT.md`](REPORT.md). It contains the current September production result and renders the three valuation figures directly on GitHub.

The LaTeX file `zinc_research_report.tex` is retained as an **earlier report vintage**. Its numerical checkpoint predates the current September production refresh, so it should not be used for current headline values. `REPORT.md` and the Zinc project README are the authoritative public summaries.

- Current Markdown report: `REPORT.md`
- Earlier LaTeX report source: `zinc_research_report.tex`
- Data-driven charts: `figures/`
- Figure builder: `build_figures.py`
- Bubble inputs: `commodity/zinc/data/processed/bubble/`

From the workspace root:

```bash
python reports/zinc/research/build_figures.py
```

To reproduce the older typeset artifact, compile the LaTeX source from this directory.
