# OpenCode新手完全教程.docx

> **自动转换视窗** (原文件: `OpenCode新手完全教程.docx`)


OpenCode

新手完全教程

从零开始掌握 AI 编码助手

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

版本 1.0  |  2026 年 4 月

基于 OpenCode + Oh My OpenCode + Superpowers 完整生态

第一章  OpenCode 简介

1.1 什么是 OpenCode？

OpenCode 是一个基于 AI 的终端编码助手（Terminal-based AI Coding Agent），它允许开发者通过自然语言与 AI 进行交互，完成代码编写、调试、重构、文档生成等各类开发任务。与传统的 IDE 插件不同，OpenCode 以独立的命令行工具运行，具有完整的代码库理解能力和自主执行能力。

OpenCode 的核心特点包括：

🤖 多模型支持 — 可配置多种 AI 模型（Qwen、GLM、Claude、Gemini 等）

🔧 工具集成 — 内置文件操作、代码搜索、LSP 语言服务器、Git 操作等

🧠 上下文感知 — 理解整个代码库的结构和模式

⚡ 插件系统 — 通过插件扩展功能（如 Oh My OpenCode、Superpowers）

🎯 技能系统 — 可自定义可复用的专业工作流

🔄 多 Agent 协作 — 支持探索、规划、实现、审查等角色分工

1.2 OpenCode 生态架构

OpenCode 的完整生态由以下核心组件构成：

1.3 适用人群

本教程适合以下读者：

从未使用过 AI 编码助手的开发者

了解 Claude Code / Cursor 等工具，想迁移到 OpenCode 的开发者

希望深度定制 AI 编码工作流的资深开发者

技术团队负责人，希望为团队搭建标准化 AI 编码环境

第二章  安装与配置

2.1 环境要求

2.2 安装 OpenCode

方法一：使用 npm 全局安装（推荐）

npm install -g opencode-ai

方法二：使用 npx 直接运行（无需安装）

npx opencode-ai@latest

💡 提示: npx 方式适合快速体验，但每次启动都需要下载，建议长期使用 npm 全局安装。

验证安装

opencode --version

如果显示版本号（如 1.3.3），说明安装成功。

Windows 常见问题

如果遇到「'opencode' 不是内部或外部命令」的错误，需要将 npm 全局目录添加到 PATH：

# PowerShell（永久添加） [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\$env:USERNAME\AppData\Roaming\npm", "User")

添加后需要重启终端。

2.3 初始化配置

首次运行 OpenCode 时，它会在以下位置创建配置目录：

# Windows C:\Users\<用户名>\.config\opencode\

该目录包含以下关键文件：

2.4 配置模型（opencode.json）

opencode.json 是 OpenCode 的核心配置文件，定义了使用的 AI 模型、MCP 服务器、插件等。以下是一个基础配置示例：

{   "$schema": "https://opencode.ai/config.json",   "model": "zhipuai-coding-plan/glm-4.6",   "small_model": "zhipuai-coding-plan/glm-4.5-air",   "provider": {     "zhipuai-coding-plan": {       "options": {         "apiKey": "你的API密钥"       }     }   } }

📌 说明: model 字段格式为 provider/model-name。你需要先在对应平台注册并获取 API Key。

常用模型提供商配置

// 百炼平台（阿里云） "bailian-coding-plan": {   "npm": "@ai-sdk/anthropic",   "name": "Model Studio Coding Plan",   "options": {     "baseURL": "https://coding.dashscope.aliyuncs.com/apps/anthropic/v1",     "apiKey": "sk-你的密钥"   },   "models": {     "qwen3.5-plus": {       "name": "Qwen3.5 Plus",       "limit": { "context": 1000000, "output": 65536 }     }   } }

2.5 安装 Oh My OpenCode 增强插件

Oh My OpenCode 是一个强大的增强插件，提供了多 Agent 矩阵、分类调度、性能优化等功能。

# 在 opencode.json 的 plugin 字段中添加 "plugin": [   "oh-my-opencode@latest" ]

安装后，Oh My OpenCode 会提供以下核心能力：

多 Agent 矩阵：Sisyphus（编排）、Hephaestus（深工）、Oracle（架构顾问）等

分类调度：visual-engineering、ultrabrain、quick 等任务类别自动路由

性能优化：根据任务复杂度自动选择最合适的模型

2.6 安装 Superpowers 工作流

Superpowers 是一套标准化的软件开发工作流，包含 TDD、代码审查、并行开发等功能。

Windows PowerShell 安装

# 1. 克隆 Superpowers git clone https://github.com/obra/superpowers.git "$env:USERPROFILE\.config\opencode\superpowers"

# 2. 创建目录 New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\opencode\plugins" New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\opencode\skills"

# 3. 创建符号链接（需要开发者模式或管理员权限） New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.config\opencode\plugins\superpowers.js" -Target "$env:USERPROFILE\.config\opencode\superpowers\.opencode\plugins\superpowers.js"

# 4. 创建技能目录连接 New-Item -ItemType Junction -Path "$env:USERPROFILE\.config\opencode\skills\superpowers" -Target "$env:USERPROFILE\.config\opencode\superpowers\skills"

⚠️ 注意: Windows 创建符号链接需要启用「开发者模式」：设置 → 系统 → 开发者选项 → 开启开发者模式。

2.7 安装 MCP 服务器（可选）

MCP（Model Context Protocol）服务器为 OpenCode 提供外部工具集成能力。

// 在 opencode.json 中配置 MCP "mcp": {   "chrome-devtools": {     "type": "local",     "command": ["npx", "-y", "chrome-devtools-mcp@latest"]   },   "zai-mcp-server": {     "type": "local",     "command": ["npx", "-y", "@z_ai/mcp-server"]   } }

第三章  核心概念

3.1 会话（Session）

OpenCode 以会话为单位工作。每次启动 OpenCode 并进入一个项目目录时，就创建了一个新的会话。会话中包含了：

你与 AI 的完整对话历史

AI 执行的所有操作记录

当前项目的上下文信息

你可以通过自然语言与 AI 交流，AI 会自动理解你的意图并执行相应操作。

3.2 Agent 系统

OpenCode 支持多 Agent 协作，每个 Agent 有专门的角色和职责：

📌 说明: 你不需要手动调用这些 Agent，Oh My OpenCode 会根据任务类型自动路由到合适的 Agent。

3.3 技能系统（Skills）

技能（Skills）是 OpenCode 的核心扩展机制。每个技能是一个独立的 Markdown 文件（SKILL.md），定义了：

触发条件（description）

详细的工作流程和操作指南

所需的工具和依赖

技能优先级

OpenCode 按以下优先级发现技能：

项目技能（.opencode/skills/）— 最高优先级

个人技能（~/.config/opencode/skills/）

Superpowers 技能（~/.config/opencode/skills/superpowers/）

如何创建自定义技能

# 创建技能目录 mkdir -p ~/.config/opencode/skills/my-skill

# 创建 SKILL.md 文件 --- name: my-skill description: 当 [条件] 时使用 - [功能描述] ---   # My Skill   [技能详细说明和工作流程]

3.4 任务分类（Categories）

Oh My OpenCode 提供了任务分类系统，自动将任务路由到最适合的模型：

3.5 AGENTS.md — AI 行为指令

AGENTS.md 是定义 AI Agent 行为准则的核心文件。它告诉 AI：

如何思考和分解问题

应该遵循哪些工作流

什么情况下应该委托给子 Agent

代码规范和项目约定

验证和质量保证要求

你可以在项目根目录放置 AGENTS.md 来定义项目特定的行为规范。全局 AGENTS.md 位于 ~/.config/opencode/AGENTS.md。

第四章  日常使用

4.1 启动 OpenCode

# 进入你的项目目录 cd C:\path\to\your\project   # 启动 OpenCode opencode

启动后，你会进入交互式对话界面。可以直接用自然语言描述你的需求。

4.2 基本交互方式

直接对话

最简单的方式就是直接告诉 AI 你想做什么：

> 帮我创建一个用户登录功能，包含邮箱和密码验证

指定文件操作

> 修改 src/auth/login.ts 中的错误处理逻辑

代码库探索

> 帮我找一下项目中所有处理 HTTP 请求的地方

4.3 常用操作示例

创建新文件

> 在 src/utils/ 下创建一个日期格式化工具函数

修改现有代码

> 把 src/api/users.ts 中的回调改为 async/await 风格

调试问题

> 这段代码报 TypeError: Cannot read property 'name' of undefined > 帮我找出原因并修复

重构代码

> 重构 src/services/ 目录，提取公共逻辑到基类

生成文档

> 为 src/api/ 下的所有路由处理函数生成 JSDoc 注释

4.4 工具使用

OpenCode 内置了多种工具，AI 会自动选择适合的工具完成任务：

4.5 Git 集成

OpenCode 可以执行所有常见的 Git 操作：

查看状态和差异（git status, git diff）

提交更改（git commit）

创建和管理分支（git branch, git checkout）

创建 Pull Request（通过 gh 命令）

查看提交历史（git log）

📌 说明: AI 默认不会自动提交代码，除非你明确要求。这避免了意外提交不完整的工作。

4.6 多项目管理

OpenCode 是项目感知的。每次启动时需要指定项目目录：

# 方式一：cd 到项目目录后启动 cd /path/to/project && opencode   # 方式二：直接指定项目路径 opencode /path/to/project

每个项目可以有独立的配置：

项目级 AGENTS.md（.opencode/AGENTS.md）

项目级 Skills（.opencode/skills/）

项目级配置（.opencode/opencode.json）

第五章  Superpowers 标准化工作流

5.1 工作流概览

Superpowers 提供了一套标准化的软件开发流程，确保 AI 的工作质量可控、可追溯。完整流程如下：

5.2 头脑风暴（Brainstorming）

在开始编码前，brainstorming 技能会通过苏格拉底式提问来明确你的真实需求：

你想要解决什么问题？

有哪些可能的方案？

每种方案的优缺点是什么？

最终确定哪种方案？

触发方式：描述一个功能需求时自动触发。

5.3 测试驱动开发（TDD）

Superpowers 强制执行标准的 TDD 循环：

RED — 编写一个失败的测试

GREEN — 编写最少的代码让测试通过

REFACTOR — 重构代码，保持测试通过

💡 提示: TDD 确保每一行代码都有测试覆盖，大幅降低回归 Bug 的概率。

5.4 子 Agent 驱动开发

对于复杂任务，Superpowers 会将工作分解为多个独立任务，并并行分发给不同的子 Agent：

每个子 Agent 独立工作在一个任务单元上

完成后自动进行规范符合性审查

再进行代码质量审查

通过后才合并到主分支

5.5 代码审查

每次任务完成后，自动触发代码审查：

对照计划检查是否完成所有要求

检查代码质量和最佳实践

严重问题会阻止进度

生成审查报告供你确认

第六章  进阶配置

6.1 自定义系统提示（AGENTS.md）

AGENTS.md 是控制 AI 行为的最强大工具。你可以定义：

# 项目级 AGENTS.md 示例   ## 项目约定 - 使用 TypeScript 严格模式 - 所有 API 响应必须符合 JSON Schema - 错误处理使用自定义 Error 子类   ## 开发流程 1. 修改前先理解现有代码 2. 小步提交，每次提交一个逻辑单元 3. 完成后运行 npm test 验证   ## 禁止事项 - 不要使用 any 类型 - 不要删除测试文件 - 不要修改构建配置

6.2 性能调优

Oh My OpenCode 提供了性能优化配置（oh-my-opencode.json）：

6.3 LSP 语言服务器配置

LSP（Language Server Protocol）为 AI 提供代码理解能力，包括跳转定义、查找引用、类型检查等：

// opencode.json 中的 LSP 配置 "lsp": {   "pyright": {     "command": ["pyright-langserver", "--stdio"],     "extensions": [".py", ".pyi"]   },   "typescript": {     "command": ["typescript-language-server", "--stdio"],     "extensions": [".ts", ".tsx", ".js", ".jsx"]   } }

💡 提示: 安装 LSP 服务器：npm install -g typescript-language-server typescript（TypeScript）或 pip install pyright（Python）。

6.4 自动更新配置

OpenCode 提供了自动更新脚本：

# 手动更新 C:\Users\<用户名>\.config\opencode\scripts\update-opencode.bat   # 设置每日自动更新（管理员权限） C:\Users\<用户名>\.config\opencode\scripts\setup-auto-update-scheduler.bat

第七章  常见问题与故障排除

7.1 安装问题

Q: 安装后 opencode 命令找不到

原因：npm 全局目录不在 PATH 中。

解决：

# PowerShell（永久添加） [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\$env:USERNAME\AppData\Roaming\npm", "User")

添加后重启终端。

Q: npm install 权限错误

解决：以管理员身份运行终端，或修改 npm 全局目录权限：

takeown /f C:\Users\<用户名>\AppData\Roaming\npm\node_modules\opencode-ai /r /d y icacls C:\Users\<用户名>\AppData\Roaming\npm\node_modules\opencode-ai /grant %USERNAME%:F /t

7.2 配置问题

Q: AI 响应很慢

可能原因和解决方案：

模型选择：简单任务使用 quick 分类（自动路由到快模型）

Variant 设置：使用 low variant 减少推理深度

网络延迟：检查 API 连接稳定性

上下文过大：对话历史太长会拖慢响应，可以开新会话

Q: API 调用失败 / 认证错误

检查清单：

确认 API Key 正确且未过期

确认模型名称拼写正确（provider/model-name 格式）

确认账户余额充足

检查网络连接（特别是企业防火墙）

Q: 技能（Skills）不生效

排查步骤：

确认 SKILL.md 文件存在且格式正确（需要 YAML frontmatter）

确认 skills 配置中 enabled: true

使用 skill 工具列出所有可用技能，确认被发现

检查 description 字段是否准确描述了触发条件

7.3 Superpowers 问题

Q: Superpowers 插件未加载

排查步骤：

确认插件文件存在：

dir "$env:USERPROFILE\.config\opencode\superpowers\.opencode\plugins\superpowers.js"

确认符号链接正确：

Get-ChildItem "$env:USERPROFILE\.config\opencode\plugins" | Where-Object { $_.LinkType }

检查 OpenCode 日志：

opencode run "test" --print-logs --log-level DEBUG

Q: Windows 符号链接创建失败

原因：需要开发者模式或管理员权限。

解决：

方法一：开启开发者模式（设置 → 系统 → 开发者选项）

方法二：以管理员身份运行终端

方法三：使用 Junction 代替 Symbolic Link（目录连接）

7.4 日常使用问题

Q: AI 没有按照我的要求做

改进方法：

更明确地描述需求，包含具体的文件路径和期望结果

使用 AGENTS.md 定义项目约定和禁止事项

对于重要要求，使用强调语气（如「必须」「禁止」）

如果 AI 偏离方向，直接指出问题并要求修正

Q: 对话上下文太长导致响应变慢

解决：

开启新的会话（退出后重新 opencode）

在 AGENTS.md 中定义关键约定，这样新会话也能继承

使用 /handoff 命令创建上下文摘要，然后在新会话中继续

Q: 如何备份配置？

推荐定期备份以下目录：

~/.config/opencode/opencode.json（主配置）

~/.config/opencode/AGENTS.md（行为指令）

~/.config/opencode/oh-my-opencode.json（性能配置）

~/.config/opencode/skills/（自定义技能）

# 备份到指定目录 cp -r ~/.config/opencode D:\backup\opencode-config-$(date +%Y%m%d)

第八章  进阶技巧与最佳实践

8.1 高效使用技巧

1. 善用上下文

OpenCode 会自动读取项目结构。在对话中引用具体文件路径可以大幅提高 AI 的准确性：

# 好的提问方式 > 修改 src/auth/jwt.ts 中的 token 验证逻辑，参考 src/auth/middleware.ts 中的现有模式   # 不好的提问方式 > 帮我改一下认证

2. 分步执行

对于复杂任务，建议分步进行：

先让 AI 分析现有代码结构

确认方案后再让 AI 制定计划

审查计划后批准执行

每完成一个阶段就验证结果

3. 利用并行 Agent

OpenCode 支持并行执行多个探索任务。当需要了解代码库时，可以让多个 explore agent 同时搜索不同方面，大幅提高效率。

8.2 项目初始化最佳实践

为新项目配置 OpenCode 的推荐步骤：

创建项目级 AGENTS.md，定义代码规范和开发流程

配置适合项目的模型（考虑速度和质量的平衡）

安装 LSP 服务器以获得更好的代码理解

创建项目级 Skills 封装常见操作模式

配置 Git hooks 确保代码质量

8.3 团队协作配置

在团队中使用 OpenCode 的建议：

将 AGENTS.md 提交到版本控制，确保团队使用统一的 AI 行为规范

创建团队共享的 Skills 库，封装常见的开发模式

使用 oh-my-opencode.json 统一模型配置，控制 API 成本

定义代码审查标准，利用 Superpowers 的自动审查功能

8.4 成本控制

AI 编码助手的使用会产生 API 费用。以下方法可以帮助控制成本：

附录

A. 常用命令速查

B. 配置文件速查

C. 资源链接

OpenCode 官方文档：https://opencode.ai

Superpowers GitHub：https://github.com/obra/superpowers

Oh My OpenCode GitHub：https://github.com/code-yeongyu/oh-my-opencode

npm 包页面：https://www.npmjs.com/package/opencode-ai

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

— 教程结束 —

祝你在 OpenCode 的世界中高效编码！


| --- | --- | --- |

| 组件 | 功能 | 必要性 |

| OpenCode 核心 | AI 编码助手主程序 | 必需 |

| opencode.json | 主配置文件（模型、MCP、插件等） | 必需 |

| AGENTS.md | AI Agent 行为指令文件 | 推荐 |

| Oh My OpenCode | 增强插件（多 Agent 矩阵、分类调度） | 推荐 |

| Superpowers | 标准化开发工作流（TDD、代码审查等） | 可选 |

| Skills | 专业技能模块（可自定义） | 可选 |

| MCP Servers | 外部工具集成（浏览器、AI 视觉等） | 可选 |





| --- | --- | --- |

| 要求 | 最低配置 | 推荐配置 |

| Node.js | 18.x | 20.x 或更高 |

| npm | 9.x | 10.x 或更高 |

| 内存 | 4 GB | 8 GB 或更高 |

| 磁盘空间 | 500 MB | 1 GB 或更高 |

| 操作系统 | Windows 10 / macOS 11 / Linux | 最新稳定版 |

| 网络 | 需要访问 npm registry 和 AI API | 稳定网络连接 |





| --- | --- |

| 文件/目录 | 用途 |

| opencode.json | 主配置文件 |

| AGENTS.md | AI Agent 行为指令 |

| plugins/ | 插件目录 |

| skills/ | 技能模块目录 |

| commands/ | 自定义命令目录 |

| scripts/ | 辅助脚本目录 |





| --- | --- |

| MCP 服务器 | 功能 |

| chrome-devtools | 浏览器自动化（点击、填表、截图等） |

| zai-mcp-server | AI 视觉分析（UI 转换、错误诊断、图表分析） |





| --- | --- | --- |

| Agent | 角色 | 使用场景 |

| Sisyphus | 主编排器 | 任务分解、调度、质量把关 |

| Hephaestus | 深工智能体 | 复杂实现、配置修改 |

| Oracle | 架构顾问 | 架构评审、安全审查 |

| Librarian | 外部参考检索 | 文档、最佳实践查找 |

| Explore | 代码库探索 | 模式发现、文件结构分析 |

| Prometheus | 规划师 | 任务分解、路径规划 |

| Metis | 预规划顾问 | 模糊需求分析 |

| Momus | 计划审查员 | 计划审查、变更审查 |





| --- | --- | --- |

| 分类 | 适用场景 | 推荐模型 |

| visual-engineering | 前端、UI/UX、样式、动画 | Qwen3.5 Plus |

| ultrabrain | 复杂逻辑、算法、架构决策 | Qwen3 Coder Next |

| deep | 自主问题解决、端到端实现 | Qwen3 Max |

| artistry | 创造性问题、非传统方案 | Kimi K2.5 |

| quick | 简单修改、拼写修复 | MiniMax M2.5 |

| writing | 文档撰写、技术写作 | GLM-4.7 |





| --- | --- |

| 工具 | 功能 |

| bash | 执行终端命令 |

| read | 读取文件内容 |

| edit | 精确编辑文件 |

| write | 创建/写入文件 |

| glob | 文件路径模式匹配 |

| grep | 文件内容搜索 |

| lsp_* | 语言服务器协议（跳转定义、查找引用等） |

| ast_grep_* | AST 感知的代码搜索和替换 |





| --- | --- | --- |

| 步骤 | 技能 | 说明 |

| 1. 头脑风暴 | brainstorming | 明确需求、探索方案 |

| 2. 隔离工作区 | using-git-worktrees | 创建独立分支 |

| 3. 编写计划 | writing-plans | 分解为具体任务 |

| 4. 执行开发 | subagent-driven-dev | 多 Agent 并行实现 |

| 5. 测试驱动 | test-driven-development | RED-GREEN-REFACTOR |

| 6. 代码审查 | requesting-code-review | 质量检查 |

| 7. 完成分支 | finishing-a-development-branch | 合并/PR 决策 |





| --- | --- | --- |

| 优化项 | 效果 | 配置位置 |

| 模型路由 | 简单任务用快模型，复杂任务用强模型 | categories 配置 |

| Variant 选择 | low/medium/high 控制推理深度 | agents 配置 |

| Token 优化 | 减少 40-70% 的 token 消耗 | optimized 配置 |

| 响应加速 | 首 Token 时间减少 40-60% | 模型选择策略 |





| --- | --- | --- |

| 策略 | 说明 | 节省幅度 |

| 模型分级 | 简单任务用快/便宜模型 | 30-50% |

| Variant 控制 | 降低推理深度（low/medium） | 20-40% |

| 上下文管理 | 定期开启新会话，避免过长历史 | 15-30% |

| 并行优化 | 减少重复探索 | 10-20% |

| 缓存利用 | 复用已有的分析结果 | 10-15% |





| --- | --- |

| 命令 | 功能 |

| opencode | 启动 OpenCode |

| opencode --version | 查看版本 |

| opencode /path/to/project | 打开指定项目 |

| opencode run "question" | 非交互式运行 |

| npm install -g opencode-ai | 安装/更新 |

| npm update -g opencode-ai | 更新到最新版 |





| --- | --- | --- |

| 文件 | 位置 | 用途 |

| opencode.json | ~/.config/opencode/ | 主配置（模型、MCP、插件） |

| AGENTS.md | ~/.config/opencode/ 或项目根目录 | AI 行为指令 |

| oh-my-opencode.json | ~/.config/opencode/ | 多 Agent 和分类配置 |

| SKILL.md | ~/.config/opencode/skills/<skill>/ | 技能定义 |


