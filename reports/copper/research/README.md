# Copper Research Report

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
