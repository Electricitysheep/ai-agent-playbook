<div align="center">

# 🚀 AI Agent Playbook

**AI Agent 工程 × 量化金融 前沿知识库** — 源码级调研 · 可运行代码 · 深度行业观察

一个由**实测驱动**的 AI Agent 知识库：Agent 架构源码拆解、Agent-to-Agent 协议调研、AI×量化全链路实战。所有内容均为原创深度调研，标注证据来源分级。

[![Stars](https://img.shields.io/github/stars/Electricitysheep/ai-agent-playbook?style=for-the-badge&logo=github)](https://github.com/Electricitysheep/ai-agent-playbook)
[![License](https://img.shields.io/github/license/Electricitysheep/ai-agent-playbook?style=for-the-badge)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Electricitysheep/ai-agent-playbook?style=for-the-badge)](https://github.com/Electricitysheep/ai-agent-playbook/commits/master)
[![Content](https://img.shields.io/badge/Content-106%20Notes-blue?style=for-the-badge)](.)
[![Experiments](https://img.shields.io/badge/Code-16%20Experiments-green?style=for-the-badge)](./02-量化金融/02-AI与量化前沿/03-代码实验/)
[![Obsidian](https://img.shields.io/badge/Obsidian-Vault-purple?style=for-the-badge&logo=obsidian)](.)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)](CONTRIBUTING.md)

**中文 · [English](./README.en.md)**

</div>

---

## 📑 目录

- [✨ 这是什么](#-这是什么)
- [📊 内容统计](#-内容统计)
- [🎯 适用人群](#-适用人群)
- [📚 内容清单](#-内容清单)
  - [🧠 AI Agent 源码级调研](#-ai-agent-源码级调研)
  - [🛠 AI 辅助开发实战](#-ai-辅助开发实战)
  - [📈 AI × 量化金融](#-ai--量化金融)
  - [📰 行业深度观察](#-行业深度观察)
  - [📖 论文与文献](#-论文与文献)
- [🚀 快速上手](#-快速上手)
- [🤝 贡献](#-贡献)
- [📜 License](#-license)

---

## ✨ 这是什么

不是又一个链接收藏夹，而是 **AI Agent 时代的深度工程笔记**：

- 🧠 **源码级拆解**：Claude Code Agent Teams、Devin 消息架构、omp hub IPC——直接读源码，不只看文档
- 🤝 **A2A 协议调研**：14 家主流 agent 对比矩阵、协议生态现状
- 📈 **AI×量化全链路**：LLM 因子挖掘 → TSFM 选型 → RL 执行 → 生产风控
- 📰 **行业深度观察**：Harness 开源版图、模型研判、前沿范式

每一篇调研都标注**证据来源分级**（官方文档 / 社区逆向 / 本机实测），拒绝二手转述。

## 📊 内容统计

| 板块 | 数量 | 说明 |
|------|------|------|
| 🧠 AI Agent 深度调研 | 16 篇 | 源码级拆解 + A2A 协议 + Harness 分析 |
| 🛠 AI 辅助开发实战 | 18 篇 | Claude Code / OpenCode / OMP / Orca 教程 |
| 📈 AI×量化主题笔记 | 11 篇 | 因子挖掘到生产风控全链路 |
| 📖 量化论文精读 | 9 篇 | Trading-R1 / Chain-of-Alpha / Fin-R1 等 |
| 🧪 可运行代码实验 | 16 个 | clone 即跑，无需 API key |
| 📰 行业深度观察 | 19 篇 | Harness 版图 / 模型研判 / 前沿范式 |

**合计 106 篇原创内容笔记 + 16 个可运行实验**，全部标注证据来源。

## 🎯 适用人群

- **AI 工程师 / Agent 开发者**：深入理解主流 agent 架构与消息机制
- **量化研究员**：LLM/Agent 如何嵌入因子挖掘、回测与生产风控
- **AI 原生工程师**：追踪 Agent Harness、A2A 协议等 2026 前沿范式
- **转码学习者**：从 Agent 开发到量化工程的完整实战路径

---

## 📚 内容清单

### 🧠 AI Agent 源码级调研

#### A2A 协议与生态

- [主流 Agent 的 Agent-to-Agent 能力对比调研报告](./01-AI工程/01-Agent智能体/20260812_主流Agent的Agent-to-Agent能力对比调研报告.md) — 14 家对比：仅 4 家支持 agent 直接互发消息，附完整矩阵
- [A2A 协议与 MCP-bridge 生态现状调研](./01-AI工程/01-Agent智能体/20260812_A2A协议与MCP-bridge生态现状_调研报告.md) — 核实 A2A 实为 v1.0.1，Agent-DID 是未合并 PR
- [Agent-to-Agent 调研综合结论](./01-AI工程/01-Agent智能体/20260812_Agent-to-Agent调研_综合结论.md) — 该借鉴（wait_any 竞态原语）与该避免（idle pings）清单
- [Agent-to-Agent 编排提示词 v2](./01-AI工程/01-Agent智能体/20260812_Agent-to-Agent编排提示词_v2.md) — 4 方向并行调研的 master 编排 prompt

#### 源码级架构拆解

- [Claude Code Agent Teams 源码深挖](./01-AI工程/01-Agent智能体/20260812_ClaudeCode_AgentTeams与DynamicWorkflows_源码级深挖.md) — 🔬 三层证据：邮箱+flock 机制、SendMessage 身份不可伪造
- [Devin 多 Agent 消息架构](./01-AI工程/01-Agent智能体/20260812_Devin多Agent消息架构与权限模型_调研报告.md) — manager 经 MCP 注入、child 拓扑禁通信、三层权限
- [omp hub IPC 并发模型深挖](./01-AI工程/01-Agent智能体/20260812_omp_hub与task工具IPC并发模型深挖_深度调研报告.md) — 三层 IPC：IrcBus + AsyncJobManager + daemon broker
- [腾讯 TencentDB-Agent Memory 拆解](./01-AI工程/01-Agent智能体/腾讯TencentDB-Agent-Memory拆解.md) — 数据库 Agent 的记忆实现

#### Harness 与自我进化

- [LongHorizon-Harness 技术架构分析](./01-AI工程/01-Agent智能体/20260806_LongHorizon-Harness技术架构分析.md)
- [Agent 自我进化 Harness 深度检索](./01-AI工程/01-Agent智能体/20260806_Agent自我进化Harness深度检索报告.md)
- [LongHorizon-Harness MEA 整合蓝图](./01-AI工程/01-Agent智能体/LongHorizon-Harness_MEA_自我进化整合蓝图_20260806.md)

#### 基础与课程

- [Coding Agents 101 阅读摘要](./01-AI工程/01-Agent智能体/Coding_Agents_101_阅读摘要.docx.md)
- [CS146S 斯坦福 AI 教学总结](./01-AI工程/01-Agent智能体/CS146S斯坦福大学ai教学总结.docx.md) · [详细学习](./01-AI工程/01-Agent智能体/CS146S课程内容详细学习.docx.md)
- [AI 代码评审技术指南](./01-AI工程/01-Agent智能体/AI代码评审技术指南-摘要笔记.docx.md)

### 🛠 AI 辅助开发实战

- [多 Agent 工作流手册](./01-AI工程/04-AI辅助开发工作流/多Agent工作流手册_v1.md) — ⭐ 总纲：三份订阅、四个 agent 入口、一个驾驶舱
- [Anthropic Claude Code 使用指南（核心精炼版）](./01-AI工程/04-AI辅助开发工作流/Anthropic-Claude-Code-使用指南-核心精炼版.md)
- [OpenCode 新手完全教程](./01-AI工程/04-AI辅助开发工作流/OpenCode新手完全教程.docx.md) · [版本更新与进阶玩法](./01-AI工程/04-AI辅助开发工作流/20260728_OpenCode版本更新与进阶玩法_学习笔记.md) · [接入 DeepSeek](./01-AI工程/04-AI辅助开发工作流/opencode-deepseek-tutorial.md) · [+Obsidian](./01-AI工程/04-AI辅助开发工作流/OpenCode+Obsidian教程.docx.md)
- [OMP 使用教程](./01-AI工程/04-AI辅助开发工作流/OMP使用教程.md) · [Orca 使用教程](./01-AI工程/04-AI辅助开发工作流/Orca使用教程.md)
- [AI 十倍速学习十步闭环法](./01-AI工程/04-AI辅助开发工作流/20260728_AI十倍速学习十步闭环法_学习笔记.md) — STORM + 矛盾图谱 + 考官模式
- [利用 AI 进行费曼学习法](./01-AI工程/04-AI辅助开发工作流/利用AI进行费曼学习法.docx.md)
- [数据与财务分析工具栈及 AI 实操](./01-AI工程/04-AI辅助开发工作流/20260801_数据与财务分析工具栈及AI实操_实战手册.md) — 三大工具栈 + AI 厂商祛魅对照表
- [AI 写作工作流速查表](./01-AI工程/04-AI辅助开发工作流/AI写作工作流_速查表.md) · [搭建教程企业版](./01-AI工程/04-AI辅助开发工作流/AI写作工作流搭建教程_企业版.md)
- [GitHub AI 成本优化工具 2026](./01-AI工程/04-AI辅助开发工作流/GitHub_AI_Cost_Optimization_Tools_2026.md)

### 📈 AI × 量化金融

#### 主题深度笔记（11 篇）

- [LLM 因子挖掘工程化](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/01_LLM因子挖掘工程化.md) — 生成→评估→筛选完整管道
- [时序基础模型 TSFM 选型与微调](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/02_时序基础模型TSFM选型与微调.md) — Chronos/TimesFM 谁适合金融
- [RL 最优执行](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/03_RL最优执行.md) — Almgren-Chriss vs 强化学习
- [多智能体交易框架源码精读](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/04_多智能体交易框架源码精读.md) — TradingAgents 辩论路由
- [端到端 AI 量化管线 Qlib 与 RD-Agent](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/05_端到端AI量化管线_Qlib与RD-Agent.md)
- [另类数据与 LLM 解析](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/06_另类数据与LLM解析.md)
- [回测纪律与过拟合诊断](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/07_回测纪律与过拟合诊断.md) — PSR/DSR/PBO 防自欺
- [中国市场 AI 量化实践](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/09_中国市场AI量化实践.md)
- [行情数据工程实战](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/10_行情数据工程实战.md)
- [生产系统与合规架构](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/11_生产系统与合规架构.md) — Agent 幻觉如何被风控拦截

#### 论文精读（9 篇）

[Trading-R1](./02-量化金融/02-AI与量化前沿/02-论文精读/01_Trading-R1.md) · [Fin-R1](./02-量化金融/02-AI与量化前沿/02-论文精读/02_Fin-R1.md) · [RETuning](./02-量化金融/02-AI与量化前沿/02-论文精读/03_RETuning.md) · [LLM 股价预测综述](./02-量化金融/02-AI与量化前沿/02-论文精读/04_LLM股价预测综述.md) · [Can LLMs Trade](./02-量化金融/02-AI与量化前沿/02-论文精读/05_Can_LLMs_Trade.md) · [TradingGNN](./02-量化金融/02-AI与量化前沿/02-论文精读/06_TradingGNN.md) · [Chain-of-Alpha](./02-量化金融/02-AI与量化前沿/02-论文精读/07_Chain-of-Alpha.md) · [TSFM 金融综述](./02-量化金融/02-AI与量化前沿/02-论文精读/08_TSFM金融综述.md) · [Lopez de Prado AFML](./02-量化金融/02-AI与量化前沿/02-论文精读/09_Lopez_de_Prado_AFML与文本因子.md)（[完整索引](./02-量化金融/02-AI与量化前沿/02-论文精读/00_索引.md)）

#### 可运行代码实验（16 个）

- [01 LLM 因子三道检验](./02-量化金融/02-AI与量化前沿/03-代码实验/01_LLM因子三道检验/) · [02 TSFM 金融适配实测](./02-量化金融/02-AI与量化前沿/03-代码实验/02_TSFM金融适配实测/) · [03 RL 最优执行](./02-量化金融/02-AI与量化前沿/03-代码实验/03_RL最优执行/) · [04 TradingAgents 源码走读](./02-量化金融/02-AI与量化前沿/03-代码实验/04_TradingAgents源码走读/) · [05 PIT 幸存者偏差](./02-量化金融/02-AI与量化前沿/03-代码实验/05_Qlib_PIT数据库与幸存者偏差/) · [06 另类数据正交性](./02-量化金融/02-AI与量化前沿/03-代码实验/06_另类数据情绪与量价正交性/) · [07 过拟合诊断套件](./02-量化金融/02-AI与量化前沿/03-代码实验/07_回测纪律与过拟合诊断/) · [08 行情数据工程](./02-量化金融/02-AI与量化前沿/03-代码实验/08_行情数据工程实战/) · [09 全市场因子检验](./02-量化金融/02-AI与量化前沿/03-代码实验/09_全市场因子检验/) · [10 生产风控模拟器](./02-量化金融/02-AI与量化前沿/03-代码实验/10_生产风控叠加层模拟器/) · [11 LLM-MCTS 因子搜索](./02-量化金融/02-AI与量化前沿/03-代码实验/11_LLM-MCTS因子搜索骨架/) · [12 walk-forward 实现](./02-量化金融/02-AI与量化前沿/03-代码实验/12_walk-forward完整实现/) · [13 多因子合成](./02-量化金融/02-AI与量化前沿/03-代码实验/13_多因子合成/) · [14 全市场检验 baostock](./02-量化金融/02-AI与量化前沿/03-代码实验/14_全市场因子检验_baostock300/) · [15 组合优化](./02-量化金融/02-AI与量化前沿/03-代码实验/15_组合优化/) · [16 完整策略闭环](./02-量化金融/02-AI与量化前沿/03-代码实验/16_完整策略闭环/)（[🏆 完整地图](./02-量化金融/02-AI与量化前沿/03-代码实验/README.md)）

### 📰 行业深度观察

- [国内大厂 Agent Harness 开源版图](./03-行业观察/02-趋势与洞察/20260807_国内大厂Agent_Harness开源版图_深度调研报告.md) — GitHub API 逐仓库实测，字节 deer-flow 79.5k star
- [DeepSeek Harness 团队与 Agent 编程基础设施](./03-行业观察/02-趋势与洞察/DeepSeek_Harness团队与AI_Agent编程基础设施深度分析报告.md) — SCMP 一手报道核实
- [长程 Agent 框架与长时间任务管理](./03-行业观察/02-趋势与洞察/20260806_长程Agent框架与长时间任务管理工具_深度调研报告.md)
- [Graph Engineering 图工程范式演进](./03-行业观察/02-趋势与洞察/Graph_Engineering图工程与AI_Agent范式演进深度总结笔记.md) — Loop Engineering 已死？
- [阿里 Qwen3.8-Max 旗舰研判](./03-行业观察/02-趋势与洞察/20260803_阿里通义千问Qwen3.8_Max旗舰研判报告_深度分析.md)
- [DeepSeek V4 Pro 评测深度报告](./03-行业观察/02-趋势与洞察/20260812_DeepSeekV4Pro正式版0813_Agent评测深度报告.md)
- [中国主流 AI 大厂 Harness 进展与 Agent 评级](./03-行业观察/02-趋势与洞察/中国主流AI大厂Harness技术进展与Agent评级报告_2026.md)
- [Context-Rot：LLM 长上下文性能研究](./03-行业观察/02-趋势与洞察/Context-Rot-LLM长上下文性能研究-核心摘要.md)
- [YC 开源 QM 多 Agent 办公系统](./03-行业观察/03-案例研究/20260801_YC开源QM多Agent办公系统_学习笔记.md)
- [为什么顶尖投行选择 Rogo 金融 Agent](./03-行业观察/03-案例研究/为什么顶尖投行都选择了_Rogo_这个金融_Agent.docx.md)
- [AI 行业月度研究报告 2026-07](./03-行业观察/01-最新月报/AI行业月度研究报告_2026年7月.md)（[更多](./03-行业观察/README.md)）

### 📖 论文与文献

- [Brady Neal 因果推断课程笔记](./04-编程基础/01-ML经典理论/20260728_BradyNeal因果推断课程_学习笔记.md) — 15 周大纲 + 40+ 篇论文清单
- [Google AI Agents 白皮书学习笔记](./01-AI工程/06-白皮书与论文/Google_AI_Agents_白皮书学习笔记.docx.md)
- [Agentic Environment Engineering 论文解读](./01-AI工程/06-白皮书与论文/Agentic_Environment_Engineering_论文解读与分析.md)
- [Kimi K3 技术报告从业者解读](./01-AI工程/06-白皮书与论文/20260728_Kimi_K3技术报告从业者解读_学习笔记.md)
- [Docker 个人上手清单](./05-工程实践/01-容器化与系统设计/Docker个人上手清单.md) · [K8s 入门清单](./05-工程实践/01-容器化与系统设计/K8s入门清单.md)

---

## 🚀 快速上手

```bash
# 克隆知识库
git clone https://github.com/Electricitysheep/ai-agent-playbook.git

# 或直接用 Obsidian 打开（推荐）
# Obsidian → Open folder as vault → 选择本目录
```

**3 分钟阅读路径**：

1. 🏆 [主流 Agent 的 Agent-to-Agent 能力对比](./01-AI工程/01-Agent智能体/20260812_主流Agent的Agent-to-Agent能力对比调研报告.md)
2. 📊 [AI 如何嵌入量化金融](./02-量化金融/02-AI与量化前沿/01-主题深度笔记/01_LLM因子挖掘工程化.md)
3. 🔬 [Claude Code Agent Teams 源码深挖](./01-AI工程/01-Agent智能体/20260812_ClaudeCode_AgentTeams与DynamicWorkflows_源码级深挖.md)

**跑一个实验**：

```bash
cd 02-量化金融/02-AI与量化前沿/03-代码实验/01_LLM因子三道检验/
python main.py   # 需要 pandas / yfinance
```

## 🤝 贡献

欢迎 PR！无论是修正、补充还是新的调研方向。详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

- 有调研想法？[开 Issue 讨论](https://github.com/Electricitysheep/ai-agent-playbook/issues/new)
- 发现错误？直接提 PR，24 小时内响应

## 📜 License

[MIT](./LICENSE) © Electricitysheep

---

**如果这个知识库对你有帮助，点个 ⭐ 支持一下吧！**

[![Star History Chart](https://api.star-history.com/svg?repos=Electricitysheep/ai-agent-playbook&type=Date)](https://star-history.com/#Electricitysheep/ai-agent-playbook&Date)
