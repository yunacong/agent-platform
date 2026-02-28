cat > docs/METRIC_DEFS.md <<'EOF'
# METRIC_DEFS（指标口径 v0）

- CTR = clicks / impressions
- CVR = conversions / clicks
- CPA = spend / conversions
- ROAS = revenue / spend
- ROI = (revenue - spend) / spend

## 注意事项
- 分母为 0：返回 N/A，并标注“样本不足”
- 小样本：clicks < 50 或 conversions < 10 → 低置信度
- conversions/revenue 为模拟口径：用于 Demo 演示与规则链路跑通
EOF
