# Copper Research Report

The report leads with certificate versus physical (primary), followed by two
independent intrinsic-value comparisons. Refresh copper processed outputs before
building figures; numerical annotations come from those inputs, not fixed prose.
Research regression and gap-study files are not part of this report's routine results.

- LaTeX source: `copper_research_report.tex`
- Data-driven charts: `figures/`
- Figure builder: `build_figures.py`
- Bubble inputs: `commodity/copper/data/processed/bubble/`

From the workspace root:

```powershell
python .\reports\copper\research\build_figures.py
```

From this directory, compile twice to resolve references:

```powershell
pdflatex copper_research_report.tex
pdflatex copper_research_report.tex
```
