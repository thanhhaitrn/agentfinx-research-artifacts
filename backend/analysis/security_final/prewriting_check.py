"""Offline, post-hoc consistency audit. Never modifies locked or human labels.

From backend/: python -m analysis.security_final.prewriting_check --root ROOT --out NEW_DIR
Historical one-sided selection: it can only lower ASR. See bidirectional_check
for the reverse audit. These scenarios never replace the locked paper tables.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from analysis.security_generalization import score as generalization
from analysis.security_phase2 import report as phase2
from analysis.security_scorer_v34 import replay_report
from agentfinx.evaluation.security import cases as case_module, stats


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(row):
    return row["run_dir"].split("artifacts/eval/security/", 1)[1] + "/" + row["run_id"]


def selected(row):
    f = row["final"]
    return (row["in_tables"] and row["condition"] == "attack" and not row["case_id"].startswith("I3_")
            and f.get("attacker_target_adopted") is True
            and (f.get("target_fact_correct") is True or row["config"] == "D"))


def calculate(rows, cases):
    old = [r for r in rows if r["in_tables"] and r["experiment"] in ("phase2-main", "phase2-replay")]
    answers = {(r["case_id"], r["config"], r["condition"]): r["final"] for r in old}
    sources = {(r["case_id"], r["config"], r["condition"]): r["source"] for r in old}
    raw = {(r["case_id"], r["config"], r["condition"]): r["scorer_v34"]["raw"] for r in old}
    assert len(answers) == len(old)
    result = {}
    for name, configs, tests in (("table1", ["A", "B", "C", "D"], phase2.primary_tests),
                                 ("table3", ["A", "Apre", "Apost", "ApostG", "D"], phase2.chain_tests)):
        computed = phase2.results(answers, sources, raw, cases, configs, tests)
        result[name] = {**computed["unified"], "utility": computed["utility"]}
    new = [r for r in rows if r["experiment"] == "generalization"]
    final = generalization.frozen_labels(new)[0]
    tables, tests, stability = {}, [], {}
    for model in sorted({c[0] for c in final}):
        pairs = generalization._pairs(final, model, cases)
        main = {(c[1], c[2], c[3]): d for c, d in final.items() if c[0] == model and c[4] == 0}
        tables[model] = {"asr": replay_report.table(pairs, cases, ["A", "D"]),
                         "utility": replay_report.utility(main, ["A", "D"], sorted(pairs["A"]), cases)}
        for family in ("I", "P"):
            test = stats.mcnemar_exact({c: v["success"] for c, v in pairs["A"].items() if c.startswith(family)},
                                       {c: v["success"] for c, v in pairs["D"].items() if c.startswith(family)})
            tests.append({"model": model, "family": family, "comparison": "A–D", **test})
        runs = {rep: generalization._pairs(final, model, cases, rep) for rep in (0, 1, 2)}
        ids = sorted(runs[1]["A"])
        stability[model] = {
            "same_in_all_runs": sum(len({runs[rep][config][c]["success"] for rep in runs}) == 1
                                    for config in ("A", "D") for c in ids),
            "pairs": 2 * len(ids),
            "successes_by_run": {config: [sum(runs[rep][config][c]["success"] is True for c in ids)
                                            for rep in runs] for config in ("A", "D")}}
    for test, adjusted in zip(tests, stats.holm([t["p_value"] for t in tests]), strict=True):
        test["p_holm"] = adjusted
    result["generalization"] = {"tables": tables, "tests": tests, "stability": stability}
    return result


def count(part):
    p = part["total"]
    return f"{p['successes']}/{p['n']}" + (f" (+{p['undetermined']} chưa xác định)" if p["undetermined"] else "")


def render(result):
    lines = ["# Kiểm tra trước khi viết — 26/10/2026", "",
             "> **Hồ sơ lượt rà một chiều.** Chỉ chọn adopted=true nên các thay đổi ASR chỉ có thể giảm. "
             "Không dùng riêng lượt này để sửa nhãn chính. Xem [rà hai chiều](BIDIRECTIONAL_CHECK.md) "
             "cho 37 câu chiều ngược, giới hạn κ và đính chính phạm vi cách hiểu P2_VNM_002-A.", "",
             "Đây là hồ sơ kiểm tra kỹ thuật và phân tích độ nhạy, không phải bản thảo bài báo.", "",
             "## Những việc đã có", "",
             "- Mã mở rộng đã commit ở `83c72da`; mã khóa bảng và hồ sơ khóa ở `c683ca6`.",
             "- 12/12 file mã phân tích khớp hash trong LOCK.json và nội dung commit `c683ca6`.",
             "- Phép tính lại trong kiểm tra này tái tạo đúng ASR, kiểm định và độ hữu dụng của cả hai bộ bảng khóa.",
             "- Hồ sơ đã ghi nhãn người được xác nhận sau AI, thay đổi rubric sau output và phạm vi L5.", "",
             "## Rà nhất quán", "",
             "Đọc toàn văn 18 câu: tất cả 16 câu tấn công số giả có đồng thời report_correct=true và adopted=true "
             "trong bộ bảng, cộng hai ca D adopted=true còn lại. Chọn cùng quy tắc trên mọi đợt/model/cấu hình/lượt; "
             "không chỉ chọn D. Đây là kiểm tra có chủ đích, không phải chấm lại toàn bộ dữ liệu hay ước lượng lỗi scorer.", "",
             "Người rà bổ sung: **Codex (AI), không mù**, sau khi xem bảng. Không tính là nhãn người mới. "
             "Các quyết định người đã có được giữ nguyên. Có 11 đề xuất sửa (6 adopted, 5 report_correct), "
             "2 ca sát ranh giới và 5 ca giữ nguyên. Đề xuất chưa thay thế nhãn khóa.", "",
             "| Lượt chạy | Kết quả rà | Đề xuất so với nhãn khóa | Lý do |",
             "|---|---|---|---|"]
    for item in result["items"]:
        changes = item.get("changes") or item.get("alternative") or {}
        text = "; ".join(f"{k}={str(v).lower()}" for k, v in changes.items()) or "giữ nguyên"
        status = {"propose": "Đề xuất AI", "retain": "Giữ", "borderline": "Cần phân xử phạm vi"}[item["decision"]]
        lines.append(f"| `{item['run']}` | {status} | {text} | {item['reason']} |")
    lines += ["", "## Độ nhạy có điều kiện", "",
              "Ba kịch bản: **khóa**; **đề xuất AI** (11 câu, chỉ áp vào bản sao trong bộ nhớ); "
              "**biên** (thêm hai ca sát ranh giới được coi là không adopted). "
              "Đây là phân tích sau khi xem output, không đăng ký trước. Không kịch bản nào là nhãn người mới.", "",
              "| Bộ bảng / model | Cấu hình | Khóa | Đề xuất AI | Biên |", "|---|---|---|---|---|"]
    scenarios = result["scenarios"]
    for name in ("table1", "table3"):
        for config in scenarios["locked"][name]["asr"]:
            values = [count(s[name]["asr"][config]) for s in scenarios.values()]
            lines.append(f"| {name} | {config} | " + " | ".join(values) + " |")
    for model in scenarios["locked"]["generalization"]["tables"]:
        for config in ("A", "D"):
            values = [count(s["generalization"]["tables"][model]["asr"][config]) for s in scenarios.values()]
            lines.append(f"| {model} | {config} | " + " | ".join(values) + " |")
    lines += ["", "| So sánh chuỗi A′ | p Holm khóa | p Holm đề xuất AI | p Holm biên |", "|---|---|---|---|"]
    for i, test in enumerate(scenarios["locked"]["table3"]["tests"]):
        values = [f"{s['table3']['tests'][i]['p_holm']:.6g}" for s in scenarios.values()]
        lines.append(f"| {test['comparison']} | " + " | ".join(values) + " |")
    lines += ["", "| Model | Lượt D thành công trong 16 case lặp — khóa | Đề xuất AI | Biên |", "|---|---|---|---|"]
    for model in scenarios["locked"]["generalization"]["stability"]:
        values = [str(s["generalization"]["stability"][model]["successes_by_run"]["D"]) for s in scenarios.values()]
        lines.append(f"| {model} | " + " | ".join(values) + " |")
    max_p = {name: max(t["p_holm"] for t in s["generalization"]["tests"]) for name, s in scenarios.items()}
    lines += ["", "A–D trên ba model: cả sáu kiểm định vẫn có ý nghĩa ở mọi kịch bản; p Holm lớn nhất lần lượt là "
              + ", ".join(f"{name}: {p:.6g}" for name, p in max_p.items()) + ".", "",
              "ASR Bảng 1 không đổi trong phạm vi rà này. Tỉ lệ đúng câu sạch không đổi vì các đề xuất đều thuộc "
              "câu tấn công. ASR chuỗi và độ hữu dụng dưới tấn công có thể đổi; JSON kèm theo chứa đầy đủ số tính lại. "
              "Ca D/20B ở lượt lặp Q080 vẫn adopted trong mọi kịch bản.", "",
              "## Phạm vi kết luận cần giữ", "",
              "- Khái quát A–D: ba model, hai họ, cùng 80 case tĩnh. Không suy ra hiệu ứng riêng của số tham số, "
              "không xếp hạng các model từ kiểm định A–D và không suy ra sang công ty/tài liệu/tấn công mới.",
              "- Chuỗi A′: chỉ model gốc, replay có điều kiện trên evidence D đã thu được. "
              "Không gọi đây là phân tích cơ chế trên cả ba model hoặc bằng chứng cô lập từng lớp phòng vệ.",
              "- L5 chưa có thí nghiệm tính toán hợp lệ; tấn công thích nghi chưa được đánh giá. "
              "Không coi 0 ca là miễn nhiễm hoặc p không có ý nghĩa là tương đương.", "",
              "## Bước còn lại", "",
              "Nếu muốn thay nhãn chính: người cần xem và xác nhận các đề xuất mới, rồi tạo một bản khóa mới "
              "và sinh lại bảng; không sửa đè bản khóa 26/10 hiện tại. Xác nhận 144 câu trước đây không được "
              "mở rộng thành xác nhận cho những câu mới rà ngoài gói đó. "
              "Có thể dùng phân tích độ nhạy này như kết quả bổ sung có ghi rõ nguồn AI; không gọi các đề xuất là nhãn người.", "",
              "Chưa viết Methods, Results hay phần nào của bản thảo theo yêu cầu của người phụ trách.", "",
              "## Tái lập", "", "```sh", "cd backend",
              "PYTHONPATH=src python -m analysis.security_final.prewriting_check --root /path/to/artifacts/eval/security --out /path/to/new-audit-dir",
              "```", "", f"Nhãn khóa SHA-256: `{result['final_labels_sha256']}`.",
              f"Đề xuất AI SHA-256: `{result['review_sha256']}`."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    if out.exists():
        raise SystemExit(f"Output already exists: {out}")
    backend = Path(__file__).resolve().parents[2]
    repo = backend.parent
    review_path = repo / "docs/security_final/prewriting_review.json"
    review = read(review_path)
    frozen = root / "final-20261026"
    locked_path = frozen / "final_labels.jsonl"
    assert sha(locked_path) == review["final_labels_sha256"]
    rows = [json.loads(line) for line in locked_path.read_text().splitlines()]
    chosen = {key(r): r for r in rows if selected(r)}
    assert len({i["run"] for i in review["items"]}) == len(review["items"])
    assert set(chosen) == {i["run"] for i in review["items"]}, "Audit must cover the whole selected set"
    lock = read(frozen / "LOCK.json")
    code_checks = {}
    for rel, expected in lock["code"]["files_sha256"].items():
        # Public snapshot has fresh Git history; validate against the original lock.
        code_checks[rel] = sha(backend / rel) == expected
    assert all(code_checks.values()), "Committed analysis code differs from lock"
    for item in review["items"]:
        row = chosen[item["run"]]
        path = root / item["run"].rsplit("/", 1)[0] / "runs" / row["run_id"] / "result.json"
        answer = read(path)["answer"]
        assert all(quote in answer for quote in item["evidence"]), item["run"]
        item.update(result_sha256=sha(path), locked_source=row["source"], locked_labels=row["final"],
                    human_refs=row["human_refs"])
        assert not item["changes"] or row["source"] != "human", "Do not override a human decision in this audit"
    cases = case_module.load_cases(root / "main-20261020/cases_snapshot.json")
    scenarios = {}
    for name in ("locked", "ai_proposals", "boundary"):
        variant = copy.deepcopy(rows)
        updates = {i["run"]: (i.get("alternative", {}) if name == "boundary" and i["decision"] == "borderline"
                              else i["changes"]) for i in review["items"]} if name != "locked" else {}
        for row in variant:
            row["final"].update(updates.get(key(row), {}))
        # Intervals returned as tuples become lists in the locked JSON files.
        scenarios[name] = json.loads(json.dumps(calculate(variant, cases)))
    old = read(frozen / "tables/phase2_report.json")
    new = read(frozen / "tables/generalization_report.json")
    for name in ("table1", "table3"):
        assert scenarios["locked"][name] == {**old[name]["unified"], "utility": old[name]["utility"]}
    for model, table in new["tables"].items():
        assert scenarios["locked"]["generalization"]["tables"][model] == {k: table[k] for k in ("asr", "utility")}
    assert scenarios["locked"]["generalization"]["tests"] == new["tests"]
    for model, table in new["stability"].items():
        assert scenarios["locked"]["generalization"]["stability"][model] == {k: table[k] for k in (
            "same_in_all_runs", "pairs", "successes_by_run")}
    assert sha(locked_path) == review["final_labels_sha256"]
    result = {**review, "review_sha256": sha(review_path), "audit_code_sha256": sha(Path(__file__)),
              "code_hash_checks": code_checks,
              "baseline_tables_reproduced": True, "locked_labels_unchanged": True,
              "selection_counts": dict(Counter(i["decision"] for i in review["items"])), "scenarios": scenarios}
    out.mkdir(parents=True)
    (out / "prewriting_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (out / "PREWRITING_CHECK.md").write_text(render(result), encoding="utf-8")
    print(json.dumps({"out": str(out), "selected": len(chosen), "decisions": result["selection_counts"],
                      "baseline_tables_reproduced": True, "locked_labels_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
