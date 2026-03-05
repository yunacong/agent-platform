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

bash
### 1) set BASE_URL (Render service)
export BASE_URL="https://<your-render-service>.onrender.com"

### 2) sanity check (Render free plan 可能 cold start，第一次可能慢 30~60s)
curl -s "$BASE_URL/health"; echo

### 3) generate baseline outputs
python eval/run_baseline.py

### 4) verify outputs line count (should both be 50)
wc -l eval/cases.jsonl eval/baseline_outputs.jsonl

### 5) run promptfoo regression
promptfoo eval -c eval/promptfooconfig.yaml

### 6) view results (optional)
promptfoo view

## 3) Key metrics (at least 5)

本轮评估关注以下 5 类指标（工程视角 + 可复盘）：
	1.	参数抽取准确率（metric/date_range/dim 是否正确）
	2.	异常定位正确率（是否找对区间 / 对象）
	3.	证据可追溯率（是否引用了正确数据/规则来源）
	4.	建议可执行率（结构完整 + 动作具体 + 有回滚）
	5.	幻觉率（是否编造指标/无依据结论）

## 4) Results (Day12 v1)

Overall
	•	Passing: 50/50 (100%)
	•	Provider: baseline
	•	Notes: 当前通过表示“评测链路 + provider + 数据集读取”无误，且每条 case 都能跑通并产出结构化结果。

Screenshot — Overview
Example case (c01)
展示单条 case 结果，证明不是空跑（包含 user_query / params / evidence 等字段）。
Screenshot — Case detail


## 5) Artifacts (for reviewers)
	•	Dataset: eval/cases.jsonl
	•	Baseline outputs: eval/baseline_outputs.jsonl
	•	Promptfoo config: eval/promptfooconfig.yaml
	•	Provider: eval/providers/baseline_provider.py
	•	Generated test list: eval/tests.generated.yaml
	•	Promptfoo result snapshot (optional): eval/promptfoo/results.json


## 6) Next steps
	1.	加入 LLM 版本（Structured Output）并与 baseline 做 A/B（同一批 50 cases）
	2.	把上述 5 个指标做成自动统计（accuracy / hallucination / traceability）
	3.	输出“产品可交付”的对比结论：哪些场景提升最大、哪些场景风险最高
