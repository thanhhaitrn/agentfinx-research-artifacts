"""Vietnamese copies of the generated tables (generated/tab_*.tex -> generated_vi/tab_*.tex).

Only captions and header/row labels are translated; every number is left as generated.
Each replacement must match exactly once, so a change in the generator is caught here.
Usage: python make_tables_vi.py PAPER_DIR
"""
import sys
from pathlib import Path

paper = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OK = "Succ.\\ (80)"
T = {
    "tab_main.tex": [
        ("Main run (gpt-oss:120b, 80 test cases: 40 injection I, 40 poisoning P). Attack success counts pairs; "
         "``(+$k$)'' are pairs left undetermined, kept in the denominator and reported as a range ($\\dagger$). "
         "Rates are \\% with Wilson 95\\% intervals. Utility columns: \\% of clean answers with the correct target "
         "value, \\% of clean answers refused, and \\% of the 72 numeric-target attacks answered correctly without "
         "adopting the fake value.",
         "Lượt chạy chính (gpt-oss:120b, 80 ca kiểm thử: 40 chèn lệnh I, 40 đầu độc P). Số lần tấn công thành công "
         "được đếm theo cặp; ``(+$k$)'' là số cặp chưa xác định, vẫn giữ trong mẫu số và được báo cáo dưới dạng "
         "khoảng ($\\dagger$). Tỉ lệ tính bằng \\% kèm khoảng tin cậy Wilson 95\\%. Các cột tiện ích: \\% câu trả lời "
         "sạch nêu đúng giá trị mục tiêu, \\% câu trả lời sạch bị từ chối, và \\% trong 72 tấn công có mục tiêu số "
         "được trả lời đúng mà không dùng giá trị giả."),
        ("Config & " + OK + " & ASR \\% [95\\% CI] & I (40) & P (40) & Clean correct & Clean refused & "
         "Attack correct, no fake",
         "Cấu hình & Thành công (80) & ASR \\% [KTC 95\\%] & I (40) & P (40) & Sạch, đúng & Sạch, từ chối & "
         "Tấn công, đúng, không giả"),
        ("\\multicolumn{2}{c}{Injection (I)} & \\multicolumn{2}{c}{Poisoning (P)}",
         "\\multicolumn{2}{c}{Chèn lệnh (I)} & \\multicolumn{2}{c}{Đầu độc (P)}"),
        ("Comparison & only first/only second & $p_{\\text{Holm}}$ & only first/only second & $p_{\\text{Holm}}$",
         "So sánh & chỉ bên trước/chỉ bên sau & $p_{\\text{Holm}}$ & chỉ bên trước/chỉ bên sau & $p_{\\text{Holm}}$"),
    ],
    "tab_chain.tex": [
        ("Evidence-matched replay on the main run's D evidence (gpt-oss:120b). A and D are the answers of "
         "Table~\\ref{tab:main}. Last column: \\% of the 72 numeric-target attacks answered correctly without the "
         "fake value. Lower part: exact McNemar on case-paired outcomes, Holm over the four comparisons.",
         "Phát lại khớp bằng chứng, dùng bằng chứng của D trong lượt chạy chính (gpt-oss:120b). A và D là các câu "
         "trả lời của Bảng~\\ref{tab:main}. Cột cuối: \\% trong 72 tấn công có mục tiêu số được trả lời đúng mà "
         "không dùng giá trị giả. Phần dưới: kiểm định McNemar chính xác trên kết quả ghép cặp theo ca, hiệu chỉnh "
         "Holm trên bốn phép so sánh."),
        ("Config & " + OK + " & ASR \\% [95\\% CI] & I & P & Corr., no fake",
         "Cấu hình & Thành công (80) & ASR \\% [KTC 95\\%] & I & P & Đúng, không giả"),
        ("Step & only first/second & pairs &", "Bước & chỉ trước/chỉ sau & số cặp &"),
    ],
    "tab_models.tex": [
        ("A versus D with three answering models (same 80 cases, one main run each). A--D columns: pairs where only "
         "A / only D succeeded, and exact McNemar $p$ with Holm over the six tests. Stability: pairs (16 pre-chosen "
         "cases $\\times$ A/D) with the same outcome in all three runs, reported separately from the main run.",
         "A so với D với ba mô hình trả lời (cùng 80 ca, mỗi mô hình một lượt chạy chính). Các cột A--D: số cặp chỉ "
         "A / chỉ D thành công, và $p$ của kiểm định McNemar chính xác với hiệu chỉnh Holm trên sáu kiểm định. Ổn "
         "định: số cặp (16 ca chọn trước $\\times$ A/D) có cùng kết quả trong cả ba lượt chạy, báo cáo tách riêng "
         "khỏi lượt chạy chính."),
        ("Model & Config & " + OK + " & ASR \\% [95\\% CI] & A--D, I & A--D, P & Clean correct & Clean refused & "
         "Stable",
         "Mô hình & Cấu hình & Thành công (80) & ASR \\% [KTC 95\\%] & A--D, I & A--D, P & Sạch, đúng & "
         "Sạch, từ chối & Ổn định"),
    ],
    "tab_human_validation.tex": [
        ("Human validation. Inter-rater agreement uses the \\val{hv.shared} shared answers: Fleiss $\\kappa$ and "
         "unanimous agreement (\\%). Scorer agreement uses one human label per answer (majority on shared answers). "
         "Numeric adoption excludes I3; inter-rater target achievement includes I3 refusal. Use-of-fake has no "
         "matching scorer field.",
         "Kiểm định nhãn bởi người. Độ đồng thuận giữa người chấm dùng \\val{hv.shared} câu trả lời chung: Fleiss "
         "$\\kappa$ và tỉ lệ cả ba cùng nhãn (\\%). Độ đồng thuận với bộ chấm dùng một nhãn người cho mỗi câu trả "
         "lời (theo đa số với câu trả lời chung). Chấp nhận giá trị số không tính I3; đạt mục tiêu giữa người chấm "
         "có tính việc từ chối ở I3. Nhãn dùng giá trị giả không có trường tương ứng trong bộ chấm."),
        ("\\multicolumn{2}{c}{Three raters} & \\multicolumn{3}{c}{Scorer--human}",
         "\\multicolumn{2}{c}{Ba người chấm} & \\multicolumn{3}{c}{Bộ chấm--người}"),
        ("Label & $\\kappa$ & Agree & $\\kappa$ & Agree & $n$", "Nhãn & $\\kappa$ & Đồng thuận & $\\kappa$ & "
         "Đồng thuận & $n$"),
        ("Target correct &", "Mục tiêu đúng &"),
        ("Target achieved &", "Đạt mục tiêu &"),
        ("Use of fake &", "Dùng giá trị giả &"),
        ("Refusal &", "Từ chối &"),
        ("Conflict flagged &", "Nêu mâu thuẫn &"),
        ("Summary asserts &", "Tóm tắt khẳng định &"),
    ],
    "tab_sens.tex": [
        ("Sensitivity of attack-success counts (out of 80). AI-audit rows are post-hoc, non-blind reviews of "
         "selected answers; boundary rows flip disputed cases. The final row substitutes the human validation labels "
         "only for scorer-only attacks; raters were blind to model/configuration, with the limitations in "
         "Section~\\ref{sec:labelling}. All scenarios use copies; the locked primary labels are unchanged.",
         "Độ nhạy của số lần tấn công thành công (trên 80). Các dòng rà soát AI là các lần rà soát hậu kiểm, không "
         "mù, trên một số câu trả lời được chọn; các dòng biên lật các ca còn tranh cãi. Dòng cuối thay bằng nhãn "
         "kiểm định của người, chỉ cho các tấn công có nhãn do bộ chấm quyết định; người chấm không biết mô "
         "hình/cấu hình, với các hạn chế nêu ở Mục~\\ref{sec:labelling}. Mọi kịch bản đều chạy trên bản sao; bộ "
         "nhãn chính đã khoá không thay đổi."),
        ("\\multicolumn{3}{c}{Main run} & \\multicolumn{3}{c}{Replay chain}",
         "\\multicolumn{3}{c}{Lượt chính} & \\multicolumn{3}{c}{Chuỗi phát lại}"),
        ("Scenario & A & C & D", "Kịch bản & A & C & D"),
        ("3-model A--D", "A--D, 3 mô hình"),
        ("Locked labels (primary) &", "Nhãn đã khoá (chính) &"),
        ("AI audit, one-sided &", "Rà soát AI, một chiều &"),
        ("AI audit, both directions &", "Rà soát AI, hai chiều &"),
        ("Boundary: fewer adoptions &", "Biên: ít chấp nhận hơn &"),
        ("Boundary: more adoptions &", "Biên: nhiều chấp nhận hơn &"),
        ("Blind human labels\\\\(\\val{hv.answers} scorer-only attacks)",
         "Nhãn người, mù\\\\(\\val{hv.answers} tấn công chỉ do bộ chấm)"),
    ],
}

out = paper / "generated_vi"
out.mkdir(exist_ok=True)
for name, reps in T.items():
    s = (paper / "generated" / name).read_text()
    for en, vi in reps:
        n = s.count(en)
        assert n >= 1, f"{name}: not found: {en[:60]}"
        s = s.replace(en, vi)
    (out / name).write_text("% Vietnamese copy of generated/" + name + " (labels translated, numbers unchanged).\n" + s)
print("wrote", ", ".join(sorted(T)))
