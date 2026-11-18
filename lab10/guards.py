"""Cổng phòng ngừa cho quyết định hoàn tiền và tác động tới bên thứ ba."""
from . import helpers as H
from .tools import Verdict


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
        if action.get("payer") != "LOGIX":
            return Verdict.escalate("bên trả tiền không phải LogiX; cần người duyệt")

        approval_id = action.get("approval_id")
        if approval_id:
            approvals = ctx.tools.lookup_approvals(approval_id=approval_id)
            valid = any(a.get("ticket_id") == action.get("ticket_id")
                        and a.get("status") == "valid"
                        and a.get("expires_at", "") >= ctx.as_of
                        and a.get("max_vnd", 0) >= action.get("amount_vnd", 0)
                        for a in approvals)
            if not valid:
                return Verdict.escalate("phê duyệt không hợp lệ cho ticket hoặc số tiền này")
        else:
            if order.get("refund_status") != "NONE":
                return Verdict.escalate("trạng thái hoàn không còn là NONE")
            parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
            delay = H.db_delay_days(parcel, ctx.as_of)
            amount = H.entitlement_vnd(policy, order, delay, parcel.get("delay_cause"))
            if amount <= 0:
                return Verdict.deny("tracking và chính sách không cho phép hoàn tự động")
            limit = min(policy.get("auto_limit_vnd", 0),
                        ctx.tools.ops_limits().get("max_auto_refund_per_customer_per_day_vnd", 0))
            if amount > limit:
                return Verdict.escalate("vượt hạn mức tự động; cần người duyệt")
            cap = (ctx.gates or {}).get("business", {}).get("daily_refund_cap_vnd")
            spent = ctx.tools.auto_refund_today_vnd()
            if cap is not None and spent + amount > cap:
                return Verdict.escalate("vượt trần hoàn tự động trong ngày")
            ctx.log("hoan_tien_tinh_lai_tu_nguon", order_id=order["order_id"],
                    delay_days=delay, amount_vnd=amount)
            if action.get("amount_vnd") != amount:
                return Verdict.modify("điều chỉnh theo tracking và chính sách", amount_vnd=amount)

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
