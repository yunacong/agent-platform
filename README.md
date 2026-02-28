# Project 1: 运营/投放诊断 Agent 平台（含 Dify）

一句话：把“每天看盘→诊断→建议→导出报告”变成可复用的 Agent 工作流，并支持证据可追溯。

## 能做什么（MVP）
- 上传/粘贴指标数据（离线样例）
- 自动生成：异常诊断 + 可执行建议 + 证据引用
- 一键导出：Markdown 报告（后续可扩展 Doc/Notion）

## Repo 结构
- docs/：ONE_PAGER、PRD、指标口径、case库、迭代日志
- data_raw/、data_processed/：样例数据与处理结果
- backend/：FastAPI tools（供 Dify 调用）
- dify/：workflow 截图、导出配置说明
- eval/：promptfoo 评测用例与配置

## Roadmap
- Day1：定范围 + 建仓库骨架 + 写 ONE_PAGER
- Day2：指标口径 & 样例数据 & 诊断规则 v0


## Docs
- PRD: docs/PRD.md
- Workflow diagram: docs/flow.mmd


## Knowledge Base (for RAG)
- kb/metric_definitions.md
- kb/learning_phase_rules.md
- kb/common_failure_cases.md
- kb/action_playbook.md
- kb/risk_and_rollback.md
