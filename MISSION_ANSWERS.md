# Day 14 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns tìm thấy trong `01-localhost-vs-production/develop/app.py`

1. **Hardcode secrets trong source code (dòng 17–18):**
   - `OPENAI_API_KEY = "sk-hardcoded-fake-key-never-do-this"` và `DATABASE_URL = "postgresql://admin:password123@localhost:5432/mydb"`.
   - Rủi ro: Nếu push lên GitHub (đặc biệt repo public), key và mật khẩu DB bị lộ ngay lập tức và rất khó thu hồi hoàn toàn khỏi git history.
2. **Không có quản lý cấu hình theo môi trường (dòng 21–22):**
   - `DEBUG = True`, `MAX_TOKENS = 500` được gán cứng trong code thay vì đọc từ biến môi trường (`os.getenv` / `pydantic-settings`).
3. **Dùng `print()` để log và in thẳng secret ra stdout (dòng 33–34, 38):**
   - `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")` làm lộ API key trong log và không có cấu trúc JSON/log level để các hệ thống thu thập log (Loki, Datadog...) lọc và cảnh báo.
4. **Không có endpoint health check & readiness check (dòng 42–43):**
   - Không có `/health` và `/ready`. Khi deploy lên cloud hoặc container orchestrator, nền tảng không biết app còn sống hay đã sẵn sàng nhận traffic để restart hoặc route request.
5. **Bind `host="localhost"`, `port=8000` cố định và bật `reload=True` (dòng 49–53):**
   - `host="localhost"` chỉ lắng nghe loopback bên trong container, không nhận được kết nối từ bên ngoài container.
   - `port=8000` cứng không đọc biến `PORT` do Railway/Render tự inject.
   - `reload=True` tốn tài nguyên và không an toàn trong production.
6. **Không xử lý Graceful Shutdown & CORS:**
   - Khi nhận tín hiệu tắt (`SIGTERM`), server ngắt đột ngột các request đang xử lý; đồng thời nhận input qua query param (`question: str`) thay vì JSON body chuẩn.

---

### Exercise 1.2: Kết quả chạy bản `develop`

Lệnh test (truyền `question` qua query string):
```bash
curl -X POST "http://localhost:8000/ask?question=Hello"
```

Kết quả trả về:
```json
{"answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic."}
```

---

### Exercise 1.3: So sánh `develop/app.py` vs `production/app.py`

| Feature | Develop (`develop/app.py`) | Production (`production/app.py`) | Tại sao quan trọng? |
|---|---|---|---|
| **Config & Secrets** | Hardcode `OPENAI_API_KEY`, `DATABASE_URL`, `DEBUG`, `port=8000` trực tiếp trong code (L17–22, L52) | Đọc từ biến môi trường qua `config.settings` (`from config import settings`, `.env` không commit lên git) | Tránh lộ secret trên Git; cùng 1 codebase/image chạy được ở nhiều môi trường (dev/staging/prod) chỉ bằng cách đổi env vars. |
| **Host & Port binding** | `host="localhost"`, `port=8000`, `reload=True` (L51–53) | `host=settings.host` (`0.0.0.0`), `port=settings.port` (đọc `PORT`), `reload=settings.debug` (L196–198) | `0.0.0.0` cho phép nhận traffic từ bên ngoài container; đọc `PORT` để tương thích Railway/Render/Cloud Run. |
| **Health & Readiness** | Không có | `/health` (liveness, L135–149) và `/ready` (readiness trả `503` nếu `is_ready=False`, L152–161) | Cloud platform và Load Balancer dùng `/health` để restart container treo và `/ready` để chỉ route traffic khi app sẵn sàng. |
| **Logging** | `print(...)` và in ra cả `OPENAI_API_KEY` (L33–38) | `logging` định dạng JSON (`{"time":...,"level":...,"msg":...}`), chỉ log `question_length`, `client_ip`, không log secret (L28–31, L111–122) | Bảo mật secret, dễ tìm kiếm/phân tích trên hệ thống tập trung log (Loki, Datadog, CloudWatch). |
| **Shutdown / Lifecycle** | Tắt đột ngột, không cleanup | Dùng `lifespan` (`@asynccontextmanager`, L39–68) đặt `is_ready = False` khi shutdown và bắt `signal.SIGTERM` (L180–189) | Cho phép các request đang chạy hoàn tất trước khi container dừng hẳn (zero-downtime rolling deploy). |
| **API Input & CORS** | Nhận `question` qua query param, không có CORS | Nhận JSON body `{"question": "..."}` (kiểm tra rỗng trả `422`), cấu hình `CORSMiddleware` (L77–82, L102–108) | Chuẩn REST API, bảo vệ trình duyệt bằng danh sách `allowed_origins` cụ thể. |

**Kết quả test bản `production`:**
* `GET /health`:
  ```json
  {"status":"ok","uptime_seconds":1.8,"version":"1.0.0","environment":"development","timestamp":"2026-11-25T07:58:21.249933+00:00"}
  ```
* `GET /ready`:
  ```json
  {"ready":true}
  ```
* `POST /ask` (`{"question":"Hello"}`):
  ```json
  {"question":"Hello","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","model":"gpt-4o-mini"}
  ```
* Log khi gửi `SIGTERM`:
  ```text
  INFO:     Shutting down
  INFO:     Waiting for application shutdown.
  INFO:     Application shutdown complete.
  INFO:     Finished server process [12647]
  ```

---

## Part 2: Docker

### Exercise 2.1: Đọc `02-docker/develop/Dockerfile`

1. **Base image:** `python:3.11` (bản Python đầy đủ ~1 GB trên Debian).
2. **Working directory:** `/app` (`WORKDIR /app`).
3. **Tại sao `COPY 02-docker/develop/requirements.txt .` phải đứng trước `COPY 02-docker/develop/app.py .`?**
   - Vì Docker cache từng layer theo thứ tự từ trên xuống. `requirements.txt` ít thay đổi hơn source code (`app.py`). Đặt `COPY requirements.txt` + `RUN pip install` lên trước giúp Docker tái sử dụng cache khi chỉ sửa code, tránh phải cài lại toàn bộ thư viện mỗi lần build.
4. **`CMD` vs `ENTRYPOINT` khác nhau thế nào?**
   - `CMD` định nghĩa lệnh/tham số mặc định khi container chạy và **có thể bị ghi đè** dễ dàng khi truyền thêm lệnh ở cuối `docker run <image> <cmd>`.
   - `ENTRYPOINT` cố định executable chính của container (khó ghi đè hơn, phải dùng `--entrypoint`), còn `CMD` lúc đó đóng vai trò tham số mặc định truyền vào `ENTRYPOINT`.

### Exercise 2.2: Build và test container `my-agent:develop`

Lệnh build từ gốc repo:
```bash
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .
```

Test gọi container (`develop` nhận `question` qua query):
```bash
curl -sS -X POST "http://localhost:8000/ask?question=What+is+Docker%3F"
```
Kết quả trả về:
```json
{"answer":"Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!"}
```

### Exercise 2.3: Multi-stage build & So sánh kích thước image

- **Stage 1 (`builder` từ `python:3.11-slim`):** Cài build tools (`gcc`, `libpq-dev`) và biên dịch/cài toàn bộ thư viện Python vào `/root/.local` (`pip install --user`). Stage này không dùng để deploy.
- **Stage 2 (`runtime` từ `python:3.11-slim`):** Tạo non-root user `appuser`, chỉ `COPY --from=builder /root/.local /home/appuser/.local` (packages đã cài) và source code (`main.py`, `utils/mock_llm.py`), không mang theo `gcc`, header files hay cache của `apt`/`pip`.
- **Tại sao image nhỏ hơn?** Dùng base `python:3.11-slim` thay cho `python:3.11` đầy đủ, và loại bỏ hoàn toàn compiler (`gcc`, `libpq-dev`) cùng các file tạm của quá trình build khỏi image cuối cùng.

**Kích thước đo thực tế bằng `docker images my-agent`:**

| Image | Size |
|---|---|
| `my-agent:develop` | `1.67GB` (~1670 MB) |
| `my-agent:advanced` | `240MB` |

- **Chênh lệch:** `my-agent:advanced` nhỏ hơn **85.6%** so với `my-agent:develop` (giảm từ `1.67GB` xuống `240MB`, tức nhẹ hơn gần 7 lần).

### Exercise 2.4: Docker Compose stack (`02-docker/production/docker-compose.yml`)

**Kiến trúc các service và cách giao tiếp:**
```text
Client (HTTP :80 / HTTPS :443)
        │
        ▼
   [ nginx ]  (Reverse proxy & Load balancer, network: internal)
        │
        ▼  (proxy tới cổng 8000 nội bộ)
   [ agent ]  (FastAPI app, không expose port ra ngoài host)
     ├──► [ redis ]   (redis://redis:6379/0  — session cache & rate limit, volume: redis_data)
     └──► [ qdrant ]  (http://qdrant:6333    — vector DB cho RAG, volume: qdrant_data)
```
- Tất cả 4 service nằm chung bridge network `internal`, giao tiếp bằng **service name** (`redis`, `qdrant`, `agent`). Chỉ `nginx` mở cổng `80`/`443` ra ngoài host; `agent` chờ `redis` và `qdrant` đạt trạng thái `healthy` mới khởi động (`depends_on: condition: service_healthy`).

**Kết quả test qua Nginx:**
- `curl -sS http://localhost/health`:
  ```json
  {"status":"ok","uptime_seconds":1.5,"version":"2.0.0","timestamp":"2026-11-25T08:19:07.844204"}
  ```
- `curl -sS -X POST http://localhost/ask -H "Content-Type: application/json" -d '{"question":"Explain microservices"}'`:
  ```json
  {"answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}
  ```

---

## Part 3: Cloud Deployment

### Exercise 3.1: Deploy Agent Part 6 (`06-lab-complete/`) lên Railway

- **Public URL:** `https://zucchini-simplicity-production-7b7c1dfb.up.railway.app`
- **Cấu hình trên Railway:**
  - Service Agent trỏ tới repo GitHub với **Root Directory = `06-lab-complete`** (dùng `Dockerfile` và `railway.toml`).
  - Tạo thêm **Redis** database trên Railway và gán biến `REDIS_URL=${{Redis.REDIS_URL}}`, `AGENT_API_KEY` (secret trên dashboard), `ENVIRONMENT=production`, `RATE_LIMIT_PER_MINUTE=10`, `DAILY_BUDGET_USD=1.0`.
- **Kết quả tự kiểm tra 4 lệnh CP6:**
  - `GET /health` → `200` (`{"status":"ok","environment":"production"}`)
  - `GET /ready` → `200` (`{"ready":true}`)
  - `POST /ask` (không có `X-API-Key`) → `401`
  - `POST /ask` (có `X-API-Key`) → `200` (`{"question":"Hello","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}`)
- **Screenshots:** [dashboard.png](screenshots/dashboard.png), [running.png](screenshots/running.png), [test.png](screenshots/test.png) (chi tiết trong [DEPLOYMENT.md](DEPLOYMENT.md)).

### So sánh `railway.toml` vs `render.yaml`

| Tiêu chí | `railway.toml` | `render.yaml` (Blueprint) |
|---|---|---|
| **Định dạng** | TOML (`[build]`, `[deploy]`) | YAML (`services:`, `envVars:`) |
| **Cách build** | `builder = "DOCKERFILE"` | `type: web`, `runtime: docker` |
| **Health check** | `healthcheckPath = "/health"`, `healthcheckTimeout = 30` | `healthCheckPath: /health` |
| **Quản lý env/secret** | Biến môi trường & reference Redis (`${{Redis.REDIS_URL}}`) cấu hình trên Dashboard/CLI | Khai báo trực tiếp trong `envVars` (`generateValue: true` tự sinh secret hoặc `sync: false` nhập trên Dashboard) |
| **Restart policy** | `restartPolicyType = "ON_FAILURE"`, `restartPolicyMaxRetries = 5` | Render tự quản lý health check & auto-restart khi container lỗi |

### Exercise 3.3: Pipeline Google Cloud Run (`03-cloud-deployment/production-cloud-run/`)

- **`cloudbuild.yaml`** định nghĩa pipeline CI/CD 4 bước tuần tự (`waitFor`) trên Cloud Build:
  1. **Step 1 (`test`):** Dùng `python:3.11-slim` cài dependencies và chạy `pytest tests/ -v --tb=short`; chỉ tiếp tục nếu toàn bộ test pass.
  2. **Step 2 (`build`):** Build Docker image gắn tag `$COMMIT_SHA` và `latest` (tận dụng `--cache-from` layer cache).
  3. **Step 3 (`push`):** Push cả hai tag lên Google Container Registry (`gcr.io/$PROJECT_ID/ai-agent`).
  4. **Step 4 (`deploy`):** Chạy `gcloud run deploy ai-agent` lên region `asia-southeast1` với `--min-instances=1` (tránh cold start), `--max-instances=10`, `512Mi` RAM, 1 CPU và lấy secret `OPENAI_API_KEY` từ Secret Manager (`--set-secrets`).
- **`service.yaml`** là file Infrastructure-as-Code (Knative Serving) khai báo chi tiết cấu hình runtime của Cloud Run: autoscale `1–10` instances (concurrency `80` req/instance), `livenessProbe` (`/health`), `startupProbe` (`/ready`) và inject secret qua `secretKeyRef`.

---

## Part 4: API Security

### Exercise 4.1: API Key Authentication (`04-api-gateway/develop/`)

Khởi động bản `develop` với `AGENT_API_KEY=secret-key-123 python app.py`:

- **Không có key (`401 Unauthorized`):**
  ```text
  HTTP/1.1 401 Unauthorized
  date: Wed, 25 Nov 2026 08:23:50 GMT
  server: uvicorn
  content-length: 67
  content-type: application/json

  {"detail":"Missing API key. Include header: X-API-Key: <your-key>"}
  ```
- **Có header `X-API-Key: secret-key-123` (`200 OK`):**
  ```text
  HTTP/1.1 200 OK
  date: Wed, 25 Nov 2026 08:23:50 GMT
  server: uvicorn
  content-length: 114
  content-type: application/json

  {"question":"hello","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."}
  ```

### Exercise 4.2 & 4.3: JWT Auth & Rate Limiting (`04-api-gateway/production/`)

Lấy JWT token qua `POST /auth/token` với tài khoản `student` / `demo123` (giới hạn 10 request/phút; token đã được che `eyJhbGciOiJI...or49z4`):

- **Không gửi Bearer token (`401 Unauthorized`):**
  ```text
  HTTP/1.1 401 Unauthorized
  date: Wed, 25 Nov 2026 08:23:53 GMT
  server: uvicorn
  www-authenticate: Bearer
  content-length: 76
  content-type: application/json
  x-content-type-options: nosniff
  x-frame-options: DENY
  x-xss-protection: 1; mode=block
  referrer-policy: strict-origin-when-cross-origin

  {"detail":"Authentication required. Include: Authorization: Bearer <token>"}
  ```
- **Vòng lặp 12 request liên tiếp bằng Bearer token:**
  - **Request 1 (`200 OK`):**
    ```text
    HTTP/1.1 200 OK
    date: Wed, 25 Nov 2026 08:23:53 GMT
    server: uvicorn
    content-length: 209
    content-type: application/json
    x-content-type-options: nosniff
    x-frame-options: DENY
    x-xss-protection: 1; mode=block
    referrer-policy: strict-origin-when-cross-origin

    {"question":"hello","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":9,"budget_remaining_usd":2.1e-05}}
    ```
  - **Request 2 → 10:** `HTTP 200`
  - **Request 11 (`429 Too Many Requests`):**
    ```text
    HTTP/1.1 429 Too Many Requests
    date: Wed, 25 Nov 2026 08:23:54 GMT
    server: uvicorn
    x-ratelimit-limit: 10
    x-ratelimit-remaining: 0
    x-ratelimit-reset: 1795595095
    retry-after: 59
    content-length: 98
    content-type: application/json
    x-content-type-options: nosniff
    x-frame-options: DENY
    x-xss-protection: 1; mode=block
    referrer-policy: strict-origin-when-cross-origin

    {"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
    ```
  - **Request 12:** `HTTP 429`

### Exercise 4.4: Cost Guard (`04-api-gateway/production/cost_guard.py`) & Vì sao cần cả Rate Limit lẫn Cost Guard

- **Cách triển khai Cost Guard trong code:**
  - `CostGuard` theo dõi `input_tokens`, `output_tokens` và `request_count` theo từng `user_id` và theo ngày (`UsageRecord`), tính chi phí dựa trên đơn giá token (`PRICE_PER_1K_INPUT_TOKENS = 0.00015`, `PRICE_PER_1K_OUTPUT_TOKENS = 0.0006`).
  - Trước khi gọi LLM, `check_budget(user_id)` kiểm tra 2 ngưỡng: ngân sách toàn hệ thống (`global_daily_budget_usd = $10.0/ngày`, vượt thì trả `503`) và ngân sách từng user (`daily_budget_usd = $1.0/ngày`, vượt thì trả `402 Payment Required`), đồng thời log cảnh báo khi đạt `80%` (`warn_at_pct = 0.8`).
  - Sau khi LLM trả lời, `record_usage(user_id, input_tokens, output_tokens)` cộng dồn token và chi phí. Trong production (nhiều instance), state này phải lưu trên Redis/DB thay vì in-memory dict.
- **Vì sao cần cả Rate Limit và Cost Guard?**
  - **Rate limit** bảo vệ **tốc độ & tài nguyên server** (ngăn spam/DDoS, giới hạn số request/phút bằng thuật toán Sliding Window).
  - **Cost guard** bảo vệ **ngân sách tiền API LLM** (chỉ 1–2 request có prompt/response cực dài vẫn lọt qua rate limit nhưng có thể đốt rất nhiều token). Kết hợp cả hai giúp hệ thống vừa không bị quá tải vừa không bị "cháy ví".

---

## Part 5: Scaling & Reliability

### Exercise 5.1–5.2: Liveness (`/health`), Readiness (`/ready`) & Graceful Shutdown (`05-scaling-reliability/develop/app.py`)

- **Phân biệt Liveness (`/health`) và Readiness (`/ready`):**
  - **Liveness (`GET /health`):** Trả lời câu hỏi *"Agent có còn sống không?"* (`status`, `uptime_seconds`, `version`). Platform dùng endpoint này để biết process có bị treo/crash hay không; nếu trả non-200 hoặc timeout thì platform **restart container**.
  - **Readiness (`GET /ready`):** Trả lời câu hỏi *"Agent đã sẵn sàng nhận traffic chưa?"* (kiểm tra `_is_ready` và dependency như Redis). Nếu trả `503` (ví dụ lúc mới khởi động hoặc đang shutdown), Load Balancer sẽ **tạm ngừng route request** vào instance đó nhưng **không restart** container.
- **Kết quả test bản `develop`:**
  - `GET /health`:
    ```json
    {"status":"ok","uptime_seconds":1.8,"version":"1.0.0","environment":"development","timestamp":"2026-11-25T08:29:14.621716+00:00","checks":{"memory":{"status":"ok","note":"psutil not installed"}}}
    ```
  - `GET /ready`:
    ```json
    {"ready":true,"in_flight_requests":1}
    ```
  - **Graceful shutdown:** Khi nhận `SIGTERM`, `lifespan` đặt `_is_ready = False` để `/ready` trả `503` (ngừng nhận request mới) và chờ `_in_flight_requests` về `0` (tối đa 30s) trước khi tắt hẳn, tránh cắt ngang request đang xử lý.

### Exercise 5.3–5.5: Stateless Scaling với 3 Instances + Redis + Nginx (`05-scaling-reliability/production/`)

- **Vì sao state lưu trong RAM hỏng khi chạy nhiều instance?**
  - Khi scale lên 3 instance sau Nginx Load Balancer, request 1 có thể vào `instance-A` (lưu lịch sử chat vào RAM của A), nhưng request 2 lại được route sang `instance-B` — RAM của B không có session đó, dẫn đến mất ngữ cảnh/lỗi session.
  - Giải pháp: thiết kế **stateless**, đẩy toàn bộ session history và rate-limit/cost state ra **Redis** dùng chung (`REDIS_URL=redis://redis:6379/0`).

- **Kết quả chạy `docker compose -p k5-day14-scaling up -d --build --scale agent=3` và `python test_stateless.py` (cổng `8080`, endpoint `POST /chat`):**
  ```text
  ============================================================
  Stateless Scaling Demo
  ============================================================

  Session ID: cdc6d117-0e96-41dd-bd27-17403a72533e

  Request 1: [instance-58ce25]
    Q: What is Docker?
    A: Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!...

  Request 2: [instance-075f00]
    Q: Why do we need containers?
    A: Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận....

  Request 3: [instance-58ce25]
    Q: What is Kubernetes?
    A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

  Request 4: [instance-a23b3a]
    Q: How does load balancing work?
    A: Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ O...

  Request 5: [instance-075f00]
    Q: What is Redis used for?
    A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

  ------------------------------------------------------------
  Total requests: 5
  Instances used: {'instance-075f00', 'instance-58ce25', 'instance-a23b3a'}
  ✅ All requests served despite different instances!

  --- Conversation History ---
  Total messages: 10
    [user]: What is Docker?...
    [assistant]: Container là cách đóng gói app để chạy ở mọi nơi. Build once...
    [user]: Why do we need containers?...
    [assistant]: Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã đư...
    [user]: What is Kubernetes?...
    [assistant]: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đ...
    [user]: How does load balancing work?...
    [assistant]: Đây là câu trả lời từ AI agent (mock). Trong production, đây...
    [user]: What is Redis used for?...
    [assistant]: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đ...

  ✅ Session history preserved across all instances via Redis!
  ```
- **Giải thích kết quả:** 5 request trong cùng 1 `Session ID` (`cdc6d117-0e96-41dd-bd27-17403a72533e`) được Nginx chia đều qua cả 3 instance (`instance-58ce25`, `instance-075f00`, `instance-a23b3a`), nhưng khi đọc lại `/chat/{session_id}/history` vẫn giữ đủ toàn bộ 10 message (5 user + 5 assistant) nhờ lưu tập trung trong Redis.

---

## Part 6: Final Project (`06-lab-complete/`)

Kết quả chạy `python check_production_ready.py` (chế độ đầy đủ, có Docker):

```text
================================================================
  📋 Checklist Deliverable
     ✅ Dockerfile (multi-stage, < 500 MB)
     ✅ docker-compose.yml (agent + redis)
     ✅ .dockerignore
     ✅ Health check endpoint (GET /health)
     ✅ Readiness endpoint (GET /ready)
     ✅ API Key authentication
     ✅ Rate limiting
     ✅ Cost guard
     ✅ Config từ environment variables
     ✅ Structured logging
     ✅ Graceful shutdown
     ✅ Public URL ready (Railway / Render config)
----------------------------------------------------------------
  Result: 12/12 tiêu chí đạt · 43/43 checks passed
  🎉 PASS 12/12 — PRODUCTION READY! Deploy nào!
================================================================
```

- Kích thước Docker image thực tế: **368 MB** (< 500 MB, multi-stage `python:3.11-slim`, non-root `appuser`).
- Thời gian `docker stop` graceful shutdown: **0.8s** (exit code `0`).

---

## AI log

* **Part 1 (CP1):**
  * **Hỏi gì:** Nhờ hỗ trợ kiểm tra môi trường WSL2/Docker (CP0) và chạy thử, đối chiếu hai file `01-localhost-vs-production/develop/app.py` và `production/app.py` để hoàn thiện Part 1.
  * **Nhận gì:** Chạy kiểm tra thực tế trên WSL2 (`Python 3.14.4`, `posix`, `Docker 29.9.3`), bật WSL Integration cho Ubuntu, chạy cả hai bản `develop` và `production` để lấy output `curl` và log shutdown, tổng hợp bảng so sánh vào `MISSION_ANSWERS.md`.
  * **Tự sửa & tự kiểm tra:** Đã đối chiếu lại từng dòng code (`L17–54` ở `develop/app.py`, `L28–199` ở `production/app.py`) và kiểm tra output thực tế từ các lệnh `curl` trên máy.
* **Part 2 (CP2):**
  * **Hỏi gì:** Nhờ hỗ trợ chạy build `my-agent:develop` và `my-agent:advanced`, test container, chạy Docker Compose stack và tổng hợp kết quả Part 2.
  * **Nhận gì:** Build 2 image từ gốc repo, đo kích thước thực tế (`1.67GB` vs `240MB`), tạo `.env.local`, test stack qua Nginx (`/health`, `/ask`) rồi `down -v` dọn dẹp, ghi câu trả lời vào `MISSION_ANSWERS.md`.
  * **Tự sửa & tự kiểm tra:** Đã đối chiếu lại `02-docker/develop/Dockerfile`, `02-docker/production/Dockerfile`, `docker-compose.yml` và số đo thực tế từ `docker images`.
* **Part 4 (CP3):**
  * **Hỏi gì:** Nhờ hỗ trợ chạy test API Key (`develop`), JWT + Rate Limiting (`production`), vòng lặp curl để lấy 401/200/429 và giải thích Cost Guard.
  * **Nhận gì:** Chạy cả hai bản trên WSL2, lấy token `student`/`demo123` tại `POST /auth/token`, chạy vòng lặp 12 request thấy rõ request 1–10 trả `200` và request 11–12 trả `429`, che token và ghi kết quả vào `MISSION_ANSWERS.md`.
  * **Tự sửa & tự kiểm tra:** Đã đối chiếu `04-api-gateway/production/cost_guard.py` và `rate_limiter.py` với output `curl -i` thực tế.
* **Part 5 (CP4):**
  * **Hỏi gì:** Nhờ hỗ trợ chạy kiểm tra bản `develop` (`/health`, `/ready`, `SIGTERM`) và chạy stack 3 instance `05-scaling-reliability/production/` với `test_stateless.py`.
  * **Nhận gì:** Bật stack bằng `docker compose -p k5-day14-scaling up -d --build --scale agent=3`, chạy `python test_stateless.py` thấy cả 3 instance cùng xử lý 5 request nhưng vẫn giữ đủ 10 message qua Redis, sau đó `down -v` dọn dẹp và ghi kết quả vào `MISSION_ANSWERS.md`.
  * **Tự sửa & tự kiểm tra:** Đã kiểm tra `05-scaling-reliability/develop/app.py`, `docker-compose.yml` và `test_stateless.py` khớp với output thực tế.
* **Part 6 (CP5):**
  * **Hỏi gì:** Nhờ hỗ trợ hoàn thiện các file TODO trong `06-lab-complete/` (`app/main.py`, `config.py`, `auth.py`, `redis_client.py`, `rate_limiter.py`, `cost_guard.py`, `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.env.example`, `railway.toml`, `render.yaml`) và chạy `check_production_ready.py`.
  * **Nhận gì:** Lần 1 đạt `10/12` (lỗi `pip install --user` khi chạy non-root trong container), sửa `Dockerfile` sang `/opt/venv` và chạy lại đạt `PASS 12/12` (`43/43 checks passed`, image `368 MB`, `docker stop` `0.8s`).
  * **Tự sửa & tự kiểm tra:** Đã kiểm tra toàn bộ 12 tiêu chí và dán phần Checklist Deliverable vào `MISSION_ANSWERS.md`, không chỉnh sửa `check_production_ready.py`.
* **Part 3 (CP6):**
  * **Hỏi gì:** Nhờ hướng dẫn deploy `06-lab-complete/` lên Railway kèm Redis, chạy kiểm tra 4 endpoint public và hoàn thiện `DEPLOYMENT.md` + Part 3 (bao gồm so sánh `railway.toml`/`render.yaml` và Exercise 3.3 Cloud Run).
  * **Nhận gì:** Deploy lên `https://zucchini-simplicity-production-7b7c1dfb.up.railway.app`, kiểm tra `/health` (`200`), `/ready` (`200`), `/ask` không key (`401`), `/ask` có key (`200`), đọc `03-cloud-deployment/production-cloud-run/cloudbuild.yaml` & `service.yaml` để tổng hợp vào `MISSION_ANSWERS.md` và `DEPLOYMENT.md`.
  * **Tự sửa & tự kiểm tra:** Tự thao tác cấu hình service, Redis và biến môi trường trên Railway Dashboard, tự test lại 4 lệnh `curl` và chụp 3 ảnh lưu vào `screenshots/`.

