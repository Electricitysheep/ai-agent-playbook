# 国内大厂 Agent Harness 开源版图深度调研报告

> **报告日期**：2026-08-07
> **归档位置**：`06_行业观察/03_趋势与洞察/`
> **研究方法**：GitHub REST API 逐仓库实测（stars / created_at / pushed_at / language / description）+ 官方 README + 中文二手报道交叉核对
> **证据分级**：仓库元数据为**实测硬数据**；架构描述来自官方 README（未读源码）；产品动态来自二手中文站点（**未核实**，文中逐条标注）
> **档位**：A 档（含判断、取舍与实测结论）

---

## 我能讲出来的版本（5 行）

1. **这份材料反对"看 star 排序选 harness"**，主张**必须同时看 `pushed_at`**——2025 年那批自进化明星（Darwin Gödel Machine 2.2k、SEAL 1.8k、Memento 2.6k）star 都不低，但全部停更近一年，照 star 选型会直接选到死项目。
2. **最意外的事实**：字节 `deer-flow` 有 **79,504 star**，自我定位就是 "long-horizon SuperAgent harness"，体量是高德 LongHorizon-Harness（375）的 **212 倍**。我原以为国内 harness 还在起步，实际上头部已经是平台级。但要打个折——它 2025-05 起家时是 Deep Research 框架，2026-02 才推倒重写成 harness，star 里有相当部分是前世攒的。
3. **核心方法一句话**：判断一家厂在 harness 上的真实投入，不看它发了什么模型，**看它的 org 里有没有一组互相咬合的小仓库**——高德 ML 一家就同时挂着长程 harness、技能进化、协同演化、RL 策略四条线，这种"体系感"比单个爆款仓库更能说明问题。
4. **代价与边界（初稿在这里栽过一次，已更正）**：GitHub 的空白有**两种截然不同的含义**——"没投入"和"投了但闭源"，仅凭 org 扫描**无法区分**。我初稿据此断言"DeepSeek harness 方向完全空白"，经 SCMP 两篇报道核实后证明是错的：DeepSeek 2026 年 5 月就组建了 Harness 团队、由前 Jane Street 工程师崔添翼带队、正在 from the ground up 造 CodeHarness，只是**全程闭源**（见 §2.4.1）。**这份报告的所有结论只在"开源生态"这个切面成立。**
5. **下周我会做的一个具体动作**：核实 `ByteDance-Seed/DAComp`（ICLR 2026，数据智能全生命周期的 Data Agent 基准）**测不测时序泄漏与因果正确性**——它跟我正在做的 ChronoGuard-ETF 直接撞题，而我之前那轮覆盖 12 个基准的调研里没有它。

---

## 回头查什么

| 需要…… | 去看 |
|---|---|
| 各厂具体仓库的 star / 活跃度硬数据 | 第 2 节各厂梯队表 |
| 字节 deer-flow 的架构（子 agent / 上下文压缩 / checkpoint） | 第 1 节 |
| 哪些仓库看着热但其实已死 | 第 3 节「停更名单」 |
| 国内 vs 海外的路线分叉 | 第 4 节判断三 |
| 跟我自己项目撞题的基准 | 第 5 节 |
| 这份报告哪些数字不可信 | 第 6 节可信度声明 |

---

## 1. 头条：字节 deer-flow 是国内 harness 的绝对头部

| 项 | 值 |
|---|---|
| 仓库 | `bytedance/deer-flow` |
| **Stars / Forks** | **79,504 / 10.9k** |
| 创建 / 最后提交 | 2025-05-07 / 2026-08-07（观测当日） |
| 语言 / 自我定位 | Python ／ "open-source **long-horizon SuperAgent harness** that researches, codes, and creates" |
| 形态 | Web UI + CLI/TUI + 嵌入式 Python client + REST API |
| 任务尺度 | 官方描述 "minutes to hours" |

**架构要点**（来自官方 README，未读源码）：

- **动态子 agent**：按需生成 sub-agent，各自拥有独立作用域的上下文、工具与终止条件
- **激进上下文管理**：已完成子任务摘要化、中间结果卸载到文件系统、压缩不再直接相关的内容
- **状态持久化**：使用 **LangGraph checkpoint** 保存会话状态，支持线程分支与从存档点重新生成
- **隔离沙箱**：`/mnt/user-data/{uploads,workspace,outputs}` 三段式文件系统
- **跨会话长期记忆**：DeerMem（本地）或可选托管后端

> **star 数解读警告**：它 2025-05 起家时是 Deep Research 框架，**2.0 是 2026-02 的推倒重写**才变成 harness。7.95 万 star 里有相当部分是 Deep Research 时代攒的，不能直接读成"harness 采纳度"。但今天仍在提交、10.9k fork，热度是真实的。

---

## 2. 各厂梯队（GitHub API 实测，观测日 2026-08-07）

### 2.1 字节 — 唯一有平台级体量的

| 仓库 | Stars | 最后提交 | 定位 |
|---|---:|---|---|
| `bytedance/deer-flow` | **79,504** | 08-07 | 长程 SuperAgent harness |
| `bytedance/UI-TARS-desktop` | 38,500 | 08-05 | 多模态 AI agent stack |
| `ByteDance-Seed/DAComp` | 434 | 07-10 | ICLR 2026 · Data Agent 基准 |
| `bytedance/agentkit-samples` | 415 | 08-07 | 火山引擎 AgentKit / VeADK 样例 |

### 2.2 阿里系 — 战线最宽，分工最明确

| 仓库 | Stars | 最后提交 | 定位 |
|---|---:|---|---|
| `QwenLM/qwen-code` | 26,825 | 08-07 | coding agent CLI |
| `alibaba/spring-ai-alibaba` | 10,535 | 08-06 | Java agentic 框架 |
| `modelscope/ms-agent` | 4,358 | 08-06 | 轻量 agentic 执行框架 |
| **`AMAP-ML/SkillClaw`** | **2,380** | 08-06 | **技能集体进化** |
| `QwenLM/Qwen-AgentWorld` | 936 | 07-20 | language world model |
| `alibaba/skill-up` | 431 | 08-07 | Agent Skills 评测与进化（Go） |
| **`AMAP-ML/LongHorizon-Harness`** | **375** | 08-07 | **长程 computer-use harness** |
| `alibaba/anolisa` | 326 | 08-07 | agentic 操作层 |
| `QwenLM/Qwen-MM-Plugins` | 120 | 08-06 | 让任意 harness 多模态化 |
| `modelscope/ms-enclave` | 54 | 08-04 | agent sandbox runtime |

> **高德 ML 团队（`AMAP-ML`）是国内最像"研究型 harness lab"的一支**：
> LongHorizon-Harness + SkillClaw + CoEvolve + Ace-Skill + ActGuide-RL 五条线并行，全部围绕"长程 + 技能进化"。
> LongHorizon-Harness 在观测期间 **一天涨 52 star**（08-06 的 323 → 08-07 的 375）。

### 2.3 腾讯 — 仓库都很小很新，但方向极准

| 仓库 | Stars | 创建 | 定位 |
|---|---:|---|---|
| `Tencent/BrowserSkill` | 855 | — | 让 agent 使用真实登录态浏览器 |
| `Tencent/teamai-cli` | 59 | 2026-04-27 | **"The team harness for AI agents"**（TypeScript） |
| **`Tencent/LoopForge`** | **7** | **2026-07-28** | **可恢复的多 agent 开发工作流，跨 CodeBuddy / Codex / Cursor / Claude Code** |

> `LoopForge` 只有 7 star、诞生十天，但它解决的正是"多个 coding agent 之间可恢复的工作流编排"——
> 与我目前用 Orca + git worktree 手工做的事情是同一个问题域。**值得持续盯。**

### 2.4 模型厂 — 走 CLI 路线而非 harness 路线

| 仓库 | Stars | 归属 |
|---|---:|---|
| `zai-org/Open-AutoGLM` | 25,963 | 智谱 |
| `MoonshotAI/kimi-cli` | 11,130 | 月之暗面 |
| `zai-org/GLM-5` | 6,905 | 智谱 |
| `MoonshotAI/kimi-code` | 6,157 | 月之暗面 |
| `MoonshotAI/kimi-agent-sdk` | 553 | 月之暗面 |
| `MoonshotAI/kosong` | 523 | 月之暗面（LLM 抽象层） |

**Moonshot / 智谱走的是 Claude Code 对标 CLI 路线，不是 harness 路线。**

### 2.4.1 ⚠️ 关于 DeepSeek 的更正（2026-08-07 补充核实）

**本报告初稿曾写"DeepSeek harness 方向完全空白"，这是一个由观测切面导致的错误结论，现更正。**

GitHub 观测事实不变：`deepseek-ai` org 下只有 `awesome-deepseek-agent`（5,153 star）一个清单仓库，无 harness 代码。
**但经全网核实，DeepSeek 是所有厂商中 harness 投入最明确的之一，只是完全走闭源路线。**

一手信源（South China Morning Post，两篇独立报道）确认：

| 事实 | 内容 | 来源 |
|---|---|---|
| 团队组建 | 2026 年 5 月中下旬内部组建 Harness 团队，对标 Anthropic Claude Code | SCMP |
| 负责人 | **崔添翼（Cui Tianyi）**，2026 年 3 月加盟；前 Jane Street 量化工程师，2022 年联合创立港资量化机构 TSY Capital 并在其工作四年 | SCMP（据其 LinkedIn） |
| 招聘状态 | 崔在 X 上表示团队「人才严重短缺」，原话：**"I interview candidates every day and post recruitment ads across various platforms"** | SCMP 2026-06-23 |
| 岗位 | 已公开发布两个岗位：Agent Harness 产品经理、Agent Harness 研发工程师。JD 原文口径：**「除模型本身之外的所有工作都属于 Harness 范畴」** | SCMP |
| 产品 | 资深研究员**陈德里**披露团队正在 **"building CodeHarness from the ground up"**，可能形成独立产品 **"DeepSeek Code"** | SCMP 2026-06-23 |
| Harness 定义 | 被描述为连接基础模型与外部工具的软件，是模型的**「神经系统」**：管理上下文、调用工具、文件操作、协调工作流 | SCMP |

二手中文信源（**未核实**）补充：2026 年 7 月下旬起 Harness 开启小范围内测招募，入选需签《保密承诺函》，
申请窗口据称开放至 8 月 31 日；V4-Flash 正式版已于 2026-07-31 上线，V4-Pro 预计 8 月中旬。
**是否开源，未找到任何官方确认。**

> **这次更正的方法论教训，比结论本身更值得记住：**
> GitHub 的空白有两种截然不同的含义——**「没投入」**和**「投了但闭源」**，
> 而仅凭 org 扫描**无法区分这两者**。DeepSeek 恰恰是后者，且是本报告覆盖的所有厂商中
> **唯一一个把 harness 完全闭源的**（字节、阿里、腾讯、蚂蚁、美团均有开源仓库）。
> 这反而是一条更有信息量的发现：**在国内大厂普遍开源 harness 的背景下，DeepSeek 选择闭源，本身就是一个战略信号。**
>
> 本目录既有的《DeepSeek_Harness团队与AI_Agent编程基础设施深度分析报告.md》（2026-07-29）
> 对上述事实的记载**经核实基本准确**（崔添翼履历、Model+Harness=Agent 理念、内测传闻、与 V4 协同发布预期均得到 SCMP 或二手源支持），
> 该报告与本文**不存在结论冲突**，是本文在 DeepSeek 一项上的**更权威来源**。

### 2.5 蚂蚁 / 美团 — 小而专

| 仓库 | Stars | 定位 |
|---|---:|---|
| `antgroup/agentic-ai-landscape` | 524 | agentic landscape 数据 |
| `meituan/EvoCUA` | 336 | 进化式 computer-use agent |
| `antgroup/agent-aegis` | 191 | 全生命周期安全插件 |
| `antgroup/aievo` | 98 | 多 agent 框架 |

### 2.6 百度 — 基本缺席

搜到最相关的是 `baidu/cosui`（88 star），其余为 2020 年的老仓库。
**在开源 harness 这条线上，百度没有存在感。**

---

## 3. 停更名单：star 高但已死的项目

这是本次调研**最有实操价值的一节**。以下项目 star 都不低，但已近一年无提交：

| 仓库 | Stars | 最后提交 |
|---|---:|---|
| `SakanaAI/AI-Scientist` | 14,353 | 2025-12-19 |
| `Memento-Teams/Memento` | 2,559 | 2025-10-05 |
| `jennyzzt/dgm`（Darwin Gödel Machine） | 2,209 | **2025-08-13** |
| `Continual-Intelligence/SEAL` | 1,840 | **2025-08-01** |
| `CharlesQ9/Self-Evolving-Agents` | 1,272 | 2025-10-15 |
| `microsoft/autogen` | 60,268 | **2026-04-15**（已由 `microsoft/agent-framework` 继任） |
| `HKUDS/OpenHarness` | 15,235 | 2026-06-04 |
| `modelscope/AgentEvolver` | 1,517 | 2026-04-01 |

**教训：选型时 `pushed_at` 与 star 同等重要。** 我自己在这次调研的第一轮就踩了这个坑，
给出的推荐里混进了 Darwin Gödel Machine 和 SEAL 这类已停更一年的项目。

---

## 4. 三个判断

**判断一：国内 harness 的重心在字节和高德，不在模型厂。**
模型厂在卷 CLI（qwen-code / kimi-cli / kimi-code / Open-AutoGLM），字节在卷平台，高德在卷长程研究。

**判断二：腾讯的方向比体量更值得关注。**
`teamai-cli`（59 star）与 `LoopForge`（7 star）体量都极小，但"团队 harness"与"跨 agent 可恢复工作流"这两个切入点非常精准，是目前最贴近个人多 agent 实操场景的开源实现。

**判断三：国内与海外路线明显分叉。**
国内三家大厂同时在做"技能进化"（`SkillClaw` 2,380 / `skill-up` 431 / `EvoCUA` 336）——让 agent 的技能库自己长大；
海外主流则偏向 durable execution 与 context engineering（Temporal / DBOS / LangGraph checkpoint / 各类 compaction 方案）。
**同一个"让 agent 跑得久"的问题，两边给的答案不一样：国内加技能，海外加状态机。**

---

## 5. 与本人在研项目的交叉点

**`ByteDance-Seed/DAComp`（ICLR 2026）—— "Benchmarking Data Agents across the Full Data Intelligence Lifecycle"**

这与我正在做的 ChronoGuard-ETF（面向清华数据库组「自主数据科学系统」征集的任务包）**直接撞题**，
而此前那轮覆盖 12 个 agentic DS 基准的调研（见 `ChronoGuard-ETF/_research/NOVELTY.md`）**没有收录它**。

必须核实两件事：
1. DAComp 覆盖"数据智能全生命周期"，**它测不测时序泄漏 / 因果正确性？**
2. 若测了 → 我的差异化在哪；若没测 → 这是**又一个强力佐证**（一个 ICLR 2026 的全生命周期数据 agent 基准都不测这一维）。

**另一条交叉**：LongHorizon-Harness 的 **Auditor 角色**（用独立只读工具复核 executor 的实际影响，而不是信它的自评）
与 ChronoGuard 的"审计模式"是同一思想。区别在于它审"这一步做成了没有"，我审"代码的时间契约有没有被破坏"。
**可作为同期佐证写入 NOVELTY.md。**

---

## 6. 可信度声明

| 内容 | 可信度 |
|---|---|
| 所有 star 数、创建/提交日期、语言、仓库描述 | **硬数据**，GitHub REST API 观测日实测 |
| deer-flow 的架构描述 | 来自官方 README，**未读源码验证** |
| LongHorizon-Harness 的 benchmark 数字（WeaveBench 51.8%→80.7% 等） | 来自论文 arXiv:2608.01964 本身，**未独立复现** |
| **DeepSeek Harness 团队的存在、崔添翼任职、陈德里的 CodeHarness 表述、两个招聘岗位** | **已核实**，来自 South China Morning Post 两篇独立报道（2026-06-23 等），属一手媒体报道 |
| DeepSeek Harness 内测时间窗、V4-Pro 发布节奏、是否开源 | 来自搜狐 / 钛媒体 / 知乎等二手中文站点，**未核实**；开源与否无任何官方确认 |
| TRAE Work、Kimi Work、GLM-5.2 参数量、AutoGLM 开源 24 小时 1.7k star 等产品动态 | 来自 CSDN / 51CTO / 博客园 / 火山引擎社区等二手中文站点，**未核实** |
| Claude Code 五级渐进式压缩、Microsoft BUILD 2026 发布内容 | 二手博客，**未核实** |

**方法论局限**：
- GitHub star 只能测**开源开发者关注度**，测不出企业内部落地程度。本报告结论**只在"开源生态"这个切面成立**。
- Reddit / Twitter / 知乎 / 小红书通道在调研时未接通（OpenCLI 需 Chrome 开启并启用扩展），
  **国内开发者一手讨论与真实使用评价这一层完全缺失**。

---

## 7. 关联材料

**本目录内**：
- `中国主流AI大厂Harness技术进展与Agent评级报告_2026.md`（2026-07-29）—— **产品/评级视角**，与本文的**开源仓库实测视角**互补；该报告未涵盖本文列出的任一仓库
- `DeepSeek_Harness团队与AI_Agent编程基础设施深度分析报告.md` —— **在 DeepSeek 一项上比本文更权威**；本文初稿的错误结论已在 §2.4.1 更正，两份材料现已一致
- `20260806_长程Agent框架与长时间任务管理工具_深度调研报告.md` —— **海外**长程框架（OpenHands / SWE-agent / LangGraph / OSWorld / InfiAgent / MAGE）
- `Agent自进化的两大方向与四大趋势.docx`

**跨目录**（`02_AI工程/01_Agent智能体/`）：
- `20260806_LongHorizon-Harness技术架构分析.md` —— 同一对象的**源码级**分析（固定提交 `24ad75c`），本文只到 README 层
- `20260806_Agent自我进化Harness深度检索报告.md` —— 自进化闭环的项目级检索
- `LongHorizon-Harness_MEA_自我进化整合蓝图_20260806.md`

**外部项目**：`C:\Users\24835\Downloads\ChronoGuard-ETF\_research\NOVELTY.md`（待补入 DAComp）

---

## 来源

**一手（GitHub API / 官方 README）**：
- https://github.com/bytedance/deer-flow
- https://github.com/AMAP-ML/LongHorizon-Harness ｜ https://github.com/AMAP-ML/SkillClaw
- https://github.com/Tencent/LoopForge ｜ https://github.com/Tencent/teamai-cli
- https://github.com/ByteDance-Seed/DAComp
- https://github.com/alibaba/skill-up ｜ https://github.com/modelscope/ms-agent ｜ https://github.com/meituan/EvoCUA
- https://github.com/QwenLM/qwen-code ｜ https://github.com/MoonshotAI/kimi-cli ｜ https://github.com/zai-org/Open-AutoGLM
- 论文：https://arxiv.org/abs/2608.01964（LongHorizon-Harness）

**一手媒体报道（DeepSeek Harness 团队，已核实）**：
- https://www.scmp.com/tech/big-tech/article/3358077/deepseeks-harness-team-races-recruit-talent-booming-ai-agent-market （SCMP，2026-06-23）
- https://www.scmp.com/tech/big-tech/article/3354113/deepseek-recruits-former-jane-street-engineer-catch-ai-agents-revenue-race （SCMP）

**二手（未核实）**：
- https://www.tmtpost.com/8083615.html （钛媒体·DeepSeek Harness 内测）
- https://m.sohu.com/a/1057805191_122066679 （搜狐·内测招募）
- https://www.51cto.com/aigc/11212.html（字节开源 Harness 报道）
- https://blog.csdn.net/qq_44866828/article/details/160622087（2026 国产 AI Agent 工具全景盘点）
- https://developer.volcengine.com/articles/7660044882941050930（2026 主流自主智能体产品清单）

**海外 harness 追踪列表（本轮附带发现）**：
- https://github.com/ai-boost/awesome-harness-engineering（3,429 star，日更）
- https://github.com/earendil-works/pi（84,695 star）
- https://github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers（625 star）
- https://github.com/NeuZhou/awesome-ai-anatomy（236 star，15 个 coding agent 源码解剖）

**归档日期**：2026-08-07
