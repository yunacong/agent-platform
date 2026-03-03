  date_range

- type: String (或 Enum)
- allowed:
  - 昨天 / 近7天 / 近30天 / 上周 / 本周 / 本月 / 上月
  - 自定义：YYYY-MM-DD~YYYY-MM-DD
- default: 近7天
- description:
  时间范围。优先抽为：昨天/近7天/近30天/上周/本周/本月/上月/自定义YYYY-MM-DD~YYYY-MM-DD。
  用户未说明默认“近7天”。“最近/近一周/近七天”→近7天；“最近一个月/近30天/近一月”→近30天。

### 2. metric（必填）
- name: metric
- type: Enum（推荐）或 String
- allowed: ROI | ROAS | CPA | CVR | CTR | SPEND
- default: ROI
- description:
  核心指标。用户说“花费/消耗/预算”→SPEND；
  “成本/CPA/获客成本/成本变贵”→CPA；
  “转化率/CVR”→CVR；“点击率/CTR”→CTR；
  “ROI/回报/收益率”→ROI；“ROAS”→ROAS。
  未提及默认 ROI。

### 3. dimension（必填）
- name: dimension
- type: Enum（推荐）或 String
- allowed: campaign | creative | audience | geo | device | all
- default: all
- description:
  分析维度。按计划/活动→campaign；按素材/创意→creative；
  按人群/定向→audience；按地区/地域→geo；按设备→device。
  未提及默认 all（先整体再下钻 campaign）。

### 4. goal（必填）
- name: goal
- type: Enum（推荐）或 String
- allowed: raise_roi | lower_cpa | stabilize_delivery | debug_drop | improve_ctr | improve_cvr
- default: debug_drop
- description:
  用户目标。提ROI/提升ROAS→raise_roi；降CPA/降成本→lower_cpa；
  稳量/放量/跑量→stabilize_delivery；
  掉了/下降/异常/排查原因→debug_drop；
  提CTR→improve_ctr；提CVR/转化率→improve_cvr。
  未提及默认 debug_drop。

---

## 2) 参数提取器「指令」（Prompt，可直接复制到 Dify）
```text
你是投放诊断工作流的参数抽取器。请从用户输入中抽取并填充四个参数：date_range, metric, dimension, goal。
要求：必须优先遵循【硬规则】，没有命中才使用默认值。只输出结构化参数，不要输出解释。

【硬规则-时间 date_range】
- 出现“昨天” -> date_range=昨天
- 出现“近7天/最近一周/近一周/近七天/最近7天” -> date_range=近7天
- 出现“近30天/最近一个月/近一月/最近30天” -> date_range=近30天
- 出现“上周/本周/本月/上月” -> 对应取值
- 出现“YYYY-MM-DD~YYYY-MM-DD” -> 直接作为自定义范围
- 未提到任何时间 -> date_range=近7天

【硬规则-指标 metric & 目标 goal】
- 出现“CPA/成本/获客成本/成本变贵/想降成本/降CPA” -> metric=CPA 且 goal=lower_cpa
- 出现“花费/消耗/预算/spend” -> metric=SPEND
- 出现“CTR/点击率” -> metric=CTR；若出现“提升/提高/想提”则 goal=improve_ctr；若出现“下降/掉了/异常/变差/排查原因”则 goal=debug_drop
- 出现“CVR/转化率” -> metric=CVR；若出现“提升/提高/想提”则 goal=improve_cvr；若出现“下降/掉了/异常/变差/排查原因”则 goal=debug_drop
- 出现“ROAS” -> metric=ROAS；若出现“提升/提高/想提”则 goal=raise_roi；若出现“下降/掉了/异常/变差/排查原因”则 goal=debug_drop
- 出现“ROI/回报/收益率” -> metric=ROI；若出现“提升/提高/想提”则 goal=raise_roi；若出现“下降/掉了/异常/变差/排查原因”则 goal=debug_drop
- 若用户只说“掉了/下降/异常/排查原因”但没说指标 -> metric=ROI 且 goal=debug_drop

【硬规则-维度 dimension】
- 出现“按计划/活动/campaign/下钻计划” -> dimension=campaign
- 出现“按素材/创意/creative/下钻素材” -> dimension=creative
- 出现“按人群/定向/audience” -> dimension=audience
- 出现“按地域/地区/geo” -> dimension=geo
- 出现“按设备/device” -> dimension=device
- 未提到维度 -> dimension=all

【默认值】
date_range 默认 近7天；metric 默认 ROI；dimension 默认 all；goal 默认 debug_drop# workflow_params.md（Day8：Parameter Extractor）

目标：用户一句话 → 自动抽出「时间范围/指标/维度/目标」，用于后续 workflow 的查数/异常/归因。

---

## 1) 参数 Schema（建议字段）

> 适配 Dify Parameter Extractor 的“表单字段”方式：创建 4 个必填参数。
> 如果你的界面支持 Enum，就用 Enum；不支持就用 String，并在描述里写可选值。

### 1. date_range（必填）
- name: 
