# Luật lab — Day 14

## 1. Dùng AI

- Được dùng AI (ChatGPT, Claude, Gemini, Copilot, Cursor…) để hỏi khái niệm, đọc lỗi, gợi ý cách sửa.
- Mỗi lần dùng AI cho code Part 6 hoặc cho câu trả lời, ghi vào cuối `MISSION_ANSWERS.md` mục **AI log**: hỏi gì, nhận gì, bạn tự sửa và tự kiểm tra thế nào.
- Lab Coach có thể yêu cầu bạn giải thích bất kỳ đoạn code nào trong `06-lab-complete/app/`, hoặc bất kỳ con số nào trong `BENCHMARK_REPORT.md`.
- Không dùng AI để bịa số đo. Mọi số (kích thước image, latency, accuracy, thời gian alert firing) phải lấy từ lệnh bạn đã chạy và file report bạn nộp.

## 2. Sao chép

- Được thảo luận với bạn. Code, câu trả lời, số đo và ảnh chụp phải là của bạn.
- URL deploy, ảnh dashboard và file report trùng với bài khác là dấu hiệu sao chép.
- Bài sao chép: cả hai bài bị 0 điểm phần liên quan và báo lên chương trình.

## 3. Không được sửa

- `06-lab-complete/check_production_ready.py` (script chấm).
- `06-lab-complete/benchmark-observability/develop/eval/golden_dataset.jsonl` (bộ câu hỏi eval). Exercise 7.3 sửa `KNOWLEDGE_BASE` trong `06-lab-complete/benchmark-observability/develop/utils/mock_llm.py`, không sửa đáp án.

## 4. Deadline và nộp muộn

- Deadline: xem [SUBMISSION.md](SUBMISSION.md#deadline). Thông báo của Lab Coach được ưu tiên.
- Bản được chấm là **commit cuối cùng trước deadline**. Commit sau deadline không được chấm, trừ khi Lab Coach đã đồng ý trước (lý do sức khoẻ, sự cố kỹ thuật có bằng chứng).
- Được commit tiếp sau deadline để tự học, nhưng không đổi điểm. Không force-push, không sửa ngày commit.

## 5. Secret, tài khoản cloud và dữ liệu

- Lab dùng mock LLM, không cần API key LLM.
- **Không bao giờ** commit `.env`, `AGENT_API_KEY` thật, token Railway/Render. Chỉ commit `.env.example` (đã có trong `.gitignore`).
- Lỡ commit secret: đổi key mới ngay trên dashboard rồi báo Lab Coach. Xoá file thôi chưa đủ, vì secret vẫn nằm trong lịch sử git.
- Dùng gói miễn phí hoặc gói dùng thử của Railway hoặc Render. Nếu nền tảng đòi thẻ thanh toán mà bạn không muốn nhập, báo Lab Coach trước khi làm tiếp.
- Xong lab thì tắt stack Docker (`docker compose down -v`, thêm đúng `-p` nếu lúc bật có dùng `-p`). Sau khi đã được chấm có thể xoá service trên cloud.
- Không ghi email, số điện thoại vào bài. Họ tên và MSSV chỉ ghi ở tên repo và ô Họ tên của `BENCHMARK_REPORT.md`.
