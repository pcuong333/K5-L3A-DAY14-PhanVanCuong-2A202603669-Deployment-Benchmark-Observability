# Cách nộp bài — Day 14 (cá nhân)

> Mỗi học viên nộp **một** repo, **một** link trên LMS.
> Điểm: [RUBRIC.md](RUBRIC.md) · Luật: [RULES.md](RULES.md) · Lịch làm: [CHECKPOINTS.md](CHECKPOINTS.md).
> Nội dung từng file nộp (mẫu `MISSION_ANSWERS.md`, `DEPLOYMENT.md`, `BENCHMARK_REPORT.md`): [DAY14_DELIVERY_CHECKLIST.md](DAY14_DELIVERY_CHECKLIST.md).

## Tên repository

```text
K5-<L3A hoặc L3B>-DAY14-HoVaTen-MSSV-Deployment-Benchmark-Observability
```

Ví dụ: `K5-L3A-DAY14-NguyenVanA-2A2026xxxxx-Deployment-Benchmark-Observability`.
Họ tên viết liền, không dấu, viết hoa chữ cái đầu. Repo để **Public** để Lab Coach mở được.

### Tạo repo

1. Fork repo này về tài khoản GitHub cá nhân.
2. Vào **Settings → Repository name**, đổi tên theo mẫu trên.
3. Clone bản fork về máy và làm bài **trong bản fork**, không làm trên repo đề bài.

Làm Part 6 ngay trong `06-lab-complete/` của bản fork, không copy code ra thư mục khác: Lab Coach chạy `check_production_ready.py` và eval tại đúng các đường dẫn này. Cây thư mục `app/` ở gốc repo trong `DAY14_DELIVERY_CHECKLIST.md` mục 2 không áp dụng cho lớp K5.

## Cấu trúc phải nộp

```text
K5-L3A-DAY14-HoVaTen-MSSV-Deployment-Benchmark-Observability/
├── MISSION_ANSWERS.md          # Part 1–5 + output check_production_ready.py + AI log
├── DEPLOYMENT.md               # URL public, lệnh test, biến môi trường đã đặt
├── BENCHMARK_REPORT.md         # Part 7, copy từ BENCHMARK_REPORT_TEMPLATE.md rồi điền
├── reports/                    # Part 7 — JSON của load test và eval
│   ├── load_v2_c1.json … load_v2_c100.json
│   ├── load_v2_slow_0.json, load_v2_slow_0.03.json, load_v2_slow_0.1.json   # so sánh MOCK_SLOW_RATE
│   ├── eval_v1.json
│   ├── eval_v2.json
│   └── eval_v2_fixed.json
├── benchmark-results/          # Part 7 — CSV của Locust
│   ├── scale_1_stats.csv
│   └── scale_3_stats.csv
├── screenshots/
│   ├── dashboard.png  running.png  test.png             # Part 3 / 6 — deploy
│   └── grafana-dashboard.png  jaeger-slow-trace.png
│       jaeger-error-trace.png  prometheus-alert-firing.png   # Part 7
└── 06-lab-complete/            # Part 6 — code đã sửa hết TODO, PASS 12/12
```

`load_test.py`, `run_eval.py` (khi có `--out`) và Locust ghi file ở thư mục chạy lệnh. `BENCHMARK_REPORT.md` đã tạo ở đầu CP7, không copy lại template. Trước khi nộp, từ gốc repo copy JSON và CSV ra:

```bash
mkdir -p reports benchmark-results
cp -r 06-lab-complete/benchmark-observability/develop/reports/. reports/
cp -r 06-lab-complete/benchmark-observability/production/benchmark-results/. benchmark-results/
```

## Deadline

- **23h59 (GMT+7) ngày lab.** Lab Coach có thể thông báo deadline khác; thông báo của Lab Coach được ưu tiên.
- Nộp **link repo** trên LMS. Không nộp file zip. Commit cuối trước deadline là bản được chấm (xem [RULES.md](RULES.md)).

## Tự kiểm tra trước khi nộp

- [ ] Tên repo đúng mẫu, repo Public, mở link ở cửa sổ ẩn danh không bị 404.
- [ ] Trong `06-lab-complete/`: `python check_production_ready.py` báo `PASS 12/12` (bản đầy đủ, có Docker).
- [ ] `MISSION_ANSWERS.md` trả lời đủ Part 1–5, có dán output script chấm và mục AI log.
- [ ] `DEPLOYMENT.md` có URL chạy được: `/health` và `/ready` trả 200, `/ask` không có key trả 401, có key trả 200 (4 lệnh ở CP6).
- [ ] `BENCHMARK_REPORT.md` điền đủ; `reports/`, `benchmark-results/` và 7 ảnh trong `screenshots/` có mặt.
- [ ] Số trong `BENCHMARK_REPORT.md` khớp file JSON/CSV.
- [ ] Không có `.env` hay secret trong repo và lịch sử commit (`git log --all --oneline -- '*.env' '.env'` không in gì).
- [ ] Không có email, số điện thoại trong bài.
