# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): `XYZ`
- Lớp: `L3A`
- Repo của bàn: `K5-L3A-DAY10-XYZ-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): `S2`

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; thêm dòng nếu cần. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Phạm Hồng Khánh Huy | 2A202603588 | Kỹ sư cổng; trưởng nhóm | Phạm Hồng Khánh Huy |
|   2 | Trần Hoàng Phát | 2A202603536 | Sản phẩm và kinh doanh | |
|   3 | Nguyễn Quốc Việt | 2A202603556 | Vận hành | |
|   4 | Trịnh Quốc Đạt | 2A202603581 | Pháp lý và rà soát dữ liệu cá nhân | |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## PhamHongKhanhHuy-2A202603588

### Phần việc phụ trách

Kỹ sư cổng và trưởng nhóm; phụ trách Phiếu B mục B0–B2, B7.1–B7.3, B8 và Phiếu C mục C0, C2, C4, C5, C7, C8, C9; xây dựng `lab10/guards.py`, `lab10/monitors.py`, chốt mốc `prepared` và chạy đánh giá hồi quy + tự kiểm tra thẻ S2.

### Đóng góp cụ thể

Vòng 1: viết cổng chọn chính sách theo ngày hiệu lực, tính lại khoản hoàn từ tracking, kiểm tra phê duyệt, xác minh nguyên nhân ghi lỗi hãng, lọc trường dữ liệu gửi hãng và monitor `carrier_pii_attempts_per_100`. Vòng 2 (thẻ S2): nâng cấp `write_gate(issue_refund)` tính lại quyền lợi trước khi xét `payer` (`deny` khi không đủ điều kiện, ép `payer="LOGIX"`, bắt buộc `approval_id` hợp lệ khi `> auto_limit`), bổ sung `_customer_auto_refund_today_vnd` chặn cộng dồn vượt 300.000đ/khách/ngày, chống ghi trùng sổ cái và thêm monitor `refund_policy_override_or_cap_pct`.

### Bằng chứng

Commit `70890e7`, `2cb889e`; mốc chốt `2e1ab687`; lần chạy `R-S2-grade-20261118-173430-c1d0fc`, `R-S2-after-20261118-173429-c1d0fc`, `R-base-after-20261118-173429-c1d0fc`; Phiếu B (B7.1–B8) và Phiếu C (C0–C9).

### Exit ticket

Học được rằng không thể dùng lọc từ khóa đơn thuần để chống prompt injection (trực tiếp lẫn gián tiếp qua `checkout_note`), mà phải cưỡng chế bất biến từ nguồn sự thật ngay trước lệnh ghi và kiểm soát hạn mức cộng dồn theo khách trong ngày. Còn băn khoăn cách phát hiện sớm tấn công tách nhiều tài khoản (`customer_id`) cùng SĐT/địa chỉ trong pilot thật.

## TranHoangPhat-2A202603536

### Phần việc phụ trách

Sản phẩm và kinh doanh; phụ trách tiêu chí chấp nhận (Phiếu A), bản đồ dữ liệu (B3), cổng kinh doanh (`config/operating_gates.json` mục `business`), phân tích chi phí/ROI theo phân khúc kho trên S2, Risk register (C10) và quyết định Gate 1 v1 (B8) & v2 (C12).

### Đóng góp cụ thể

Đặt ngưỡng tiêu chí chấp nhận và ký khóa trước khi đo; đặt trần hoàn tự động, ngân sách chi phí LLM, ngưỡng ROI và phạm vi pilot; phối hợp phân tích nguyên nhân kho HCM vượt làm tay ở mốc `prepared` trên S2 (`10.570đ → 670đ` sau khi sửa `deny` ca `entitlement=0`) và chốt quyết định v2 (`Tiếp tục`) khớp bằng chứng.

### Bằng chứng

Commit `6448b17`, `8bd2c17`; cấu hình `config/operating_gates.json`; Phiếu A, Phiếu B (B3, B7.4, B8) và Phiếu C (C1, C10, C12) với report `R-S2-grade-20261118-173430-c1d0fc`.

### Exit ticket

Học được rằng chính sách chuyển người duyệt nếu thiết kế quá rộng (`escalate` cả ca không đủ điều kiện) sẽ phá hỏng ROI từng kho ngay cả khi an toàn kỹ thuật đã đạt. Chưa chắc cơ cấu tỉ lệ tấn công và chi phí theo từng kho có giữ ổn định khi mở rộng toàn bộ depot thật hay không.

## NguyenQuocViet-2A202603556

### Phần việc phụ trách

Vận hành; phụ trách cổng `operations` trong `config/operating_gates.json` (PIC, người duyệt, năng lực và SLA hàng chờ, điều kiện dừng, kênh cảnh báo), Runbook phần 1–3, Giờ cao điểm (B7.5–B7.6), cập nhật checklist và Runbook phần 4–5 (C11).

### Đóng góp cụ thể

Thiết lập năng lực 2 người duyệt/ca (`12 ca/giờ`), SLA `60 phút`, ghi chú quyết định và kiểm mẫu `10%`; bổ sung tín hiệu `refund_policy_override_or_cap_pct` và ngưỡng 300.000đ/khách/ngày vào Runbook 4–5 cùng 3 kịch bản ứng phó tuần đầu pilot.

### Bằng chứng

Commit `a73f30e`; `config/operating_gates.json`; Phiếu B (B7.5–B7.6) và Phiếu C (C11) khớp report `R-S2-grade-20261118-173430-c1d0fc` (`queue_wait_max = 0 phút`, `queue_stuck = 0`).

### Exit ticket

Học được rằng hàng chờ, SLA và quy trình dừng khẩn cấp phải gắn trực tiếp với các tín hiệu máy đo trong `monitors.py` thay vì chờ khiếu nại thủ công. Chưa chắc năng lực `12 ca/giờ` duy trì được liên tục trong ca sale lớn nếu phát sinh nhiều ca cần đối soát chứng từ.

## TrinhQuocDat-2A202603581

### Phần việc phụ trách

Pháp lý và rà soát dữ liệu cá nhân; phụ trách cổng `legal` trong `config/operating_gates.json`, bảng mức kiểm soát của con người (C3.1), rà soát trách nhiệm bên thứ ba (shop và hãng vận chuyển) và quy trình thông báo sự cố pháp lý trong Runbook.

### Đóng góp cụ thể

Thiết lập danh sách trường cá nhân bị chặn gửi hãng và yêu cầu nguyên nhân ghi nhận trước khi quy lỗi hãng; rà soát bảng mức kiểm soát ở C3.1 để bảo vệ shop khỏi bị trừ tiền oan (`merchant_debit_vnd: 32.750.000đ → 0đ`) và hãng khỏi lỗi oan (`15 → 0`).

### Bằng chứng

`config/operating_gates.json` mục `legal`; `lab10/guards.py` nhánh `issue_refund`, `file_carrier_fault`, `notify_carrier`; Phiếu C mục C3.1, C11 và report `R-S2-grade-20261118-173430-c1d0fc`.

### Exit ticket

Học được rằng lỗi chìm ở trợ lý có quyền ghi sổ thường gây thiệt hại trực tiếp cho bên thứ ba (shop, hãng vận chuyển) không trực tiếp dùng hệ thống, nên phải chặn cứng ở tầng ghi và đối soát quyền kiểm soát con người. Chưa chắc danh sách trường allowlist và quy trình thông báo đối tác 2 giờ đã bao phủ hết mọi yêu cầu hợp đồng thực tế.
