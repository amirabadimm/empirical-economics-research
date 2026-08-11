# Zinc Research Report

- LaTeX source: `zinc_research_report.tex`
- Data-driven charts: `figures/`
- Figure builder: `build_figures.py`

From the workspace root:

```powershell
python .\reports\zinc\research\build_figures.py
```

From this directory, compile twice to resolve references:

```powershell
pdflatex zinc_research_report.tex
pdflatex zinc_research_report.tex
```
