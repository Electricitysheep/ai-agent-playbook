<div align="center">

# 🚀 AI Agent Playbook

**AI Agent 工程 × 量化金融 前沿知识库** — 源码级调研、可运行代码、深度行业观察

一个由**实测驱动**的 AI Agent 知识库：从 Agent 架构源码拆解、Agent-to-Agent 协议调研，到 AI×量化交易的全链路实战（论文精读 → 代码实验 → 生产风控）。所有内容均为原创深度调研，非链接搬运。

[![Stars](https://img.shields.io/github/stars/Electricitysheep/ai-agent-playbook?style=for-the-badge&logo=github)](https://github.com/Electricitysheep/ai-agent-playbook)
[![License](https://img.shields.io/github/license/Electricitysheep/ai-agent-playbook?style=for-the-badge)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Electricitysheep/ai-agent-playbook?style=for-the-badge)](https://github.com/Electricitysheep/ai-agent-playbook/commits/master)
[![Content](https://img.shields.io/badge/Content-100%2B%20Notes-blue?style=for-the-badge)](.)
[![Obsidian](https://img.shields.io/badge/Obsidian-Vault-purple?style=for-the-badge&logo=obsidian)](.)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)](CONTRIBUTING.md)

**中文 · [English](./README.en.md)**

</div>

---

## ✨ 这是什么

不是又一个链接收藏夹，而是 **AI Agent 时代的深度工程笔记**：

- 🧠 **Agent 架构源码级拆解**：Claude Code Agent Teams、Devin 消息架构、omp hub IPC 并发模型——不只看文档，直接读源码
- 🤝 **Agent-to-Agent 协议调研**：A2A 协议生态、14 家主流 agent 对比矩阵、MCP-bridge 现状
- 📈 **AI × 量化金融全链路**：从 LLM 因子挖掘、TSFM 时序模型选型、RL 最优执行，到 16 个可运行代码实验
- 📰 **行业深度观察**：Harness 开源版图、模型发布研判、前沿范式追踪（图工程、长上下文退化）

每一篇调研都标注**证据来源与可信度分级**（官方文档 / 社区逆向 / 本机实测），拒绝二手转述。

## 🎯 适用人群

- **AI 工程师 / Agent 开发者**：想深入理解主流 agent 的架构与消息机制
- **量化研究员**：想知道 LLM/Agent 如何嵌入因子挖掘、回测与生产风控
- **AI 原生工程师**：追踪 Agent Harness、A2A 协议等 2026 前沿范式
- **转码学习者**：从 Agent 开发到量化工程的完整实战路径

## 🗂 目录结构

```
ai-agent-playbook/
├── 01-AI工程/
│   ├── 01-Agent智能体/          # 源码级调研：Claude/Devin/omp/A2A 协议/Harness
│   ├── 02-RAG与向量数据库/      # 向量库入门到实战
│   ├── 03-提示工程/             # Prompt 工程完整教程
│   ├── 04-AI辅助开发工作流/     # Claude Code/OpenCode/OMP/Orca 实战
│   ├── 05-深度学习教程/         # 全栈 AI 开发者教程
│   └── 06-白皮书与论文/         # 论文与技术报告解读
├── 02-量化金融/
│   ├── 01-高频量化教程/         # 高频量化工程技能体系
│   └── 02-AI与量化前沿/         # ⭐ 核心：11 主题笔记 + 9 论文精读 + 16 代码实验
├── 03-行业观察/
│   ├── 01-最新月报/             # AI 行业月度报告
│   ├── 02-趋势与洞察/           # 深度调研：Harness/模型研判/前沿范式
│   └── 03-案例研究/             # 具体产品与公司案例
├── 04-编程基础/                 # ML 经典理论（Brady Neal 因果推断）
├── 05-工程实践/                 # Docker/K8s/测试工程学习路线
└── 06-原始文献/                 # 论文清单与索引
```

## 🚀 快速上手

```bash
# 克隆知识库
git clone https://github.com/Electricitysheep/ai-agent-playbook.git

# 或直接用 Obsidian 打开（推荐）
# Obsidian → Open folder as vault → 选择本目录
```

**推荐阅读路径**（3 分钟了解本库价值）：

1. 🏆 [主流 Agent 的 Agent-to-Agent 能力对比调研报告](./01-AI工程/01-Agent智能体/20260812_主流Agent的Agent-to-Agent能力对比调研报告.md) — 14 家 agent 对比矩阵
2. 📊 [AI 如何嵌入量化金融深度调研报告](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/01_LLM因子挖掘工程化.md) — AI×量化全链路
3. 🔬 [Claude Code Agent Teams 源码级深挖](./01-AI工程/01-Agent智能体/20260812_ClaudeCode_AgentTeams与DynamicWorkflows_源码级深挖.md) — 三层证据交叉验证

## ⭐ 特色内容

### AI Agent 深度调研（2026-08 最新）

| 报告 | 亮点 |
|------|------|
| [A2A 协议与 MCP-bridge 生态现状](./01-AI工程/01-Agent智能体/20260812_A2A协议与MCP-bridge生态现状_调研报告.md) | 核实 A2A v1.0.1 现状，Agent-DID 未合并 |
| [主流 Agent 的 A2A 能力对比](./01-AI工程/01-Agent智能体/20260812_主流Agent的Agent-to-Agent能力对比调研报告.md) | 14 家对比，prime-agent 唯一本地 daemon 方案 |
| [Claude Code Agent Teams 源码深挖](./01-AI工程/01-Agent智能体/20260812_ClaudeCode_AgentTeams与DynamicWorkflows_源码级深挖.md) | 邮箱+flock 机制、权限委托链路 |
| [Devin 多 Agent 消息架构](./01-AI工程/01-Agent智能体/20260812_Devin多Agent消息架构与权限模型_调研报告.md) | manager→child 拓扑、三层权限模型 |
| [国内大厂 Harness 开源版图](./03-行业观察/02-趋势与洞察/20260807_国内大厂Agent_Harness开源版图_深度调研报告.md) | 字节 deer-flow 79.5k star 实证 |

### AI × 量化金融（差异化核心）

- **11 篇主题深度笔记**：LLM 因子挖掘、TSFM 选型、RL 最优执行、多智能体交易、回测纪律
- **9 篇论文精读**：Trading-R1、Fin-R1、Can LLMs Trade、Chain-of-Alpha 等
- **16 个可运行代码实验**：每个实验含 `main.py` + 说明文档，开箱即跑（见 [代码实验索引](./02-量化金融/02-AI与量化前沿/03-代码实验/)）

## 🤝 贡献

欢迎 PR！无论是修正、补充还是新的调研方向。详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

- 有调研想法？[开 Issue 讨论](https://github.com/Electricitysheep/ai-agent-playbook/issues/new)
- 发现错误？直接提 PR，24 小时内响应

## 📜 License

[MIT](./LICENSE) © Electricitysheep

---

**如果这个知识库对你有帮助，点个 ⭐ 支持一下吧！**

[![Star History Chart](https://api.star-history.com/svg?repos=Electricitysheep/ai-agent-playbook&type=Date)](https://star-history.com/#Electricitysheep/ai-agent-playbook&Date)
