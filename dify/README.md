# Dify Demo — How to Run

## 1) Start FastAPI (local)

Run:

    cd ~/projects/agent-platform
    uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

## 2) Expose with ngrok

Run:

    ngrok http 8000

## 3) Configure Dify ENV

Workflow page → ENV:

- BASE_URL = https://<your-ngrok-domain>.ngrok-free.dev

## 4) Verify

- Local health: http://127.0.0.1:8000/health
- Public health: https://<your-ngrok-domain>.ngrok-free.dev/health
- Swagger: https://<your-ngrok-domain>.ngrok-free.dev/docs

## 5) Test Cases

1) 近7天 ROI 掉了，按 campaign 下钻  
2) 昨天 CPA 变贵了，想降 CPA  
3) 上周 ROAS 怎么样，有没有异常
