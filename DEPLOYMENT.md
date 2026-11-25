# Deployment Information

## Public URL
https://zucchini-simplicity-production-7b7c1dfb.up.railway.app

## Platform
Railway (Root Directory: `06-lab-complete`, kèm Redis managed service)

## Test Commands

### Health Check
```bash
curl -sS https://zucchini-simplicity-production-7b7c1dfb.up.railway.app/health
# Expected (200): {"status":"ok","environment":"production"}
```

### Readiness Check (Redis)
```bash
curl -sS https://zucchini-simplicity-production-7b7c1dfb.up.railway.app/ready
# Expected (200): {"ready":true}
```

### API Test (without key → 401, with authentication → 200)
```bash
# Không có key → 401
curl -sS -o /dev/null -w '%{http_code}\n' -X POST https://zucchini-simplicity-production-7b7c1dfb.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

# Có X-API-Key → 200
curl -X POST https://zucchini-simplicity-production-7b7c1dfb.up.railway.app/ask \
  -H "X-API-Key: YOUR_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

## Environment Variables Set
- `PORT` (Railway tự inject)
- `REDIS_URL` (`${{Redis.REDIS_URL}}`)
- `AGENT_API_KEY` (đặt trên Railway Variables, không commit vào Git)
- `ENVIRONMENT` (`production`)
- `RATE_LIMIT_PER_MINUTE` (`10`)
- `DAILY_BUDGET_USD` (`1.0`)

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
