# PRD｜运营/投放诊断 Agent 平台（Day4：流程&信息架构）

> 本 PRD 先写产品，不写技术实现。目标：让面试官一眼看到“你有完整的运营工作流 + 页面信息架构”。

---

## 1. 背景与问题（Why）
运营/投放人员每天需要看盘、查数、定位异常、写复盘。当前痛点：
- 耗时高：重复查数/对比/写总结
- 证据不可追溯：结论难复盘、难协作
- 建议不可执行：没有动作对象/阈值/验证方案
- 易误导：小样本/口径不一致导致错误结论

---

## 2. 目标（What）
产品目标（面向业务结果）：
- 诊断耗时下降（从“人工 30-60min”到“5-10min 可出初版”）
- 证据可追溯率提升（每条结论必须挂证据：数据切片/规则命中）
- 建议可执行率提升（动作明确、可验证、可回滚）
- 误导率下降（提示小样本、不确定性与假设）

非目标（Not now）：
- 不做真实下发投放（只给建议+导出）
- 不替代全量 BI（只做诊断/归因/建议/汇报）
- 不追求全行业通用（先打透投放看盘/复盘）

---

## 3. 用户（Who）
核心用户：
- 投放优化师（广告投放/商业化）
- 商家运营/增长运营（需要每日看盘与复盘）

用户诉求：
- 快速发现“ROI/ROAS 掉了”的原因
- 给出下一步动作（能落地、能验证）
- 把结果一键变成可分享的汇报材料

---

## 4. 典型场景（When）
1) 日常看盘（Daily）
- 早上打开：昨日/近7日表现是否异常？
- 需要：异常定位 + 快速建议 + 导出日报

2) 异常诊断（Troubleshooting）
- ROI 掉了/CPA 升了/CTR 掉了
- 需要：确定开始时间、影响面、可能原因、验证路径

3) 复盘汇报（Weekly/Campaign recap）
- 活动/大促后复盘
- 需要：结论+证据+建议+后续实验计划，一键导出

---

## 5. 核心工作流（How）
> 对齐 docs/flow.mmd

提问 → 澄清 → 查数 → 异常定位 → 归因拆解 → 建议 → 导出 → 反馈回流

澄清项（最少要问清）：
- 时间范围：昨日/近7日/自定义
- 目标 KPI：ROI/ROAS/CPA/CVR/CTR
- 分析维度：campaign/creative/audience/geo/device（先用 campaign 代理，后续扩展）
- 业务上下文：是否有素材/预算/落地页/活动变化

---

## 6. KPI（产品层）
效率类：
- 平均诊断耗时（TTR：time to reason）
- 导出耗时（生成报告时间）

质量类：
- 证据可追溯率：输出结论中带证据的比例
- 建议可执行率：建议中包含「动作+对象+阈值/范围+验证方式」的比例
- 误导率：被判定为错误/不严谨的结论比例（小样本、口径错误等）

结果类（可选）：
- 运营采纳率、复盘满意度（主观评分）

---

## 7. 页面信息架构（UI 模块）
> 目标：让输出结构可映射到 Dify 的 workflow 输出

页面/报告分为 5 个模块：

### 7.1 结论（TL;DR）
- 一句话总结：发生了什么（KPI、变化幅度、开始时间）
- 优先级：P0/P1/P2（影响程度+紧急程度）
- 建议概览：最关键的 1-3 条动作

### 7.2 异常定位（何时/多大/影响面）
- 异常开始时间：start_date
- 变化幅度：相对基线（昨日 vs 近3日/近7日均值）
- 影响面：贡献占比（哪个 campaign/维度贡献最大）

### 7.3 归因拆解（按维度对比）
- 维度拆分：campaign / creative / geo / device（当前版本可先做到 campaign）
- 漏斗拆解：impressions → clicks → conversions → revenue
- 假设列表：列 2-3 个可能原因（给置信度/证据）

### 7.4 建议动作（含风险/回滚）
每条建议必须包含：
- 动作：做什么（停/降预算/换素材/扩定向/回滚落地页等）
- 对象：对哪个 campaign/素材/地域
- 阈值/范围：调整多少
- 预期影响：对 CTR/CVR/CPA/ROAS 的方向与幅度（定性也可）
- 验证方式：看哪些指标、观察多久
- 风险与回滚：失败时怎么恢复

### 7.5 证据（指标引用/规则引用）
- 数据切片：关键表格/指标对比
- 规则命中：触发了哪些异常规则（RULES_V0）
- 口径提示：小样本/分母为0/归因窗口等风险提示

---

## 8. 交互与输出（Deliverables）
- 输入：选择时间范围 + KPI + 维度（可选） + 上传数据
- 输出：
  - 结构化诊断结果（JSON，用于工具/工作流）
  - Markdown 报告（用于导出与分享）

## 9.风险与治理
	•	风险1：幻觉/编造证据
	  •	表现：输出“看起来很对”但证据字段 source/key/value 对不上，或 citations 编造文件名
	  •	治理：
	        1.	LLM 输出强制 structured schema（root_causes/actions 必填 + evidence 对象结构）
	        2.	citations 不确定则输出 []（你已经这么做了）
	        3.	引入“幻觉率”指标（Day12 评测指标之一）
        
	•	风险2：错误建议（不具备回滚/风险说明）
	  •	表现：建议不可执行、不说明风险、不提供 rollback
	  •	治理：Day10 structured output 强制 risk/rollback 字段；当 baseline=-1 或 baseline revenue=0 时，要求 risk 写明“样本不足/口径异常”，confidence ≤ 0.5
    
	•	风险3：数据缺失/口径不一致导致误判
	  •	表现：compare_window baseline revenue=0 或 anomalies_top3 baseline=-1
	  •	治理：
	        1.	在证据聚合阶段（EVIDENCE）把这些信号显式写入 evidence_json
	        2.	LLM 强制降低 confidence
	        3.	建议动作里优先做“数据校验/扩大窗口/回放验证”

## 10.可观测性设计（Trace）
我们为每次诊断生成 trace（可用于排障、A/B对比、回归）：
	•	trace.user_query：原始问题
	•	trace.params：抽取后的参数（date_range/metric/dimension/goal）
	•	trace.tool_calls[]：工具调用记录（每一步 FastAPI API）
	•	name：query_metrics / detect_anomaly / slice_compare
	•	url
	•	request_payload
	•	status_code
	•	latency_ms
	•	error（失败时）
	•	trace.evidence_summary：证据摘要（top3 异常 + top5 贡献 + compare_window）
	•	trace.output：最终 structured_output
	•	trace.confidence：0~1

说明：
	•	Dify 自带 Tracing 可看节点耗时/状态；我们在 EVIDENCE/BASELINE 输出里保留 debug 字段，保证“证据链可追溯”。


## 11.迭代路线图
	•	MVP（已完成）
	    •	NL 参数抽取 → FastAPI 指标工具（trend/anomaly/slice）→ 证据组装 → structured 输出（含风险/回滚）
	    •	离线评测集 + baseline（50条） + promptfoo 回归跑通
      
	•	v1（可交付增强）
	    •	支持更多维度：adgroup/creative/geo/device/audience
	    •	支持更多动作：预算控制、出价策略、创意替换、受众收敛/扩量
	    •	引入“规则引用/强制引用”：把 KB 中关键规则作为 must_cite
      
	•	v2（工程化）
	    •	权限与审计：谁触发了诊断、谁改了参数、谁执行了动作建议（只给建议不自动执行）
	    •	多租户：workspace/advertiser_id 隔离；不同租户独立数据源与模型配置
	    •	监控与告警：异常阈值可配置；失败重试与降级（只出“数据异常提示+检查清单”）
