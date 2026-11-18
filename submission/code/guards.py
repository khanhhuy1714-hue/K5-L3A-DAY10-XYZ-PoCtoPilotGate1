"""Cổng phòng ngừa cho quyết định hoàn tiền và tác động tới bên thứ ba."""
from . import helpers as H
from .tools import Verdict


def _customer_auto_refund_today_vnd(ctx, customer_id):
    """Tổng tiền đã hoàn tự động (không có approval_id) cho một khách trong ngày hiện tại."""
    total = 0
    for row in ctx.tools.ledger_rows(customer_id=customer_id):
        if row.get("approval_id"):
            continue
        r_order = ctx.tools.lookup_order(row.get("order_id"))
        if r_order and r_order.get("refund_status") == "REFUNDED":
            continue
        total += row.get("amount_vnd", 0)
    return total


def pre_guard(ctx):
    # Chọn chính sách theo ngày hiệu lực trong nguồn dữ liệu.
    policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
    if policy is None:
        return Verdict.escalate("không xác định được chính sách có hiệu lực")
    return Verdict.allow(policy_id=policy["policy_id"])


def write_gate(ctx, action):
    tool = action.get("tool")
    if tool == "issue_refund":
        order = ctx.tools.lookup_order(action.get("order_id"))
        policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
        if order is None or policy is None:
            return Verdict.escalate("thiếu đơn hoặc chính sách làm căn cứ hoàn")

        # Chống ghi trùng trên cùng một đơn (ví dụ khi retry sau lỗi confirm).
        if ctx.tools.ledger_rows(order_id=order["order_id"]):
            return Verdict.deny("đơn hàng đã có giao dịch hoàn tiền trong sổ cái")
        if order.get("refund_status") != "NONE":
            return Verdict.escalate("trạng thái hoàn không còn là NONE")

        # Luôn tính lại quyền lợi từ nguồn sự thật (tracking + chính sách hiệu lực),
        # không tin đề xuất bị tiêm lệnh từ nội dung ticket hay checkout_note.
        parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
        delay = H.db_delay_days(parcel, ctx.as_of)
        amount = H.entitlement_vnd(policy, order, delay, parcel.get("delay_cause"))
        proposed_payer = action.get("payer")
        proposed_amount = action.get("amount_vnd", 0)

        if amount <= 0:
            if proposed_payer != "LOGIX" or proposed_amount > 0:
                ctx.log("chan_lenh_hoan_vi_pham_chinh_sach",
                        order_id=order["order_id"],
                        proposed_payer=proposed_payer,
                        proposed_amount_vnd=proposed_amount,
                        entitlement_vnd=0)
            return Verdict.deny("tracking và chính sách không cho phép hoàn tiền")

        auto_limit = policy.get("auto_limit_vnd", 0)
        approval_id = action.get("approval_id")
        if approval_id or amount > auto_limit:
            if not approval_id:
                ctx.log("chan_hoan_vuot_han_muc_khong_phe_duyet",
                        order_id=order["order_id"],
                        proposed_payer=proposed_payer,
                        proposed_amount_vnd=proposed_amount,
                        entitlement_vnd=amount,
                        auto_limit_vnd=auto_limit)
                return Verdict.escalate("vượt hạn mức tự động và chưa có phê duyệt hợp lệ; cần người duyệt")
            approvals = ctx.tools.lookup_approvals(approval_id=approval_id)
            valid = any(a.get("ticket_id") == action.get("ticket_id")
                        and (not a.get("order_id") or a.get("order_id") == order["order_id"])
                        and (not a.get("customer_id") or a.get("customer_id") == order["customer_id"])
                        and a.get("status") == "valid"
                        and a.get("expires_at", "") >= ctx.as_of
                        and a.get("max_vnd", 0) >= amount
                        for a in approvals)
            if not valid:
                return Verdict.escalate("phê duyệt không hợp lệ cho ticket hoặc số tiền này")
        else:
            ops_lim = ctx.tools.ops_limits()
            # Trần cộng dồn hoàn tự động theo từng khách trong ngày.
            cust_limit = ops_lim.get("max_auto_refund_per_customer_per_day_vnd")
            cust_spent = _customer_auto_refund_today_vnd(ctx, order["customer_id"])
            if cust_limit is not None and cust_spent + amount > cust_limit:
                ctx.log("vuot_tran_hoan_tu_dong_khach_ngay",
                        order_id=order["order_id"],
                        customer_id=order["customer_id"],
                        spent_today_vnd=cust_spent,
                        requested_vnd=amount,
                        limit_vnd=cust_limit)
                return Verdict.escalate("vượt trần hoàn tự động theo khách trong ngày; cần người duyệt")

            # Trần hoàn tự động toàn hệ thống trong ngày (config đội và ngân sách Finance).
            team_cap = (ctx.gates or {}).get("business", {}).get("daily_refund_cap_vnd")
            fin_cap = ops_lim.get("daily_auto_refund_budget_vnd")
            caps = [c for c in (team_cap, fin_cap) if c is not None]
            cap = min(caps) if caps else None
            spent = ctx.tools.auto_refund_today_vnd()
            if cap is not None and spent + amount > cap:
                return Verdict.escalate("vượt trần hoàn tự động trong ngày")

        ctx.log("hoan_tien_tinh_lai_tu_nguon", order_id=order["order_id"],
                delay_days=delay, amount_vnd=amount)

        # Giao trễ luôn do LOGIX chịu và đúng số tiền theo nguồn sự thật.
        changes = {}
        if proposed_payer != "LOGIX":
            changes["payer"] = "LOGIX"
        if proposed_amount != amount:
            changes["amount_vnd"] = amount
        if changes:
            ctx.log("dieu_chinh_lenh_hoan_theo_nguon",
                    order_id=order["order_id"],
                    proposed_payer=proposed_payer,
                    proposed_amount_vnd=proposed_amount,
                    final_payer="LOGIX",
                    final_amount_vnd=amount)
            return Verdict.modify("điều chỉnh bên chịu tiền LogiX và số tiền theo tracking/chính sách", **changes)

    elif tool == "file_carrier_fault":
        order = ctx.tools.lookup_order(action.get("order_id"))
        policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
        if order is None or policy is None:
            return Verdict.escalate("thiếu đơn hoặc chính sách để ghi lỗi hãng")
        parcel = next((p for p in order.get("parcels", [])
                       if p.get("parcel_id") == action.get("parcel_id")), None)
        if parcel is None:
            return Verdict.deny("không khớp được kiện hàng")
        delay = H.db_delay_days(parcel, ctx.as_of)
        if not parcel.get("delay_cause") or not H.carrier_at_fault(policy, parcel, delay):
            return Verdict.deny("không có nguyên nhân ghi nhận đủ điều kiện quy lỗi")
        changes = {"carrier_id": parcel["carrier_id"], "delay_days": delay}
        if action.get("carrier_id") != changes["carrier_id"] or action.get("delay_days") != delay:
            return Verdict.modify("đồng bộ hãng và độ trễ từ kiện hàng", **changes)

    elif tool == "notify_carrier":
        payload = action.get("payload") or {}
        allowed = {"order_id", "parcel_id", "district", "delay_days"}
        clean = {k: v for k, v in payload.items() if k in allowed}
        if clean != payload:
            return Verdict.modify("chỉ gửi trường vận hành đã cho phép", payload=clean)
    return Verdict.allow()
