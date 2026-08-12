# 2025–2026 Agent 自我进化 Harness 深度检索与技术趋势报告

> **观测日期**：2026-08-06  
> **检索范围**：GitHub 开源仓库、仓库 README/源码、GitHub API 元数据、项目论文/官方文档。  
> **核心问题**：哪些项目真正形成了“执行 → 反馈/归因 → 记忆或策略更新 → 回归验证”的自我进化闭环？  
> **说明**：Stars 是 GitHub API 在观测日读取的动态快照，不是项目质量评分；后续会变化。项目论文发表年份与代码仓库活跃年份分开记录。

---

## 我能讲出来的版本（5 行）

1. **Self-evolving Harness 不是“会反思”就够了**：至少要有可持久化的学习状态、可观测反馈和可重复验证。
2. **AgentEvolver** 把自进化拆成 Self-Questioning、Self-Navigating、Self-Attributing，最接近完整的训练型 Harness。
3. **TextGrad** 把自然语言反馈变成“文本梯度”，适合作为 Prompt/规则/答案优化器，但本身不是长期运行的 Agent Harness。
4. **Letta Code 与 GenericAgent** 把学习状态落到 memory、skill、prompt 甚至 harness/mod 层，代表 2026 年工程化方向。
5. **Reflexion、CLIN** 是重要基础范式；**Agent0** 代表零数据、工具集成和自博弈式数据生成；**Aurogen** 更像运行时与技能生态底座，而不是自进化算法。

---

## 1. 先定义“自我进化 Harness”

本报告把项目按下面的闭环判断，而不是按 README 中是否出现 “self-improving” 字样判断：

```text
任务/环境
   ↓
Agent 执行并产出轨迹（action、observation、tool result、final outcome）
   ↓
评估器：结果评分 + 步骤级归因 + 失败分类
   ↓
学习器：更新记忆、Prompt/规则、经验池、Skill、Mod，或模型参数
   ↓
验证器：hold-out 任务、回归测试、沙箱、安全检查
   ↓
通过才晋级；失败则回滚/隔离并进入下一轮
```

### 1.1 四类机制标签

| 标签 | 判定标准 | 典型项目 |
|---|---|---|
| **失败轨迹归因** | 对长轨迹的中间步骤标 GOOD/BAD、做因果/信用分配，而不只看最终成功率 | AgentEvolver、Agent0、Reflexion、CLIN |
| **Prompt/规则变异重写** | 将自然语言反馈转成新 Prompt、规则或上下文，不改模型权重也能改变行为 | TextGrad、Letta Code、CLIN、GenericAgent |
| **Test-Driven 闭环演进** | 候选策略/Mod/Skill 生成后自动执行场景、断言和回归，通过才晋级 | Letta Code、SkillWeaver；AgentEvolver/Agent0 更偏训练评测闭环 |
| **技能晶体化** | 把一次成功轨迹压缩为可复用的 Skill/SOP/API，并在后续任务中直接召回 | GenericAgent、SkillWeaver、Letta Code、Aurogen 技能生态 |

“记忆/反思”是横切能力：它可以只是短期 verbal feedback，也可以进化为可版本控制、可回滚的程序性知识。

---

## 2. 代表性仓库总览（8 个）

### 2.1 快照表

| 项目 | Canonical GitHub 仓库 | Stars（2026-08-06） | 代码/项目活动证据 | 自进化定位 |
|---|---|---:|---|---|
| **AgentEvolver** | [modelscope/AgentEvolver](https://github.com/modelscope/AgentEvolver) | **1,517**（[API 快照](https://api.github.com/repos/modelscope/AgentEvolver)） | `pushed_at=2026-04-01`；README 有 2025-11 技术报告、2025-12 Game Arena、2026-03 SeeUPO | **完整训练型 Harness**：自动任务生成、经验导航、步骤归因、RL 更新 |
| **TextGrad** | [zou-group/textgrad](https://github.com/zou-group/textgrad) | **3,689**（[API 快照](https://api.github.com/repos/zou-group/textgrad)） | `pushed_at=2025-07-25`；README 标注 2025-03-19 发表 Nature | **文本优化器**：LLM 反馈充当 textual gradients，直接重写变量/Prompt |
| **Reflexion** | [noahshinn/reflexion](https://github.com/noahshinn/reflexion) | **3,223**（[API 快照](https://api.github.com/repos/noahshinn/reflexion)） | `pushed_at=2025-01-14`；原论文为 NeurIPS 2023 | **反思基线**：失败后生成 verbal reflection，下一轮注入上下文 |
| **Letta（MemGPT）** | [letta-ai/letta-code](https://github.com/letta-ai/letta-code)（当前活动 Harness）；旧服务仓库 [letta-ai/letta](https://github.com/letta-ai/letta) | **2,963**（active Harness）；旧仓库 **24,121**（[API](https://api.github.com/repos/letta-ai/letta-code)、[API](https://api.github.com/repos/letta-ai/letta)） | `letta` README 明确称旧仓库是 legacy server，开发迁移到 Letta Code；Letta Code README 描述 memory/skills/prompts/mods 自改 | **长期状态型 Harness**：记忆、技能、Prompt、Mod、MemFS、dreaming/sleeptime、回归式 Mod 学习 |
| **Agent0** | [aiming-lab/Agent0](https://github.com/aiming-lab/Agent0) | **1,241**（[API 快照](https://api.github.com/repos/aiming-lab/Agent0)） | `pushed_at=2026-07-10`；README 标注 2025-11-29 发布代码 | **零数据共同进化**：Curriculum Agent 造更难任务，Executor Agent 用工具解决并训练 |
| **CLIN** | [allenai/clin](https://github.com/allenai/clin) | **89**（[API 快照](https://api.github.com/repos/allenai/clin)） | `pushed_at=2023-12-15`；原论文 2023；不是 2025-26 新项目 | **冻结模型的持续学习**：每轮把轨迹压成 causal abstractions，更新持久文本记忆 |
| **Aurogen** | [UniRound-Tec/Aurogen](https://github.com/UniRound-Tec/Aurogen) | **737**（[API 快照](https://api.github.com/repos/UniRound-Tec/Aurogen)） | `pushed_at=2026-03-21`；README 标注 2026-03 发布与 Agent Group | **运行时/技能底座**：模块化 Agent、Memory、Skills、Sub-agents；未证明自身包含完整自进化算法 |
| **GenericAgent** | [lsdefine/GenericAgent](https://github.com/lsdefine/GenericAgent) | **13,677**（[API 快照](https://api.github.com/repos/lsdefine/GenericAgent)） | `pushed_at=2026-08-06`；README 标注 2026-04 技术报告、2026-05 Goal/Mod 等持续更新 | **技能晶体化型 Harness**：成功轨迹 → Skill/SOP；5 层记忆；可自配置/自扩展 |

> **时间窗结论**：用户点名的 CLIN 与 Reflexion 是 2023 奠基工作，不能冒充 2025–2026 新发布；它们仍然必须保留，因为 AgentEvolver、Letta Code 等新系统分别继承了“轨迹归因/经验记忆/反思”路线。2025–2026 的新变化主要是把反思从一段文本升级为训练数据、程序性 Skill、可测试 Mod 和可版本控制的 Harness 状态。

---

## 3. 深度拆解：每个项目真正进化了什么

### 3.1 AgentEvolver：最完整的训练型自进化 Harness

**一手证据**：

- [README：三种 Self-Evolving Mechanisms](https://github.com/modelscope/AgentEvolver/blob/main/README.md#why-agentevolver)
- [Experience Manager 指南](https://github.com/modelscope/AgentEvolver/blob/main/docs/guidelines/exp_manager.md)
- [ADCA-GRPO / Self-Attributing 指南](https://github.com/modelscope/AgentEvolver/blob/main/docs/guidelines/adv_processor.md)
- [步骤级语义归因实现](https://github.com/modelscope/AgentEvolver/blob/main/agentevolver/module/adv_processor/semantic_attribution.py)

**闭环**：

1. **Self-Questioning**：从环境探索中自动生成任务，减少人工数据集依赖。
2. **Self-Navigating**：把轨迹异步总结到 Experience Pool；后续 rollout 检索 top-k 经验并注入上下文。
3. **Self-Attributing**：LLM 对完整轨迹中的每个步骤输出 `GOOD/BAD`，再与最终 outcome reward 分离归一化，形成步骤级 advantage。
4. **RL 更新**：通过 ADCA-GRPO/相关训练管线把步骤级优势回写到 PPO/GRPO 类策略优化。

**机制评级**：

- 失败轨迹归因：**强**。它不是只把“这次失败”写进 memory，而是问“哪一步造成了失败/成功”。
- Prompt/规则重写：**中**。经验被摘要并注入 rollout，但核心目标仍是训练 policy，不是长期重写 Prompt 文件。
- TDD 闭环：**中**。有 AppWorld/BFCL-v3 等 benchmark、奖励、轨迹记录和训练验证；不是传统软件工程意义的测试先行。
- 技能晶体化：**弱**。沉淀的是 experience/reward signal，不是面向用户的可调用 Skill 包。

**适合**：有 GPU、能部署沙箱、目标是训练一个在工具环境中越来越强的 Agent。  
**不适合**：只想给本地 Coding Agent 加一个轻量反思层；完整训练栈、VeRL/服务依赖和 API 成本都较高。

---

### 3.2 TextGrad：把自然语言反馈变成“文本梯度”

**一手证据**：

- [README：Textual Gradient Descent 示例](https://github.com/zou-group/textgrad/blob/main/README.md#quickstart)
- [TextLoss 实现](https://github.com/zou-group/textgrad/blob/main/textgrad/loss.py)
- [TextualGradientDescent 实现](https://github.com/zou-group/textgrad/blob/main/textgrad/optimizer/optimizer.py)
- [Nature 论文链接](https://www.nature.com/articles/s41586-025-08661-4)

**机制**：

```text
Variable（答案 / Prompt / 代码 / 分子）
   ↓
TextLoss：LLM 评价错误与不足
   ↓
loss.backward()：把文字反馈挂到 Variable
   ↓
TGD.step()：LLM 根据反馈生成 <IMPROVED_VARIABLE>
   ↓
替换 Variable，进入下一轮
```

源码中 `TextualGradientDescent.step()` 会读取变量描述、当前值、梯度反馈、约束、历史 feedback，再要求优化模型生成新文本并写回 `parameter.set_value(new_value)`。这就是**Prompt/规则变异重写**的清晰实现。

**边界**：TextGrad 是可组合的优化 primitive，不负责 Agent 的任务调度、长期身份、工具权限、版本发布或跨会话技能库。它最适合作为 Harness 中的 `MutationOperator`：生成若干 Prompt/规则候选，再交给外部 evaluator 和 regression gate。

**机制评级**：

- 失败轨迹归因：**中**。可把轨迹/代码放进 TextLoss，但仓库的核心抽象是 Variable 梯度，不是专门的长轨迹 credit assignment。
- Prompt/规则重写：**强**。
- TDD 闭环：**中-强**。README 明确展示 Test-Time Loss for Code 和 Prompt Optimization；是否晋级仍需调用方提供测试集/hold-out。
- 技能晶体化：**弱**。优化后的文本变量可保存，但仓库不定义 Skill 生命周期。

**适合**：Prompt optimizer、规则生成器、代码/答案的测试时修复器。  
**推荐接法**：不要直接让 TextGrad 改生产 Prompt；先生成 3–8 个候选，跑固定回归集和安全检查，再采用 best candidate。

---

### 3.3 Reflexion：最小可解释的失败 → 反思 → 下一轮上下文

**一手证据**：

- [README：Reflexion Strategies](https://github.com/noahshinn/reflexion/blob/main/README.md#reflexion-strategies)
- [Agent 实现](https://github.com/noahshinn/reflexion/blob/main/hotpotqa_runs/agents.py)
- [原论文](https://arxiv.org/abs/2303.11366)

`ReflexionStrategy` 明确区分：

- `NONE`：不提供上一轮信息；
- `LAST_ATTEMPT`：把上一轮 scratchpad 注入下一轮；
- `REFLEXION`：让 self-reflect LLM 生成 verbal reflection；
- `LAST_ATTEMPT_AND_REFLEXION`：两者同时注入。

它的进化对象是**当前任务的上下文状态**，不是模型参数或全局 Skill。优点是简单、便宜、可解释；缺点是反思容易重复、会把错误解释固化进上下文，也没有内建的反思质量 gate。

**机制评级**：

- 失败轨迹归因：**中**，有自我反思但未做细粒度因果 credit assignment。
- Prompt/规则重写：**弱**，是上下文注入，不是持久 Prompt 文件改写。
- TDD 闭环：**弱-中**，原仓库有多轮 trial 与实验日志，但不是通用 regression harness。
- 技能晶体化：**无**。

**定位**：保留为所有复杂 Harness 的 baseline。任何新机制都应该能回答：“相对于只加入 Reflexion，步骤归因/Skill/测试门禁到底带来了什么增益？”

---

### 3.4 Letta（MemGPT）：从记忆 Agent 进化为可改写 Harness

**仓库关系必须看清**：

- [letta-ai/letta](https://github.com/letta-ai/letta) README 已声明这是 legacy Letta server，主动开发转移到 [letta-ai/letta-code](https://github.com/letta-ai/letta-code)。
- 因此 2026 年评估 Letta 的自进化能力，应以 Letta Code 为 active Harness，同时把旧仓库作为 MemGPT/Letta memory server 的历史根。

**一手证据**：

- [Letta Code README：Self-improvement & Learning](https://github.com/letta-ai/letta-code/blob/main/README.md#feature-overview)
- [Self-configuration Skill](https://github.com/letta-ai/letta-code/blob/main/src/skills/builtin/self-configuration/SKILL.md)
- [Memory filesystem 实现](https://github.com/letta-ai/letta-code/blob/main/src/agent/memory-filesystem.ts)
- [Skill 工具实现](https://github.com/letta-ai/letta-code/blob/main/src/tools/impl/skill.ts)
- [Learning Harness Mod](https://github.com/letta-ai/letta-code/blob/main/src/mods/learning-harness.ts)

**进化层级**：

1. **Memory**：Agent 可通过 memory blocks 维护 persona、human、项目知识等持久上下文。
2. **Skills**：全局、项目级、Agent memory 级技能目录；技能是可加载的程序性知识。
3. **Prompt/配置**：self-configuration 明确把 memory、server fields、local settings、mods、skills、schedules 分层，避免把确定性安全规则埋在 prose memory。
4. **Harness/Mods**：README 直接声称 Agent 可以重写 memory、skills、prompts，甚至通过 mods 修改 harness；`learning-harness.ts` 的结构显示了候选生成、场景评估、断言、required/forbidden markers、score、promote 等测试型流程。
5. **版本控制**：MemFS 将上下文纳入 Git，可同步到自定义 GitHub memory repository。

**机制评级**：

- 失败轨迹归因：**中**。有 message search、history-analyzer、doctor/dreaming 等上下文分析；没有 AgentEvolver 那样的标准 GOOD/BAD 步骤优势算法。
- Prompt/规则重写：**强**。
- TDD 闭环：**强**，尤其是 Mod Learning：候选 → 场景运行 → assertions/markers → score → promotion。
- 技能晶体化：**强**。

**适合**：长期运行的 Coding/Research/个人助理 Agent，重视记忆、技能、权限和可回滚。  
**风险**：能改 Harness 就意味着供应链和权限边界必须强制化；学习型 Mod 不应直接拥有生产目录写权限。

---

### 3.5 Agent0：零数据 + 工具集成 + Curriculum/Executor 共进化

**一手证据**：

- [总 README](https://github.com/aiming-lab/Agent0/blob/main/README.md)
- [Agent0 训练 README](https://github.com/aiming-lab/Agent0/blob/main/Agent0/README.md)
- [论文](https://arxiv.org/abs/2511.16043)

**闭环**：

```text
Curriculum Agent 生成/筛选更难、工具相关的任务
       ↓
Executor Agent 在 sandbox / code interpreter 等工具中解决
       ↓
结果评估、自一致性过滤、构造训练数据
       ↓
多轮 RL / ADPO 更新 Executor
       ↓
新 Executor 反过来推动更难的 Curriculum
```

它的核心不是“把失败写成一段反思”，而是让**任务分布本身和解题策略互相施压**。这代表一种 2025–2026 的强趋势：用 Agent 自己生成训练信号，减少人工标注和固定数据集依赖。

**机制评级**：

- 失败轨迹归因：**中-强**，通过 reward、executor/curriculum 竞争和工具结果提供学习信号；不等价于 AgentEvolver 的语义步骤归因。
- Prompt/规则重写：**弱**，主要更新模型策略/训练数据。
- TDD 闭环：**中**，有 sandbox、question evaluation、self-consistency filtering、benchmark；不是软件测试驱动的 Prompt promotion。
- 技能晶体化：**无**，产物主要是训练数据、checkpoint 和 policy。

**适合**：研究“从零数据训练工具型 Agent”、拥有 GPU/沙箱基础设施的团队。  
**不适合**：个人电脑上希望快速部署的记忆型 Agent。

---

### 3.6 CLIN：冻结模型也能持续学习的因果抽象记忆

**一手证据**：

- [GitHub README](https://github.com/allenai/clin/blob/main/README.md)
- [CLIN Agent](https://github.com/allenai/clin/blob/main/scienceworld/clin_agent.py)
- [论文](https://arxiv.org/abs/2310.10134)

论文给出的关键结论是：无需参数更新，Agent 通过**persistent, dynamic, textual memory**持续改进；记忆不是泛泛的 helpful hints，而是围绕因果抽象组织。源码中每个 episode 结束后会调用 `summarize_trace_for_preconditions`，把本轮 run history 和最近若干历史记忆压成 summary；下一 episode 将上一轮 summary 作为上下文输入。

**机制评级**：

- 失败轨迹归因：**中**，强调 preconditions/causal abstractions，但不是训练时的 token-level advantage。
- Prompt/规则重写：**中**，通过 summary 改变下一轮上下文，不直接改 Prompt 文件。
- TDD 闭环：**弱**，有 ScienceWorld 多 episode 评测与迁移设置；没有通用回归测试门禁。
- 技能晶体化：**弱**，沉淀的是任务/环境抽象，不是独立 Skill 包。

**价值**：CLIN 是理解“记忆型持续学习”的理论与工程基线。报告不把它伪装成 2025–2026 新仓库，而把它作为 Letta/现代 memory harness 的先行者。

---

### 3.7 Aurogen：多 Agent 运行时与技能生态，不应误标为完整自进化算法

**一手证据**：

- [README：模块化、Memory、Skills、Agent Group](https://github.com/UniRound-Tec/Aurogen/blob/main/README.md)
- [Skills README](https://github.com/UniRound-Tec/Aurogen/blob/main/aurogen/skills/README.md)
- [MemoryStore](https://github.com/UniRound-Tec/Aurogen/blob/main/aurogen/core/memory.py)
- [SkillsLoader](https://github.com/UniRound-Tec/Aurogen/blob/main/aurogen/core/skills.py)
- [skill-creator](https://github.com/UniRound-Tec/Aurogen/blob/main/aurogen/skills/skill-creator/SKILL.md)

Aurogen 做得很好的部分：

- 把 Agents、Channels、Providers、Skills 模块化并支持多实例/Agent Group；
- `MemoryStore` 将 `MEMORY.md` 与 `HISTORY.md` 持久化，并用 LLM tool call 做 consolidation；
- `SkillsLoader` 支持 workspace/builtin skill、需求检查、动态加载和 zip 安装；
- 通过 OpenClaw/ClawHub 兼容性接入外部技能生态。

但从仓库一手源码看，**Aurogen 自身主要提供 memory consolidation、skill loading/install 和 runtime orchestration**；没有看到与 AgentEvolver、TextGrad、Letta Learning Harness 同等级的“候选变异 → 独立评测 → 晋级/回滚”的完整算法。因此应将它标为：

> **Evolution-ready substrate（可承载自进化的底座），而不是已验证的 self-evolving optimizer。**

**机制评级**：

- 失败轨迹归因：**弱**，有历史/记忆归档，但未见标准步骤归因。
- Prompt/规则重写：**弱-中**，技能文档和 memory 可更新，但更新策略不是核心算法。
- TDD 闭环：**弱**。
- 技能晶体化：**中**，技能格式/加载/生态清晰，但“从成功轨迹自动合成 Skill”需外接机制。

**推荐用法**：把 Aurogen 当作多 Agent runtime，再接入 TextGrad/评测器/SkillWeaver/自定义 mutation pipeline；不要只因为 README 使用 “evolution” 语义就认定它已实现自进化闭环。

---

### 3.8 GenericAgent：2026 年最鲜明的“技能晶体化”路线

**一手证据**：

- [README：Overview / Self-Evolution Mechanism](https://github.com/lsdefine/GenericAgent/blob/main/README.md)
- [Agent Loop](https://github.com/lsdefine/GenericAgent/blob/main/agent_loop.py)
- [Memory 目录](https://github.com/lsdefine/GenericAgent/tree/main/memory)
- [技术报告 arXiv:2604.17091](https://arxiv.org/abs/2604.17091)

**核心设计**：

- 约 3K 行 seed code、9 个原子工具、约 100 行 Agent Loop；
- 不预装大量技能，而是让 Agent 在执行任务时安装依赖、写脚本、调试、验证；
- 成功路径自动固化为可复用 Skill/SOP，形成个人 skill tree；
- L0 Meta Rules、L1 Insight Index、L2 Global Facts、L3 Task Skills/SOPs、L4 Session Archive 五层记忆；
- 支持项目级 Skill 吸收、Goal mode、子 Agent 编排、真实浏览器和本地系统控制。

`agent_loop.py` 展示了极简但关键的闭环骨架：工具调用返回 `StepOutcome`，`turn_end_callback` 可以注入下一轮 prompt，handler/hook 记录 turn、tool、result；真正的长期进化逻辑放在 memory/SOP 层，而不是堆叠 Agent Loop 本身。

**机制评级**：

- 失败轨迹归因：**中**，有 checkpoint、review、session archive 和执行经验沉淀；不是专门的步骤 credit assignment。
- Prompt/规则重写：**中-强**，Agent 可写入 memory/SOP、调整运行方式；核心不是 TextGrad 式梯度优化。
- TDD 闭环：**中**，README 说明有 cross-task benchmark、第二/第三次运行收敛和项目 Skill 吸收；但需审慎区分 README 的 benchmark 声称与仓库内可复现实验脚本。
- 技能晶体化：**强**，这是项目的第一性设计。

**适合**：个人电脑/本地自动化、Coding Agent、需要跨任务复用经验并降低 Token 的场景。  
**最大风险**：自动写脚本、装包、操作浏览器和系统权限都很强；Skill 一旦被错误经验污染，会在后续任务中高频复用，因此必须配合来源、版本、测试和回滚元数据。

---

## 4. 代表性推荐：按目标选，而不是按 Stars 选

### 4.1 最推荐的组合

| 目标 | 首选 | 配套 | 原因 |
|---|---|---|---|
| **研究完整自进化训练闭环** | AgentEvolver | Agent0、VeRL/沙箱 | AgentEvolver 负责任务生成、经验导航、步骤归因；Agent0 提供零数据 curriculum/executor 共进化视角 |
| **本地长期 Coding/Research Agent** | Letta Code | GenericAgent 的技能晶体化思想 | Letta Code 的 memory/skill/Mod/版本化边界更完整；GenericAgent 更简洁、执行权限更直接 |
| **Prompt/规则自动优化** | TextGrad | 固定回归集 + 安全 evaluator | TextGrad 负责 mutation，外部 Harness 负责候选选择，避免“一次 LLM 改写直接进生产” |
| **轻量反思 baseline** | Reflexion | CLIN 式持久总结 | 最适合做消融实验：无反思、短期反思、持久因果记忆、步骤归因逐层对比 |
| **多 Agent runtime/技能生态** | Aurogen | 自定义 evaluator + SkillWeaver | Aurogen 提供模块化运行时和技能安装，外接自进化算法；不要把 runtime 当 optimizer |
| **技能自动沉淀/低 Token** | GenericAgent | regression gate、skill provenance | 直接针对“成功轨迹 → SOP/Skill”，适合个人生产力，但必须补安全与晋级门禁 |

### 4.2 推荐排序（按“自进化 Harness 完整度”而非流行度）

1. **Letta Code**：状态层、Skill 层、Harness/Mod 层和测试型学习流程覆盖最全。
2. **AgentEvolver**：训练型闭环最完整，步骤归因与经验管理有明确算法化设计。
3. **GenericAgent**：技能晶体化最鲜明，工程上容易理解和落地。
4. **Agent0**：零数据、工具集成、任务分布共进化有研究突破性，但基础设施门槛高。
5. **TextGrad**：作为 Prompt/规则变异算子非常强，需被嵌入更大的 Harness。
6. **CLIN**：持久 causal memory 的经典基线，适合做 memory ablation。
7. **Reflexion**：最小反思基线，适合低成本验证反馈是否有用。
8. **Aurogen**：运行时和技能生态有价值，但自进化闭环应由外部组件补齐。

> **相邻参考**： [OSU-NLP-Group/SkillWeaver](https://github.com/OSU-NLP-Group/SkillWeaver)（观测日约 150 Stars）专门展示“探索网站 → 合成 API Skill → 练习/测试 → 修复”的技能发现路线；如果目标是浏览器 Agent 的技能晶体化，它比 Aurogen 更接近研究型 skill synthesis，但整体活跃度和通用性不如上述 8 个主样本。

---

## 5. 2025–2026 技术大趋势

### 趋势 A：从“反思文本”转向“可执行学习状态”

Reflexion 的 verbal reflection 主要是下一轮上下文；CLIN 将其升级为持久 causal abstraction；Letta Code/GenericAgent 则继续升级成 memory files、skills、SOPs、mods。趋势不是“反思写得更长”，而是：

```text
reflection text → structured memory → procedural skill → executable harness change
```

### 趋势 B：从最终奖励转向步骤级信用分配

AgentEvolver 的 Self-Attributing/ADCA-GRPO 直接回应长轨迹的 credit assignment：最终成功不代表每一步都对，最终失败也不代表每一步都错。未来可靠 Harness 会同时记录：

- final outcome reward；
- step/process quality；
- tool validity；
- safety/policy violations；
- cost/latency/token usage。

### 趋势 C：从人工数据集转向 Agent 自生成课程与训练信号

Agent0 的 Curriculum Agent ↔ Executor Agent 共进化说明：只要有工具、沙箱和可验证 reward，Agent 可以自己提出任务并生成训练数据。AgentEvolver 的 Self-Questioning 也在同一方向上。真正的难点转移到：任务难度控制、奖励黑客检测、数据去重、hold-out 防泄漏。

### 趋势 D：Prompt 优化器与 Harness 运行时分层

TextGrad 证明了 LLM 可以用文字反馈优化 Prompt/代码/答案；Letta Code/Aurogen/GenericAgent 证明了运行时需要承载长期状态和工具权限。推荐的模块边界是：

```text
Runtime / tools / permissions
        ↓ trace schema
Evaluator / attribution / tests
        ↓ feedback + score
Mutation operator（TextGrad / LLM proposer / hand-written transform）
        ↓ candidate artifact
Promotion gate（hold-out / security / cost / rollback）
        ↓
Memory / Skill / Prompt / Mod registry
```

### 趋势 E：TDD 正在从“代码测试”扩展到“Agent 行为测试”

Letta Learning Harness 的 `assertions`、required/forbidden markers、scenario、score、promote 体现了行为型 TDD：测试的不是函数返回值，而是 Agent 是否在一组场景中加载正确 Mod、注入正确消息、改写正确工具参数、产生可接受轨迹。

未来测试对象会包括：

- 工具调用序列与参数；
- 是否遵守权限/安全策略；
- memory 写入是否有 provenance；
- Skill 是否在相似任务中降低成本且不降低成功率；
- Prompt 变异是否只改善目标集而不破坏 hold-out。

### 趋势 F：Skill 成为 Agent 的“程序性权重”

模型权重更新昂贵、慢且难回滚；Skill/SOP/Mod 是更便宜的外部权重。GenericAgent 的 skill tree、Letta Code 的 agent-scoped skills、SkillWeaver 的 API skills、Aurogen 的 OpenClaw/ClawHub skill 兼容，说明 Agent 的能力正在从“模型参数”迁移到“可组合程序性知识”。

但 Skill 不能只存 Markdown：生产级 Skill 至少应包含：

```yaml
name: ...
version: ...
source_trace_ids: [...]
preconditions: [...]
postconditions: [...]
test_cases: [...]
required_permissions: [...]
model_or_tool_dependencies: [...]
success_rate: ...
last_validated_at: ...
rollback_ref: ...
```

### 趋势 G：自我修改的安全边界成为一等公民

当 Agent 可以修改 Prompt、Skill、Mod、工具脚本甚至自身 Harness 时，主要风险不再只是 hallucination，而是：

- 错误经验被永久固化；
- Skill 供应链污染；
- 自我修改绕过权限；
- 评测集泄漏造成虚假进步；
- 通过改 evaluator 而不是改能力来“刷分”；
- 长期 memory 泄露隐私或秘密。

因此必须把可变对象分层：**memory 可改、Skill 候选可写、生产 Mod 需测试与审批、权限/安全规则不可由 Agent 单方面放宽**。

---

## 6. 建议在本 Worktree 继续采用的 Harness 蓝图

如果要把本报告中的结论落成一个可维护的自进化 Harness，推荐以下最小但完整的组件：

### 6.1 Trace Schema

每次执行记录：

```json
{
  "trace_id": "...",
  "task": "...",
  "agent_version": "...",
  "prompt_ref": "...",
  "steps": [
    {"action": "...", "observation": "...", "tool": "...", "result": "..."}
  ],
  "outcome": {"success": true, "score": 0.87},
  "cost": {"tokens": 0, "latency_ms": 0},
  "safety": {"violations": []}
}
```

### 6.2 Failure Attribution

至少分成四种错误：

1. **规划错误**：目标/子任务拆解错误；
2. **工具错误**：工具选择、参数、权限或解析错误；
3. **知识/记忆错误**：召回了过期/错误 Skill；
4. **验证错误**：结果看似成功但没有通过真实 postcondition。

AgentEvolver 的步骤级 GOOD/BAD 可以作为 process signal；CLIN/Reflexion 的总结可以作为 explanation；二者不要混成同一字段。

### 6.3 Mutation Layer

同时支持三类变异：

- `PromptMutation`：TextGrad/LLM proposer 重写 Prompt；
- `RuleMutation`：生成/合并规则，带冲突检测；
- `SkillMutation`：把成功轨迹抽象成 Skill/SOP，生成 precondition/postcondition 和测试。

### 6.4 Promotion Gate

候选只有满足以下条件才能写入 production registry：

- 目标任务集成功率不低于 baseline；
- hold-out 任务不显著退化；
- 安全违规数为 0；
- Token/延迟成本在预算内；
- Skill 有 source trace、版本和 rollback ref；
- 至少一次冷启动复现成功。

### 6.5 Memory / Skill / Harness 三层写权限

| 层 | 默认权限 | 晋级方式 |
|---|---|---|
| Session memory | Agent 可写 | 会话结束摘要 |
| Candidate Skill/Prompt | Agent 可写 | 测试集 + hold-out + 安全扫描 |
| Production Skill/Mod/Permission | Agent 不可单独放宽 | 人工或受限审批 + Git 版本化 |

---

## 7. 风险与反模式清单

- **把 Star 当质量**：Stars 只表示关注度，不能替代可复现实验。
- **把 README 声称当实现**：尤其是 Aurogen、GenericAgent 等快速迭代项目，应逐文件核对“已实现”与“路线/宣传”。
- **只做最终结果反思**：没有步骤归因，长轨迹学习信号过于稀疏。
- **没有 hold-out**：Agent 可以记住测试集或针对 evaluator 过拟合。
- **无版本/回滚的 Skill**：错误 SOP 会在未来任务中被重复放大。
- **把 runtime 当 evolution algorithm**：Aurogen 提供承载能力，不代表自动产生更优策略。
- **让 Agent 修改安全边界**：可修改 memory 不等于可修改权限、审计、网络或 secrets 规则。
- **无限增长的 memory**：必须摘要、去重、衰减、引用来源和定期 doctor，否则上下文会反噬性能。

---

## 8. 最终结论

2025–2026 的 Agent 自我进化并没有收敛为单一算法，而是形成四条互补路线：

1. **训练型进化**：AgentEvolver、Agent0 —— 自生成任务/经验，做步骤归因和 RL/策略更新；
2. **文本优化型进化**：TextGrad —— 将评价反馈变成 Prompt/代码/答案变异；
3. **记忆型进化**：CLIN、Reflexion、Letta —— 从短期 reflection 发展到持久、结构化、可版本化状态；
4. **技能/运行时型进化**：GenericAgent、Letta Code、Aurogen、SkillWeaver —— 把经验变成 Skill、SOP、API 或可测试 Harness 组件。

**推荐的生产答案不是单选一个仓库，而是组合**：

> **Letta Code/GenericAgent 负责长期状态与技能；TextGrad 负责候选 Prompt/规则变异；AgentEvolver/Agent0 的步骤归因和自生成任务思想负责训练/评估；Aurogen 负责多 Agent runtime 时，必须外接 promotion gate、安全审计和回滚。**

真正成熟的 Self-Evolving Harness 的判据是：它能证明“下一轮更好”，并且能回答**为什么更好、改了什么、在哪些任务上变差、如何回滚**。

---

## 9. 一手来源索引

### 核心仓库与 API 快照

- [modelscope/AgentEvolver](https://github.com/modelscope/AgentEvolver) · [GitHub API](https://api.github.com/repos/modelscope/AgentEvolver)
- [zou-group/textgrad](https://github.com/zou-group/textgrad) · [GitHub API](https://api.github.com/repos/zou-group/textgrad)
- [noahshinn/reflexion](https://github.com/noahshinn/reflexion) · [GitHub API](https://api.github.com/repos/noahshinn/reflexion)
- [letta-ai/letta-code](https://github.com/letta-ai/letta-code) · [GitHub API](https://api.github.com/repos/letta-ai/letta-code)
- [letta-ai/letta](https://github.com/letta-ai/letta) · [GitHub API](https://api.github.com/repos/letta-ai/letta)
- [aiming-lab/Agent0](https://github.com/aiming-lab/Agent0) · [GitHub API](https://api.github.com/repos/aiming-lab/Agent0)
- [allenai/clin](https://github.com/allenai/clin) · [GitHub API](https://api.github.com/repos/allenai/clin)
- [UniRound-Tec/Aurogen](https://github.com/UniRound-Tec/Aurogen) · [GitHub API](https://api.github.com/repos/UniRound-Tec/Aurogen)
- [lsdefine/GenericAgent](https://github.com/lsdefine/GenericAgent) · [GitHub API](https://api.github.com/repos/lsdefine/GenericAgent)
- [OSU-NLP-Group/SkillWeaver](https://github.com/OSU-NLP-Group/SkillWeaver)（相邻参考）

### 论文/官方出版物

- [Reflexion, arXiv:2303.11366](https://arxiv.org/abs/2303.11366)
- [CLIN, arXiv:2310.10134](https://arxiv.org/abs/2310.10134)
- [AgentEvolver, arXiv:2511.10395](https://arxiv.org/abs/2511.10395)
- [Agent0, arXiv:2511.16043](https://arxiv.org/abs/2511.16043)
- [GenericAgent, arXiv:2604.17091](https://arxiv.org/abs/2604.17091)
- [TextGrad, Nature 2025](https://www.nature.com/articles/s41586-025-08661-4)
