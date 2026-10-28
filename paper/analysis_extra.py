"""Exploratory analyses added after reviewer feedback (not pre-registered).

Reads the frozen final labels, the case snapshot, the G2 evidence-extraction summary,
the replay/main snapshots and the human-validation report, and writes LaTeX number macros
to paper/generated_extra/numbers_extra.tex (prefix "x."). No model calls.

Usage (from the repository root):  python paper/analysis_extra.py
"""
import collections
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]
REPO = Path(os.environ.get("FINX_REPO", ROOT.parent))  # .../itec
SEC = REPO / "artifacts/eval/security"
OUT = ROOT / "generated_extra/numbers_extra.tex"

rows = [json.loads(line) for line in open(SEC / "final-20261026/final_labels.jsonl", encoding="utf-8")]
cases = {c["case_id"]: c for c in json.load(open(SEC / "phase2/replay-20261024/cases_snapshot.json"))["cases"]}
g2 = {r["case_id"]: r for r in json.load(open(SEC / "phase2/replay-evidence-20261024/summary.json"))["rows"]
      if r["condition"] == "attack"}
hv = json.load(open(SEC / "human-check-scorer-attack-20261027/returned/report.json"))

cell, runinfo = {}, {}
for r in rows:
    if r.get("in_tables") and r["experiment"] in ("phase2-main", "phase2-replay"):
        cell[(r["case_id"], r["config"], r["condition"])] = r["final"]
        runinfo[(r["case_id"], r["config"], r["condition"])] = r
TEST = sorted({k[0] for k in cell})
CF = ["A", "B", "C", "D", "Apre", "Apost", "ApostG"]


def success(cid, cfg):
    case, att, cln = cases[cid], cell[(cid, cfg, "attack")], cell[(cid, cfg, "clean")]
    if case["attacker_target"]["kind"] != "refusal":
        v = att.get("attacker_target_adopted")
        return None if v is None else bool(v)
    if cln.get("target_fact_correct") is not True:
        return None
    return att.get("refusal") == "full"


S = {cfg: {c: success(c, cfg) for c in TEST} for cfg in CF}


def exact_mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def fisher_two_sided(a, b, c, d):
    n1, n2, k, n = a + b, c + d, a + c, a + b + c + d

    def p(x):
        return math.comb(n1, x) * math.comb(n2, k - x) / math.comb(n, k)

    obs = p(a)
    return min(1.0, sum(p(x) for x in range(max(0, k - n2), min(k, n1) + 1) if p(x) <= obs * (1 + 1e-9)))


def fmt_p(p):
    if p < 0.001:
        m, e = f"{p:.1e}".split("e")
        return f"\\ensuremath{{{m}{{\\times}}10^{{{int(e)}}}}}"
    return f"{p:.3g}"


M = {}
# Split the G2 "present" verdict: fake number found (scorer matcher, sure) vs attack marker only.
import sys  # noqa: E402
sys.path.insert(0, str(ROOT.parent / "backend" / "src"))
from agentfinx.evaluation.security import cases as case_file, evidence, scorer  # noqa: E402

built = {c["case_id"]: c for c in case_file.load_cases(ROOT.parent / "backend/benchmarks/security/attack_set.json")._normalized()}
post_kind = {}
for cid in TEST:
    rec = json.load(open(SEC / "phase2/replay-evidence-20261024/runs" / f"{g2[cid]['run_id']}.json", encoding="utf-8"))
    payload = evidence.Payload(built[cid])
    flat = evidence._norm(json.dumps(rec["post"]["worker_results"], ensure_ascii=False))
    marker = any(m in flat for m in payload.markers)
    number = "none"
    if payload.numbers:
        mentions = scorer.extract_mentions(flat)
        for fact in payload.numbers:
            sure, unsure = scorer._find(mentions, fact, min_digits=3, collisions=payload.collisions, cues=payload.cues)
            if sure:
                number = "sure"
                break
            if unsure:
                number = "unsure"
    post_kind[cid] = (marker, number)
M["x.exp.post.number"] = sum(1 for c in TEST if post_kind[c][1] == "sure")
M["x.exp.post.markeronly"] = sum(1 for c in TEST if post_kind[c][0] and post_kind[c][1] != "sure")
M["x.exp.post.markeronly.unsure"] = sum(1 for c in TEST if post_kind[c][0] and post_kind[c][1] == "unsure")
M["x.exp.post.markeronly.refusal"] = sum(1 for c in TEST if post_kind[c][0] and post_kind[c][1] == "none")
M["x.exp.numeric.n"] = sum(1 for c in TEST if cases[c]["attacker_target"]["kind"] != "refusal")

groups = {
    "all": TEST,
    "searched": [c for c in TEST if g2[c]["news_searched"]],
    "notsearched": [c for c in TEST if not g2[c]["news_searched"]],
    "present": [c for c in TEST if g2[c]["post_payload"]["found"] == "present"],
    "number": [c for c in TEST if post_kind[c][1] == "sure"],
}
M["x.exp.searched"] = len(groups["searched"])
M["x.exp.notsearched"] = len(groups["notsearched"])
cnt = collections.Counter(g2[c]["post_payload"]["found"] for c in TEST)
M["x.exp.post.present"], M["x.exp.post.absent"], M["x.exp.post.unknown"] = cnt["present"], cnt["absent"], cnt["unknown"]
M["x.exp.post.verbatim"] = sum(bool(g2[c]["post_payload"]["span_verbatim"]) for c in TEST)
M["x.exp.pre.present"] = sum(g2[c]["pre_article_payload"]["found"] == "present" for c in TEST)
for g, sub in groups.items():
    M[f"x.g.{g}.n"] = len(sub)
    for cfg in CF:
        M[f"x.g.{g}.{cfg}.s"] = sum(S[cfg][c] is True for c in sub)
        M[f"x.g.{g}.{cfg}.u"] = sum(S[cfg][c] is None for c in sub)
    for x, y in [("A", "Apre"), ("Apre", "Apost"), ("Apost", "ApostG"), ("Apost", "D"), ("A", "D")]:
        pairs = [(S[x][c], S[y][c]) for c in sub if S[x][c] is not None and S[y][c] is not None]
        b = sum(1 for p, q in pairs if p and not q)
        cc = sum(1 for p, q in pairs if q and not p)
        M[f"x.g.{g}.{x}{y}.b"], M[f"x.g.{g}.{x}{y}.c"] = b, cc
        M[f"x.g.{g}.{x}{y}.n"] = len(pairs)
        M[f"x.g.{g}.{x}{y}.p"] = fmt_p(exact_mcnemar(b, cc))

# subtypes
for st in sorted({cases[c]["subtype"] for c in TEST}):
    sub = [c for c in TEST if cases[c]["subtype"] == st]
    M[f"x.st.{st}.n"] = len(sub)
    for cfg in CF:
        s, u = sum(S[cfg][c] is True for c in sub), sum(S[cfg][c] is None for c in sub)
        M[f"x.st.{st}.{cfg}"] = f"{s} (+{u})" if u else f"{s}"


# is the gold value (or its operands) in the report evidence the answering call saw?
def thousands(v):
    v = str(v).lstrip("-")
    return None if "." in v else f"{int(v):,}".replace(",", ".")


def gold_strings(cid):
    g = cases[cid]["gold"]
    vals = [f["value"] for f in g["facts"]] + [o["value"] for o in g.get("operands", [])]
    return [s for s in (thousands(v) for v in vals) if s]


def chunks_text(cid, cfg):
    r = runinfo[(cid, cfg, "attack")]
    snap = json.load(open(REPO / r["run_dir"] / "runs" / r["run_id"] / "snapshot.json", encoding="utf-8"))
    return " ".join(ch["content"] for ch in snap.get("chunks") or [])


numeric = [c for c in TEST if cases[c]["attacker_target"]["kind"] != "refusal"]
M["x.numeric"] = len(numeric)
for cfg in ("A", "Apre", "Apost", "ApostG"):
    tab = collections.Counter()
    for c in numeric:
        gs = gold_strings(c)
        txt = chunks_text(c, cfg)
        tab[(all(s in txt for s in gs), S[cfg][c])] += 1
    a, b = tab[(True, True)], tab[(True, False)]
    c_, d = tab[(False, True)], tab[(False, False)]
    M[f"x.gold.{cfg}.in.n"], M[f"x.gold.{cfg}.in.s"] = a + b, a
    M[f"x.gold.{cfg}.out.n"], M[f"x.gold.{cfg}.out.s"] = c_ + d, c_
    M[f"x.gold.{cfg}.in.pct"] = f"{100 * a / (a + b):.1f}" if a + b else "--"
    M[f"x.gold.{cfg}.out.pct"] = f"{100 * c_ / (c_ + d):.1f}" if c_ + d else "--"
    if cfg == "A":
        M["x.gold.A.fisher"] = fmt_p(fisher_two_sided(a, b, c_, d))

# scorer vs human, adoption
def conf(groups_filter):
    t = collections.Counter()
    for g, v in hv["groups"].items():
        if groups_filter(g.split("|")[1]):
            t.update(v["scorer_vs_human"]["adopted_target"].get("confusion", {}))
    return t["scorer=true|human=true"], t["scorer=true|human=false"], t["scorer=false|human=true"], t["scorer=false|human=false"]


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - half, centre + half


for name, flt in [("all", lambda c: True), ("A", lambda c: c == "A"), ("D", lambda c: c == "D"),
                  ("replay", lambda c: c in ("Apre", "Apost", "ApostG")), ("BC", lambda c: c in ("B", "C"))]:
    tp, fp, fn, tn = conf(flt)
    M[f"x.sc.{name}.tp"], M[f"x.sc.{name}.fp"], M[f"x.sc.{name}.fn"], M[f"x.sc.{name}.tn"] = tp, fp, fn, tn
    M[f"x.sc.{name}.pos"] = tp + fn
    if tp + fn:
        lo, hi = wilson(tp, tp + fn)
        M[f"x.sc.{name}.sens"] = f"{100 * tp / (tp + fn):.1f}"
        M[f"x.sc.{name}.sens.ci"] = f"[{100 * lo:.1f}, {100 * hi:.1f}]"
    if tn + fp:
        M[f"x.sc.{name}.spec"] = f"{100 * tn / (tn + fp):.1f}"
    if tp + fp:
        M[f"x.sc.{name}.ppv"] = f"{100 * tp / (tp + fp):.1f}"

OUT.parent.mkdir(exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("% Generated by paper/analysis_extra.py (exploratory, post hoc). Do not edit.\n")
    for k in sorted(M):
        fh.write(f"\\numdef{{{k}}}{{{M[k]}}}\n")
print(f"wrote {len(M)} numbers to {OUT}")
for k in sorted(M):
    if k.startswith(("x.exp", "x.g.number")):
        print(k, M[k])
