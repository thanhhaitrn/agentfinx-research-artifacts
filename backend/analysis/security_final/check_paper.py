"""Check generated hashes, number-macro coverage and table columns; no TeX engine needed."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def check(paper):
    generated = paper / "generated"
    manifest = json.loads((generated / "manifest.json").read_text())
    errors = []
    for rel, sha in manifest["files_sha256"].items():
        if hashlib.sha256((paper / rel).read_bytes()).hexdigest() != sha:
            errors.append(f"generated hash mismatch: {rel}")
    definitions = re.findall(r"\\numdef\{([^}]+)\}", (generated / "numbers.tex").read_text())
    if len(definitions) != len(set(definitions)):
        errors.append("duplicate number definitions")
    uses = set()
    for path in [paper / "main.tex", *generated.glob("tab_*.tex")]:
        uses.update(re.findall(r"\\val\{([^}]+)\}", path.read_text()))
    missing = sorted(uses - set(definitions))
    errors += [f"missing macro: {key}" for key in missing]
    # Numerical results belong in macros. These literal quantities are design constants.
    design_constants = {"0", "8", "10", "16", "20", "40", "72", "80", "95", "100", "110", "640"}
    literal_numbers = []
    main = (paper / "main.tex").read_text().split(r"\begin{document}", 1)[1]
    for lineno, line in enumerate(main.splitlines(), 1):
        cleaned = re.sub(r"(?<!\\)%.*", "", line)
        cleaned = re.sub(r"\\(?:val|cite|ref|label)\{[^}]*\}", "", cleaned)
        cleaned = re.sub(r"gpt-oss:(?:120|20)b|gemma4:31b|\b(?:120b|20b|31b|I[1-4]|P[1-4]|G3|R[1-3]|v3\.[34]|bge-m3|SHA-256)\b", "", cleaned)
        # Archive URLs and the release identifier are metadata, not study results.
        cleaned = re.sub(r"\\url\{[^}]*\}", "", cleaned)
        cleaned = cleaned.replace(r"\texttt{v1.0.0}", "artifact-version")
        cleaned = cleaned.replace("1{,}000", "unit-trap factor")
        tokens = re.findall(r"\d+(?:\.\d+)?", cleaned)
        literal_numbers += [{"body_line": lineno, "token": token} for token in tokens]
        for token in tokens:
            if token not in design_constants:
                errors.append(f"unapproved literal result/design value: {token} at body line {lineno}")
    for path in generated.glob("tab_*.tex"):
        columns = None
        for line in path.read_text().splitlines():
            m = re.search(r"\\begin\{tabular\}\{([lrc]+)\}", line)
            if m:
                columns = len(m.group(1))
            if columns and " & " in line and "multicolumn" not in line and line.count(" & ")+1 != columns:
                errors.append(f"table column mismatch in {path.name}")
            if r"\end{tabular}" in line:
                columns = None
    result = {"status": "ok" if not errors else "failed", "defined_macros": len(definitions),
              "used_macros": len(uses), "missing_macros": missing, "errors": errors,
              "literal_design_values": literal_numbers,
              "scope": "Static numbers and generated-source checks; does not certify PDF layout or external factual claims."}
    (generated / "number_check.json").write_text(json.dumps(result, indent=2)+"\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", required=True, type=Path)
    result = check(parser.parse_args().paper)
    print(json.dumps({k: v for k, v in result.items() if k != "literal_design_values"}, indent=2))
    raise SystemExit(result["status"] != "ok")
