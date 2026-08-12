# OpenCode+Obsidian教程.docx

> **自动转换视窗** (原文件: `OpenCode+Obsidian教程.docx`)


OpenCode + Obsidian 深度整合教程

🧠 OpenCode + Obsidian：最强本地 AI 知识库工作流（全网整合版）

🧩 3. Obsidian 端需要安装什么？

3.1 安装 OpenCode for Obsidian 插件（可选但强烈推荐）

GitHub 项目：obsidian-opencode

功能：在 Obsidian 侧边栏嵌入 OpenCode Web IDE，自动启动 OpenCode 服务 Github。

优势：

不需要切换窗口

直接在 Obsidian 内写代码、调试、运行 AI

自动管理 OpenCode 服务

3.2 安装官方 Skills（Claude/Obsidian 专属）

博客园教程指出：Obsidian CEO 开源了三大 Skills，用于生成 Canvas、Markdown、结构化内容 博客园。

常用技能：

obsidian-markdown：生成高质量 Markdown

obsidian-bases：结构化数据库

json-canvas：自动生成 Canvas 思维导图

🧭 4. OpenCode + Obsidian 的最佳工作流（全网整合）

🧱 Step 1：在 Obsidian Vault 目录运行 OpenCode

cd ~/Obsidian/你的Vault

opencode

这样 OpenCode 能直接读写你的笔记。

🧠 Step 2：让 OpenCode 具备“Obsidian 大脑”

通过 Skills，你可以让 OpenCode 执行：

创建笔记

重构笔记

生成 Canvas

生成 Excalidraw

批量整理标签

生成 Dataview 查询

这些能力来自 Skills + MCP（全网教程一致强调） 博客园 CSDN博客。

🎨 Step 3：用 OpenCode 自动生成图表（全网最强技巧）

知乎实战经验指出：先生成 Mermaid，再转 Excalidraw 是最稳定的流程 知乎专栏。

示例提示词：

请使用 [SKILL名称] 在 [目录] 下创建一个 excalidraw 流程图，名称为 [文件名]。

请先用 mermaid 绘制流程，再转换为 excalidraw。

主题是：[你的主题]

为什么这样做？

Mermaid 结构清晰

Excalidraw 更美观

OpenCode 在 Mermaid → Excalidraw 的转换上最稳定（知乎实测） 知乎专栏

🗂 Step 4：自动整理 Obsidian 笔记

你可以让 OpenCode 执行：

批量重构笔记标题

自动生成摘要

自动生成标签

自动生成双向链接

自动生成 Dataview 查询

示例提示词：

请扫描当前 Vault，找出所有没有标签的笔记，并为它们生成合适的标签。

🧩 Step 5：在 Obsidian 内嵌 OpenCode IDE（可选）

使用 obsidian-opencode 插件，你可以：

在侧边栏运行 OpenCode

直接在 Obsidian 内写代码

让 AI 自动修改你的笔记

让 AI 生成图表并保存到 Vault

Github

🧨 5. 高阶玩法：多 Agent 协作（OpenCode 的杀手级能力）

CSDN 的保姆级教程指出：OpenCode 支持多 Agent 协作（类似 AutoGPT，但更稳定） CSDN博客。

你可以：

一个 Agent 负责整理笔记

一个 Agent 负责生成图表

一个 Agent 负责写总结

一个 Agent 负责生成 Canvas

示例：

agent("整理者").task("扫描 Vault 并生成知识结构图")

agent("画图者").task("根据结构图生成 Canvas")

agent("总结者").task("根据 Canvas 生成总结笔记")

🧱 6. 完整落地方案（从零到可用）

你需要准备：

Obsidian

OpenCode

Obsidian Skills

可选：obsidian-opencode 插件

你将获得：

自动生成笔记

自动整理知识库

自动生成图表（Mermaid → Excalidraw）

自动生成 Canvas

多 Agent 协作

本地私有化 AI 知识库（不依赖云端）

📦 7. 最终给你一套可直接复制的工作流模板

① 写作模板

请根据以下主题生成 Obsidian Markdown 笔记：

- 结构化大纲

- 关键要点

- 反思与行动项

主题：[主题]

② 知识整理模板

请扫描当前 Vault，找出重复笔记、无标签笔记、结构混乱笔记，并生成一份整理计划。

③ 图表模板

请使用 obsidian-markdown 在 /图表 目录下创建一个流程图。

主题：[主题]

请先生成 Mermaid，再生成 Excalidraw。

④ Canvas 模板

请使用 json-canvas 在 /Canvas 目录下创建一个 Canvas 思维导图。

主题：[主题]

想进一步，我可以为你做什么？

你现在已经有了全网最完整的 OpenCode + Obsidian 教程。如果你愿意，我可以为你：

👉 定制一套适合你个人知识库的自动化工作流（含提示词 + 文件结构 + 自动化脚本）

你希望我按 程序员工作流、知识管理工作流、还是 AI 研发工作流 来定制？

文章核心观点：2026 年个人 AI 知识库的最优解

作者提出一个清晰的两分法：

自己的内容 → 放进 Obsidian（本地 Markdown，主权、安全、可被 AI 深度操作）

外部内容 → 放进 NotebookLM（强大的外部资料处理能力）

这套组合被称为“前店后厂”式知识管理体系。

🧠 为什么“自产内容”必须放进 Obsidian？

文章强调 数据主权 和 AI 可操作性：

Markdown 本地存储：完全掌控数据，不被 Notion/OneNote 等平台锁死。

可被任意 AI 工具操作：本地 MD 文件能被 Claude Code、OpenCode、Skills、MCP 等工具直接读写。

避免平台 AI 绑架：不依赖某个软件的付费 AI 服务。

作者使用两种 AI 接入方式：

轻方案：Codia（Claude Code 插件） 直接在 Obsidian 内使用 Claude Code，安装简单，但 Mac 初次启动可能遇到 code 127 错误，可通过填写完整路径解决。

重方案：OpenCode 直接在笔记仓库目录运行 OpenCode，让 Obsidian 退居为编辑器，OpenCode 作为前端。 支持多 Agent、本地模型、自定义命令、MCP，且无需迁移数据。

📚 为什么“外部信息”交给 NotebookLM？

作者把 NotebookLM 当作“外部世界的情报处理中心”：

处理能力极强：尤其是 PDF、长文、YouTube 视频等复杂内容。

Deep Research 功能：可自动扩展搜索相关内容，形成完整知识链路。

隐私不敏感：外部内容本身不涉及个人隐私，适合交给云端处理。

⚙️ 作者的自动化工作流（前店后厂模式）

文章描述了一个非常实用的双屏 + 自动化体系：

Obsidian（上屏）：最终编辑、知识沉淀。

OpenCode（下屏 iPad）：与 AI 深度对话、调度 Agent、批量处理笔记。

自动化示例：

自动周报：AI 每周扫描收藏文章 → 自动生成结构化报告 → 存入指定文件夹。

多 Agent 协作：OpenCode 负责复杂任务，如批量重构笔记、生成图表、知识库清洗。

🧭 作者的最终结论

Obsidian 是 “私人保险柜”：存放最核心的原创思考（本地、可控、可被 AI 操作）。

NotebookLM 是 “全球情报处理中心”：处理外部世界的复杂信息。

OpenCode 是 “AI 工作台”：让 Obsidian 的知识库真正具备自动化与智能化能力。

🎯 实践建议（来自文章）

所有原创内容必须本地化（Markdown）。

外部内容交给 NotebookLM 做深度处理。

使用 OpenCode + Skills 打造自动化知识库。

通过双屏布局提升效率（Obsidian 编辑 + OpenCode 对话）。

如果你愿意，我可以把这篇文章的内容 转写成一份可直接放进你 Obsidian 的笔记模板，包括结构化标题、标签、Dataview 属性和行动项。