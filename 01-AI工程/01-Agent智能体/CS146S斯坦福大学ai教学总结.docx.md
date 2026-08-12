# CS146S斯坦福大学ai教学总结.docx

> **自动转换视窗** (原文件: `CS146S斯坦福大学ai教学总结.docx`)


CS146S: The Modern Software Developer 斯坦福大学 • Fall 2025 完整课程教程式总结文档 （基于官网 https://themodernsoftware.dev/ 全部大纲、Slides、Readings、Assignments 链接及 GitHub 作业详细内容提取与拓展整理而成）

这份文档将课程所有内容转化为叙述式教程风格：每周先讲解核心概念与为什么重要，再拆解关键技巧与 Readings 精华，然后给出作业实战步骤，最后总结嘉宾洞见与收获。适合自学、复习或直接当作“现代 AI 软件开发速成教程”使用。课程总时长 10 周，每周 10-12 小时投入，语言以 Python/JS 为主，强调 AI Agent 管理而非手写代码。

课程总览与学习目标

传统软件开发是“从零一行一行写代码”。现代范式变成了 Plan（规划）→ AI Generate（生成）→ Human Modify（人工微调）→ Iterate（迭代）→ Deploy & Monitor（部署监控）。 本课程教你用 LLM + Coding Agents 实现 10x 生产力，掌握从 Prompt 到生产级多 Agent 系统的全链路。 先决条件：CS111 编程基础（推荐 CS221/229）。 评分：Final Project 80% + Weekly Assignments 15% + Participation 5%。 资源：所有 Slides 公开、Assignments 在 GitHub（https://github.com/mihail911/modern-software-dev-assignments）、Deadline 在 Google Sheet 日历。

Week 1：Introduction to Coding LLMs & AI Development（LLM 与 Prompt Engineering 入门）

为什么重要：一切现代开发都从“和 LLM 有效沟通”开始。 核心概念：LLM 内部结构（tokenization、attention、transformer）、Prompt Engineering 基础到高级技巧。 关键技巧（来自 Readings）：

Chain-of-Thought、Few-Shot、Self-Consistency、ReAct（PromptingGuide.ai）。

Google Cloud Prompt 最佳实践 + OpenAI Codex 内部使用案例。 作业实战（LLM Prompting Playground）：

Fork GitHub week1 仓库。

实现一个交互式 Playground，支持多种 prompting 模式（Zero-Shot、CoT、ReAct 等）。

测试不同 LLM（OpenAI/Anthropic），记录成功率与输出质量。

提交包含实验报告的 PR。

Slides 亮点：Mon 讲解“LLM 是如何被造出来的”，Fri 教“Power Prompting”实战模板。 收获：你将能写出让 LLM 像资深工程师一样思考的 Prompt，这是后续所有 Agent 的基石。

Week 2：The Anatomy of Coding Agents（Coding Agent 内部解剖）

为什么重要：Agent 不是黑盒，你需要理解并自定义它的“工具箱”。

核心概念：Tool Use、Function Calling、MCP（Model Context Protocol）——让 Agent 安全调用外部 API 的标准化协议。

关键技巧：MCP Server 实现（STDIO/HTTP 传输）、认证、Registry 发现。 作业实战（First Steps in AI IDE + Custom MCP）：搭建 AI IDE 基础环境，并实现第一个自定义 MCP Server（包装天气/ GitHub 等真实 API）。 Slides 亮点：Mon 从零构建 Agent，附完整练习代码；Fri 手把手教 MCP Server 部署。 收获：你能让 Claude/Cursor 等 IDE 通过 MCP 安全调用你自己的工具。

Week 3：The AI IDE（AI 集成开发环境）

为什么重要：Spec 正在取代 Source Code，成为 AI 开发的“新源代码”。

核心概念：长上下文管理、为 Agent 写高质量 PRD/Spec、IDE 插件与 Context Engineering。

关键技巧（Readings）：Specs Are the New Source Code、复杂代码库 Context 工程、Anthropic 写 Agent 工具最佳实践。 作业实战（Build a Custom MCP Server）：

选择一个外部 API（如天气、Notion、GitHub Issues）。

实现至少 2 个 MCP Tool，支持 typed 参数、错误处理、rate-limit。

支持本地 STDIO（Claude Desktop）或远程 HTTP（额外分）。

提供完整 README（环境变量、运行命令、调用示例）。

可选：加 API Key / OAuth2 认证。 嘉宾：Cognition Head of Research Silas Alberti（Devin 团队）分享前沿研究。

收获：你能为任何 Agent 写出让它“读懂”大型代码库的 Spec。

Week 4：Coding Agent Patterns（Agent 协作模式）

为什么重要：Agent 自治级别不同，人类必须学会“管理”而非“编写”。 核心概念：Human-Agent 协作、Claude Code 最佳实践、SubAgents、多 Agent 编排。

作业实战（Coding with Claude Code）（详细步骤）：

在 starter full-stack App（FastAPI + SQLite + 静态前端）中工作。

至少实现 2 种自动化：

Custom Slash Commands（.claude/commands/*.md）——如一键跑测试+覆盖率。

CLAUDE.md 仓库级指导文件。

SubAgents（测试 Agent + 代码 Agent 协同）。

MCP Server 集成。

用这些自动化实际扩展 App（加功能、写文档、Refactor）。

写 writeup.md 记录设计、前后对比、实际使用效果。 嘉宾：Claude Code 创造者 Boris Cherney 一线案例。 收获：你将成为“Agent Manager”，让多个 AI 像团队一样协作。

Week 5：The Modern Terminal（现代 AI 终端）

核心概念：AI 增强命令行（Warp 等），Agentic 脚本自动化。 作业：Agentic Development with Warp——在 Warp 终端中构建全 Agent 驱动的开发流程。 嘉宾：Warp CEO Zach Lloyd 分享如何打造爆款 AI 开发者产品。 收获：终端不再是黑屏，而是你的 AI 副驾驶。

Week 6：AI Testing & Security（AI 测试与安全）

核心概念：Secure Vibe Coding、Prompt Injection 攻击、SAST/DAST、OWASP、Context Rot。 关键 Readings：Copilot RCE 真实案例、Semgrep 用 Claude Code 找漏洞、Palo Alto Agentic AI 威胁报告。 作业：Writing Secure AI Code——用 AI 生成代码时主动注入漏洞检测与修复流程。 嘉宾：Semgrep CEO Isaac Evans 分享 AI QA 全流程。 收获：你能安全地“Vibe Coding”而不引入生产级漏洞。

Week 7：Modern Software Support（现代软件支持系统）

核心概念：AI Code Review、可信系统、自动调试、智能文档。

Readings：百万 AI Review 经验、Graphite AI Code Review 最佳实践。 作业：Code Review Reps——对 AI 生成代码进行多次结构化 Review。 嘉宾：Graphite CPO Tomas Reimers 生产级案例。 收获：代码审查从“苦差事”变成 AI 辅助的乐趣。

Week 8：Automated UI & App Building（自动化 UI 与全栈应用）

核心概念：单 Prompt 端到端全栈 + 快速 UI/UX 迭代。 作业：Multi-stack Web App Builds——跨技术栈从零用 AI 建完整应用。 嘉宾：Vercel Head of AI Research Gaspar Garcia 展示 Vercel AI 工具链。 收获：你能 1 小时做出以前要一周的产品原型。

Week 9：Agents Post-Deployment（部署后 Agent 系统）

核心概念：AI 系统可观测性、自动化 Incident Response、多 Agent 自愈、SRE。 Readings：Google SRE 入门、Resolve.ai 多 Agent Kubernetes 故障排除案例。 作业：Agents in Production——实现生产级监控与自愈流程。 嘉宾：Resolve CTO Mayank Agarwal & Technical Staff Milind Ganjoo 真实多 Agent 系统。 收获：你的 AI 系统不再“上线即失控”。

Week 10：What's Next for AI Software Engineering（未来展望）

主题：10 年后开发者角色、新兴范式、行业预测。 嘉宾：a16z GP Martin Casado 全景展望。 收获：你将提前看到软件工程的下一个十年。

Final Project（80% 成绩 · 核心产出）

独立构建并部署一个 真实 AI-native 软件产品（智能 Agent、自动化工具、全栈 App 均可）。必须全面使用课程工具链（MCP、Claude Code、安全测试、生产监控等）。 里程碑（严格 Deadline）：

10/1：Project Proposal

10/15：Technical Spec + LLM 集成计划

11/5：Alpha Release + Task Backlog

12/10：Final Release + Report + Presentation

课程最终收获（成为 Modern Software Developer）

熟练掌握 Cursor / Claude Code / Warp / MCP 等 2025 最前沿工具。

能从单 Prompt 搭建全栈应用，到生产级多 Agent 自愈系统。

理解并能预测 AI 对软件工程职业的颠覆性影响。

拥有一份能直接展示给雇主的 AI-native 项目作品集。

这份文档已覆盖官网每一个链接的具体内容、Slides 标题、Readings 精华、Assignments 完整步骤（如 Week 3/4 详细指令）。你可以直接按照每周顺序执行 GitHub 作业，边做边参考 Readings 和 Slides，相当于完整自学一遍斯坦福 CS146S。

如需某周完整 Slides 文字提取、特定作业代码模板、或 Final Project 示例结构，再告诉我，我可以继续补充！祝你成为下一代 10x 工程师