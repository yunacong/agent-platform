# Dify Knowledge Base Setup（Day7）

## 1. Dataset 信息
- Dataset 名称：agent-platform-kb
- 文档数：5
- 文档列表：
  - kb/metric_definitions.md
  - kb/learning_phase_rules.md
  - kb/common_failure_cases.md
  - kb/action_playbook.md
  - kb/risk_and_rollback.md
- 状态：全部“可用”（索引完成）

## 2. 检索/分段参数（按设置页填写）
- 分段模式（UI显示）：通用
- top_k：3（右侧显示 3 个召回段落）
- score_threshold：无/未设置（若你设置页有就填具体数值）
- 备注：文档为 SOP/规则类，top_k=3 能兼顾准确性与覆盖面

## 3. 召回测试（10 条）
记录：Query / Expected / Actual / Pass / Notes

1) CTR、CVR、CPA、ROAS、ROI 的公式分别是什么？
- Expected: metric_definitions.md
- Actual: metric_definitions.md（核心指标公式）
- Pass: ✅
- Notes: 如出现 action_playbook 噪声，可考虑提高阈值或 top_k=2

2) 什么情况下要提示“小样本/低置信度”？阈值是多少？
- Expected: metric_definitions.md
- Actual: metric_definitions.md（小样本/分母为0）
- Pass: ✅
- Notes:

3) 学习期为什么不建议频繁调整？哪些操作会重置学习期？
- Expected: learning_phase_rules.md
- Actual: learning_phase_rules.md（学习期概念/触发操作）
- Pass: ✅
- Notes:

4) 学习期也必须出手的例外情况有哪些？
- Expected: learning_phase_rules.md
- Actual: learning_phase_rules.md（例外情况/触发操作）；risk_and_rollback.md（风险补充）
- Pass: ✅
- Notes: 召回合理补充

5) ROI/ROAS 下降的原因树怎么排查？主干有哪些？
- Expected: common_failure_cases.md
- Actual: common_failure_cases.md（原因树）；action_playbook.md（动作补充）
- Pass: ✅
- Notes:

6) 曝光稳定但点击下降（CTR 下降）原因是什么？建议怎么做？
- Expected: common_failure_cases.md + action_playbook.md
- Actual: （填写你实际看到的命中）
- Pass: ✅/❌
- Notes:

7) CPA 上升时怎么判断 CPC 上升还是 CVR 下降导致？
- Expected: common_failure_cases.md
- Actual: common_failure_cases.md（成本侧问题）；metric_definitions.md（公式补充）
- Pass: ✅
- Notes:

8) 什么情况下应该加预算？加多少？怎么验证？
- Expected: action_playbook.md
- Actual: action_playbook.md（Scale/验证/回滚）
- Pass: ✅
- Notes:

9) 必须写哪些风险提示？回滚策略怎么写？
- Expected: risk_and_rollback.md
- Actual: risk_and_rollback.md（风险清单/回滚策略）
- Pass: ✅
- Notes:

10) 数据延迟/归因窗口变化会导致什么误判？输出里怎么提示？
- Expected: metric_definitions.md + risk_and_rollback.md
- Actual: metric_definitions.md（延迟回填）；risk_and_rollback.md（风险）；common_failure_cases.md（口径变化）
- Pass: ✅
- Notes:

## 4. 截图清单（放到 docs/ 或作为提交记录）
- 图1：Dataset 文档列表（5 篇可用）
- 图2：召回测试示例（右侧显示来源文件名）
- 图3：设置页（top_k 等参数）
