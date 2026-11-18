"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
  "day"            một ngày vận hành giả lập: các ticket cùng "day" và cùng "seed" chạy nối nhau trên cùng một sổ cái
  "arrive_min"     phút ticket tới trong ca (0..480)          "warehouse"   kho của đơn
  "cost_vnd"       tiền LLM + nền tảng đã tốn cho ticket      "review_kind" None / "escalated" (trợ lý chuyển người) /
  "queue_wait_min" số phút chờ người duyệt (None nếu không vào hàng chờ)     "recheck" (nhân viên tự kiểm lại)
Chỉ số có thể là kỹ thuật (tỉ lệ model đè số trong ticket lên DB), vận hành (số ca cần người trong giờ đông nhất),
hay kinh doanh (tỉ lệ ticket trợ lý đọc xong vẫn phải chuyển người).

lab10.grade kiểm: monitor chạy không lỗi, và giá trị trên gói sự cố khác giá trị trên bộ nền,
tức là monitor "sáng đèn" khi sự cố xảy ra.
"""


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


def carrier_pii_attempts(trials):
    """Số lần hệ thống phải loại trường cá nhân khỏi thông báo hãng trên 100 ticket."""
    attempts = 0
    for trial in trials:
        for event in trial.get("events", []):
            attempts += (event.get("type") == "gate"
                         and event.get("tool") == "notify_carrier"
                         and event.get("action") == "modify")
            attempts += (event.get("type") == "legal_gate"
                         and event.get("gate") == "pii_fields_blocked_to_third_party")
    return round(100 * attempts / max(1, len(trials)), 2)


MONITORS = {
    "escalation_rate": escalation_rate,     # có sẵn; KHÔNG tính là metric mới của đội
    "carrier_pii_attempts_per_100": carrier_pii_attempts,
}
STARTER_MONITORS = ("escalation_rate",)
