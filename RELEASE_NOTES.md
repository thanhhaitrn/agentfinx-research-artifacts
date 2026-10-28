Public source and data snapshot for the AgentFinX news-borne attack study.

- 9,017 research data files: frozen labels, run results, evidence snapshots, prompt logs, case/protocol snapshots, and anonymized human-validation outputs.
- Download `agentfinx-artifacts-v1.0.0.tar.gz` and `SHA256SUMS`; extract the archive into a checkout of tag `v1.0.0`.
- Run `python3 scripts/verify_public_artifact.py`, then follow `paper/BUILD.md` to reproduce tables offline without model calls.
- All six primary generated LaTeX files (including 1,409 number macros), supplementary tables and Vietnamese tables reproduced byte-for-byte. The frozen label SHA-256 remains `bf1a72baf2bb2bc93cc62a1fd1ade96973c6fced8be95eaf42bd385f811a273e`.
- 15 targeted tests passed. Archive contents were independently checked against the per-file SHA-256 manifest.

Original rater workbooks and identity mappings, credentials, databases, and application runtime storage are excluded. The public source snapshot has fresh Git history. Manuscripts are LaTeX source drafts; compiled Word/PDF manuscripts are not included. See `PUBLICATION.json` and the README for provenance, exclusions and reproduction limits.
