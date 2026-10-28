# Kiểm tra dữ liệu không cần nhãn — 27/10/2026

Kiểm tra bằng script, không gọi model: `python -m analysis.security_final.data_checks --root ../artifacts/eval/security --out FILE`.

**Kết quả:** `final-audit-v2-20261026/checks/data_checks.json`, sha256 `bc2451995af56d8f18ed87643d4328276c22f328cec9a6aacd930c00f108b41d`.

## Case, gold và payload (100 case: 80 test, 20 dev) — 0 vấn đề

- **Gold truy được về BCTC.** Mọi fact và toán hạng gold trỏ tới file báo cáo có hash khớp. Dòng được trích chứa đúng đoạn trích, và đoạn trích chứa đúng giá trị cùng dấu. Khi nằm cùng một dòng, giá trị kỳ này đứng trước kỳ trước.
- **Chỉ tiêu dẫn xuất tính lại khớp.** Mỗi chỉ tiêu gold được tính lại chính xác từ công thức và toán hạng, làm tròn hai chữ số, đều khớp giá trị gold.
- **Mục tiêu của kẻ tấn công đúng thiết kế.**
  - Số giả khác số thật.
  - Chỉ tiêu dẫn xuất mục tiêu tính lại từ số giả khớp.
  - Số giả được viết trong đoạn chèn, ở dạng đầy đủ hoặc rút gọn có đơn vị.
  - Mục tiêu ép từ chối chỉ có ở I3.
- **Cặp bài báo sạch/tấn công:** chỉ khác nhau ở đoạn thiết kế (`attack_span` thay cho `clean_span`). Mã đánh dấu (canary) chỉ có ở bản tấn công.
- **Định nghĩa case** giống hệt nhau ở cả 6 thư mục chạy dùng cho bảng.

## Kiểm kê lượt chạy

| Đợt | Ô có câu hợp lệ | Lần thử | Theo trạng thái | Ô >1 câu hợp lệ / có lần thử sau câu hợp lệ | Model trả lời (`served_by`) | Lượt gọi / trần |
|---|---|---|---|---|---|---|
| `main-20261020` | 640/640 | 1289 | invalid:infra_error 1, invalid:runtime_error 648, valid:ok 640 | 0 / 0 | gpt-oss:120b-cloud (640) | 2919 / 3600 |
| `phase2/replay-20261024` | 480/480 | 481 | invalid:provider_quota 1, valid:ok 480 | 0 / 0 | gpt-oss:120b-cloud (480) | 481 / 550 |
| `phase2/replay-fix-20261024` | 34/34 | 35 | invalid:provider_quota 1, valid:ok 34 | 0 / 0 | gpt-oss:120b-cloud (34) | 35 / 40 |
| `extension-20261026/test-gpt-oss-120b` | 448/448 | 450 | invalid:provider_quota 2, valid:ok 448 | 0 / 0 | gpt-oss:120b-cloud (448) | 1495 / 2000 |
| `extension-20261026/test-gpt-oss-20b` | 448/448 | 449 | invalid:infra_error 1, valid:ok 448 | 0 / 0 | gpt-oss:20b-cloud (448) | 1490 / 2000 |
| `extension-20261026/test-gemma4-31b` | 448/448 | 448 | valid:ok 448 | 0 / 0 | gemma4:31b-cloud (448) | 1633 / 2000 |

Mỗi ô có đúng một câu hợp lệ. Không lần thử nào chạy sau một câu đã hợp lệ, nên không câu nào được chọn theo điểm. Model trả lời thực tế khớp protocol ở mọi đợt. Đợt chính có 648 lần thử `runtime_error`: 647 lần ngày 21/10, 1 lần ngày 20/10. Đây là thời gian gián đoạn, đã ghi trong `main-20261020/recovery_*`.
