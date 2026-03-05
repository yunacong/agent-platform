集成指南 — Dify Web App + API

本项目提供一个基于 Dify Workflow 的「广告诊断 Agent（Ad Diagnose Agent）」。
你可以通过 Web App 直接体验，也可以通过 API 集成到你自己的产品里。

⸻

1）Web App 演示（给面试官用）
	•	Demo 链接：https://udify.app/workflow/sfbKPdKzf6tCQ6SJ
	•	说明：
	•	WebApp 用于交互式演示。
	•	不要在公开页面中暴露任何 API Key。

⸻

2）API 集成（chat-messages）

Dify 提供服务端 API，可以把同样的能力嵌入到你自己的产品里。

2.1 获取 API Key

在 Dify Studio → 你的 App → API Access：
	•	点击创建一个新的 API Key（只会完整显示一次；请立即复制并安全保存）。

永远不要把 API Key 写进前端代码或公开仓库。

2.2 接口地址（Endpoint）

Dify Cloud 的接口为：
	•	POST https://api.dify.ai/v1/chat-messages

2.3 conversation_id 规则（重要）
	•	开启新对话：conversation_id 传空 / null / 或直接不传。
	•	Dify 会在响应里返回一个 conversation_id。
	•	延续同一对话：后续请求带上该 conversation_id，用于保持上下文。

Dify 说明：API 发起的对话与 WebApp 的对话是相互隔离的。

2.4 cURL 示例

export DIFY_API_KEY="<app-hWeAlJYPOFbrkhiio6NGLtlp>"
curl --location --request POST "https://api.dify.ai/v1/chat-messages" \
  --header "Authorization: Bearer $DIFY_API_KEY" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "inputs": {},
    "query": "近7天 ROI 掉了，按 campaign 下钻",
    "response_mode": "blocking",
    "conversation_id": "",
    "user": "interviewer-demo"
  }'
