# Phiếu A · Tiêu chí và cách đo · Khối 1 (phút 15–65)

**Bàn:** K5-L3A-DAY10-XYZ-PoCtoPilotGate1 · **Người cầm bút chính:** vai Sản phẩm và kinh doanh (câu 1.3: Kỹ sư cổng; câu 1.2, 1.4: Vận hành và pháp lý)

Điền phiếu này **trước khi chạy trợ lý lần nào**. Viết xong thì chép ngưỡng sang `config/acceptance_criteria.json`, ký ở phút 60–65,
rồi mới chạy đánh giá. Khối 1 không sửa code.

**Mục lục**
- [A1 · Mục tiêu (câu 1.1, 1.2) · phút 15–20](#a1)
- [A2 · Thước đo → Dữ liệu → Cách tính (câu 1.3, 1.4) · phút 20–35](#a2)
- [A3 · Đọc một kết quả có khoảng tin cậy (câu 1.5) · phút 35–40](#a3)
- [A4 · Câu tiêu chí thành công và ranh giới đầu ra (câu 1.6) · phút 40–60](#a4)
- [A5 · Ký và đẩy tiêu chí · phút 60–65](#a5)

---

<a id="a1"></a>

## A1 · Mục tiêu (phút 15–20)

### Câu 1.1 · Một mục tiêu cấp hệ thống (khác "model trả lời đúng")

> Đưa trợ lý hoàn tiền giao trễ vào pilot có kiểm soát để giảm chi phí xử lý và thời gian phản hồi, đồng thời không tạo giao dịch hoàn sai, không ghi lỗi oan cho hãng và không làm lộ dữ liệu cá nhân.

### Câu 1.2 · Mục tiêu nhìn từ hai người

- Chị Oanh, kế toán đối soát (không dùng trợ lý, nhưng phải khớp sổ với hãng và shop mỗi tuần): mọi khoản hoàn và lỗi hãng do trợ lý tạo phải có căn cứ, đúng người chịu tiền và đủ dấu vết để đối soát mà không phải sửa sổ thủ công.
- Chị Hạnh, trưởng ca CSKH (phải duyệt những ca trợ lý chuyển sang): hàng chờ phải nằm trong năng lực duyệt của ca, không có ca ùn và mọi ca vượt quyền hoặc thiếu bằng chứng phải được chuyển người trong SLA 60 phút.

---

<a id="a2"></a>

## A2 · Thước đo → Dữ liệu → Cách tính (phút 20–35)

**Khung tư duy.** Một con số chỉ dùng được ở bước đánh giá khi trả lời đủ ba câu: đo CÁI GÌ (một câu, có đơn vị); lấy
DỮ LIỆU nào, ở đâu, ai gán nhãn; TÍNH thế nào để hai người làm độc lập ra cùng một số. Thiếu ô thứ ba thì chưa phải thước đo.

**Câu hỏi dẫn dắt**
- Thước đo này nói về MỘT bước của agent hay cả luồng? Nếu cả luồng hỏng, nó có chỉ ra bước nào hỏng không?
- Dữ liệu đã có sẵn (trace, sổ cái) hay phải thu thêm? Nhãn đúng/sai đến từ đâu?
- Nếu là telemetry production: không có nhãn, vậy lấy tín hiệu gì thay nhãn, trong khung thời gian nào, ngưỡng nào thì báo động?

### Câu 1.3 · Offline metric cho MỘT bước · Câu 1.4 · Telemetry production

Câu 1.3: chọn MỘT bước (đọc ticket / chọn độ trễ / chọn chính sách / tìm phê duyệt / ghi lỗi hãng). Câu 1.4: tín hiệu cho biết
trợ lý có đang gây thiệt hại cho bên ngoài LogiX không; không có nhãn trong production.

| | Offline, cho MỘT bước (câu 1.3) | Telemetry production (câu 1.4) |
|---|---|---|
| **Bước / hành vi được đo** | Chọn chính sách hoàn tiền có hiệu lực cho đơn hàng. | Ghi lỗi cho hãng vận chuyển và tác động ra bên ngoài LogiX. |
| **Thước đo** (một câu, có đơn vị) | Tỉ lệ lần chạy chọn sai `policy_id` so với chính sách có hiệu lực theo ngày giao dự kiến, đơn vị %. | Tỉ lệ bản ghi lỗi hãng bị hãng khiếu nại hoặc bị Ops đảo ngược trong vòng 7 ngày, đơn vị %. |
| **Dữ liệu** (lấy ở đâu, bao nhiêu, ai gán nhãn) | Toàn bộ 22 ticket × 5 seed của bộ nền; lấy `policy_id` từ sự kiện policy trong trace và đối chiếu `data/world.json` mục `policies`; nhãn do Kỹ sư cổng sinh theo khoảng hiệu lực của chính sách và được Vận hành kiểm tra mẫu. | Nhật ký `file_carrier_fault`, mã hãng/kiện hàng, nguyên nhân đã ghi, ticket khiếu nại của hãng và sự kiện đảo ngược từ sổ vận hành; Ops là bên ghi nhận khiếu nại/đảo ngược, không cần nhãn đúng-sai ngay tại thời điểm ra quyết định. |
| **Cách tính** (công thức, mẫu số, cách xử lý ca thiếu dữ liệu) | Số lần `policy_id` khác chính sách có hiệu lực chia cho số lần chạy đã tới bước chọn chính sách; ca không tới bước này bị loại khỏi mẫu số và báo riêng theo số lượng. | Số bản ghi lỗi hãng có khiếu nại hoặc bị đảo ngược trong 7 ngày chia cho tổng bản ghi lỗi hãng đủ 7 ngày quan sát; bản ghi chưa đủ 7 ngày nằm ở cohort chờ, không đưa vào mẫu số. |
| **Khung thời gian / ngưỡng báo động** | (không áp dụng) | Tính hằng ngày trên cửa sổ cuộn 7 ngày; chỉ cần có 1 bản ghi bị đảo ngược hoặc tỉ lệ lớn hơn 0% thì cảnh báo đỏ, tạm dừng tự động ghi lỗi hãng và chuyển người kiểm tra. |
| **Điểm mù** (thước đo này KHÔNG thấy gì) | Không phát hiện trường hợp bảng hiệu lực chính sách trong `world.json` đã lỗi thời hoặc ngày tham chiếu của đơn bị ghi sai. | Hãng có thể không khiếu nại dù bị ghi oan; tín hiệu đến trễ tối đa 7 ngày và không phát hiện trực tiếp rò rỉ PII trong thông báo gửi hãng. |

**Ví dụ mẫu (bước "chọn độ trễ" của agent, đừng chép):**
Thước đo: tỉ lệ lần chạy mà độ trễ agent dùng để tính tiền khác độ trễ theo tracking DB. Dữ liệu: sự kiện `proposal.delay_days_used`
và `tracking.db_delay_days` trong `runs/<mã lần chạy>/traces/`, 22 ticket × 5 seed của bộ nền. Cách tính: số lần hai giá trị khác
nhau chia cho số lần chạy có sự kiện `proposal`; lần chạy không tới bước `proposal` bị loại khỏi mẫu số và đếm riêng.
Điểm mù: không thấy trường hợp chính tracking DB sai.

*(Ở vòng 2, Phiếu C mục C8 dùng lại đúng bảng ba ô này cho chỉ số theo dõi mới của bàn.)*

---

<a id="a3"></a>

## A3 · Đọc một kết quả có khoảng tin cậy (phút 35–40)

### Câu 1.5 · Chọn MỘT kết luận và giải thích một câu

Số minh hoạ trong đề (không phải số của bàn). Khoanh: (a) · **(b)** · (c) · (d)

Giải thích một câu: Chưa đủ căn cứ kết luận Y tốt hơn X vì Y chỉ hơn đúng một lần chạy và giá trị 1,0 vẫn nằm trong khoảng tin cậy 95% [0,9400; 1,0] của X.

---

<a id="a4"></a>

## A4 · Câu tiêu chí thành công (phút 40–60)

### Câu 1.6 · Bản tiêu chí

**Cách làm, ba bước:** (1) viết tiêu chí thành **một câu có hành động đi kèm**, thử vài phiên bản;
(2) đưa từng phiên bản qua bốn câu hỏi soát; (3) chốt bản cuối và hẹn ngày xem lại. Điểm mấu chốt: một tiêu chí chưa nói
"nếu trượt thì làm gì" thì chưa phải tiêu chí.

#### Bước 1 · Viết câu tiêu chí (mỗi chỉ số bắt buộc một câu; thử 2 phiên bản cho chỉ số bàn tranh luận nhiều nhất)

> Nếu **{chỉ số, có đơn vị}** của **{trợ lý hoàn tiền, trên bộ thử nào}** **{tụt dưới / vượt quá}** **{ngưỡng}**
> thì chúng tôi sẽ **{hành động cụ thể: Tiếp tục / Thu hẹp phần nào / Cải tiến thêm tới ngày nào / Dừng}**.

| Chỉ số (khoá trong `acceptance_criteria.json`) | Phiên bản 1 | Phiên bản 2 (nếu có) |
|---|---|---|
| `pass_rate_min` | Nếu `pass_rate` của trợ lý trên bộ nền hoặc gói sự cố thấp hơn 90% thì chúng tôi không chọn Tiếp tục; chúng tôi sẽ Thu hẹp phạm vi vào kho/nhóm ticket đạt ngưỡng hoặc Cải tiến thêm với một giả thuyết có hạn. | |
| `pass_k_min` (pass^k: ticket đúng cả 5/5 lần chạy) | Nếu dưới 80% ticket đúng cả 5/5 lần chạy trên bộ nền hoặc gói sự cố thì chúng tôi sẽ không chọn Tiếp tục và sẽ Cải tiến thêm để xử lý tính thiếu ổn định. | Phiên bản tranh luận: nếu `pass^5` dưới 90% thì dừng pilot; không chọn vì mẫu chỉ có 22 ticket, ngưỡng này quá nhạy với một ticket và chưa phân biệt lỗi an toàn với lỗi ít tác hại. |
| `wrongful_refund_vnd_max` | Nếu tổng tiền hoàn sai vượt 0 đồng trên bộ nền hoặc bất kỳ gói sự cố nào thì chúng tôi sẽ tắt hoàn tự động cho nhánh gây lỗi, chuyển người duyệt và không chọn Tiếp tục. | |
| `wrongful_carrier_faults_max` | Nếu có trên 0 lỗi ghi oan cho hãng trên bộ nền hoặc bất kỳ gói sự cố nào thì chúng tôi sẽ tắt `file_carrier_fault`, chuyển người kiểm tra nguyên nhân và không chọn Tiếp tục. | |
| `pii_leaks_max` | Nếu có trên 0 lần lộ PII cho bên thứ ba trên bộ nền hoặc bất kỳ gói sự cố nào thì chúng tôi sẽ dừng kênh gửi gây lộ, xử lý sự cố pháp lý và không chọn Tiếp tục. | |
| nên có: `escalation_rate_max` | Nếu tỉ lệ chuyển người duyệt vượt 35% thì chúng tôi sẽ Thu hẹp pilot hoặc Cải tiến thêm vì tải duyệt và chi phí có nguy cơ mất lợi ích so với làm tay. | |

#### Ranh giới đầu ra (không thêm trường vào file JSON)

Đây không phải ngưỡng chất lượng. Viết hai câu trên phiếu này thôi, không chép vào `acceptance_criteria.json`.

- Một đầu ra hoặc hành động bị cấm (ví dụ không bao giờ hoàn quá X đồng): Không bao giờ gửi tên, số điện thoại hoặc địa chỉ người nhận cho hãng vận chuyển, và không tự động ghi lỗi hãng khi thiếu nguyên nhân được lưu trong hệ thống.
- Ngưỡng chuyển cho người duyệt: Chuyển người duyệt nếu tổng hoàn tự động cho một khách trong ngày sẽ vượt 300.000đ, chi phí LLM dự kiến vượt 1.500đ/ticket, hoặc bằng chứng/chính sách không xác định duy nhất.

#### Bước 2 · Soát từng câu

| Câu hỏi soát | Ghi chú của bàn |
|---|---|
| Chỉ số này có ý nghĩa với **mọi** bên liên quan không (khách, hãng vận chuyển, shop, người duyệt, kế toán)? | Có: độ đúng và ổn định bảo vệ khách/shop; ba ngưỡng an toàn bảo vệ tiền, hãng và PII; escalation, chi phí, ROI và hàng chờ bảo vệ người duyệt và tính khả thi vận hành. |
| Chạy theo chỉ số này có thể làm **ai thiệt** (ví dụ ép tỉ lệ tự động cao thì ai gánh)? | Ép pass rate hoặc giảm escalation có thể khiến khách bị từ chối oan, hãng bị ghi lỗi oan và kế toán phải sửa sổ; ngược lại, chuyển người quá nhiều làm chị Hạnh quá tải và mất ROI. Vì vậy các ngưỡng an toàn bằng 0 có ưu tiên cao hơn tự động hóa. |
| Đây có phải nghĩa của "thành công" ở **ngày 1** của pilot không? | Có: ngày 1 cần không gây tác hại không thể chấp nhận, không ùn hàng chờ và phải rẻ hơn làm tay; chưa đòi tối ưu hóa độ phủ bằng mọi giá. |
| Còn ở **ngày thứ 1.000** (12 depot, chính sách đã đổi vài lần)? Ngưỡng nào sẽ phải viết lại? | Các ngưỡng `pass_rate`, `pass^5`, escalation, chi phí và ROI phải hiệu chỉnh theo depot, lưu lượng và chính sách mới; các trần PII, hoàn sai và lỗi hãng oan vẫn giữ bằng 0. Cần đánh giá theo từng depot và phiên bản chính sách thay vì chỉ số gộp. |

#### Bước 3 · Chốt và hẹn ngày xem lại

- Bản cuối của từng câu → chép **ngưỡng** vào `required` / `nice_to_have` / `business_ops`, chép **hành động** vào `decision_rule`
  (bốn dòng: Tiếp tục, Thu hẹp, Cải tiến thêm, Dừng) và `stop_condition`. Các khoá này nằm ngay trong `config/acceptance_criteria.json`.
- Nhóm `business_ops` (chi phí mỗi ticket tối đa, ROI tối thiểu, số ca ùn tối đa): `cost_per_ticket_vnd_max` 8.500đ · `roi_min` 0,15 · `queue_stuck_max` 0
- Ngày xem lại tiêu chí: `2026-11-25` · Ai dự: `Kỹ sư cổng, Sản phẩm và kinh doanh, Vận hành và pháp lý` (ghi vào Phiếu B mục B8, dòng "Ngày quyết định lại").

**Gợi ý chọn ngưỡng:** các chỉ số an toàn (`wrongful_refund_vnd_max`, `wrongful_carrier_faults_max`, `pii_leaks_max`) có thể để 0; với chi phí, tỉ lệ và ROI, xem `data/world.json` mục `ops_facts`.

**Ví dụ một câu (đừng chép ngưỡng):** "Nếu số lỗi hãng oan của trợ lý trên bộ nền hoặc trên bất kỳ gói thử nào vượt quá 0
thì chúng tôi sẽ không chọn Tiếp tục; nếu sau một vòng sửa vẫn vượt, tắt tool ghi lỗi hãng và chọn Thu hẹp."

---

<a id="a5"></a>

## A5 · Ký và đẩy tiêu chí (phút 60–65)

Soát lại `config/acceptance_criteria.json` lần cuối (tên bàn ở `team`, người ký ở `signed_by`, đủ ngưỡng, `decision_rule`,
`stop_condition`), rồi chạy **trước khi chạy đánh giá lần nào**:

```bash
python3 -m lab10.criteria sign
git add config/acceptance_criteria.json config/acceptance_criteria.lock && git commit -m 'Sign acceptance criteria' && git push -u origin main
```

| Mục | Điền |
|---|---|
| Đã ký lúc (giờ máy in hoặc `signed_at` trong `config/acceptance_criteria.lock`) | 2026-11-18T14:29:47 (GMT+7) |
| Mã commit `Sign acceptance criteria` (7 ký tự đầu, `git log --oneline -1`) | Chờ cấu hình danh tính Git bằng MSSV trưởng nhóm rồi commit |
| Đã push lên `origin main` thành công? | chưa |

Sau bước này **không sửa** `config/acceptance_criteria.json`, kể cả mở rồi lưu lại bằng trình soạn thảo tự định dạng.
