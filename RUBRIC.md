# Rubric — Day 14: Deployment, Benchmark & Observability

> Bài **cá nhân**. Điểm từng Part theo [INSTRUCTOR_GUIDE.md](INSTRUCTOR_GUIDE.md); riêng Part 3 và Part 6, lớp K5 chấm theo hai bảng chi tiết bên dưới.
> **Tổng thô 120**, quy về thang 100: `Điểm = Tổng thô × 100 / 120` (làm tròn 0,5). **Đạt:** 70/100 (tương đương 84/120).
> **Cách chấm:** mở link repo nộp trên LMS, chấm commit cuối trước deadline. Bước đầu tiên là chạy `python check_production_ready.py` trong `06-lab-complete/` trên máy có Docker.

## Điểm chính

| Hạng mục | Điểm | Checkpoint | Bằng chứng |
| --- | ---: | --- | --- |
| Part 1 — Localhost vs Production | 8 | CP1 | `MISSION_ANSWERS.md` mục Part 1 |
| Part 2 — Docker | 8 | CP2 | `MISSION_ANSWERS.md` mục Part 2, có số MB đo được |
| Part 3 — Cloud Deployment | 8 | CP6 | `MISSION_ANSWERS.md` mục Part 3, URL public trả lời được |
| Part 4 — API Security | 8 | CP3 | `MISSION_ANSWERS.md` mục Part 4, có output 401 / 200 / 429 |
| Part 5 — Scaling & Reliability | 8 | CP4 | `MISSION_ANSWERS.md` mục Part 5 |
| **Part 6 — Final Project** | **60** | CP5, CP6 | `06-lab-complete/` báo `PASS 12/12`; `DEPLOYMENT.md` có URL chạy được; ảnh trong `screenshots/` |
| Part 7 — Load test & SLO | 4 | CP7 | Bảng 4 mức concurrency (RPS, p50/p95/p99, error rate); so sánh `MOCK_SLOW_RATE` |
| Part 7 — Eval & quality gate | 5 | CP7 | v1 vs v2; v2 đạt 23/23 không regression; cách dùng exit code để chặn merge |
| Part 7 — Observability stack | 4 | CP8 | Ảnh Grafana có tải; trả lời Exercise 7.4 |
| Part 7 — Tracing | 3 | CP8 | Ảnh trace chậm (span chậm nhất + số ms); `trace_id` khớp một dòng log JSON |
| Part 7 — Alerts & chaos | 4 | CP8 | Một ảnh `prometheus-alert-firing.png` (trang Alerts) thấy ≥ 2 alert đang firing; thời gian tới lúc firing; phân tích thí nghiệm |
| **Tổng thô** | **120** | | |

Tiêu chí con và đáp án mong đợi của Part 1, 2, 4, 5, 7 nằm trong [INSTRUCTOR_GUIDE.md](INSTRUCTOR_GUIDE.md). Part 3 và Part 6 chấm theo hai bảng dưới đây.

## Part 3 — Cloud Deployment (8 điểm)

Chọn Railway **hoặc** Render làm nền tảng chính; chọn nền tảng nào cũng lấy được đủ 8 điểm.

| Mục | Điểm | Cách đạt |
| --- | ---: | --- |
| Deploy trên nền tảng chính (Exercise 3.1 hoặc 3.2) | 4 | URL public của agent Part 6 chạy đúng 4 lệnh tự kiểm ở CP6 |
| Nền tảng còn lại | 3 | Deploy thêm lên nền tảng kia, **hoặc** so sánh `railway.toml` với `render.yaml` trong `MISSION_ANSWERS.md` (khác nhau chỗ nào, vì sao) |
| Exercise 3.3 — Cloud Run | 1 | Đọc `cloudbuild.yaml` và `service.yaml` trong `03-cloud-deployment/production-cloud-run/`, viết 3–5 dòng trong `MISSION_ANSWERS.md` mô tả pipeline CI/CD đi qua những bước nào. Không cần tài khoản GCP, không cần deploy |

## Part 6 — Final Project (60 điểm)

Mỗi mục con chấm **đạt hoặc không**: đạt thì đủ điểm mục đó, không đạt thì 0. Mục nào `check_production_ready.py` báo ❌ thì mục con tương ứng 0 điểm. Mục ⚠️ (không kiểm tra được, ví dụ thiếu Docker) cũng tính là chưa đạt.

| Nhóm | Mục con | Điểm |
| --- | --- | ---: |
| Functional (15) | `POST /ask` trả lời đúng | 10 |
| | Xử lý lỗi: input sai trả mã lỗi rõ ràng, không lộ stack trace | 5 |
| Docker & cấu hình (10) | Dockerfile multi-stage | 4 |
| | Image < 500 MB | 2 |
| | `docker-compose.yml` có agent + Redis | 2 |
| | Mọi cấu hình đọc từ biến môi trường | 2 |
| Security (15) | API key (`X-API-Key`, thiếu hoặc sai → 401) | 4 |
| | Rate limit (vượt → 429, state trong Redis) | 4 |
| | Cost guard (vượt ngân sách → 402) | 4 |
| | Không hardcode secret | 3 |
| Reliability (10) | `/health` | 2 |
| | `/ready` (503 khi mất Redis) | 2 |
| | Tắt an toàn khi nhận SIGTERM | 3 |
| | Stateless: state trong Redis, không trong RAM | 3 |
| Deployment (10) | URL public chạy được (ghi trong `DEPLOYMENT.md`) | 5 |
| | File config nền tảng (`railway.toml` hoặc `render.yaml`) | 3 |
| | Biến môi trường đặt trên nền tảng (`AGENT_API_KEY`, `REDIS_URL`…), không ghi trong code | 2 |
| **Tổng** | | **60** |

- Conversation history không tính điểm (xem mục Bonus).
- URL deploy được chấm ở cả Part 3 và nhóm Deployment của Part 6, vì lớp K5 deploy chính agent Part 6 ở CP6.
- Sửa `check_production_ready.py` để lấy `PASS`: Part 6 bị 0 điểm.

## Bonus

Lab này không có bonus. Các mục "Mở rộng" ở Part 6 (lưu history trong Redis, streaming, Nginx + 3 instance) không tính điểm.

## Trừ điểm và điều kiện không chấm

| Tình huống | Xử lý |
| --- | --- |
| Commit `.env`, API key hoặc token deploy (kể cả trong lịch sử commit) | −10 điểm; phải thu hồi (revoke) và tạo key mới. Xoá file thôi không đủ |
| Số liệu trong `BENCHMARK_REPORT.md` không khớp file JSON/CSV đã nộp | Mục Part 7 tương ứng 0 điểm |
| Sai tên repo hoặc sai chỗ file (xem [SUBMISSION.md](SUBMISSION.md)) | −5 điểm nếu vẫn tìm được bài; không chấm nếu không tìm được |
| Repo private, Lab Coach không mở được | Không chấm |
| Nộp muộn, sửa sau deadline, sao chép, dùng AI không khai báo | Theo [RULES.md](RULES.md) |
