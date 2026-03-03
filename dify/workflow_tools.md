# Day9/Day10 — Dify Workflow 接 FastAPI（HTTP Request）

## Overview
Workflow: 用户输入 → 参数提取器 → DATE_PARSE → WINDOW_SPLIT → HTTP_QUERY_METRICS → HTTP_DETECT_ANOMALY → HTTP_SLICE_COMPARE → EVIDENCE(Code) → 输出

## ENV
- BASE_URL: ngrok 公网地址（在 Dify 右上角 ENV 配置）

## Nodes

### 1) 参数提取器（Parameter Extractor）
- input: user (String)
- output:
  - date_range (String)：昨天/近7天/近30天/上周/本周/本月/上月/自定义YYYY-MM-DD~YYYY-MM-DD
  - metric (String，小写)：roi/roas/cpa/cvr/ctr/spend
  - dimension (String)：campaign/creative/audience/geo/device/all
  - goal (String)：raise_roi/lower_cpa/stabilize_delivery/debug_drop/improve_ctr/improve_cvr

### 2) DATE_PARSE（Code/Python）
- input: date_range_text = 参数提取器.date_range
- output: date_range (Object) = {"start":"YYYY-MM-DD","end":"YYYY-MM-DD"}
- demo说明：为适配 Avazu demo 数据时间范围，DATE_PARSE 将“近7天”等映射到数据范围附近（避免落到真实今天导致无数据）

### 3) WINDOW_SPLIT（Code/Python）
- input: date_range (Object)
- output: b_start/b_end/c_start/c_end (String)
- rule: baseline=前2天，compare=后2天（贴边处理）

### 4) HTTP_QUERY_METRICS
- POST {BASE_URL}/query_metrics
- headers: Content-Type=application/json
- body(JSON):
  - metric="roi"
  - group_by=["date"]
  - date_range.start = WINDOW_SPLIT.b_start
  - date_range.end   = WINDOW_SPLIT.c_end
- output: body (String JSON) => {"rows":[...]}

### 5) HTTP_DETECT_ANOMALY
- POST {BASE_URL}/detect_anomaly
- headers: Content-Type=application/json
- body(JSON):
  - metric="roi"
  - group_by="campaign_id"
  - date_range.start = WINDOW_SPLIT.b_start
  - date_range.end   = WINDOW_SPLIT.c_end
  - baseline_days=2 compare_days=2 threshold_pct=0.2
- output: body (String JSON) => {"anomalies":[...]}

### 6) HTTP_SLICE_COMPARE
- POST {BASE_URL}/slice_compare
- headers: Content-Type=application/json
- body(JSON):
  - metric="revenue"
  - dim="campaign_id"
  - baseline_range: b_start/b_end
  - compare_range:  c_start/c_end
  - top_k=10
- output: body (String JSON) => {"baseline_summary":...,"compare_summary":...,"contributions":[...]}

### 7) EVIDENCE（Code/Python）
- inputs: 3个HTTP的body(JSON string)
- output: evidence (Object)
  - trend_rows
  - anomalies_top3
  - contributions_top5
  - compare_window (baseline/compare)

## Test Cases
1) 近7天 ROI 掉了，按 campaign 下钻
2) 昨天 CPA 变贵了，想降 CPA
3) 上周 ROAS 怎么样，有没有异常

## Common Pitfalls
- FastAPI metric 只接受小写（roi/cpa/...），参数提取器需输出小写或中间 normalize
- HTTP Request 建议使用 JSON 模式 + {x} 插入变量，raw 手写 {{...}} 可能不渲染
