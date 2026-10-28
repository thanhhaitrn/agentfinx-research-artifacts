"""Checks of the case data behind every table, without any label (offline, no model call).

Run from ``backend/``::

    python -m analysis.security_final.data_checks --root ../artifacts/eval/security --out DIR

- **Same cases everywhere:** every run directory used by the tables carries the same case
  definitions (gold, target, spans, articles).
- **Gold traced to the report:** every gold fact and operand points to a report file whose
  hash matches; the cited line holds the excerpt, and the excerpt holds the value with its sign.
- **Derived values recomputed:** each derived gold value equals its formula evaluated exactly on
  the operands, at two decimals.
- **Attacker target:** fake values differ from gold; a derived target equals the formula evaluated
  with the fake operand(s); the fake value is written in the attack span; refusal targets only in I3.
- **Clean/attack pair:** the attack and clean articles differ only by the designed span
  (attack_span in one, clean_span in the other); the canary appears only in the attack version.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

RUN_DIRS = ("main-20261020", "phase2/replay-20261024", "phase2/replay-fix-20261024",
            "extension-20261026/test-gpt-oss-120b", "extension-20261026/test-gpt-oss-20b",
            "extension-20261026/test-gemma4-31b")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canon(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _vn(value: str) -> str:
    """Integer in Vietnamese grouping: 36158929436 → 36.158.929.436."""

    digits = str(abs(int(Decimal(value))))
    groups = []
    while digits:
        groups.insert(0, digits[-3:])
        digits = digits[:-3]
    return ".".join(groups)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\\", "")).strip()


UNITS = {"tỷ": Decimal(10) ** 9, "triệu": Decimal(10) ** 6, "nghìn": Decimal(10) ** 3, "ngàn": Decimal(10) ** 3,
         "đồng": Decimal(1), "vnd": Decimal(1), "%": Decimal(1)}


def written_in(value: str, text: str) -> str | None:
    """How ``value`` is written in ``text`` (Vietnamese digits, optional unit), within half of the
    last written digit; None if it is not."""

    target = Decimal(value)
    for match in re.finditer(r"(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?\s*(tỷ|triệu|nghìn|ngàn|đồng|VND|%)?", text,
                             flags=re.IGNORECASE):
        whole, frac, unit = match.group(1), match.group(2) or "", (match.group(3) or "đồng").lower()
        number = Decimal(whole.replace(".", "") + ("." + frac if frac else ""))
        scale = UNITS.get(unit, Decimal(1))
        half = Decimal(5) / Decimal(10) ** (len(frac) + 1) * scale
        if abs(number * scale - abs(target)) <= half:
            return match.group(0)
    return None


def _evaluate(formula: str, values: dict[str, Decimal]) -> Decimal:
    expression = formula
    for key in sorted(values, key=len, reverse=True):
        expression = re.sub(rf"\b{re.escape(key)}\b", f"Decimal('{values[key]}')", expression)
    if re.search(r"[A-Za-z_]", expression.replace("Decimal", "")):
        raise ValueError(f"unresolved name in {formula!r}")
    return eval(expression, {"Decimal": Decimal, "__builtins__": {}})  # noqa: S307 — formulas from the frozen case file


def _two(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def check_case(case: dict, repo: Path, datasets: dict) -> list[str]:
    problems = []
    cid = case["case_id"]
    gold = case["gold"]
    report = datasets[case["dataset_id"]]["report"]
    values = {}
    for fact in list(gold.get("facts") or []) + list(gold.get("operands") or []):
        values[fact["key"]] = Decimal(fact["value"])
        source = fact.get("source") or {}
        path = repo / source.get("file", "")
        if not path.is_file():
            problems.append(f"{cid}.{fact['key']}: source file missing {source.get('file')}")
            continue
        if _sha(path) != source.get("sha256") or source.get("sha256") != report["sha256"]:
            problems.append(f"{cid}.{fact['key']}: source hash differs from the case or dataset")
        lines = path.read_text(encoding="utf-8").splitlines()
        line = lines[source["line"] - 1] if 0 < source.get("line", 0) <= len(lines) else ""
        if _norm(source.get("excerpt", "")) not in _norm(line):
            problems.append(f"{cid}.{fact['key']}: line {source.get('line')} does not hold the excerpt")
        if source.get("value") != fact["value"]:
            problems.append(f"{cid}.{fact['key']}: source value {source.get('value')} ≠ gold {fact['value']}")
        written = _vn(fact["value"])
        excerpt = _norm(source.get("excerpt", ""))
        if written not in excerpt:
            problems.append(f"{cid}.{fact['key']}: {written} not in the excerpt")
        elif Decimal(fact["value"]) < 0 and f"({written})" not in excerpt and f"-{written}" not in excerpt:
            problems.append(f"{cid}.{fact['key']}: negative gold but the excerpt shows no sign")
        elif Decimal(fact["value"]) > 0 and (f"({written})" in excerpt or f"-{written}" in excerpt):
            problems.append(f"{cid}.{fact['key']}: positive gold but the excerpt shows a negative")
    # current before previous in the same row (the report's column order)
    operands = gold.get("operands") or []
    by_role = {o.get("period_role"): o for o in operands}
    if "current" in by_role and "previous" in by_role:
        cur, prev = by_role["current"], by_role["previous"]
        if cur["source"].get("line") == prev["source"].get("line"):
            excerpt = _norm(cur["source"]["excerpt"])
            if excerpt.find(_vn(cur["value"])) > excerpt.find(_vn(prev["value"])):
                problems.append(f"{cid}: current value stands after the previous one in the row")
    for derived in gold.get("derived") or []:
        try:
            exact = _evaluate(derived["formula"], values)
        except Exception as error:  # noqa: BLE001
            problems.append(f"{cid}.{derived['key']}: {error}")
            continue
        if _two(exact) != Decimal(derived["value"]):
            problems.append(f"{cid}.{derived['key']}: formula gives {exact:.6f}, gold {derived['value']}")
    target = case["attacker_target"]
    if target["kind"] == "refusal":
        if case["subtype"] != "I3":
            problems.append(f"{cid}: refusal target outside I3")
    else:
        if case["subtype"] == "I3":
            problems.append(f"{cid}: I3 with a numeric target")
        fake = dict(values)
        for fact in target.get("facts") or []:
            if fact["key"] in values and Decimal(fact["value"]) == values[fact["key"]]:
                problems.append(f"{cid}.{fact['key']}: fake equals gold")
            fake[fact["key"]] = Decimal(fact["value"])
            if written_in(fact["value"], case["attack_span"]) is None:
                problems.append(f"{cid}.{fact['key']}: fake value not written in the attack span")
        for derived in target.get("derived") or []:
            formula = next((d["formula"] for d in gold.get("derived") or [] if d["key"] == derived["key"]), None)
            if formula is None:
                problems.append(f"{cid}.{derived['key']}: target derived without a gold formula")
                continue
            if _two(_evaluate(formula, fake)) != Decimal(derived["value"]):
                problems.append(f"{cid}.{derived['key']}: fake operands give {_two(_evaluate(formula, fake))}, "
                                f"target {derived['value']}")
    # clean/attack articles
    arts = case.get("articles") or {}
    attack, clean = arts.get("attack") or [], arts.get("clean") or []
    if [a["article_key"] for a in attack] != [a["article_key"] for a in clean]:
        problems.append(f"{cid}: attack and clean article sets differ")
    for a, c in zip(attack, clean, strict=False):
        for field in a:
            if field == "content":
                continue
            if a[field] != c.get(field) and field not in {"source_url"}:
                problems.append(f"{cid}.{a['article_key']}.{field}: differs between attack and clean")
        if a["content"] != c["content"]:
            if case["attack_span"] not in a["content"] or case["clean_span"] not in c["content"]:
                problems.append(f"{cid}.{a['article_key']}: spans not found where the articles differ")
            elif a["content"].replace(case["attack_span"], case["clean_span"]) != c["content"]:
                problems.append(f"{cid}.{a['article_key']}: articles differ beyond the designed span")
        canary = case.get("canary") or ""
        if canary and canary in _canon(c):
            problems.append(f"{cid}.{a['article_key']}: canary in the clean article")
    if case.get("canary") and case["canary"] not in _canon(attack):
        problems.append(f"{cid}: canary missing from the attack articles")
    return problems


def inventory(root: Path) -> dict:
    """Per run directory: cells, attempts by status, that each cell has exactly one valid answer and
    no attempt after it (a valid answer is never rerun, so nothing is chosen by score), the model
    that actually answered, and model calls against the cap."""

    out = {}
    for rel in RUN_DIRS:
        folder = root / rel
        attempts = [json.loads(line) for line in (folder / "attempts.jsonl").read_text(encoding="utf-8").splitlines()]
        cells: dict[tuple, list[dict]] = {}
        for record in attempts:
            cells.setdefault(tuple(record["cell"]), []).append(record)
        served, multi, after = Counter(), 0, 0
        for records in cells.values():
            records.sort(key=lambda r: r.get("attempt", 0))
            valid = [r for r in records if r["valid"]]
            multi += len(valid) > 1
            if valid:
                first = valid[0]
                after += any(r.get("attempt", 0) > first.get("attempt", 0) for r in records)
                result = json.loads((folder / "runs" / first["run_id"] / "result.json").read_text(encoding="utf-8"))
                served[",".join(sorted({s.get("model") for s in result.get("served_by") or []}))] += 1
        budget = json.loads((folder / "budget.json").read_text(encoding="utf-8"))
        out[rel] = {"cells": len(cells), "cells_with_valid_answer": sum(any(r["valid"] for r in v) for v in cells.values()),
                    "attempts": len(attempts),
                    "attempts_by_status": {f"{'valid' if k[0] else 'invalid'}:{k[1]}": n for k, n in
                                           Counter((r["valid"], r["status"]) for r in attempts).items()},
                    "cells_with_several_valid": multi, "cells_with_attempts_after_valid": after,
                    "duplicate_run_ids": len(attempts) - len({r["run_id"] for r in attempts}),
                    "served_by": dict(served), "model_calls": budget.get("used"), "call_limit": budget.get("limit")}
    return out


def run(root: Path) -> dict:
    repo = root.parents[2]
    snapshots = {rel: json.loads((root / rel / "cases_snapshot.json").read_text(encoding="utf-8")) for rel in RUN_DIRS}
    reference = snapshots[RUN_DIRS[0]]
    ref_cases = {c["case_id"]: c for c in reference["cases"]}
    consistency = {}
    for rel, snap in snapshots.items():
        cases = {c["case_id"]: c for c in snap["cases"]}
        differ = sorted(cid for cid in set(cases) & set(ref_cases) if _canon(cases[cid]) != _canon(ref_cases[cid]))
        consistency[rel] = {"cases": len(cases), "missing_vs_main": sorted(set(ref_cases) - set(cases)),
                            "differing_cases": differ, "datasets_identical": _canon(snap["datasets"]) == _canon(reference["datasets"]),
                            "snapshot_sha256": _sha(root / rel / "cases_snapshot.json")}
    problems = {}
    for case in reference["cases"]:
        found = check_case(case, repo, reference["datasets"])
        if found:
            problems[case["case_id"]] = found
    splits = Counter(c["split"] for c in reference["cases"])
    return {"cases": len(reference["cases"]), "splits": dict(splits), "inventory": inventory(root),
            "test_cases_with_problems": sorted(cid for cid in problems if ref_cases[cid]["split"] == "test"),
            "problems": problems, "consistency": consistency}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run(args.root.resolve())
    text = json.dumps(result, ensure_ascii=False, indent=1)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("consistency", "inventory")} | {
        "consistency": {k: {"differing": len(v["differing_cases"]), "missing": len(v["missing_vs_main"]),
                            "datasets_identical": v["datasets_identical"]} for k, v in result["consistency"].items()}},
        ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
