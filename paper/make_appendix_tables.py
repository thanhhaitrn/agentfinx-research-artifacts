"""Fit two generated tables to the text width for main_iccit_long.tex (layout only, numbers unchanged).

Reads generated/tab_sens.tex (unchanged numbers) and writes generated_extra/tab_sens_fit.tex:
footnote size, scaled to the text width, and the row label "Blind human labels" renamed to
"Model/config.-blinded human labels" so that the blinding is not overstated.
Usage: python make_appendix_tables.py [PAPER_DIR]
"""
import sys
from pathlib import Path

paper = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
src = (paper / "generated/tab_sens.tex").read_text(encoding="utf-8")
for old, new in [("\\begin{table*}[t]", "\\begin{table}[H]"), ("\\end{table*}", "\\end{table}"),
                 ("\\centering\\small", "\\centering\\footnotesize"),
                 ("\\begin{tabular}", "\\resizebox{\\textwidth}{!}{\\begin{tabular}"),
                 ("\\end{tabular}", "\\end{tabular}}"),
                 ("Blind human labels", "Model/config.-blinded human labels")]:
    if old not in src:
        raise SystemExit(f"generated/tab_sens.tex no longer contains {old!r}")
    src = src.replace(old, new)
out = paper / "generated_extra/tab_sens_fit.tex"
out.write_text("% Derived from generated/tab_sens.tex by make_appendix_tables.py (layout only).\n" + src, encoding="utf-8")
print("wrote", out)

src = (paper / "generated/tab_models.tex").read_text(encoding="utf-8")
for old, new in [("\\begin{table*}[t]\\centering\\small", "\\begin{table}[t]\\centering\\footnotesize"),
                 ("\\end{table*}", "\\end{table}"),
                 ("\\begin{tabular}", "\\resizebox{\\textwidth}{!}{\\begin{tabular}"),
                 ("\\end{tabular}", "\\end{tabular}}")]:
    if old not in src:
        raise SystemExit(f"generated/tab_models.tex no longer contains {old!r}")
    src = src.replace(old, new)
out = paper / "generated_extra/tab_models_fit.tex"
out.write_text("% Derived from generated/tab_models.tex by make_appendix_tables.py (layout only).\n" + src, encoding="utf-8")
print("wrote", out)
