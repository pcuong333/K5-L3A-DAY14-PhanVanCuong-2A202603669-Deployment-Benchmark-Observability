#  Code Lab: Deploy Your AI Agent to Production

> **AICB-P1 · VinUniversity 2026**  
> Thời gian: 4-5 giờ | Độ khó: Intermediate

##  Mục Tiêu

Sau khi hoàn thành lab này, bạn sẽ:
- Hiểu sự khác biệt giữa development và production
- Containerize một AI agent với Docker
- Deploy agent lên cloud platform
- Bảo mật API với authentication và rate limiting
- Thiết kế hệ thống có khả năng scale và reliable
- Benchmark hiệu năng & chất lượng agent, giám sát bằng metrics, traces và alerts

---

##  Yêu Cầu

```bash
 Python 3.11+
 Docker & Docker Compose
 Git
 Text editor (VS Code khuyến nghị)
 Terminal/Command line
```

**Không cần:**
-  OpenAI API key (dùng mock LLM)
-  Credit card
-  Kinh nghiệm DevOps trước đó

---

##  Lộ Trình Lab

| Phần | Thời gian | Nội dung |
|------|-----------|----------|
| **Part 1** | 30 phút | Localhost vs Production |
| **Part 2** | 45 phút | Docker Containerization |
| **Part 3** | 45 phút | Cloud Deployment |
| **Part 4** | 40 phút | API Security |
| **Part 5** | 40 phút | Scaling & Reliability |
| **Part 6** | 60 phút | Final Project |
| **Part 7** | 75 phút | Benchmark & Observability |

---

## Part 1: Localhost vs Production (30 phút)

###  Concepts

**Vấn đề:** "It works on my machine" — code chạy tốt trên laptop nhưng fail khi deploy.

**Nguyên nhân:**
- Hardcoded secrets
- Khác biệt về environment (Python version, OS, dependencies)
- Không có health checks
- Config không linh hoạt

**Giải pháp:** 12-Factor App principles

###  Exercise 1.1: Phát hiện anti-patterns

```bash
cd 01-localhost-vs-production/develop
```

**Nhiệm vụ:** Đọc `app.py` và tìm ít nhất 5 vấn đề.

<details>
<summary> Gợi ý</summary>

Tìm:
- API key hardcode
- Port cố định
- Debug mode
- Không có health check
- Không xử lý shutdown

</details>

###  Exercise 1.2: Chạy basic version

```bash
pip install -r requirements.txt
python app.py
```

Test:
```bash
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

**Quan sát:** Nó chạy! Nhưng có production-ready không?

###  Exercise 1.3: So sánh với advanced version

```bash
cd ../production
cp .env.example .env
pip install -r requirements.txt
python app.py
```

**Nhiệm vụ:** So sánh 2 files `app.py`. Điền vào bảng:

| Feature | Basic | Advanced | Tại sao quan trọng? |
|---------|-------|----------|---------------------|
| Config | Hardcode | Env vars | ... |
| Health check |  |  | ... |
| Logging | print() | JSON | ... |
| Shutdown | Đột ngột | Graceful | ... |

###  Checkpoint 1

- [ ] Hiểu tại sao hardcode secrets là nguy hiểm
- [ ] Biết cách dùng environment variables
- [ ] Hiểu vai trò của health check endpoint
- [ ] Biết graceful shutdown là gì

---

## Part 2: Docker Containerization (45 phút)

###  Concepts

**Vấn đề:** "Works on my machine" part 2 — Python version khác, dependencies conflict.

**Giải pháp:** Docker — đóng gói app + dependencies vào container.

**Benefits:**
- Consistent environment
- Dễ deploy
- Isolation
- Reproducible builds

###  Exercise 2.1: Dockerfile cơ bản

```bash
cd ../../02-docker/develop
```

**Nhiệm vụ:** Đọc `Dockerfile` và trả lời:

1. Base image là gì?
2. Working directory là gì?
3. Tại sao COPY requirements.txt trước?
4. CMD vs ENTRYPOINT khác nhau thế nào?

###  Exercise 2.2: Build và run

```bash
# Build image
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .

# Run container
docker run -p 8000:8000 my-agent:develop

# Test
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
```

**Quan sát:** Image size là bao nhiêu?
```bash
docker images my-agent:develop
```

###  Exercise 2.3: Multi-stage build

```bash
cd ../production
```

**Nhiệm vụ:** Đọc `Dockerfile` và tìm:
- Stage 1 làm gì?
- Stage 2 làm gì?
- Tại sao image nhỏ hơn?

Build và so sánh:
```bash
docker build -t my-agent:advanced .
docker images | grep my-agent
```

###  Exercise 2.4: Docker Compose stack

**Nhiệm vụ:** Đọc `docker-compose.yml` và vẽ architecture diagram.

```bash
docker compose up
```

Services nào được start? Chúng communicate thế nào?

Test:
```bash
# Health check
curl http://localhost/health

# Agent endpoint
curl http://localhost/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain microservices"}'
```

###  Checkpoint 2

- [ ] Hiểu cấu trúc Dockerfile
- [ ] Biết lợi ích của multi-stage builds
- [ ] Hiểu Docker Compose orchestration
- [ ] Biết cách debug container (`docker logs`, `docker exec`)

---

## Part 3: Cloud Deployment (45 phút)

###  Concepts

**Vấn đề:** Laptop không thể chạy 24/7, không có public IP.

**Giải pháp:** Cloud platforms — Railway, Render, GCP Cloud Run.

**So sánh:**

| Platform | Độ khó | Free tier | Best for |
|----------|--------|-----------|----------|
| Railway | ⭐ | $5 credit | Prototypes |
| Render | ⭐⭐ | 750h/month | Side projects |
| Cloud Run | ⭐⭐⭐ | 2M requests | Production |

###  Exercise 3.1: Deploy Railway (15 phút)

```bash
cd ../../03-cloud-deployment/railway
```

**Steps:**

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login:
```bash
railway login
```

3. Initialize project:
```bash
railway init
```

4. Set environment variables:
```bash
railway variables set PORT=8000
railway variables set AGENT_API_KEY=my-secret-key
```

5. Deploy:
```bash
railway up
```

6. Get public URL:
```bash
railway domain
```

**Nhiệm vụ:** Test public URL với curl hoặc Postman.

Test:
```bash
# Health check
curl http://student-agent-domain/health

# Agent endpoint
curl http://studen-agent-domain/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": ""}'
```

###  Exercise 3.2: Deploy Render (15 phút)

```bash
cd ../render
```

**Steps:**

1. Push code lên GitHub (nếu chưa có)
2. Vào [render.com](https://render.com) → Sign up
3. New → Blueprint
4. Connect GitHub repo
5. Render tự động đọc `render.yaml`
6. Set environment variables trong dashboard
7. Deploy!

**Nhiệm vụ:** So sánh `render.yaml` với `railway.toml`. Khác nhau gì?

###  Exercise 3.3: (Optional) GCP Cloud Run (15 phút)

```bash
cd ../production-cloud-run
```

**Yêu cầu:** GCP account (có free tier).

**Nhiệm vụ:** Đọc `cloudbuild.yaml` và `service.yaml`. Hiểu CI/CD pipeline.

###  Checkpoint 3

- [ ] Deploy thành công lên ít nhất 1 platform
- [ ] Có public URL hoạt động
- [ ] Hiểu cách set environment variables trên cloud
- [ ] Biết cách xem logs

---

## Part 4: API Security (40 phút)

###  Concepts

**Vấn đề:** Public URL = ai cũng gọi được = hết tiền OpenAI.

**Giải pháp:**
1. **Authentication** — Chỉ user hợp lệ mới gọi được
2. **Rate Limiting** — Giới hạn số request/phút
3. **Cost Guard** — Dừng khi vượt budget

###  Exercise 4.1: API Key authentication

```bash
cd ../../04-api-gateway/develop
```

**Nhiệm vụ:** Đọc `app.py` và tìm:
- API key được check ở đâu?
- Điều gì xảy ra nếu sai key?
- Làm sao rotate key?

Test:
```bash
python app.py

#  Không có key
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

#  Có key
curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

###  Exercise 4.2: JWT authentication (Advanced)

```bash
cd ../production
```

**Nhiệm vụ:** 
1. Đọc `auth.py` — hiểu JWT flow
2. Lấy token:
```bash
python app.py

curl http://localhost:8000/token -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}'
```

3. Dùng token để gọi API:
```bash
TOKEN="<token_từ_bước_2>"
curl http://localhost:8000/ask -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain JWT"}'
```

###  Exercise 4.3: Rate limiting

**Nhiệm vụ:** Đọc `rate_limiter.py` và trả lời:
- Algorithm nào được dùng? (Token bucket? Sliding window?)
- Limit là bao nhiêu requests/minute?
- Làm sao bypass limit cho admin?

Test:
```bash
# Gọi liên tục 20 lần
for i in {1..20}; do
  curl http://localhost:8000/ask -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}'
  echo ""
done
```

Quan sát response khi hit limit.

###  Exercise 4.4: Cost guard

**Nhiệm vụ:** Đọc `cost_guard.py` và implement logic:

```python
def check_budget(user_id: str, estimated_cost: float) -> bool:
    """
    Return True nếu còn budget, False nếu vượt.
    
    Logic:
    - Mỗi user có budget $10/tháng
    - Track spending trong Redis
    - Reset đầu tháng
    """
    # TODO: Implement
    pass
```

<details>
<summary> Solution</summary>

```python
import redis
from datetime import datetime

r = redis.Redis()

def check_budget(user_id: str, estimated_cost: float) -> bool:
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current = float(r.get(key) or 0)
    if current + estimated_cost > 10:
        return False
    
    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)  # 32 days
    return True
```

</details>

###  Checkpoint 4

- [ ] Implement API key authentication
- [ ] Hiểu JWT flow
- [ ] Implement rate limiting
- [ ] Implement cost guard với Redis

---

## Part 5: Scaling & Reliability (40 phút)

###  Concepts

**Vấn đề:** 1 instance không đủ khi có nhiều users.

**Giải pháp:**
1. **Stateless design** — Không lưu state trong memory
2. **Health checks** — Platform biết khi nào restart
3. **Graceful shutdown** — Hoàn thành requests trước khi tắt
4. **Load balancing** — Phân tán traffic

###  Exercise 5.1: Health checks

```bash
cd ../../05-scaling-reliability/develop
```

**Nhiệm vụ:** Implement 2 endpoints:

```python
@app.get("/health")
def health():
    """Liveness probe — container còn sống không?"""
    # TODO: Return 200 nếu process OK
    pass

@app.get("/ready")
def ready():
    """Readiness probe — sẵn sàng nhận traffic không?"""
    # TODO: Check database connection, Redis, etc.
    # Return 200 nếu OK, 503 nếu chưa ready
    pass
```

<details>
<summary> Solution</summary>

```python
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    try:
        # Check Redis
        r.ping()
        # Check database
        db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready"}
        )
```

</details>

###  Exercise 5.2: Graceful shutdown

**Nhiệm vụ:** Implement signal handler:

```python
import signal
import sys

def shutdown_handler(signum, frame):
    """Handle SIGTERM from container orchestrator"""
    # TODO:
    # 1. Stop accepting new requests
    # 2. Finish current requests
    # 3. Close connections
    # 4. Exit
    pass

signal.signal(signal.SIGTERM, shutdown_handler)
```

Test:
```bash
python app.py &
PID=$!

# Gửi request
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Long task"}' &

# Ngay lập tức kill
kill -TERM $PID

# Quan sát: Request có hoàn thành không?
```

###  Exercise 5.3: Stateless design

```bash
cd ../production
```

**Nhiệm vụ:** Refactor code để stateless.

**Anti-pattern:**
```python
#  State trong memory
conversation_history = {}

@app.post("/ask")
def ask(user_id: str, question: str):
    history = conversation_history.get(user_id, [])
    # ...
```

**Correct:**
```python
#  State trong Redis
@app.post("/ask")
def ask(user_id: str, question: str):
    history = r.lrange(f"history:{user_id}", 0, -1)
    # ...
```

Tại sao? Vì khi scale ra nhiều instances, mỗi instance có memory riêng.

###  Exercise 5.4: Load balancing

**Nhiệm vụ:** Chạy stack với Nginx load balancer:

```bash
docker compose up --scale agent=3
```

Quan sát:
- 3 agent instances được start
- Nginx phân tán requests
- Nếu 1 instance die, traffic chuyển sang instances khác

Test:
```bash
# Gọi 10 requests
for i in {1..10}; do
  curl http://localhost/ask -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "Request '$i'"}'
done

# Check logs — requests được phân tán
docker compose logs agent
```

###  Exercise 5.5: Test stateless

```bash
python test_stateless.py
```

Script này:
1. Gọi API để tạo conversation
2. Kill random instance
3. Gọi tiếp — conversation vẫn còn không?

###  Checkpoint 5

- [ ] Implement health và readiness checks
- [ ] Implement graceful shutdown
- [ ] Refactor code thành stateless
- [ ] Hiểu load balancing với Nginx
- [ ] Test stateless design

---

## Part 6: Final Project (60 phút)

###  Objective

Tự xây một production-ready AI agent từ **bản khung** trong `06-lab-complete/` (mọi file đã có sẵn, phần việc nằm ở các chỗ `TODO`), kết hợp TẤT CẢ concepts đã học. Bài hoàn thành khi `python check_production_ready.py` báo **PASS 12/12**.

###  Requirements

**Bắt buộc — 12 tiêu chí được script chấm tự động:**
- [ ] Dockerfile (multi-stage, < 500 MB)
- [ ] docker-compose.yml (agent + redis)
- [ ] .dockerignore
- [ ] Health check endpoint (`GET /health`)
- [ ] Readiness endpoint (`GET /ready`)
- [ ] API Key authentication
- [ ] Rate limiting
- [ ] Cost guard
- [ ] Config từ environment variables
- [ ] Structured logging
- [ ] Graceful shutdown
- [ ] Public URL ready (Railway / Render config)

Quy ước chi tiết mà script chấm dựa vào (endpoint, header, mã lỗi, biến môi trường...) nằm ở mục **Hợp đồng** trong [06-lab-complete/README.md](06-lab-complete/README.md).

**Mở rộng (không chấm tự động, khuyến khích làm thêm):**
- [ ] Lưu conversation history trong Redis
- [ ] Streaming responses
- [ ] Nginx load balancer + scale 3 instance (như sơ đồ dưới)

### 🏗 Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Nginx (LB)     │
└──────┬──────────┘
       │
       ├─────────┬─────────┐
       ▼         ▼         ▼
   ┌──────┐  ┌──────┐  ┌──────┐
   │Agent1│  │Agent2│  │Agent3│
   └───┬──┘  └───┬──┘  └───┬──┘
       │         │         │
       └─────────┴─────────┘
                 │
                 ▼
           ┌──────────┐
           │  Redis   │
           └──────────┘
```

###  Step-by-step

#### Step 1: Mở bản khung (5 phút)

```bash
cd 06-lab-complete
pip install -r requirements.txt
python check_production_ready.py --static-only   # xem các tiêu chí đang ❌ ở đâu
```

Muốn làm trong repo riêng để nộp bài: copy cả thư mục `06-lab-complete/` sang repo của bạn, giữ nguyên `check_production_ready.py`.

#### Step 2: Config từ environment (5 phút)

**File:** `app/config.py`

```python
import os
from dataclasses import dataclass, field

@dataclass
class Settings:
    agent_api_key: str = field(default_factory=lambda: os.getenv("AGENT_API_KEY", ""))
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    # TODO: PORT, ENVIRONMENT, RATE_LIMIT_PER_MINUTE (int), DAILY_BUDGET_USD (float)

settings = Settings()
```

Đồng thời liệt kê đủ các biến trong `.env.example` (không ghi secret thật).

#### Step 3: Health, readiness và log JSON (10 phút)

**File:** `app/main.py`, `app/redis_client.py`

```python
@app.get("/health")
def health():
    # TODO: luôn trả 200 khi process còn chạy (không phụ thuộc Redis)
    ...

@app.get("/ready")
def ready():
    # TODO: Redis không kết nối được → raise HTTPException(503)
    ...
```

Mỗi dòng log phải là 1 JSON object hợp lệ. Tự viết formatter:

```python
class JsonFormatter(logging.Formatter):
    def format(self, record):
        # TODO: return json.dumps({...}) gồm thời gian, level, message và các field khác
        ...
```

#### Step 4: Authentication (5 phút)

**File:** `app/auth.py`

```python
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    # TODO: thiếu hoặc khác settings.agent_api_key → raise HTTPException(401)
    ...
```

> Dùng `auto_error=False` rồi tự trả 401. Nếu khai báo header là bắt buộc (`Header(...)`), FastAPI trả **422** khi thiếu header và không đạt tiêu chí.

#### Step 5: Rate limiting với Redis (10 phút)

**File:** `app/rate_limiter.py`

```python
def check_rate_limit(key: str) -> None:
    # TODO: sliding window 60 giây bằng Redis sorted set:
    #   ZREMRANGEBYSCORE (xoá request cũ) → ZCARD (đếm)
    #   → vượt RATE_LIMIT_PER_MINUTE: raise HTTPException(429, headers={"Retry-After": "60"})
    #   → ZADD + EXPIRE
    ...
```

> Phải lưu trong Redis, không lưu dict trong memory: Dockerfile chạy 2 worker, và script chấm sẽ restart agent để kiểm tra state còn không.

#### Step 6: Cost guard (5 phút)

**File:** `app/cost_guard.py`

```python
def check_budget() -> None:
    # TODO: tổng chi phí trong Redis >= DAILY_BUDGET_USD → raise HTTPException(402)
    ...

def record_cost(input_tokens: int, output_tokens: int) -> float:
    # TODO: tính cost theo PRICE_*_PER_1K rồi cộng vào Redis (INCRBYFLOAT)
    ...
```

Nối tất cả vào `/ask`: `Depends(verify_api_key)` → `check_rate_limit(...)` → `check_budget()` → gọi LLM → `record_cost(...)`.

#### Step 7: Graceful shutdown (5 phút)

Khi `docker stop`, container nhận SIGTERM: agent phải xử lý xong request đang chạy rồi thoát với exit code 0. uvicorn làm sẵn việc này. Nếu bạn tự đăng ký handler SIGTERM (vd để ghi log), phải gọi lại handler cũ:

```python
_previous = signal.getsignal(signal.SIGTERM)

def _on_sigterm(signum, frame):
    logger.info(json.dumps({"event": "sigterm"}))
    if callable(_previous):
        _previous(signum, frame)   # không gọi lại → uvicorn không bao giờ tắt

signal.signal(signal.SIGTERM, _on_sigterm)
```

#### Step 8: Dockerfile + .dockerignore (5 phút)

```dockerfile
# Stage 1: builder — cài dependencies
FROM python:3.11-slim AS builder
# TODO

# Stage 2: runtime — chỉ copy kết quả, user non-root, HEALTHCHECK
FROM python:3.11-slim AS runtime
# TODO
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
```

> Nếu cài bằng `pip install --user` ở builder rồi copy sang `/home/<user>/.local`, nhớ đặt `ENV PYTHONUSERBASE=/home/<user>/.local`. Nếu không, user non-root sẽ không tìm thấy package và container crash ngay khi chạy.

#### Step 9: Docker Compose (5 phút)

```yaml
services:
  agent:
    build: .
    # TODO: ports, env_file (.env, required: false), REDIS_URL=redis://redis:6379/0, depends_on: redis
  redis:
    image: redis:7-alpine
    # TODO: healthcheck
```

Mở rộng: thêm Nginx làm load balancer và chạy `docker compose up --scale agent=3`.

#### Step 10: Test & deploy (5 phút)

```bash
docker compose up --build
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl -X POST http://localhost:8000/ask -H "X-API-Key: <key>" \
  -H "Content-Type: application/json" -d '{"question": "Hello"}'

# Điền railway.toml (hoặc render.yaml) rồi deploy
railway up
```

###  Validation

Chạy script kiểm tra (với project của bạn: copy `check_production_ready.py` vào thư mục gốc project, cùng cấp với `app/`):

```bash
cd 06-lab-complete
pip install -r requirements.txt
python check_production_ready.py                 # đầy đủ (lần đầu build image mất vài phút)
python check_production_ready.py --skip-docker   # bỏ phần build/chạy Docker image
python check_production_ready.py --static-only   # chỉ kiểm tra tĩnh
python check_production_ready.py --public-url https://your-app.railway.app   # thêm kiểm tra URL đã deploy
```

Script chấm theo đúng 12 tiêu chí trong "Checklist Deliverable" của `06-lab-complete/README.md`, mỗi tiêu chí kiểm tra cả file lẫn hành vi thật:

| Tiêu chí | Script kiểm tra |
|----------|-----------------|
| Dockerfile (multi-stage, < 500 MB) | ≥ 2 lệnh FROM, base slim, user non-root, HEALTHCHECK; **build image, đo kích thước, chạy container và gọi /health** |
| docker-compose.yml (agent + redis) | `docker compose config` hợp lệ, có service build từ Dockerfile + service Redis, `REDIS_URL` + `depends_on` |
| .dockerignore | Có file, loại trừ `.env`, `__pycache__`, `venv` |
| Health / Readiness | `GET /health` → 200, `GET /ready` → 200, Redis mất kết nối → `/ready` 503 |
| API Key authentication | Thiếu hoặc sai key → 401, key đúng → 200 |
| Rate limiting | Vượt giới hạn → 429 (script đặt `RATE_LIMIT_PER_MINUTE=5`); restart agent vẫn bị 429 → state nằm trong Redis |
| Cost guard | Budget gần bằng 0 → 402 |
| Config từ environment variables | `config.py` đọc env, `.env.example` đủ biến, `.env` trong `.gitignore`, không hard-code secret, agent dùng giá trị env khi chạy |
| Structured logging | Mọi dòng log của app là JSON hợp lệ |
| Graceful shutdown | SIGTERM lúc đang có request → request vẫn 200; `docker stop` → exit code 0 trong < 10s |
| Public URL ready | `railway.toml` / `render.yaml` hợp lệ (healthcheck `/health`, secret không ghi thẳng), app nghe theo biến `PORT` |

> Agent được chạy bằng `uvicorn app.main:app --workers 2` (giống CMD trong Dockerfile) với API key ngẫu nhiên. Bài test stateless cần Redis: script dùng `REDIS_URL` nếu có, không thì tự bật `redis-server` hoặc container `redis:7-alpine`. Không có Docker thì các mục build/chạy image bị đánh dấu ⚠️ (bỏ qua).

###  Grading Rubric

| Criteria | Points | Description |
|----------|--------|-------------|
| **Functionality** | 20 | Agent hoạt động đúng |
| **Docker** | 15 | Multi-stage, optimized |
| **Security** | 20 | Auth + rate limit + cost guard |
| **Reliability** | 20 | Health checks + graceful shutdown |
| **Scalability** | 15 | Stateless + load balanced |
| **Deployment** | 10 | Public URL hoạt động |
| **Total** | 100 | |

---

## Part 7: Benchmark & Observability (75 phút)

###  Concepts

**Vấn đề:** Agent đã lên cloud. Nhưng nó có đủ **nhanh** không? Có trả lời **đúng** không? Và ngay lúc này nó có đang **khoẻ** không, nếu chậm thì chậm ở bước nào?

**Giải pháp:**
1. **Load test** — đo RPS, error rate, latency p50/p95/p99 rồi so với SLO
2. **Eval** — chạy golden dataset, so sánh với phiên bản trước, chặn deploy nếu có regression
3. **Metrics** — Prometheus scrape `/metrics`, Grafana vẽ 4 Golden Signals + token/cost
4. **Traces** — OpenTelemetry ghi từng bước của request, xem trong Jaeger
5. **Alerts** — Prometheus báo động khi vi phạm SLO kéo dài

Lý thuyết chi tiết (percentile, SLO, cardinality...): [06-lab-complete/benchmark-observability/README.md](06-lab-complete/benchmark-observability/README.md)

###  Exercise 7.1: Đọc metrics của agent (10 phút)

```bash
cd 06-lab-complete/benchmark-observability/develop
pip install -r requirements.txt

# Terminal 1: agent v1 (không retrieval)
AGENT_VERSION=v1 PORT=8001 python app.py
# Terminal 2: agent v2 (có retrieval)
AGENT_VERSION=v2 PORT=8002 python app.py

# Terminal 3
curl -s -X POST http://localhost:8002/ask -H "Content-Type: application/json" \
  -d '{"question": "Prometheus thu thập metrics như thế nào?"}'
curl -s http://localhost:8002/metrics | grep -v "^#"
```

**Câu hỏi:**
1. Tìm trong output 1 ví dụ cho mỗi loại metric: Counter, Gauge, Histogram.
2. Middleware `observe_requests` dùng `route.path` làm label `route` (URL không khớp route nào thì gán `unmatched`). Nếu dùng URL thật (`request.url.path`) thì chuyện gì xảy ra khi bot quét gọi hàng nghìn URL lạ như `/wp-admin`, `/.env`, `/a1b2c3`...?

**Nhiệm vụ:** Thêm metric đo phân bố độ dài câu hỏi, đặt tên `agent_question_length_chars`.

<details>
<summary> Solution</summary>

```python
QUESTION_LENGTH = Histogram(
    "agent_question_length_chars", "Độ dài câu hỏi (ký tự)",
    buckets=(20, 50, 100, 200, 500, 1000, 2000),
)

# trong endpoint ask(), trước khi gọi LLM:
QUESTION_LENGTH.observe(len(body.question))
```

Dùng Histogram (không dùng label `length=...`) vì độ dài có vô số giá trị, nếu làm label thì cardinality sẽ bùng nổ.

</details>

###  Exercise 7.2: Load test & SLO (15 phút)

```bash
python load_test.py --url http://localhost:8002 --requests 300 --concurrency 20
```

**Nhiệm vụ:**
1. Chạy với `--concurrency` 1, 10, 50, 100 và ghi lại RPS, p50, p95, p99.
2. Khởi động lại agent v2 với `MOCK_SLOW_RATE=0`, sau đó `MOCK_SLOW_RATE=0.1`. So sánh avg, p95, p99.

**Câu hỏi:** Vì sao avg chỉ tăng nhẹ trong khi p99 tăng vọt? SLO nên đặt theo chỉ số nào?

###  Exercise 7.3: Eval & quality gate (15 phút)

```bash
python eval/run_eval.py --url http://localhost:8001 --out reports/eval_v1.json
python eval/run_eval.py --url http://localhost:8002 --out reports/eval_v2.json \
       --baseline reports/eval_v1.json
```

**Nhiệm vụ:**
1. v2 trả lời sai 2 câu. Đọc `missing_keywords` trong `reports/eval_v2.json`, thêm tài liệu vào `KNOWLEDGE_BASE` (file `utils/mock_llm.py`) để đạt 100% mà **không có regression**.
2. Viết 1 job CI chạy eval và fail nếu accuracy < 85%.

<details>
<summary> Solution</summary>

```python
# utils/mock_llm.py — thêm vào cuối KNOWLEDGE_BASE
(["hpa", "kubernetes", "autoscal"],
 "Kubernetes HPA (Horizontal Pod Autoscaler) scale số pod dựa trên CPU, memory "
 "hoặc custom metrics như RPS hay độ dài hàng đợi."),
(["jwt"],
 "API key là chuỗi bí mật cố định, không tự hết hạn. JWT là token có chữ ký số, chứa "
 "thông tin user và thời điểm hết hạn; server xác minh chữ ký mà không cần tra database."),
```

```yaml
# .github/workflows/eval.yml
name: quality-gate
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Run agent + eval
        working-directory: 06-lab-complete/benchmark-observability/develop
        run: |
          pip install -r requirements.txt
          AGENT_VERSION=v2 MOCK_ERROR_RATE=0 python app.py &
          sleep 3
          python eval/run_eval.py --url http://localhost:8000 --min-accuracy 0.85
```

`run_eval.py` trả exit code 1 khi không đạt, nên job fail và PR không merge được.

</details>

###  Exercise 7.4: Observability stack (15 phút)

```bash
cd ../production
docker compose up --build -d
docker compose ps
```

| Service | URL |
|---------|-----|
| Agent (qua Nginx) | http://localhost:8080 (header `X-API-Key: day14-lab-key`) |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| Jaeger | http://localhost:16686 |
| Locust | http://localhost:8089 |

Mở Locust, chạy **30 users / ramp up 5**, rồi mở dashboard **Day 14 — AI Agent Overview** trong Grafana.

**Câu hỏi:**
1. p95 và avg đang là bao nhiêu? Khoảng cách giữa chúng nói lên điều gì?
2. Panel "Requests/s theo instance": Nginx có chia đều traffic cho 2 instance không?
3. Vì sao input tokens/s lớn hơn output tokens/s?
4. `curl http://localhost:8080/metrics` trả về gì? Vì sao?

###  Exercise 7.5: Tracing (10 phút)

1. Jaeger → Service `observable-agent` → Find Traces → sắp xếp **Longest First**
2. Mở trace chậm nhất: span nào chiếm nhiều thời gian nhất?
3. Tìm 1 trace lỗi (tag `error=true`) và xem event `exception`
4. Lấy `trace_id` từ log rồi tìm lại trace đó trong Jaeger:

```bash
docker compose logs agent | grep llm_error | head -1
```

###  Exercise 7.6: Alerts — phá hệ thống và quan sát (10 phút)

```bash
# Unit test alert rules
docker run --rm -v "$PWD/prometheus:/p" --entrypoint promtool \
  prom/prometheus:v3.16.0 test rules /p/alert_rules_test.yml
```

Làm **ít nhất 2** thí nghiệm trong bảng ở mục 2.6 của [README Benchmark & Observability](06-lab-complete/benchmark-observability/README.md) (ví dụ `MOCK_ERROR_RATE=0.2`, `LLM_MODEL=mock-llm-large`). Ghi lại alert nào firing và mất bao lâu.

**Câu hỏi:** Đổi `AGENT_VERSION=v1` thì không alert nào firing dù chất lượng giảm mạnh. Vậy loại sự cố này được phát hiện bằng cách nào?

###  Exercise 7.7: Benchmark report

Điền [06-lab-complete/benchmark-observability/BENCHMARK_REPORT_TEMPLATE.md](06-lab-complete/benchmark-observability/BENCHMARK_REPORT_TEMPLATE.md), lưu thành `BENCHMARK_REPORT.md` kèm report JSON, CSV của Locust và screenshot.

```bash
docker compose down   # dọn dẹp khi xong
```

###  Checkpoint 7

- [ ] Giải thích được p50/p95/p99 và vì sao SLO đặt theo percentile
- [ ] Chạy load test và đánh giá kết quả so với SLO
- [ ] Chạy eval, so sánh 2 phiên bản, hiểu quality gate
- [ ] Đọc dashboard Grafana theo 4 Golden Signals
- [ ] Tìm được span gây chậm trong Jaeger
- [ ] Làm ít nhất 2 alert firing và giải thích nguyên nhân
- [ ] Hoàn thành `BENCHMARK_REPORT.md`

---

##  Hoàn Thành!

Bạn đã:
-  Hiểu sự khác biệt dev vs production
-  Containerize app với Docker
-  Deploy lên cloud platform
-  Bảo mật API
-  Thiết kế hệ thống scalable và reliable
-  Benchmark agent và giám sát bằng Prometheus, Grafana, Jaeger

###  Next Steps

1. **Alerting:** Alertmanager gửi cảnh báo qua Slack/PagerDuty
2. **CI/CD:** GitHub Actions auto-deploy
3. **Advanced scaling:** Kubernetes
4. **Managed observability:** Google Cloud Monitoring & Cloud Trace, Grafana Cloud, Langfuse cho LLM
5. **Cost optimization:** Spot instances, auto-scaling
6. **Eval nâng cao:** LLM-as-judge, semantic similarity, eval trên traffic thật

###  Resources

- [12-Factor App](https://12factor.net/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Prometheus Docs](https://prometheus.io/docs/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [Locust Docs](https://docs.locust.io/)

---

##  Q&A

**Q: Tôi không có credit card, có thể deploy không?**  
A: Có! Railway cho $5 credit, Render có 750h free tier.

**Q: Mock LLM khác gì với OpenAI thật?**  
A: Mock trả về canned responses, không gọi API. Để dùng OpenAI thật, set `OPENAI_API_KEY` trong env.

**Q: Làm sao debug khi container fail?**  
A: `docker logs <container_id>` hoặc `docker exec -it <container_id> /bin/sh`

**Q: Redis data mất khi restart?**  
A: Dùng volume: `volumes: - redis-data:/data` trong docker-compose.

**Q: Làm sao scale trên Railway/Render?**  
A: Railway: `railway scale <replicas>`. Render: Dashboard → Settings → Instances.

---

**Happy Deploying! **
