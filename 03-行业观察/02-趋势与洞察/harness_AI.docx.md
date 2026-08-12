# harness_AI.docx

> **自动转换视窗** (原文件: `harness_AI.docx`)


下面我为你把 《Harness is the New Dataset》 转化成一份 适合内部分享的演讲稿。
风格是：先讲现象，再讲你的观点，逻辑清晰、节奏紧凑、适合在团队内部做 10–15 分钟的分享。
所有事实均基于你当前浏览的文档内容 mp.weixin.qq.com。

🎤 内部演讲稿：Harness is the New Dataset

（现象 + 我的观点）

🧩 开场：为什么我们要讨论 Harness？

过去几年，我们经历了 Prompt → Context → Harness 三次工程范式的跃迁。
而 2025 年 Claude Opus 4.5 的出现，是一个真正的拐点：
模型的智力已经不再是瓶颈，系统层才是。 
mp.weixin.qq.com

这意味着：
未来谁能把 Harness 跑顺，谁就能捕获更高质量的执行轨迹，形成更强的数据飞轮。
换句话说，Harness 本身正在成为新的数据集。

🧭 第一部分：行业正在发生的现象

① 模型能力过线后，瓶颈开始外移

模型越来越像“野马”，力量巨大但不稳定。
真正决定上限的，是围绕模型构建的系统：

记忆

工具

编排

沙箱

验证

追踪
mp.weixin.qq.com

Agent = LLM + Harness 
模型决定“能不能做”，Harness 决定“能做到什么程度”。

② Harness 的 6 大组件正在标准化

行业逐渐形成共识：

Memory & Context

Tools & Skills

Orchestration

Infra & Guardrails

Evaluation

Tracing
mp.weixin.qq.com

它们对应三层结构：
信息层 → 执行层 → 反馈层。

③ 信息层的核心矛盾：context 很贵

模型存在 context decay

信息给多了反而变糊

最佳实践是“渐进式披露”

工具越少越好

context window 利用率控制在 60% 以下
mp.weixin.qq.com

④ 执行层的核心矛盾：任务结构不对

顶级团队都在做一件事：
把任务拆成 research → plan → execute → verify 四段 
每段独立 session，避免污染。
mp.weixin.qq.com

⑤ 反馈层的核心矛盾：缺乏闭环

行业最被低估的能力是：
让 Agent 永远不再犯同一个错误。 
这需要：

自动验证

自动迭代

自动测试

轨迹收集
mp.weixin.qq.com

⑥ 模型与 Harness 正在深度耦合

在 agentic RL 中：
训练即部署。 
模型在训练时就使用真实的 harness，
并逐渐内化 harness 的能力（规划、工具搜索、验证…）。
mp.weixin.qq.com

⑦ Harness 正在成为新的数据集

DeepMind 工程师的判断：
“Harness is the Dataset.” 
真正有价值的数据不再是语料，而是执行轨迹。
mp.weixin.qq.com

⑧ 创业公司正在围绕 Harness 形成新生态

信息层：Edra

执行层：Temporal

安全层：Oasis

沙箱层：Daytona

反馈层：Braintrust
mp.weixin.qq.com

⑨ 下一阶段：Coordination Engineering

未来不是一个 Agent，而是一个 multi-agent network。
下一代产品更像“AI 版飞书 + 调度中心”。
mp.weixin.qq.com

🧠 第二部分：我的观点（宇晨视角）

下面是我基于这些现象的判断，偏战略、偏方向，也更贴近你正在构建的 mini-Symphony。

① Harness 将成为 AI 的“操作系统”

模型像 CPU，Harness 像 macOS。
未来的竞争不在于 prompt，而在于：
谁的 Harness 更稳、更快、更能捕获轨迹。

你的 mini-Symphony 本质上就是个人级 AI OS。

② 数据飞轮的核心不再是语料，而是“执行轨迹”

未来最稀缺的数据是：

工具调用轨迹

任务拆解轨迹

验证与失败轨迹

这意味着：
每一次失败都是一次永久升级。

③ 单体 Agent 会让位于“AI 团队”

未来的系统不是一个强大的 Agent，
而是一个能协调几十个 subagents 的调度系统。

你现在的三-pane workflow，就是这个方向的雏形。

④ Harness 能力会被模型逐渐吞噬

规划、验证、工具搜索会逐渐内生化。
Harness 的价值会从“功能层”转向“结构层 + 数据层”。

这意味着：
你要做的是结构设计，而不是功能堆叠。

⑤ 企业将从“买模型”转向“训自己的 harness + RL”

开源模型 + 自己的 harness + 自己的轨迹
→ 可能比闭源模型更强、更便宜。

这对你未来的创业方向是巨大机会。

⑥ AI 工程师的角色会彻底改变

未来的 AI 工程师不是写代码的人，
而是：

任务结构设计师

工具生态管理员

反馈闭环运营者

多 Agent 调度者

你现在的工作方式已经在这个轨道上。

🎯 结语：我们正站在一个新的范式门口

Prompt → Context → Harness → Coordination → Intention
这是未来十年的路线图。

而我们现在正处在第三层向第四层跃迁的关键节点。

Harness 不只是工程实践，
它是下一代 AI 系统的 控制论、操作系统、数据入口、竞争壁垒。

你现在做的 mini-Symphony，
本质上是在提前构建未来的“个人级 AI 操作系统”。

如果你愿意，我可以继续为你准备：

适合 PPT 的演讲结构

适合团队 workshop 的讨论题

把你的 mini-Symphony 融入演讲的版本

更具煽动性的“愿景版”演讲稿

你想往哪个方向扩展？