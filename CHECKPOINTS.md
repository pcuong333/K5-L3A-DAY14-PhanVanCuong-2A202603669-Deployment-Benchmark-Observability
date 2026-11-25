# Checkpoints — Day 14

> 👤 **Cá nhân** · **4 giờ tại lớp** · Deadline: xem [SUBMISSION.md](SUBMISSION.md#deadline).
> Đề từng bài tập xem trong [CODE_LAB.md](CODE_LAB.md). File này chia giờ cho vừa 4 tiếng và nói rõ mỗi mốc phải có gì.

Lộ trình trong `CODE_LAB.md` dài 335 phút (Part 1–7). Để vừa 240 phút, lớp K5 làm khác ba điểm:

1. Rút ngắn Part 1, 2, 4, 5: chạy ví dụ có sẵn và trả lời câu hỏi vào `MISSION_ANSWERS.md`, không tự viết lại code mẫu.
2. Đưa **Part 3 (deploy) ra sau Part 6** và deploy luôn agent Part 6, thay vì deploy app mẫu trong `03-cloud-deployment/` rồi deploy lại lần nữa. Exercise 3.3 (Cloud Run) không cần deploy: chỉ đọc `cloudbuild.yaml` và `service.yaml` rồi viết 3–5 dòng mô tả pipeline (1 điểm, xem [RUBRIC.md](RUBRIC.md#part-3--cloud-deployment-8-điểm)).
3. Làm **Part 7 Bước 1** (chạy local, Exercise 7.1–7.3) tại lớp. **Part 7 Bước 2** (Docker stack Grafana/Jaeger/alerts, Exercise 7.4–7.7) làm sau giờ lab, trước deadline.

| Giờ | Checkpoint | Phần trong `CODE_LAB.md` | Thời gian |
| --- | --- | --- | ---: |
| 0:00 | CP0 · Setup | Fork, đổi tên repo, cài Python + Docker | 10' |
| 0:10 | CP1 · Localhost vs Production | Part 1 (Exercise 1.1–1.3) | 20' |
| 0:30 | CP2 · Docker | Part 2 (Exercise 2.1–2.4) | 30' |
| 1:00 | CP3 · API Security | Part 4 (Exercise 4.1–4.4) | 25' |
| 1:25 | CP4 · Scaling & Reliability | Part 5 (Exercise 5.1–5.5) | 20' |
| 1:45 | Nghỉ | | 5' |
| 1:50 | CP5 · Final Project | Part 6, `06-lab-complete/` → `PASS 12/12` | 60' |
| 2:50 | CP6 · Cloud Deployment | Part 3, deploy agent Part 6 → `DEPLOYMENT.md` | 25' |
| 3:15 | CP7 · Benchmark local | Part 7 Bước 1 (Exercise 7.1–7.3) | 45' |
| Sau lab | CP8 · Observability stack + nộp | Part 7 Bước 2 (Exercise 7.4–7.7), đóng gói | trước deadline |

Kẹt quá 10 phút ở một mốc: gọi Lab Coach, ghi lại lỗi, rồi đi tiếp mốc sau. CP5 là phần nhiều điểm nhất (60/120), không để CP1–CP4 lấn sang giờ của CP5.

## CP0 — Setup (0:00 → 0:10)

- **Mục tiêu:** có repo bài làm đúng tên và máy chạy được Python, Docker.
- **Cần làm:** fork repo, đổi tên theo [SUBMISSION.md](SUBMISSION.md#tên-repository), clone bản fork. Kiểm tra `python --version` (3.11+), `docker compose version`. Đọc mục *Lưu ý khi làm bài* trong [README.md](README.md).
- **Sản phẩm:** repo đã đổi tên, clone về máy.
- **Tự kiểm tra:** `docker run --rm hello-world` chạy được. Không có Docker thì vẫn làm được CP1, CP3, CP7, nhưng CP2, CP5 (phần build image) và CP8 cần Docker: báo Lab Coach ngay.

## CP1 — Localhost vs Production (0:10 → 0:30)

- **Mục tiêu:** chỉ ra được vì sao code chạy trên laptop chưa sẵn sàng cho production.
- **Cần làm:** Part 1, Exercise 1.1–1.3 trong `01-localhost-vs-production/`.
- **Sản phẩm:** mục Part 1 trong `MISSION_ANSWERS.md`: ít nhất 5 anti-pattern, kết quả gọi được bản develop, bảng so sánh develop/production có cột giải thích.
- **Cần hiểu:** vì sao hardcode secret nguy hiểm; vì sao cần health check và graceful shutdown.
- **Tự kiểm tra:** chỉ ra được ít nhất một anti-pattern trong `develop/app.py` mà `production/app.py` đã sửa, kèm dòng code.

## CP2 — Docker (0:30 → 1:00)

- **Mục tiêu:** đóng gói agent thành image nhỏ, chạy giống nhau ở mọi máy.
- **Cần làm:** Part 2, Exercise 2.1–2.4 trong `02-docker/`.
- **Sản phẩm:** mục Part 2 trong `MISSION_ANSWERS.md`: 4 câu trả lời của Exercise 2.1, kết quả gọi container, kích thước image develop và production đo bằng `docker images` kèm % chênh lệch, sơ đồ các service của stack 2.4 và kết quả test qua Nginx.
- **Cần hiểu:** multi-stage giảm dung lượng ở đâu; vì sao `COPY requirements.txt` phải đứng trước `COPY . .`.
- **Tự kiểm tra:** số MB trong bài là số bạn đo được, không chép từ README.

## CP3 — API Security (1:00 → 1:25)

- **Mục tiêu:** chặn được truy cập trái phép, gọi quá nhanh và tiêu quá ngân sách.
- **Cần làm:** Part 4, Exercise 4.1–4.4 trong `04-api-gateway/` (xem mục *Lưu ý khi làm bài* số 6 trong [README.md](README.md)). Exercise 4.2 không phải tự viết JWT, nhưng vẫn phải lấy token, vì vòng lặp 4.3 dùng token đó.
- **Sản phẩm:** mục Part 4 trong `MISSION_ANSWERS.md`, dán output `curl -i` của các trường hợp 401, 200, 429 (che token), và giải thích cách làm cost guard.
- **Cần hiểu:** rate limit bảo vệ tốc độ, cost guard bảo vệ tiền; vì sao cần cả hai.
- **Tự kiểm tra:** thấy được 429 bằng vòng lặp curl của chính mình.

## CP4 — Scaling & Reliability (1:25 → 1:45)

- **Mục tiêu:** chạy được nhiều instance mà không mất state, tắt không cắt ngang request.
- **Cần làm:** Part 5, Exercise 5.1–5.5 trong `05-scaling-reliability/`.
- **Sản phẩm:** mục Part 5 trong `MISSION_ANSWERS.md`.
- **Cần hiểu:** liveness (`/health`) khác readiness (`/ready`) ở đâu; vì sao state trong RAM hỏng khi chạy nhiều instance.
- **Tự kiểm tra:** trong `05-scaling-reliability/production/`, chạy `docker compose -p k5-day14-scaling up -d --build --scale agent=3` (Exercise 5.4), rồi `python test_stateless.py` và giải thích kết quả. Xong thì `docker compose -p k5-day14-scaling down` (xem mục *Lưu ý khi làm bài* số 7 trong [README.md](README.md)).

## CP5 — Final Project (1:50 → 2:50)

- **Mục tiêu:** tự ráp mọi phần trên thành một agent production đạt đủ 12 tiêu chí.
- **Cần làm:** Part 6. Sửa các chỗ `TODO` trong `06-lab-complete/` theo thứ tự gợi ý ở [06-lab-complete/README.md](06-lab-complete/README.md). Làm ngay trong thư mục đó, không chuyển code ra chỗ khác.
- **Sản phẩm:** `python check_production_ready.py` (chạy trong `06-lab-complete/`, có Docker) báo **`PASS 12/12`**. Dán phần "📋 Checklist Deliverable" của output vào `MISSION_ANSWERS.md`.
- **Cần hiểu:** từng tiêu chí trong mục *Script chấm dựa vào những tiêu chí dưới đây* của `06-lab-complete/README.md`, đặc biệt vì sao `/health` phải trả 200 khi Redis chết còn `/ready` phải trả 503.
- **Tự kiểm tra:** chạy `python check_production_ready.py --static-only` sớm và chạy lại sau mỗi bước; chạy bản đầy đủ trước khi sang CP6.

## CP6 — Cloud Deployment (2:50 → 3:15)

- **Mục tiêu:** agent Part 6 chạy trên cloud với URL public, có Redis và API key.
- **Cần làm:** Part 3, Exercise 3.1 (Railway) **hoặc** 3.2 (Render), nhưng deploy thư mục `06-lab-complete/` (dùng `railway.toml` hoặc `render.yaml` bạn viết ở CP5), không deploy app mẫu `03-cloud-deployment/`. Cách làm và phần Redis: mục *Lưu ý khi làm bài* số 8 trong [README.md](README.md). Đặt `AGENT_API_KEY` bằng biến môi trường trên nền tảng, không ghi vào code.
- **Sản phẩm:** `DEPLOYMENT.md` theo mẫu trong [DAY14_DELIVERY_CHECKLIST.md](DAY14_DELIVERY_CHECKLIST.md) mục 3; ảnh trong `screenshots/`; URL điền vào mục Part 3 của `MISSION_ANSWERS.md`, kèm phần so sánh `railway.toml` với `render.yaml` và vài dòng về pipeline Cloud Run (Exercise 3.3) để lấy đủ điểm Part 3 (xem [RUBRIC.md](RUBRIC.md#part-3--cloud-deployment-8-điểm)).
- **Tự kiểm tra:** đặt `BASE` là URL public của agent và `AGENT_API_KEY` là key đã đặt trên nền tảng, rồi chạy 4 lệnh dưới đây. Mỗi lệnh chỉ in mã HTTP, chụp ảnh được mà không lộ key.

  ```bash
  curl -sS -o /dev/null -w '%{http_code}\n' "$BASE/health"     # 200
  curl -sS -o /dev/null -w '%{http_code}\n' "$BASE/ready"      # 200
  curl -sS -o /dev/null -w '%{http_code}\n' -X POST "$BASE/ask" -H 'Content-Type: application/json' -d '{"question":"Hello"}'   # 401
  curl -sS -o /dev/null -w '%{http_code}\n' -X POST "$BASE/ask" -H 'Content-Type: application/json' -H "X-API-Key: $AGENT_API_KEY" -d '{"question":"Hello"}'   # 200
  ```

## CP7 — Benchmark local (3:15 → 4:00)

- **Mục tiêu:** đo được agent nhanh tới đâu và đúng tới đâu bằng số của chính mình.
- **Cần làm:** Part 7 Bước 1 trong `06-lab-complete/benchmark-observability/develop/` (Exercise 7.1–7.3): chạy agent v1 (cổng 8001) và v2 (cổng 8002) như Exercise 7.1, rồi:
  1. Tạo báo cáo **một lần**, từ gốc repo: `cp -n 06-lab-complete/benchmark-observability/BENCHMARK_REPORT_TEMPLATE.md BENCHMARK_REPORT.md` (`-n` để không ghi đè nếu file đã có).
  2. Load test 4 mức concurrency, mỗi mức một file. Các lệnh từ đây chạy trong thư mục `develop/`:

     ```bash
     cd 06-lab-complete/benchmark-observability/develop
     for c in 1 10 50 100; do
       python load_test.py --url http://localhost:8002 --requests 300 --concurrency "$c" --out "reports/load_v2_c${c}.json"
     done
     ```

     Lệnh trả exit code 1 khi vi phạm SLO nhưng vẫn lưu file. So sánh `MOCK_SLOW_RATE`: bật lại v2 lần lượt với `MOCK_SLOW_RATE=0`, `0.03` (mặc định) và `0.1`, mỗi lần chạy cùng `--requests 300 --concurrency 20` và lưu `--out reports/load_v2_slow_0.json`, `--out reports/load_v2_slow_0.03.json`, `--out reports/load_v2_slow_0.1.json` (ba hàng của bảng 2.2 trong mẫu báo cáo).
  3. Eval v1 và v2 bằng hai lệnh ở Exercise 7.3 (lưu `reports/eval_v1.json`, `reports/eval_v2.json`).
  4. Sửa `KNOWLEDGE_BASE`, tắt rồi bật lại v2, chạy eval cuối:

     ```bash
     python eval/run_eval.py --url http://localhost:8002 --min-accuracy 1.0 --baseline reports/eval_v2.json --out reports/eval_v2_fixed.json
     ```
  5. Job CI của Exercise 7.3: nộp file job hoặc giải thích cách dùng exit code của `run_eval.py` để chặn merge.
- **Sản phẩm:** trong `develop/reports/`: `load_v2_c1.json`, `load_v2_c10.json`, `load_v2_c50.json`, `load_v2_c100.json`, ba file `load_v2_slow_*.json`, `eval_v1.json`, `eval_v2.json`, `eval_v2_fixed.json`; `BENCHMARK_REPORT.md` ở gốc repo đã bắt đầu điền.
- **Cần hiểu:** vì sao đặt SLO theo p95/p99 chứ không theo trung bình; vì sao "cost / câu đúng" tốt hơn "cost / câu" để so hai phiên bản.
- **Tự kiểm tra:** lệnh eval cuối ở bước 4 in `Quality gate ... ✅ PASS` và file `reports/eval_v2_fixed.json` có tồn tại.

## CP8 — Observability stack và nộp bài (sau giờ lab, trước deadline)

- **Mục tiêu:** nhìn được sức khoẻ agent khi chạy (metrics, trace, alert) và nộp đủ bằng chứng.
- **Cần làm:** Part 7 Bước 2 trong `06-lab-complete/benchmark-observability/production/` (Exercise 7.4–7.7): bật stack bằng Docker Compose, tạo tải bằng Locust, chụp Grafana, tìm 1 trace chậm và 1 trace lỗi trong Jaeger (chép kèm dòng log JSON có cùng `trace_id`), làm cho ít nhất 2 alert firing và ghi thời gian tới lúc firing. Chụp một ảnh trang Alerts của Prometheus thấy cả 2 alert cùng firing, lưu là `prometheus-alert-firing.png`.
  Benchmark scale phải chạy Locust **headless** để có file CSV (Locust giao diện web không tự ghi CSV), theo mục 2.7 trong `06-lab-complete/benchmark-observability/README.md`. Bật stack ngay từ đầu bằng lệnh có `-p k5-day14-observability` dưới đây, thay cho `docker compose up` trong Exercise 7.4, rồi làm các bài 7.4–7.7 trên stack đó (lý do: mục *Lưu ý khi làm bài* số 7 trong [README.md](README.md)):

  ```bash
  docker compose -p k5-day14-observability up -d --build --scale agent=1
  docker compose -p k5-day14-observability run --rm locust -f /mnt/locust/locustfile.py --host http://nginx \
    --headless -u 100 -r 10 -t 2m --csv /mnt/results/scale_1
  docker compose -p k5-day14-observability up -d --scale agent=3
  docker compose -p k5-day14-observability run --rm locust -f /mnt/locust/locustfile.py --host http://nginx \
    --headless -u 100 -r 10 -t 2m --csv /mnt/results/scale_3
  ```

  Chụp đủ ảnh và chép log **trước** khi dọn stack (`docker compose -p k5-day14-observability down -v`). Dùng cùng `-p` khi xem log (`docker compose -p k5-day14-observability logs agent`).
- **Sản phẩm:** `BENCHMARK_REPORT.md` điền đủ; `production/benchmark-results/scale_1_stats.csv` và `scale_3_stats.csv`; 4 ảnh Part 7 trong `screenshots/`. Đóng gói theo [SUBMISSION.md](SUBMISSION.md).
- **Tự kiểm tra:** mọi con số trong `BENCHMARK_REPORT.md` khớp với file JSON/CSV đã nộp.
