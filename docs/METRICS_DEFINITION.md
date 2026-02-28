# 指标口径（v0｜投放看盘）

## 基础字段
- spend：消耗（花费）
- impressions：曝光
- clicks：点击
- conversions：转化（先按“有效转化”统一，后续可配置：下单/支付/表单）
- revenue：归因收入（可用成交额/付费金额替代）

## 核心指标
- CTR = clicks / impressions
- CVR = conversions / clicks
- CPC = spend / clicks
- CPA = spend / conversions
- CPM = spend / impressions * 1000
- ROAS = revenue / spend
- ROI（简化）= (revenue - spend) / spend

## 口径坑点（必须在输出里提示）
1) conversions 定义不清会导致 CVR/CPA 失真（必须在 case 中固定）
2) 归因窗口（D1/D7）变化会导致 ROAS/ROI 波动（输出需注明）
3) 分母为 0：impressions/clicks/conversions 为 0 → 指标不可算，输出“样本不足/不可计算”
4) 小样本：clicks < 50 或 conversions < 10 → 结论低置信度，只给“观察建议”
