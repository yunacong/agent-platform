3分钟 Demo Script — Ad Diagnose Agent（Dify Workflow + FastAPI + Eval）

0:00-0:20 业务问题（运营口吻）
“近7天 ROI 下降，帮我快速定位原因并给可执行建议（要有证据、风险、回滚）。”

0:20-1:40 演示 Workflow 跑通（强调证据链）
	1.	输入自然语言问题 → 参数抽取（date_range/metric/dim/goal）
	2.	HTTP 调用 FastAPI：
	•	query_metrics：拉趋势（看到 ROI/ROAS/CPA 等时间序列）
	•	detect_anomaly：定位异常对象（按 campaign/geo/creative）
	•	slice_compare：拆贡献（TopK 贡献/拖累项）
	3.	EVIDENCE 聚合：把趋势、异常、贡献、对比窗口合成 evidence_json
	4.	LLM 输出 structured JSON：
	•	summary / diagnosis
	•	root_causes（2~4条，每条≥2条证据 + how_to_validate）
	•	actions（2~5条，每条有风险/回滚 + 证据）
	•	confidence（样本不足会自动降低）

1:40-2:20 展示“结构化建议”亮点（可控、可评测、可复盘）
	•	不再泛泛而谈：字段固定
	•	每条建议可回滚
	•	evidence 里强制 source/key/value（可追溯）

2:20-3:00 展示评测与对比（我不是自嗨）
	•	我做了 50 条离线评测集 + baseline outputs（eval/）
	•	用 promptfoo 一键回归：跑同一批 case，输出 pass/fail + 延迟
	•	指标：参数抽取准确率、异常定位正确率、证据可追溯率、建议可执行率、幻觉率


Tips: “这套东西可以被集成：Dify Web App 可直接体验；FastAPI 已部署到 Render，可通过 API 调用。”
