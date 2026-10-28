# Rebuild the public manuscript results

The three ICCIT manuscript sources were synchronized with the submission sources in v1.0.1; their v1.0.0 data citation is intentionally retained. `SOURCE_SYNC.json` records exact source hashes.

First download and extract the versioned artifact archive as described in the repository README. Python 3.12 was used for release verification.

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e 'backend[eval]' matplotlib openpyxl pytest
python scripts/verify_public_artifact.py
cd backend
PYTHONPATH=src:. python -m analysis.security_final.paper_assets --root ../artifacts/eval/security --paper ../paper
PYTHONPATH=src:. python -m analysis.security_final.check_paper --paper ../paper
cd ..
python paper/analysis_extra.py
python paper/make_appendix_tables.py paper
python paper/make_tables_vi.py paper
```

`paper_assets` checks the frozen-label, locked-table, human-validation-report and normalized-label hashes, recomputes targeted sensitivity scenarios, and generates the main tables and 1,409 number macros. It does not call models. Generated main table and number hashes must match `paper/generated/manifest.json` in tag `v1.0.1`.

The original lock and labels are immutable. `lock verify`, `human_check_scorer validate`, and the original human-report collection commands require private adjudication inputs or original workbooks; they are not public reproduction entry points. The public pipeline uses the archived report and anonymized validated labels. The identifier-to-name mapping and returned workbooks remain private.

Targeted source tests:

```sh
cd backend
PYTHONPATH=src:. python -m pytest -q analysis/security_final/test_human_check_scorer.py tests/test_check_tracked_artifacts.py
```

For typesetting, install a TeX distribution and run `latexmk -pdf main_iccit.tex` (English) or `latexmk -pdf main_iccit_long.tex` (extended) from `paper/`. Use XeLaTeX for the Vietnamese manuscript. Word conversion additionally requires pandoc, python-docx and the compiled LaTeX `.aux` file; see `build_iccit_docx.py`. No compiled manuscript is included. The publication update was verified for data and source consistency, not rendered page layout.
