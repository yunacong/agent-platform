# 指标口径与计算（Metric Definitions）

> 目的：让模型回答“有口径、有红线、有引用”。本页用于统一投放看盘的分母分子、时间窗、归因口径与数据质量规则。

## 1. 基础字段（事实层）
- impressions：曝光次数
- clicks：点击次数
- spend：花费/消耗
- conversions：转化次数（需明确转化事件：下单/支付/表单/注册）
- revenue：收入/成交额（需明确归因口径）

## 2. 核心指标公式
- CTR = clicks / impressions
- CVR = conversions / clicks
- CPC = spend / clicks
- CPA = spend / conversions
- CPM = spend / impressions * 1000
- ROAS = revenue / spend
- ROI = (revenue - spend) / spend

## 3. 口径“红线”（必须写清）
### 3.1 转化定义（conversions）
- 必须在报告中注明：转化事件是什么（例：支付成功/下单/表单提交）
- 不同转化事件的 CVR/CPA 不可直接横比（需同口径）

### 3.2 归因窗口（attribution window）
- 常见：D1 / D7 / D14 等
- 归因窗口变化会导致 revenue/ROAS 波动（输出必须提示）

### 3.3 分母为 0 & 小样本
- impressions=0 → CTR 不可计算
- clicks=0 → CVR/CPC 不可计算
- conversions=0 → CPA 不可计算
- 小样本建议阈值（可按业务调整）：
  - clicks < 50 或 conversions < 10：结论低置信度，只给“观察/补数/再验证”

### 3.4 数据延迟/回填
- revenue/conversions 可能存在延迟回填（特别是 D7 归因）
- 当天/昨日数据需标注“未完结”，避免误判

## 4. 推荐的对比基线
- 昨日 vs 近 3 日均值（快速看盘）
- 本周 vs 上周同日（周期性更稳）
- 活动期 vs 活动前（复盘）

## 5. 输出规范（建议引用方式）
- 结论必须引用：指标、维度、时间范围、对比基线
- 风险提示必须引用：小样本/口径/延迟/分母为0
