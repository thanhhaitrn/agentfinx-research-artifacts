# v1.0.1 verification — 28 October 2026

- The three ICCIT manuscript sources match the working submission sources byte-for-byte; hashes are recorded in `paper/SOURCE_SYNC.json`.
- Every included LaTeX dependency and referenced figure exists. All numerical macros used in the three manuscript dependency trees are defined.
- Analysis code, data manifest, generated tables and authored figures are unchanged from v1.0.0.
- The data archive SHA-256 remains `44109c56ad32e3fbda4c8e890d7b1a07201b89ac976b8db966db44e1f49f63f4`.
- `scripts/verify_public_artifact.py`: all 9,017 released data files match their hashes.
- `analysis.security_final.check_paper`: passed.
- This patch synchronizes existing LaTeX sources; no manuscript was re-typeset and no models were called.

- The manuscript ZIP was reopened; all 42 members matched their prepared bytes, with no extra or duplicate members. Release checksums cover both archives.
- MIT applies to original project software; manuscript/data/third-party exclusions are recorded in `LICENSE_SCOPE.md`.

## Verification retained from v1.0.0

The original verification below applies to the unchanged data and analysis code; its test suite was not rerun solely for this source/documentation update.

- `scripts/verify_public_artifact.py`: 9,017 data files matched SHA-256.
- Compressed archive independently read and every member matched `ARTIFACT_MANIFEST.json`; no extra or duplicate members.
- `analysis.security_final.paper_assets`: rebuilt all six generated LaTeX files, including 1,409 number macros; every hash matches the upstream frozen manuscript outputs.
- `analysis.security_final.check_paper`: passed with no missing macros or numeric consistency errors.
- `analysis_extra.py`, `make_appendix_tables.py paper`, `make_tables_vi.py paper`: regenerated outputs identical to upstream.
- `pytest analysis/security_final/test_human_check_scorer.py tests/test_check_tracked_artifacts.py`: 15 passed.
- Credential-pattern scan of the selected data and source found only synthetic test fixtures; no literal matches to locally configured credentials were found in the distribution.

These checks verify distributed bytes and offline analysis, not rendered manuscript layout, scientific validity, or independent replication of live model calls. Original private human submissions are not included and were not reprocessed for this public distribution.
