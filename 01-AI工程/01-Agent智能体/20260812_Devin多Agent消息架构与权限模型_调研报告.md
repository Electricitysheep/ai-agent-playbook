# 20260812_Devin多Agent消息架构与权限模型_调研报告

## 我能讲出来的版本(5 行)
1. Devin 多 agent 经历三阶段:2024-09 MultiDevin(1 manager + ≤10 worker,manager 合并 PR)→ 2025-06 Walden Yan 公开唱衰("Don't Build Multi-Agents")→ 2026-03/04 Managed Devins 重装上阵,但**收敛为"map-reduce-and-manage"**:写操作单线程,并行 agent 只贡献智能不贡献动作。
2. manager→child 消息注入的落地 = **Devin MCP server**:manager 调用 `devin_session_create/interact/events/gather` 等工具,把指令/纠错作为消息投进子会话的事件流;manager 还能**读 child 完整 trajectory**(事件日志)来纠偏,而不是实时看屏幕。
3. child 之间**不能互相通信,这不是权限黑名单,而是拓扑上根本没这个通道**——child 唯一的对外工具面是 Devin MCP 且作用域是"自己的会话";再叠加模型没被训练过"跨 agent 发消息"这个行为,所以官方明确说 child 间不互发。
4. 权限模型三层:①每个 child 独立 VM(secrets 按 VM 最小化, brain/模型逻辑在 Cognition 侧不可从机器访问);②API 层 `bypass_approval` 按 session 授予 + service-user RBAC(`ManageOrgSessions`/`ImpersonateOrgSessions`);③ACU 预算限制每个 child 的算力上限。
5. 对 prime-agent 的借鉴:Devin 用"云端 VM 隔离 + brain 与 machine 分离"换企业级隔离与规模化;prime-agent 用"本地 daemon worker + 进程隔离(非安全沙箱)"换低延迟与零厂商锁定——两者的 sibling 通信差异源于**模型能力未到位时,Devin 选择拓扑上禁用 peer 协商,prime-agent 选择把 nuclear-family 消息作为一等公民提供**。

---

## 0. 结论速览(TL;DR)

| 问题 | 一句话答案 |
|---|---|
| Q1 manager→child 消息注入 | 通过 **Devin MCP server**(`devin_session_interact` 等)把消息投进子会话事件流;manager 可读 child 完整 trajectory 来纠偏 |
| Q2 权限模型 | 独立 VM 隔离 + `bypass_approval` 按 session + service-user RBAC + ACU 预算;child 间**无通信通道**(拓扑禁用 + 模型未训练),不是运行时黑名单 |
| Q3 self-scheduling 持久化 | "Schedule messages to itself" 是 manager 给自己的 follow-up;底层是 cron 调度器(`devin_schedule_manage`)+ session 可 `resumable`(VM 状态保留)+ Devin 跨会话读写自己的 notes |
| Q4 2025→2026 转变依据 | 模型更"agentic" + 三类受控模式被验证(clean-context reviewer/smart friend/manager-delegation)+ 踩坑:manager 过度 prescriptive、假共享状态、**cross-agent 通信不默认发生因为模型没被训练过** |
| Q5 对 prime-agent 借鉴 | 见 §5:7 条借鉴 + 3 条不借鉴(差异根因:云端隔离 vs 本地 worker;拓扑禁 peer vs nuclear-family 一等公民) |

---

## 1. 背景:28 个月三阶段演变(回答一切问题的前提)

Devin 的多 agent 架构**不是静态设计**,而是三次公开转向:

| 阶段 | 时间 | 形态 | 出处 |
|---|---|---|---|
| ① MultiDevin | 2024-09 | 1 manager + 最多 10 个 worker Devin;manager 分发任务并**合并所有成功 worker 的变更进一个分支/PR**;面向 Enterprise | [Devin September '24 Product Update](https://cognition.ai/blog/sept-24-product-update) |
| ② "Don't Build Multi-Agents" | 2025-06-12 | Walden Yan 公开反对并行写 agent;主张单线程 + 上下文压缩模型 | [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) |
| ③ Managed Devins | 2026-03-19 | manager 可 spin up child、mid-task 消息注入、监控 ACU、sleep/terminate、给自己调度消息 | [Devin can now Manage Devins](https://cognition.com/blog/devin-can-now-manage-devins) |
| ③' 立场微调 | 2026-04-22 | "writes stay single-threaded" 为总原则;三类受控模式 + map-reduce-and-manage | [Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working) |

关键认知:**2026 年的 Managed Devins 是带着 2025 年的教训重新设计的多 agent 系统**——不是回到 2024 年的天真并行,而是"manager 拆解 + child 独立执行 + manager 汇总",即 map-reduce-and-manage。

---

## 2. Q1: manager→child 消息注入的实现

### 2.1 通道:内部 Devin MCP server,不是共享消息总线

manager 与 child 的通信通过 **Devin MCP server**(对外是 `https://mcp.devin.ai/mcp`,manager 内部调用同一套工具)实现。核心工具面:

- `devin_session_create` — 创建子会话(可带 prompt/title/playbook/tags/ACU 限额)
- `devin_session_interact` — **发消息给子会话**、查状态、sleep/terminate/archive
- `devin_session_events` — 读子会话事件流(轨迹):列摘要、取详情、全文检索
- `devin_session_gather` — 等多个会话到达 settled 状态(finished/errored/sleeping/waiting),**避免轮询**
- `devin_schedule_manage` — 管理 cron/一次性调度

> 出处:[Devin MCP docs](https://docs.devin.ai/work-with-devin/devin-mcp)

### 2.2 mid-task 指令/纠错怎么"传进"独立 VM

官方功能声明:

> "**Message child sessions**:send instructions, context, or corrections to any managed Devin mid-task"
> "Each managed Devin is a full Devin,running in its own isolated virtual machine with its own terminal, browser, and development environment. Each has its own session link, so you can inspect its work or message it directly."
> — [Devin can now Manage Devins](https://cognition.com/blog/devin-can-now-manage-devins)

技术机制(结合 MCP 工具面推断):
1. manager 以工具调用形式调用 `devin_session_interact(session_id=child, message=...)`;
2. 平台把该消息注入 child 会话的**事件流/提示队列**,child 的下一轮推理会收到它;
3. manager 通过 `devin_session_events` **读回 child 的完整 trajectory**(事件日志),"understand what worked, what didn't, and where they got stuck",据此决定纠偏或改进任务拆解。

> "Devin can also read the full trajectories of its managed Devins to understand what worked, what didn't, and where they got stuck, and use that to improve how it breaks down the next task."
> — [Devin can now Manage Devins](https://cognition.com/blog/devin-can-now-manage-devins)

**注意 nuance**:manager 看到的是**事件日志(结构化的 trajectory),不是 child 的实时屏幕**。实时屏幕只有人类用户能通过 child 的公开 session URL 看。

### 2.3 架构根因:"brain vs machine" 分离

Walden Yan 在 Latent Space(2026-05-28)讲清了 Devin 从第一天起的架构原则——**brain(控制面:模型调用/路由逻辑/secret 决策)与 machine(沙箱/VM)分离**:

> "We from the start built Devin to what we called separate the brain from the machine. ... whatever you put on the machine, that is the scope of basically what the user is free to do, what the agent is free to do. So only put the most scoped secrets on that machine, and then the brain is fully not accessible from the machine."
> — [Latent Space: The Age of Async Agents](https://www.latent.space/p/cognition)

推论:manager 本地无法直接访问 child 的 brain——只能通过 MCP 读到**持久化的事件日志与结构化状态**。这正是"消息注入 = 写入事件流"这一设计的根因。

### 2.4 父子拓扑在 API 里是一等公民

`SessionResponse` schema 显式暴露父子关系:

> `parent_session_id` / `child_session_ids` 字段;
> 子会话可 `platform: "inherit"` 继承父会话的 outpost/平台放置(outpost 部署的父 spawn 出的 child 进同一池)。

> 出处:[Devin API v3 — Sessions](https://docs.devin.ai/api-reference/v3/sessions/post-organizations-sessions)

---

## 3. Q2: 权限模型 + 为何 child 间不能通信

### 3.1 权限模型三层(不是 per-message ACL)

**① 隔离层:每 child 独立 VM,secret 最小化**
每个 child 是完整 Devin,独立 VM/terminal/browser/开发环境。按 brain-machine 分离原则,**secret 只放到对应 VM 上,VM 的可达范围 = agent 的权限范围**。brain 本身从机器不可达,所以"用户对机器自由操作"不会波及控制面安全。

**② 授权层:按 session 的 approval 与 RBAC**
- API 支持 per-session `bypass_approval: true`——manager 可创建"免审批"的 child,不必每步工具调用都等人工;(child 状态机含 `waiting_for_approval` = safe mode 下等待审批)
- service-user 权限:创建会话需 `ManageOrgSessions` 组织级权限;`create_as_user_id` 需 `ImpersonateOrgSessions`;
- `origin` 枚举(webapp/slack/teams/api/linear/jira/automation/cli/desktop/code_scan/other)标记会话来源,供审计。

**③ 算力层:ACU 预算**
manager 可监控并限制每个 child 的 ACU(Agent Compute Unit)消耗(`max_acu_limit`),"sleep 或 terminate 掉走偏的 child"。

> 出处:[Devin API v3](https://docs.devin.ai/api-reference/v3/sessions/post-organizations-sessions)、[Advanced Capabilities](https://docs.devin.ai/work-with-devin/advanced-capabilities)

### 3.2 child 间能否通信?——不能,且是"拓扑禁用 + 模型未训练"双重原因

**验证**:官方从没提供 sibling→sibling 的工具原语。child 唯一的对外工具面是 Devin MCP,而其写入/操作能力的作用域是"**自己的会话 ID**"——不存在 `send_to_peer(session_id)` 这样的工具。每个 child 有自己的 session URL、VM、事件日志;manager 的 MCP 能按 ID 触达任意 child,child 手里却没有 sibling 的句柄。

**解释为何(三点)**:

1. **拓扑上无通道**:Devin 的通信图是星型(manager 在中心),不是网状。这是 map-reduce-and-manage 的物理形态——并行单元之间不建边,天然规避"并行写导致隐式决策冲突"(2025 年 Don't Build Multi-Agents 的核心论点,§4 详述)。

2. **模型行为未训练**:Walden 2026-04 的原话是 cross-agent communication **"doesn't happen by default, because models haven't been trained in environments where it needed to"**——即使给模型这个能力,它也不会自发使用,因为训练环境里没有这种需求。所以 Cognition 的判断是:与其寄望模型自发学会 peer 协商,不如先做成 manager 中转。

3. **经验判断:unstructured swarm 是 distraction**:
> "We think the unstructured-swarm approach, arbitrary networks of agents negotiating with each other, is mostly a distraction. The practical shape is map-reduce-and-manage: a manager splits work, children execute, the manager synthesizes and reports back."
> — [Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working)

**补充旁证**:Walden 在 Latent Space 里说 Devin 其实**已经能通过 MCP "arbitrarily message other Devins and create new Devins"**(给了能力),但结果是"creates a really chaotic world",所以 day-to-day 最实用的仍是单个 Devin——这解释了为什么产品层**不给 child 开放 peer 通道**。

### 3.3 一个注意:manager 能读 child trajectory 但读不到"实时思考"

manager 的监督手段是**结构化事件流**(工具调用、结果、消息),不是 child 的内心独白或屏幕流。这意味着"监控"是异步、事件驱动、可审计的,而不是同步窥视。

---

## 4. Q3: "Schedule messages to itself" 的自我调度与持久化

### 4.1 两个机制叠加

**机制 A:manager 的 self-follow-up(你要问的那个)**
> "**Schedule messages to itself** — set reminders to check back on long-running child sessions"
> — [Advanced Capabilities](https://docs.devin.ai/work-with-devin/advanced-capabilities)

即 manager 给自己会话排一条"晚点提醒我检查 child 进度"的消息——对应多 agent 场景里的 **checkpoint/follow-up**:manager 不必干等或死循环轮询,而是定时被唤醒去汇总。

**机制 B:通用调度器 `devin_schedule_manage`**
> "List, get, create, update, or delete schedules. Supports cron expressions for recurring schedules, one-time scheduling, notification preferences, and agent selection"
> — [Devin MCP docs](https://docs.devin.ai/work-with-devin/devin-mcp)

### 4.2 持久化怎么实现——三层

1. **Session 可恢复(VM 状态保留)**:API `resumable: true`(默认)——会话停止后**保留 VM 状态以便恢复**。状态机含 `sleeping/resuming`,`status_detail` 区分 `inactivity`(闲置休眠)与 `user_request`(手动休眠)。→ "follow-up 唤醒后,child 的现场还在"。

2. **跨会话笔记(Devin 自持状态)**:官方 Schedule Devins 博文明确:
> "Devin carries state between runs. It reads and writes its own notes across sessions, which means each run builds on the context of the one before it rather than starting from scratch."
> — [Devin can now Schedule Devins](https://cognition.com/blog/devin-can-now-schedule-devins)

→ 这就是持久化的**语义层**:不是靠外部 DB 存任务,而是 Devin 自己维护"我上次做到哪"的 notes,下次运行接着做(例:周五自动编译 release notes 时不会重复总结上周已覆盖的 PR)。

3. **与 managed Devins 组合**:调度器唤醒 manager → manager 扇出 child → 汇总报告 → 发 Slack。全自动。
> "set up a weekly QA pass where Devin spins up a managed Devin for each page of your application, tests them all in parallel, compiles the results into a single report, and posts it to your team's Slack channel."
> — [Devin can now Schedule Devins](https://cognition.com/blog/devin-can-now-schedule-devins)

**与 prime-agent 对照**:prime-agent 同样有 `/heartbeat`(用户级)、`rlm_heartbeat`(agent 自建多条)、`prime-agent schedule`(cron/一次性)、持久化 goals(`/goal --budget`)、autonomous gates——两者机制高度同构,区别只在 Devin 是云端托管、prime-agent 是本地 daemon(§5)。

---

## 5. Q4: Walden Yan 2025 "Don't Build" → 2026 "受控可行"的转变

### 5.1 2025-06-12 的原立场(Don't Build Multi-Agents)

两大 Context Engineering 原则:
> **P1:Share context, and share full agent traces, not just individual messages**
> **P2:Actions carry implicit decisions, and conflicting decisions carry bad results**
> — [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)

经典反例(Flappy Bird):两个 subagent 各自误解任务,产出风格冲突(马里奥背景 + 不像游戏素材的鸟),最终 agent 面对"合并两个 miscommunication"的烂摊子。结论:
> "In 2025, running multiple agents in collaboration only results in fragile systems. The decision-making ends up being too dispersed and context isn't able to be shared thoroughly enough... I don't see anyone putting a dedicated effort to solving this difficult cross-agent context-passing problem. I personally think it will come for free as we make our single-threaded agents even better at communicating with humans."
> — [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)

同时点名批评 **OpenAI swarm / Microsoft autogen** 把多 agent 当默认架构。当天/次日 Anthropic 发布 multi-agent research system(90.2% 相对提升),形成著名的 "Cognition vs Anthropic" 对撞——后来 Sunil Prakash 调和:"Multi-agent is not an architecture decision. It is a workload decision."(Anthropic 做的是可并行化的研究 workload,Devin 做的是不可并行化的编码 workload,两者都对。)

### 5.2 2026-04-22 的转变(受控多 agent 可行)

**承认转变 + 保留部分立场**:
> "A lot has changed since then... Our original observations still hold today for parallel-writer swarms... But we've found a narrower class of patterns that do: setups where multiple agents contribute intelligence to a task while writes stay single-threaded."
> — [Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working)

**转变的技术依据(模型侧)**:
> "models have become way more naturally 'agentic.' They intuitively understand tool use, their own context limits, and how to distill their context for collaborators (human or otherwise)."

**被验证的三类受控模式**:
1. **Code-Review Loop(generator-verifier)**:Devin Review 平均每 PR 抓 2 个 bug,~58% 严重。**反直觉发现:编码 agent 与评审 agent 共享最少上下文时效果最好**——评审 agent 只看到 diff,避开 coder 数小时的上下文累积(context rot / attention 数学),反向推理反而更敏锐。但**中间的"communication bridge"需要专门调**:主 agent 要用自己的全上下文过滤评审返回的 bug 列表,防止死循环/越界/违令。
2. **Smart Friend(弱主模型 + 强咨询模型)**:小模型调用大模型当工具。两个难点:**"弱模型怎么知道自己到极限了"**(SWE-1.5 在此失败,SWE-1.6 部分成功,Cognition 明确认为这是 training problem)与**"smart friend 怎么把话传回去"**(应指示主模型去查它没看过的文件,而不是编造理论)。注意:SWE-1.6 后的公开口径中,此模式已在 Fusion 里演进为**双模型各持独立缓存上下文**的 sidekick(§5.3)。
3. **Manager→Child delegation**:就是 Managed Devins,§5.4 详述。

### 5.3 Fusion(2026-06-29)是这套思路的算力版本

Devin Fusion 的 sidekick 架构 = 两个完整 agent 并行运行(主 agent 用 frontier 模型、sidekick 用便宜模型),**各自维护持久化缓存上下文**,主 agent 动态决定把哪些任务交给 sidekick。相比 Smart Friend 的按次调用,sidekick 避免每次跨模型调用的缓存未命中成本。模型切换在 **context compaction 时点**进行(反正要重算缓存,切换免费)。结果:frontier 级性能,成本降 35-60%。→ 这是"多 agent = 智能注入 + 成本工程"的终极形态。

### 5.4 他们踩的坑(cross-agent 通信需要专门训练)——Q4 核心答案

> "Getting it to feel coherent took more context engineering than we expected.
> **① Managers trained on small-scoped delegation default to being overly prescriptive, which backfires when the manager lacks deep codebase context.**
> **② Agents assume they share state with their children when they don't.**
> **③ Cross-agent communication, a sub-agent writing messages back to its manager to be passed to other agents in the agent team, doesn't happen by default, because models haven't been trained in environments where it needed to.**
> Each of these took dedicated work to fix, and we're still improving on all of them."
> — [Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working)

逐条解读:
1. **manager 过度 prescriptive**:训练数据里的小范围委托让 manager 习惯把每步都规定死,但当 manager 没有 child 那样的深层代码库上下文时,过度规定 = 给 child 塞错误前提。**修法**:提示词工程 + 后续模型训练(manager 学会"知道什么该委托出去")。
2. **假共享状态**:agent 天然假设"我 spawn 的孩子知道我知道的",但**隔离 VM 下根本没有共享状态**。这是隔离架构(§2.3 brain-machine 分离)带来的新坑——child 必须显式索要上下文,或者 manager 必须显式投喂。
3. **cross-agent 通信不默认发生**:即使拓扑上允许,模型也不会自发"写消息给 manager 转交 sibling"——因为训练语料/环境里没有这种交互场景。**这是需要专门训练的行为**,不是加个 API 就能解决。

**收束判断(未来方向)**:
> "The open problems are all communication problems. How does a weaker model learn when to escalate? How does a child agent surface a discovery that should change its siblings' work? How do you transfer context between agents without drowning the receiver? You can get decently far with prompting, but we also expect the next generation of models, **including the ones we train ourselves**, to start closing these gaps."
> — [Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working)

→ Cognition 明确表态:下一步靠**自训模型把 agent 间通信行为训练进模型**,而不是继续堆 harness 提示词。

---

## 6. Q5: 对 prime-agent 的借鉴清单

对照基线(prime-agent 现状,来自 long-running-agents.md):本地 daemon worker 进程、`agent_message.send(receiver_role, receiver_name, mode)`(nuclear-family 作用域:parent/sibling/child)、delivery mode 三档(**auto**=忙则 steer 闲则即投 / **steer**=强制注入活跃工作 / **follow_up**=等当前工作结束)、receipt(delivered/queued)、`prime-agent schedule`(cron/一次性)、`/heartbeat` + `rlm_heartbeat`(agent 自建多条)、`/goal` 持久化目标 + budget、autonomous gates、**进程隔离但非安全沙箱**(与 client 同 OS 权限)。

### 6.1 核心取舍:云端 VM 隔离 vs 本地 worker

| 维度 | Devin(云端 managed) | prime-agent(本地 daemon) |
|---|---|---|
| 隔离性质 | **安全沙箱级**:独立 VM + 最小化 secret + brain 从机器不可达 | **仅生命周期隔离**:进程隔离防崩溃/失败传播,非安全沙箱,同 OS 权限 |
| brain 位置 | Cognition 侧(不可从 VM 访问) | 进程内(client 同权限,持有 API key) |
| 状态持久化 | 云端 session store + VM 快照(resumable) | JSONL transcript + 会话 artifact 目录,重启可恢复 |
| child 通信通道 | 仅 manager↔child(MCP),child 间无通道 | nuclear-family 一等公民(parent/sibling/child 均可发) |
| 调度 | 云端 cron + manager self-follow-up | 本地 daemon 内 schedule + heartbeat + goal |
| 成本计量 | ACU(平台算力单位) | token/wall-clock |
| 适用场景 | 企业规模化、需要审计/隔离/外包基础设施 | 低延迟、完全控制、零厂商锁定、个人本地 |

**关键 insight(来自 Walden 的 brain-machine 分离)**:Devin 用隔离换到了**安全边界=能力边界**——"whatever you put on the machine, that is the scope of what the agent is free to do"。prime-agent 的文档也诚实承认"process-isolated for lifecycle and failure containment, **not security-sandboxed**"。**如果 prime-agent 需要多租户或对抗性安全边界,这是必须补齐的差距;如果只是单用户本地使用,进程隔离 + 同权限是合理取舍**(不必为此引入 VM 开销)。

### 6.2 child 间禁通信 vs prime-agent sibling 通信:设计差异的本质

- **Devin 禁 peer 通信是"能力不匹配"的务实选择**:模型没被训练过跨 agent 通信(§5.4 坑③),强行开 peer 通道只会得到 chaotic world(Walen 原话);所以拓扑上直接不建边,通信全部经 manager 中转 = **把"协调智能"收敛到单一上下文里**。
- **prime-agent 提供 sibling 通信是"harness 先行"的选择**:把 nuclear-family 消息作为一等公民,**押注模型能力追上来**;且 delivery mode(steer/follow_up)+ receipt 机制已经考虑了"消息何时该注入"的工程问题。

**借鉴判断**:
- 如果 prime-agent 的目标是**个人/小团队本地编码**,保留 sibling 通信 + 明确"**sibling 消息必须经 manager 语义过滤**"(对应 Devin 的 communication bridge 教训——见 review loop 部分:不经主上下文过滤的消息会导致死循环/越界);
- 如果目标是**多租户/生产**,则应默认采用 manager 中转拓扑,把 peer 消息降级为"manager 显式转发的消息"。

### 6.3 对 prime-agent 的 7 条具体借鉴

| # | 借鉴项 | Devin 依据 | 落地建议 |
|---|---|---|---|
| 1 | **trajectory 可读回** | manager 读 child 完整事件日志来"理解卡在哪、改进下次拆解" | 已有 JSONL transcript 基础,增加"manager 按需检索 child 历史事件的工具"而非全文灌入(防 context rot) |
| 2 | **gather/等待原语** | `devin_session_gather` 等会话到 settled 状态,避免轮询 | 补一个"等 N 个 worker 全部到终态"的原子等待 API(现有 receipt 只到 delivered/queued,缺 aggregated wait) |
| 3 | **假共享状态防御** | "Agents assume they share state with their children when they don't" | 在 spawn 子 agent 的提示里**显式声明"你与父/sibling 不共享状态,需要的信息必须自己获取或显式索要"**(文档/模板级) |
| 4 | **manager 过度 prescriptive 的抑制** | manager 无深层上下文时过度规定 = 喂错前提 | manager 模板加入"不确定的细节留给 child 自行决定;只规定契约(输入/验收/产出物)" |
| 5 | **ACU 式算力预算** | `max_acu_limit` + 监控 + sleep/terminate 走偏 child | 本地版:每 worker 的 token 预算上限 + 超预算自动暂停/降级 + "terminate 卡死 child"生命周期命令 |
| 6 | **approval 分层** | `bypass_approval` 按 session 授予,不是全局 | 本地版:高危工具(网络/写文件系统外部/执行任意命令)默认要求确认,低危工具免确认——per-session 粒度 |
| 7 | **self-follow-up 调度语义** | "schedule messages to itself" + Devin 跨会话 notes | 已有 `/goal` + heartbeat 基础,补"manager 给自己排 checkpoint 提醒,而非同步阻塞等待 child" |

### 6.4 不必借鉴(差异合理处)

1. **云端 VM + brain-machine 分离**——单用户本地场景下进程隔离足够;引入 VM 只增延迟与复杂度。但"**secret 最小化**"思想应保留(API key 不要放在可被 agent 任意写入的共享目录)。
2. **child 完全禁 peer 通信**——prime-agent 的 nuclear-family 作用域本身已有限制(只能 parent/sibling/child,且 `send("all")` 广播限于 family roster),比 Devin 的纯星型更灵活,是合理差异化;只需补上 §6.3#3 的"消息经 manager 语义过滤"防线。
3. **cron 云端托管**——本地 daemon 内 schedule 已覆盖(且文档明示 crash 后 due tick 先 claim 再投递、missed tick 合并,可靠性设计到位)。

---

## 7. 原始资料

### 一手(官方)
- [Devin can now Manage Devins](https://cognition.com/blog/devin-can-now-manage-devins)(2026-03-19)
- [Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working)(Walden Yan,2026-04-22)
- [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)(Walden Yan,2025-06-12)
- [Devin Fusion](https://cognition.com/blog/devin-fusion)(2026-06-29)
- [Devin can now Schedule Devins](https://cognition.com/blog/devin-can-now-schedule-devins)
- [Devin September '24 Product Update(MultiDevin 首宣)](https://cognition.ai/blog/sept-24-product-update)
- [Devin MCP docs](https://docs.devin.ai/work-with-devin/devin-mcp)
- [Devin Advanced Capabilities](https://docs.devin.ai/work-with-devin/advanced-capabilities)
- [Devin API v3 — Sessions/Create Session](https://docs.devin.ai/api-reference/v3/sessions/post-organizations-sessions)
- [Latent Space: The Age of Async Agents(Walden Yan + Cole Murray,2026-05-28)](https://www.latent.space/p/cognition)
- [prime-agent long-running-agents.md](https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/docs/long-running-agents.md)

### 二手(旁证/分析)
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)(2025-06-13,与 Don't Build 同日对撞)
- [Jason Liu: Why Cognition does not use multi-agent systems](https://jxnl.co/writing/2025/09/11/why-cognition-does-not-use-multi-agent-systems/)(2025-09-11)
- [Arize: Swarm management in agent harnesses](https://arize.com/blog/swarm-management-of-agent-harnesses/)(swarm 层原语清单:session keys/registry/lifecycle events/recovery sweeps)
- Sunil Prakash 调和文:"Multi-agent is not an architecture decision. It is a workload decision."(2026-06-07)

### 已验证事实清单(可信度标注)
- 功能能力(MCP 工具名、API 字段、三阶段时间线):**官方文档直接验证,高可信**
- manager 读 trajectory / brain-machine 分离 / child 间无通道:官方博文 + podcast 一手引用,**高可信**
- 消息注入的内部队列机制 / ACU 计算公式 / outpost 与 child 拓扑细节:未公开,**未知**——报告按"事件流注入"推断并标注
- Walden 个人 X 历史:未能验证(检索通道限制),但两篇博文全文已直接抓取核对

---

## 8. 遗留开放问题(诚实标注)

1. `devin_session_interact` 的消息注入是"推送进推理中模型"还是"写入队列等下一轮拾取"——官方未公开内部机制(status 有 `waiting_for_user` 态但触发路径未文档化)。
2. child session 可用的工具集是否仅限 Devin MCP,还是另有未公开的用户级工具面。
3. ACU 的计算口径未公开。
4. outpost/BYOB 部署下 manager-child 拓扑细节仅 API 提及,无深度公开文档。
