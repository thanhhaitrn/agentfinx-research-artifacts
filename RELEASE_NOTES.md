Synchronizes the ICCIT manuscript sources with the submission version.

- `paper/main_iccit.tex`, `paper/main_iccit_long.tex`, and `paper/main_iccit_vi.tex` now match the submission sources byte-for-byte. `paper/SOURCE_SYNC.json` records their SHA-256 hashes.
- Updates include URL wrapping, artifact-availability wording, and clarification that protocol commit dates refer to the development repository.
- Preserves the submission's citation to data release v1.0.0 and commit `c3a45f0`. Analysis code, frozen labels, generated tables, and all 9,017 data files are unchanged.
- Adds `agentfinx-manuscript-source-v1.0.1.zip` with the LaTeX sources, generated tables, figures, and build documentation. The unchanged data archive `agentfinx-artifacts-v1.0.0.tar.gz` is attached again for convenience. `SHA256SUMS` covers both archives.
- Adds the MIT `LICENSE` for original project software and software documentation. `LICENSE_SCOPE.md` excludes manuscripts, research data, and third-party material from the software-license grant.
- Source/dependency/macro checks and the full data-manifest verification passed. This release does not rerun models or publish new experimental results.

The v1.0.0 tag and release remain unchanged. Compiled manuscript PDF/Word files and private rater records are not included.
