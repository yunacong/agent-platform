# KNOWN_ANOMALIES（Day3 注入异常标准答案）

本文件记录“人为注入”的异常，作为后续评测/回归测试的标准答案来源（promptfoo / Dify 回归都用它）。

## 数据版本
- 输入表：data_processed/campaign_daily.csv
- 输出表：data_processed/campaign_daily_anomaly.csv
- 生成脚本：scripts/inject_anomalies.py

## 异常开始日期
- start_date = 2014-10-23

---

## 异常 1：某类人群 CVR 下滑（“质量变”）
- 作用对象：campaign_id = cmp_1000
- 注入规则：
  - 从 start_date 起，对该 campaign 的 conversions 与 revenue 按比例下降（CVR 下降）
- 现象特征（你应该能在数据里观察到）：
  - impressions/clicks 不一定明显变
  - CVR ↓ → conversions ↓ → CPA ↑
  - ROAS/ROI 下降

---

## 异常 2：某素材 CTR 下滑（“上游掉”）
- 作用对象：campaign_id = cmp_1315
- 注入规则：
  - 从 start_date 起，clicks 按比例下降（impressions 基本不变）
  - conversions 与 revenue 也随 clicks 同比例下降（保持 CVR 大体不变）
- 现象特征：
  - impressions 稳定但 CTR ↓
  - clicks ↓ → conversions ↓ → ROI 下降

---

## 异常 3：某地域 spend 飙升但 revenue 不涨（“浪费”）
- 作用对象：campaign_id = cmp_1652
- 注入规则：
  - 从 start_date 起，spend 上升（revenue 保持不变）
- 现象特征：
  - spend ↑ 但 revenue 变化小
  - ROAS/ROI 显著下降（典型浪费）
