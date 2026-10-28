# Release verification — 28 October 2026

- `scripts/verify_public_artifact.py`: 9,017 data files matched SHA-256.
- Compressed archive independently read and every member matched `ARTIFACT_MANIFEST.json`; no extra or duplicate members.
- `analysis.security_final.paper_assets`: rebuilt all six generated LaTeX files, including 1,409 number macros; every hash matches the upstream frozen manuscript outputs.
- `analysis.security_final.check_paper`: passed with no missing macros or numeric consistency errors.
- `analysis_extra.py`, `make_appendix_tables.py paper`, `make_tables_vi.py paper`: regenerated outputs identical to upstream.
- `pytest analysis/security_final/test_human_check_scorer.py tests/test_check_tracked_artifacts.py`: 15 passed.
- Credential-pattern scan of the selected data and source found only synthetic test fixtures; no literal matches to locally configured credentials were found in the distribution.

These checks verify distributed bytes and offline analysis, not rendered manuscript layout, scientific validity, or independent replication of live model calls. Original private human submissions are not included and were not reprocessed for this public distribution.
