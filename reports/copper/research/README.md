# Copper Research Report

For the current visitor-facing research summary, see [`REPORT.md`](REPORT.md). It leads with the research question, current primary result, supporting comparisons, limitations, and reproducibility notes, with figures rendered directly on GitHub.

The LaTeX file `copper_research_report.tex` is retained as a typeset source. Its figures are data-driven, but the project README and `REPORT.md` are the authoritative public summaries for the current research checkpoint.

- Current Markdown report: `REPORT.md`
- LaTeX source: `copper_research_report.tex`
- Data-driven charts: `figures/`
- Figure builder: `build_figures.py`
- Bubble inputs: `commodity/copper/data/processed/bubble/`

From the workspace root:

```bash
python reports/copper/research/build_figures.py
```

To produce the typeset document, compile the LaTeX source twice from this directory so references resolve.
