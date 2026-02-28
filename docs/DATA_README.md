cat > docs/DATA_README.md <<'EOF'
# DATA_README（v0）

## 数据来源
- Kaggle: Avazu CTR Prediction（原始文件：train.csv / train.gz）
- 放置位置：data_raw/kaggle/avazu_train.csv

## 抽样策略（为什么 & 怎么抽）
目标：把 Kaggle 原始大表变成你可控的数据集，用于 Demo / 规则诊断 / Dify 调用。

- 抽样粒度：曝光级（每行=一次展示），生成 ad_events_sample.csv
- 抽样方法（推荐）：
  1) 时间切片：选取连续 N 天（例如 2~7 天）避免分布太碎
  2) 行数上限：最多 200,000 行（保证本地跑得快）
  3) 若原始数据无真实 cost：用“规则/随机”模拟 cost（用于 spend、CPA、ROAS 的演示）

## 输出数据表
1) ad_events_sample（曝光级）
- timestamp：事件时间（由 hour 字段转换）
- campaign_id：合成（由部分字段拼接 hash）
- creative_id：来自原始字段（或合成）
- audience_id：合成（设备/站点/地域等组合）
- geo：合成/取字段
- device：合成/取字段
- clicked：0/1（原始 click）
- cost：模拟（clicked=1 的 cost 更高）

2) campaign_daily（天×活动）
- date, campaign_id
- impressions, clicks, spend
- conversions（模拟，基于 clicks & CVR）
- revenue（模拟，基于 conversions & AOV）
EOF
