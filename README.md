# AgentFinX research artifacts

Public research snapshot for **Where Does a Financial-Report Agent's Robustness to News-Borne Attacks Come From?**

**Version:** [v1.0.0](https://github.com/thanhhaitrn/agentfinx-research-artifacts/releases/tag/v1.0.0), 28 October 2026.

This repository contains analysis and application source, benchmark cases and protocols, manuscript sources, and generated tables. The release contains frozen labels, anonymized human-validation outputs, model answers, evidence snapshots, and prompt logs. Reported tables can be rebuilt offline without model calls, API keys, database access, or original rater workbooks.

## Download and verify

```sh
git clone --branch v1.0.0 https://github.com/thanhhaitrn/agentfinx-research-artifacts.git
cd agentfinx-research-artifacts
curl -fL -O https://github.com/thanhhaitrn/agentfinx-research-artifacts/releases/download/v1.0.0/agentfinx-artifacts-v1.0.0.tar.gz
curl -fL -O https://github.com/thanhhaitrn/agentfinx-research-artifacts/releases/download/v1.0.0/SHA256SUMS
shasum -a 256 -c SHA256SUMS
tar -xzf agentfinx-artifacts-v1.0.0.tar.gz
python3 scripts/verify_public_artifact.py
```

`ARTIFACT_MANIFEST.json` records every distributed data file's SHA-256. The frozen label set remains unchanged:

```text
bf1a72baf2bb2bc93cc62a1fd1ade96973c6fced8be95eaf42bd385f811a273e
```

## Reproduce the paper

See [paper/BUILD.md](paper/BUILD.md) for installation and reproduction commands. Local verification regenerated all six generated LaTeX files, including 1,409 primary number macros with exactly the original SHA-256 hashes.

- [Main ICCIT manuscript source](paper/main_iccit.tex)
- [Extended manuscript source](paper/main_iccit_long.tex)
- [Vietnamese manuscript source](paper/main_iccit_vi.tex)
- [Frozen-result analysis](backend/analysis/security_final/)
- [Cases and protocols](backend/benchmarks/security/)
- [Distribution provenance and exclusions](PUBLICATION.json)
- [Application documentation](README.application.md)

## Scope and limits

The v1 frozen labels define the main results. Human substitution and targeted AI audits remain separate sensitivity analyses; they do not overwrite the main labels. Original rater workbooks, rater identity mappings, private assignment maps, credentials, databases, and application runtime storage are excluded. Re-running the private collection/adjudication workflow is outside this public release; published tables and sensitivity analyses can be regenerated from the released frozen records.

The repository starts with fresh Git history. It derives from upstream branch `generalization-20261026`, commit `5c6b578`, plus local ICCIT manuscript sources. Audit scripts validate the original locked source hashes without requiring upstream historical Git objects. Original `LOCK.json`, labels, reports and data hashes are retained. Historical commit references and absolute paths in recorded logs are provenance, not setup instructions.

Manuscripts are research drafts, not a claim of conference acceptance. This release includes LaTeX sources and authored figures; stale compiled Word/PDF drafts are not distributed. No new software or data license is asserted by this publication; applicable third-party rights remain with their owners.
