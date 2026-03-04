# Day10 — 结构化建议模板（Structured Recommendation JSON）

目标：让输出**不再泛泛而谈**，而是可控（字段固定）、可评测（可做回归/对比）、可复盘（证据可追溯）。

---

## 1) 输出契约（Output Contract）

LLM 最终必须输出一个 JSON 对象，且包含字段：

- `summary`：一句话结论（TL;DR）
- `diagnosis`：异常是什么 + 影响面（更具体一点）
- `root_causes[]`：2~4 条根因假设（每条必须带证据 + 验证方式）
- `actions[]`：2~5 条动作建议（每条必须带风险/回滚 + 至少1条证据）
- `confidence`：0~1（证据不足时必须压低）
- `citations[]`：知识库引用点（不确定就输出 `[]`，不要编造）

---

## 2) 字段规范（Schema 约束）

### 2.1 root_causes（2~4条，必填）
每条必须包含：

- `hypothesis` (string)：假设一句话
- `evidence` (array, >=2)：证据列表，每条必须是对象
  - `source`: 只能是 `trend_rows` / `anomalies_top3` / `contributions_top5` / `compare_window`
  - `key`: 例如 `cmp_1652.pct_change`、`baseline.revenue`
  - `value`: 关键数值（number/string/object 均可）
- `how_to_validate` (string)：必须包含三段（强制格式）
  - `method: 对照/分流/A-B/回放; metric: <指标>; pass_criteria: <通过阈值>`

### 2.2 actions（2~5条，必填）
每条必须包含：

- `action` (string)：要做什么（可执行）
- `expected_impact` (string)：预期影响（最好带范围/方向）
- `risk` (string)：风险提示（证据不足/口径异常要写明）
- `rollback` (string)：回滚方案（不行怎么退）
- `evidence` (array, >=1)：证据列表（同上 source/key/value）

### 2.3 confidence（0~1）
- 若证据中出现：
  - `baseline=-1`（缺失）
  - 或 `compare_window.baseline.revenue=0`（样本不足）
- 则 `confidence <= 0.5`，并且在 **每条** `actions[].risk` 明确写“样本不足/口径异常”。

### 2.4 citations（可空）
- 仅在你**确定**命中知识库内容时填写，例如：
  - `kb/metric_definitions.md#roi`
  - `kb/action_playbook.md#scale`
- 不确定或未命中：`[]`（不要编造）

---

## 3) 参考 System Prompt（可复制）

> 注：如果你走的是「LLM(text JSON) → PARSE_LLM_JSON → 输出(Object)」链路，建议用这套更稳。

```text
你是投放诊断助手。只输出一个合法 JSON 对象（必须以 { 开头，以 } 结尾），不要输出任何解释文字、不要输出 markdown、不要输出 <think>、不要输出代码块。

输出 JSON 必须包含字段：
summary, diagnosis, root_causes, actions, confidence, citations

约束：
- root_causes: 2~4 条
  - hypothesis: string
  - evidence: 至少 2 条；每条必须是对象 {source, key, value}
    - source 只能是 trend_rows / anomalies_top3 / contributions_top5 / compare_window
  - how_to_validate: string，格式必须包含：
    method: 对照/分流/A-B/回放; metric: <指标>; pass_criteria: <通过阈值>
- actions: 2~5 条
  - action / expected_impact / risk / rollback: string
  - evidence: 至少 1 条；对象 {source, key, value}
- confidence: 0~1
  - 如果 evidence_json 中出现 baseline=-1 或 compare_window.baseline.revenue=0，则 confidence 必须 <= 0.5，
    且在每条 actions[].risk 写明“样本不足/口径异常”
- citations: 仅在确定命中知识库时填写（kb/<filename>#<section>），不确定则输出 []

再次强调：只输出 JSON。
