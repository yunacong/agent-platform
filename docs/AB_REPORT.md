# AB_REPORT — Promptfoo Regression & Baseline (Day 12)

本报告用于展示：我不是“感觉这个 Agent 好用”，而是用 **离线评测集 + 回归评测**，把输出变成可测、可比、可复盘的工程化结果。

---

## 1) What is evaluated

**Goal:** 一键跑评测，出对比结果（工程化 AI PM 产出）

**Eval type:** Baseline regression (offline dataset)

**Dataset:** `eval/cases.jsonl`（50 条自然语言问题）  
**Baseline generator:** `eval/run_baseline.py` → `eval/baseline_outputs.jsonl`（50 条对照输出）  
**Promptfoo config:** `eval/promptfooconfig.yaml`  
**Provider:** `eval/providers/baseline_provider.py`

---

## 2) Run instructions

在 repo 根目录执行：

```bash
# 1) set BASE_URL (Render service)
export BASE_URL="https://<your-render-service>.onrender.com"

# 2) sanity check (Render free plan 可能 cold start，第一次可能慢 30~60s)
curl -s "$BASE_URL/health"; echo

# 3) generate baseline outputs
python eval/run_baseline.py

# 4) verify outputs line count (should both be 50)
wc -l eval/cases.jsonl eval/baseline_outputs.jsonl

# 5) run promptfoo regression
promptfoo eval -c eval/promptfooconfig.yaml

# 6) view results (optional)
promptfoo view
