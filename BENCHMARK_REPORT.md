# Benchmark & Observability Report — Day 14

> Copy file này thành `BENCHMARK_REPORT.md` trong repo của bạn và điền đầy đủ.
> Mọi con số phải lấy từ report JSON / CSV / screenshot thật, không ước lượng.

**Họ tên:** Phan Văn Cường (`2A202603669`)
**Ngày chạy:** 2026-11-25
**Môi trường:** Windows 11 + WSL2 Ubuntu (Python 3.14.4), Docker Desktop WSL2 backend

---

## 1. SLO của agent

| SLI | SLO | Lý do chọn ngưỡng này |
|---|---|---|
| p95 latency `/ask` | `< 500 ms` | Đảm bảo 95% người dùng nhận phản hồi dưới 0.5 giây (baseline p95 ở tải thấp ~220ms, có dư địa cho tail latency). |
| Error rate `/ask` | `< 2.0 %` | Mock LLM có `MOCK_ERROR_RATE=0.01` (1%), ngưỡng 2% cho phép lỗi upstream ngẫu nhiên nhỏ mà không gây alert giả. |
| Accuracy trên golden dataset | `≥ 80 %` (mục tiêu `100 %` sau khi cập nhật KB) | Ngăn regression chất lượng khi thay đổi prompt/retrieval trước mỗi lần deploy. |

---

## 2. Benchmark hiệu năng (develop, `load_test.py`)

### 2.1 Concurrency vs latency (agent v2)

| Concurrency | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Error rate | SLO |
|---|---|---|---|---|---|---|
| 1 | 4.19 | 191.2 | 220.4 | 1671.4 | 0.33% | ✅ PASS |
| 10 | 35.50 | 189.4 | 221.2 | 1710.1 | 2.00% | ✅ PASS |
| 50 | 109.09 | 196.7 | 304.6 | 1668.3 | 1.00% | ✅ PASS |
| 100 | 58.64 | 437.4 | 3095.2 | 3529.1 | 0.00% | ❌ FAIL (p95 > 500ms) |

**Nhận xét:** RPS có tăng tuyến tính theo concurrency không? Vì sao?

- **Không.** Từ `c=1` đến `c=50`, RPS tăng gần tuyến tính (`4.19 → 35.50 → 109.09 req/s`) vì I/O async còn dư tài nguyên. Nhưng đến `c=100`, RPS **tụt xuống `58.64 req/s`** và p95 vọt lên **`3095.2 ms`** do 1 process `uvicorn` bị bão hòa CPU/event-loop và hàng đợi kết nối (queuing delay).

### 2.2 Tail latency

| `MOCK_SLOW_RATE` | avg (ms) | p95 (ms) | p99 (ms) |
|---|---|---|---|
| 0 | 189.1 | 221.3 | 237.2 |
| 0.03 (mặc định) | 239.7 | 230.1 | 1695.5 |
| 0.1 | 336.9 | 1688.7 | 1718.3 |

**Nhận xét:** Chỉ số nào nhạy nhất với request chậm? Vì sao SLO không nên đặt theo average?

- **p99** (và **p95** khi tỷ lệ chậm vượt 5%, như ở `0.1`) nhạy nhất với request chậm: ở `MOCK_SLOW_RATE=0.03`, `avg` chỉ nhích từ `189.1 ms` lên `239.7 ms` (trông vẫn rất nhanh), nhưng **p99 nhảy vọt từ `237.2 ms` lên `1695.5 ms`**.
- Nếu đặt SLO theo `average`, các request chậm bất thường ở đuôi phân phối (tail latency) bị trung bình hóa và che giấu, khiến 1–5% người dùng thực tế phải chờ gần 2 giây mà hệ thống vẫn báo đạt SLO.

---

## 3. Benchmark chất lượng (develop, `eval/run_eval.py`)

| Chỉ số | Agent v1 | Agent v2 | Agent v2 (sau khi sửa KB) |
|---|---|---|---|
| Accuracy | 4.3% (1/23) | 91.3% (21/23) | 100.0% (23/23) |
| Avg tokens / câu | 56.6 | 108.8 | 115.1 |
| Tổng cost (USD) | $0.000397 | $0.000758 | $0.000803 |
| Cost / câu đúng (USD) | $0.00039735 | $0.00003607 | $0.00003491 |
| Quality gate | FAIL | PASS | PASS (`--min-accuracy 1.0`) |

**Những câu v2 trả lời sai ban đầu và cách bạn sửa:**

| ID | Keyword bị thiếu | Bạn đã sửa gì |
|---|---|---|
| `security-02` | `token`, `hết hạn`, `chữ ký` | Thêm entry `(["jwt", "api key", "xác thực"], ...)` vào `KNOWLEDGE_BASE` trong `develop/utils/mock_llm.py` (và đồng bộ sang `production/utils/mock_llm.py`). |
| `scaling-03` | `cpu`, `memory`, `custom metrics` | Thêm entry `(["hpa", "kubernetes", "autoscal"], ...)` vào `KNOWLEDGE_BASE` trong `develop/utils/mock_llm.py` (và đồng bộ sang `production/utils/mock_llm.py`). |

**Nhận xét về trade-off chất lượng / chi phí / latency giữa v1 và v2:**

- **Chất lượng:** v2 dùng retrieval (RAG) tăng accuracy từ `4.3%` lên `91.3%` (và `100%` sau khi bổ sung KB).
- **Chi phí:** Tổng cost của v2 cao hơn gần gấp đôi v1 (`$0.000758` vs `$0.000397`) vì prompt dài hơn (`108.8` vs `56.6` tokens/câu). Tuy nhiên **cost / câu đúng** của v2 lại **rẻ hơn ~11 lần** (`$0.00003607` vs `$0.00039735`) vì v1 trả lời sai 22/23 câu.
- **Latency:** v2 chậm hơn một chút (`p95 = 214.2 ms` vs `189.8 ms`) do tốn thêm bước retrieval (~20ms), hoàn toàn xứng đáng để đổi lấy độ chính xác 100%.
- **CI Quality Gate (Exercise 7.3):** Trong GitHub Actions/CI, chạy `python eval/run_eval.py --url http://localhost:8002 --min-accuracy 0.8 --baseline reports/eval_v2.json`: nếu accuracy thấp hơn ngưỡng hoặc có câu bị regression so với baseline, script trả về **exit code `1`** để chặn merge PR tự động.

---

## 4. Observability stack (production)

### 4.1 Screenshot

- [x] Dashboard Grafana khi đang có tải (thấy rõ Golden Signals) — [grafana-dashboard.png](screenshots/grafana-dashboard.png)
- [x] Một trace chậm trong Jaeger (thấy span nào chiếm thời gian) — [jaeger-slow-trace.png](screenshots/jaeger-slow-trace.png)
- [x] Một trace lỗi trong Jaeger (có event `exception`) — [jaeger-error-trace.png](screenshots/jaeger-error-trace.png)
- [x] Trang Alerts của Prometheus với ít nhất 1 alert đang **firing** — [prometheus-alert-firing.png](screenshots/prometheus-alert-firing.png)

### 4.2 Thí nghiệm "phá hệ thống"

*(Đã kiểm chứng unit test `alert_rules_test.yml` bằng `promtool`: `SUCCESS`. Các thí nghiệm chạy thực tế trên stack `-p k5-day14-observability` với Locust 30 users)*:

| # | Thay đổi | Alert nào firing | Thời gian từ lúc đổi → firing | Panel nào phản ánh rõ nhất |
|---|---|---|---|---|
| A | `MOCK_ERROR_RATE=0.2` | `AgentHighErrorRate` (`for: 1m`) | ~72 giây | **Error rate** (Golden Signals) & **HTTP req/s theo status (5xx)** |
| B | `MOCK_SLOW_RATE=0.3` | `AgentHighLatencyP95` (`for: 2m`) | ~125 giây (pending ở 11s, firing sau `for: 2m`) | **p95 latency** & **Latency p50/p95/p99** |
| C | `LLM_MODEL=mock-llm-large` | `LLMCostBurnRateHigh` (`for: 2m`, hoặc nhanh hơn nếu có tích lũy trước) | ~6 giây (trong lần test kết hợp) | **Cost USD/giờ** & **LLM p95** |
| D | `docker pause` 1 instance | `AgentInstanceDown` (`for: 30s`, quan sát từ `alert_rules.yml`) | ~30 giây (theo cấu hình `for: 30s`) | **Instances up** |
| E | `AGENT_VERSION=v1` | Không có alert nào firing | N/A | **Retrieval hit ratio** tụt về 0 & **tokens/s** giảm |

**Thí nghiệm E không làm alert nào firing. Bạn sẽ phát hiện loại sự cố này trong production bằng cách nào?**

- Lỗi suy giảm chất lượng trả lời (như đổi nhầm từ `v2` có RAG sang `v1` không có RAG) không làm tăng HTTP 5xx hay latency nên các alert hạ tầng đều vẫn xanh. Để phát hiện sớm trong production cần:
  1. Chạy **Eval + Quality Gate** (`run_eval.py --baseline ...`) tự động trong CI/CD trước khi deploy.
  2. Theo dõi **business/LLM metrics** trên Grafana như `retrieval_hit_ratio`, `tokens_per_request`, hoặc feedback score của người dùng (thumbs up/down) và đặt alert nếu `retrieval_hit_ratio` tụt bất thường.

### 4.3 Debug bằng trace

Chọn 1 trace chậm nhất tìm được từ log & Jaeger:

- `trace_id`: `ad4bf85d6523dbee8c37fdc327799ba7`
- Tổng thời gian: `2018.3 ms`
- Span chiếm nhiều thời gian nhất: `chat mock-llm-large` (`1996.1 ms`, `98.9%`)
- Dòng log tương ứng (grep theo `trace_id`):

```json
{"ts": "2026-11-25T09:54:55.493975+00:00", "level": "INFO", "service": "observable-agent", "instance": "f54056193b6a", "event": "llm_call", "trace_id": "ad4bf85d6523dbee8c37fdc327799ba7", "span_id": "bf6e17715502cb4a", "request_id": "f23ec8d4dcfd", "model": "mock-llm-large", "agent_version": "v2", "input_tokens": 95, "output_tokens": 55, "cost_usd": 0.000788, "llm_ms": 1996.1}
{"ts": "2026-11-25T09:54:55.494132+00:00", "level": "INFO", "service": "observable-agent", "instance": "f54056193b6a", "event": "http_request", "trace_id": "ad4bf85d6523dbee8c37fdc327799ba7", "span_id": "bf6e17715502cb4a", "request_id": "f23ec8d4dcfd", "method": "POST", "route": "/ask", "status": 200, "ms": 2018.3}
```

*(Trace lỗi tham khảo: `trace_id = 231c9605ee487d359054bea004f42aac`, event `llm_error`: `Upstream LLM error: 503 Service Unavailable (mock)`).*

---

## 5. Benchmark scaling (production, Locust headless, 100 users, 2 phút)

*(Số liệu trích từ `benchmark-results/scale_1_stats.csv` và `benchmark-results/scale_3_stats.csv`, dòng `Aggregated`)*:

| Số instance | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Failures |
|---|---|---|---|---|---|
| 1 | 66.09 | 190 | 220 | 1700 | 77 / 7900 (0.97%) |
| 3 | 66.45 | 190 | 220 | 1700 | 70 / 7941 (0.88%) |

**Giải thích kết quả:** Scale có cải thiện p95 không? Nút thắt nằm ở đâu?

- **Không cải thiện đáng kể p95 hay RPS** trong bài test này (`p95` giữ nguyên `220 ms`, RPS `66.09 → 66.45 req/s`).
- **Nguyên nhân (nút thắt):**
  1. Trong `locustfile.py`, mỗi user ảo có `wait_time = between(1, 2)` giây, nên 100 users chỉ tạo ra tối đa ~66 req/s — mức tải này chưa làm bão hòa 1 instance `uvicorn` async.
  2. `p95` (`220 ms`) và `p99` (`1700 ms`) đến từ **thời gian chờ mock LLM** (`MOCK_LATENCY_MS` + `MOCK_SLOW_RATE=0.03`), không phải do CPU/queue của agent; scale từ 1 lên 3 instance không thể làm mỗi lần gọi LLM nhanh hơn.

---

## 6. Kết luận

- 3 điều bạn học được về benchmark & observability:
  1. **p95/p99 quan trọng hơn average:** Chỉ 3% request chậm cũng đủ đẩy `p99` lên gần 1.7s trong khi `avg` chỉ tăng nhẹ (~240ms).
  2. **Chất lượng phải đo bằng Eval + Golden Dataset:** Lỗi giảm chất lượng (như thiếu knowledge base hoặc đổi nhầm model/version `v1`) không làm alert hạ tầng đỏ; cần CI quality gate và `cost / câu đúng` để đánh giá trade-off.
  3. **3 trụ cột Metrics + Traces + Logs bổ trợ cho nhau:** Grafana báo triệu chứng (p95/error tăng) → Jaeger chỉ ra đúng span gây chậm/lỗi (`chat mock-llm-large`) → grep `trace_id` trong JSON logs để xem chi tiết input/cost/lỗi.
- Nếu đưa agent này lên production thật, bạn sẽ thêm metric / alert nào nữa?
  - Thêm metric **`retrieval_hit_ratio`** (và alert nếu tụt dưới ngưỡng), **`rate_limit_rejected_total`** (đếm HTTP 429 để phát hiện tấn công/abuse), **`redis_latency_seconds`**, và alert **`DailyBudgetNearLimit`** khi chi phí vượt 80% ngân sách ngày.
