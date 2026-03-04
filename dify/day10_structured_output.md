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

text
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




## 4) 示例输出

```{
  "summary": "近7天ROI下降主要由数据质量问题导致，包括基准期数据缺失和特定campaign表现异常，使得对比不准确。",
  "diagnosis": "ROI下降的警报很可能被数据缺失放大：基准期 revenue=0 且多个campaign baseline=-1，导致ROI对比失真；同时 cmp_1652 在对比期ROI显著下滑，加上高贡献campaign cmp_2141 基准期为0而对比期突增，使整体趋势更难可靠判断。",
  "root_causes": [
    {
      "hypothesis": "基准期数据收集不完整（收入/成本缺失），导致ROI计算基准异常，无法进行有效对比。",
      "evidence": [
        { "source": "compare_window", "key": "baseline.revenue", "value": 0.0 },
        { "source": "anomalies_top3", "key": "cmp_992.baseline", "value": -1.0 }
      ],
      "how_to_validate": "method: 对照; metric: baseline revenue; pass_criteria: baseline revenue > 0 且 baseline 不出现 -1"
    },
    {
      "hypothesis": "高贡献campaign cmp_2141 在基准期为0、对比期突增，可能为新启动/口径变化/数据异常，导致整体ROI被单点波动影响。",
      "evidence": [
        { "source": "contributions_top5", "key": "cmp_2141.baseline", "value": 0.0 },
        { "source": "contributions_top5", "key": "cmp_2141.compare", "value": 96.65 }
      ],
      "how_to_validate": "method: 回放; metric: cmp_2141 revenue/spend/roi; pass_criteria: 与投放日志一致且ROI在连续多天稳定为正"
    },
    {
      "hypothesis": "campaign cmp_1652 在对比期ROI显著下降（约-61%），是导致整体ROI下滑的重要直接因素。",
      "evidence": [
        { "source": "anomalies_top3", "key": "cmp_1652.pct_change", "value": -0.6097569463343343 },
        { "source": "anomalies_top3", "key": "cmp_1652.baseline_vs_compare", "value": "baseline=27.549019607843135, compare=10.750813537260004" }
      ],
      "how_to_validate": "method: A-B; metric: cmp_1652 roi; pass_criteria: 对比期ROI较当前提升>=20%且趋势稳定"
    }
  ],
  "actions": [
    {
      "action": "修复并补齐基准期数据收集（revenue/cost），确保所有campaign在基准期有有效记录，再重新跑诊断。",
      "expected_impact": "恢复对比基准的可信度，降低误报，提升诊断准确性。",
      "risk": "样本不足/口径异常：基准期 revenue=0 与 baseline=-1 可能导致当前结论失真，修复前不宜做大幅投放调整。",
      "rollback": "若短期无法补齐数据，临时改用更长窗口（如近14天/近30天）或滚动均值作为基准。",
      "evidence": [
        { "source": "compare_window", "key": "baseline.revenue", "value": 0.0 }
      ]
    },
    {
      "action": "核对 cmp_2141 的贡献计算口径与投放日志（是否新启动、是否延迟归因/回填、是否数据重复），确认其突增是否真实。",
      "expected_impact": "确认高贡献是否可持续，避免被异常数据误导预算决策。",
      "risk": "样本不足/口径异常：cmp_2141 基准期为0可能是新campaign或口径变化，单点波动会扭曲整体ROI判断。",
      "rollback": "若确认口径/数据异常，统一口径后回算；若确认真实突增，后续再考虑稳步扩量（每次10%-20%）。",
      "evidence": [
        { "source": "contributions_top5", "key": "cmp_2141.compare", "value": 96.65 }
      ]
    },
    {
      "action": "针对 cmp_1652 做归因拆解（先看CTR/CVR/CPA链路），并小步调整定向/出价/创意以恢复ROI。",
      "expected_impact": "修复单campaign ROI下滑，带动整体ROI改善。",
      "risk": "样本不足/口径异常：若基准期数据本身不可信，调整可能基于错误信号；需配合更长窗口或稳定基准再判断。",
      "rollback": "若调整后24-48小时ROI无改善或更差，回滚到原投放设置并记录失败样本。",
      "evidence": [
        { "source": "anomalies_top3", "key": "cmp_1652.pct_change", "value": -0.6097569463343343 }
      ]
    }
  ],
  "confidence": 0.4,
  "citations": []
}```


## 5) 回归用例测试
	1.	近7天 ROI 掉了，按 campaign 下钻
	2.	昨天 CPA 变贵了，想降 CPA
	3.	上周 ROAS 怎么样？有没有异常
	4.	本周 spend 暴涨但 revenue 不涨（怀疑浪费），按 geo 下钻
	5.	CTR 下滑了，按 creative 找原因并给动作建议
