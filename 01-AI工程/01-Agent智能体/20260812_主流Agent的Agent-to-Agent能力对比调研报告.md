# 20260812_主流Agent的Agent-to-Agent能力对比调研报告

> **观测日期**：2026-08-12
> **检索范围**：各 Agent 官方文档/公告/blog、GitHub 仓库、社区对比文章、prime-agent 本地源码与实测
> **核心问题**：主流 AI coding agent 中，哪些真正支持"agent 之间直接通信"（Agent-to-Agent，非经编排者中转）？prime-agent 的差异化在哪？
> **触发背景**：实测 prime-agent 的 agent-to-agent 消息（双会话 daemon 常驻 + send_message 互发成功）后，用户对其特别感兴趣，启动全网调研。

---

## 我能讲出来的版本（5 行）

1. **"多 agent 并行"已是主流标配**：Claude Code、Codex、Kimi（300 子 agent）、Cursor（8 并行）、Devin、Kiro、Amp、Zed 全都支持，但绝大多数是"编排者（主 agent）派发子 agent，子 agent 只回传父"的 hub-and-spoke 模式。
2. **"agent 之间直接互发消息"是稀缺能力**：只有 4 家支持——prime-agent（首类，`agent_message.send` + family roster）、Claude Code Agent Teams（实验性、默认关闭）、Devin（manager→child 单向为主）、omp（`hub` 工具）。Codex/opencode/Kimi 都不支持，opencode 甚至明确拒绝双向 A2A（怕 ACK 死循环）。
3. **"本地常驻 daemon + 外部触发"是另一个稀缺组合**：prime-agent 是唯一"本地 worker 进程 daemon"；其他要么无 daemon（Claude/Codex/opencode/Zed），要么是云端 daemon（Amp Orbs、Devin VM、Kiro Cloud、Cursor Cloud Agents）。
4. **标准层有 A2A 协议**（Google 2025-04 → Linux Foundation，100+ 企业采用），但 Claude Code/Codex 都未原生实现，需 MCP bridge 中转——说明"agent 互信"标准还在早期，prime-agent 自研方案暂时不必追随。
5. **prime-agent 的差异化是三者的组合**：本地 daemon + 首类 A2A API + nuclear-family 显式作用域（只允许给 parent/sibling/child 发消息，防跨会话串扰）。

---

## 1. 对比矩阵（14 家主流 agent，2026-08）

图例：🟢 支持 · 🟡 部分/实验/需自建 · 🔴 不支持 · ⚪ 未明确

| Agent | 多 Agent 并行 | 通信拓扑 | Agent↔Agent 直接通信 | 常驻 daemon+外部触发 | 核心机制 |
|---|---|---|---|---|---|
| **Claude Code** | 🟢 Subagents/Agent Teams/Workflows | 编排+实验 peer | 🟡 Agent Teams 互发消息（实验性，默认关闭）；Cross-session messaging | 🔴 无本地守护 | `Agent/Task` 工具、team lead |
| **OpenAI Codex** | 🟢 Subagents+Agents SDK | 编排者 | 🟡 仅 Agents SDK handoff（经 PM 编排），非原生 A2A | 🔴 无 | `codex()` MCP + `transfer_to_*` |
| **Antigravity CLI**（ex-Gemini CLI） | 🟢 Subagents+Async workflows | 编排者 | ⚪ 未明确 A2A | 🟡 云端 Agent Manager | 共享 harness + Agent Manager |
| **Kimi CLI / Agent Swarm** | 🟢 最多 300 并行 | 单编排者 | 🔴 无（orchestrator 模式） | 🟡 K3 Swarm 服务端 | PARL 训练 |
| **opencode** | 🟢 Subagents | 编排者 | 🔴 无（#19999 提案被拒，怕 ACK 循环） | 🔴 无 | `task` 工具 |
| **omp / pi-agent** | 🟢 `task`+`orchestrate` | 编排者 | 🟢 **有**：`hub` 工具 | 🟡 长跑 job，非系统 daemon | task fan-out + hub msg |
| **pi（upstream）** | 🔴 明示 No sub-agents | — | 🔴 | 🔴 | 最小 harness |
| **Cursor** | 🟢 最多 8 并行 | 编排+用户中转 | ⚪ Background Agents 用户中转 | 🟢 云端后台 | Agents Window |
| **Windsurf→Devin Desktop** | 🟡 Multiple Cascades | 编排者 | ⚪ | 🟢 云端 VM | Cascade→Devin Local |
| **Devin** | 🟢 Managed Devins | Manager+子 | 🟢 manager→child 发消息；child 间不互发 | 🟢 完整云端 daemon | 独立 VM/子 |
| **Aider / Cline** | 🔴 无 | — | 🔴 | 🔴 | 单 agent |
| **OpenHands** | 🟡 需自建（CAID） | Manager+worker | 🟡 经 git+JSON，非 A2A | 🟡 沙盒 | git worktrees |
| **Kiro（Amazon）** | 🟢 Agent Focus+`/spawn` | Architect 编排 | ⚪ `/spawn` 单向 | 🟢 云端 sandbox | 统一 harness |
| **Sourcegraph Amp** | 🟢 Task+Orbs | 编排者 | ⚪ Orbs 可收外部事件 | 🟢 Orbs 云端 daemon | Threads+Orbs |
| **Zed** | 🟢 Parallel Agents | 编排+ACP | 🟡 External Agents 经 ACP 并列 | 🔴 无 | Threads Sidebar |
| **⭐ prime-agent** | 🟢 `rlm()` 编程式并行 | 编排+family roster | 🟢 **首类**：`agent_message.send(role,name,mode)` | 🟢 **本地 daemon+worker 进程** | RLM IPython kernel+daemon |

---

## 2. prime-agent Agent-to-Agent 架构深度解析（本地源码）

### 2.1 三层调用链

```
Python skill (agent-message/__init__.py)
  → host_request("agent_message.send", payload)
    → Jupyter comm (control channel) → KernelManager
      → AgentSession.handleAgentMessageHostRequest()
        → DaemonMode.sendAgentSessionMessage() / sendRemoteAgentSessionMessage()
```

- **Python 层**极薄：仅参数校验 + UI 显示，路由和身份验证全在 TypeScript daemon
- **Host bridge 层**（`src/core/agent-messages.ts`）：注册 `agent_message.list_agents` / `agent_message.send` 两个 handler
- **Daemon 路由层**（`src/modes/daemon/daemon-mode.ts`）：创建带 UUID 的 payload → 计算 fromRelationship → 取目标锁 → 检查 paused/存活 → 决定投递或排队

### 2.2 关键设计点

| 设计 | 说明 |
|---|---|
| **Family roster（家庭名册）** | `buildAgentFamilyRoster()` 从 catalog 构建 parent/sibling/child 关系；`assertAgentFamilyReach()` 限制"只能给 nuclear family 发消息"，防跨会话串扰 |
| **三种投递模式** | `auto`（空闲直接投递，忙碌 steer）、`steer`（强制注入活跃工作）、`follow_up`（等当前工作完成） |
| **非阻塞投递** | 排队消息不阻塞发送方（注释明确：`awaiting here deadlocks mutual sends between busy sessions`） |
| **限流与安全** | 令牌桶 3 tokens/s、每 session 排队上限 20 条、消息最大 16K 字符、daemon 从 session 元数据推导 sender（Python 层无法伪造身份） |
| **广播** | `send("all", message)` 只广播给 family roster 成员，`Promise.allSettled` 部分失败不阻塞 |
| **跨 worker 路由** | 通过 supervisor socket 跨 worker 转发（`sendRemoteAgentSessionMessage`） |

### 2.3 与传统 subagent 模式的根本区别

| 维度 | 传统 subagent（Claude Task/Codex/Swarm） | prime-agent 对等消息 |
|---|---|---|
| 通信方向 | 单向：子→父汇报 | 双向：parent/sibling/child 任意 |
| 协调位置 | 主 agent context（会膨胀） | daemon 总线（context 互不污染） |
| 阻塞性 | 主 agent 等结果 | 非阻塞异步投递 |
| 发现机制 | 手动管理 agent 列表 | roster 动态发现（含 inactive） |
| 持久性 | 绑定主 agent 执行流 | daemon 独立，崩溃恢复后消息队列仍在 |

**一句话**：prime-agent 把"agent 间通信"从 execution context 抽离为 daemon 基础设施——"daemon 路由 peer agent"而非"主 agent 调度子 agent"。

---

## 3. 协议标准现状（2026-08 深度版）

### 3.1 三层协议架构（已收敛）

协议生态已收敛为 **MCP(工具协议) + A2A(agent 间协议) + ACP(editor↔agent 协议)** 三层,2025-12-09 起同归 **Agentic AI Foundation (AAIF)**(Linux Foundation,共同发起方 Anthropic/Block/OpenAI,白金赞助 Google/Microsoft/AWS/Cloudflare/Bloomberg)治理。

```
   ┌──────────────────┐
   │     User         │
   └────────┬─────────┘
            │ 交互
   ┌────────▼─────────┐
   │  Editor / IDE    │ ◄─── ACP (Zed/JetBrains 等)
   └────────┬─────────┘
            │ 调用
   ┌────────▼─────────┐
   │      Agent       │
   └────┬─────────┬───┘
        │         │
   MCP  │         │  A2A
   (工具)        (其他 agent)
        │         │
   ┌────▼───┐ ┌───▼────┐
   │ Tools/ │ │ 其他   │
   │ Data   │ │ Vendor │
   └────────┘ └────────┘
```

| 协议 | 定位 | 作用域 | 传输 | 现状 |
|---|---|---|---|---|
| **MCP** | Agent↔Tool | 单信任域 | JSON-RPC（2026-07-28 起无状态核心） | 4 亿下载/月，10k+ 服务器；**Tasks 扩展最接近 agent 互发消息** |
| **A2A** | Agent↔Agent | 跨组织/跨厂商 | HTTP+JSON / JSON-RPC / gRPC | v1.0(2026-03)稳定，v1.2(2026-04)签名 Agent Card；150+ 组织；22k stars |
| **ACP** | Editor↔Agent | 单客户端 | JSON-RPC stdio / HTTP | 25+ agents、9+ editors；Zed 主导+JetBrains 合治 |

### 3.2 A2A 协议详情（最接近"agent 直接发消息"的标准）

- **Agent Card**：能力描述（类似 LSP capabilities），v1.2 起签名可执行
- **Task lifecycle**：`submitted → working → input-required → auth-required → completed/failed/canceled`
- **Opaque Execution 原则**：agent 自主决策，不暴露内部工具
- **云原生集成**：Azure AI Foundry、Copilot Studio、Amazon Bedrock AgentCore、Google Agent Engine
- **安全缺陷共识**（Red Hat MAESTRO/Palo Alto Unit 42/Semgrep/Trustwave 多机构确认）：prompt injection 无防护、Agent Card 签名可选、无 consent state、无 token TTL 强制、Card 描述字段可作注入载体。**A2A 是 wire protocol，不是 execution security layer**

### 3.3 厂商策略

- **OpenAI**：无独立 A2A 协议；Responses API 私有多 agent（spawn_agent/send_message/wait_agent 等 6 动作）+ AGENTS.md(开源，60k+ 项目采用)+ 加入 AAIF
- **Microsoft**：Agent Framework 1.0（Semantic Kernel+AutoGen 合并），**押注 A2A** 作为多 agent 互联层
- **Anthropic**：Claude Agent SDK（subagents+Workflow tool+SendMessage），不发布独立跨厂商协议
- **prime-agent**：自研 `agent_message`（daemon 内部 family-scope）——**已通过 `--mode acp` 接入 ACP 标准**，支持 MCP servers、AGENTS.md

### 3.4 prime-agent 与标准的关系：互补，不重叠，不冲突

| 维度 | prime-agent `agent_message` | A2A |
|---|---|---|
| 信任域 | 同 daemon（单用户/本地） | 跨域/跨厂商 |
| 身份 | Session 名 + family 关系 | Agent Card + 可选 DID |
| 可发现 | `list_agents()` 进程内 RPC | HTTPS `/.well-known/agent.json` |
| 生命周期 | auto/steer/follow_up | submitted/working/.../completed |
| 跨组织 | ❌ 单用户信任域 | ✅ |

**判断**：prime-agent 的 nuclear family scope 在安全上是 *feature 而非 gap*（作用域受限+限流+排队上限天然规避了 opencode 担心的 ACK 死循环）。**短期推荐维持 nuclear family，把 ACP 作为外部接入界面**；未来可选路径是把 `agent_message.send` 暴露为 A2A Server（提供 Agent Card + JSON-RPC endpoint）。

### 3.5 社区关键争议

- **opencode maintainer 拒绝双向 A2A**："immediately degenerated into ACK loops where agents just kept acknowledging each other instead of doing work"——设计 A2A 最重要的反面教训
- **"Chat app is wrong primitive"**（2026-06）：延迟瓶颈在 receiver 冷启动而非传输；ticketing 比 chat room 更适合 agent；identity 比 message 持久
- **"Agents can connect. They still can't communicate."**（2026-02）：现有协议栈解决 transport 不解决 meaning，缺 Layer 8(Communication)+Layer 9(Semantic)

### 3.6 协议矩阵对比（7 个方案）

| 维度 | MCP | A2A | ACP | OpenAI Responses 多 agent | MS Agent Framework | Claude Agent SDK | prime-agent `agent_message` |
|---|---|---|---|---|---|---|---|
| **作用域** | Agent↔Tool | Agent↔Agent | Editor↔Agent | In-runtime agent tree | In-runtime agent graph | In-session subagents | In-daemon family |
| **信任域** | Single tenant | Cross-org | Single client | Single API org | Single tenant | Single session | Single daemon（本地） |
| **传输** | JSON-RPC（2026-07-28 后 stateless HTTP） | HTTP+JSON / JSON-RPC / gRPC | JSON-RPC stdio / HTTP | HTTP + WebSocket | HTTP + A2A | IPC（同进程） | Local daemon socket |
| **身份** | OAuth 2.1 | Agent Card（DID 可选） | Editor-supplied | API key | API key + A2A bridge | Session ID | Session 名 + family 关系 |
| **状态** | 2026-07-28 后无状态核心 | 有任务 lifecycle | 有 session | 树状 agent | handoff/group chat | fork / resume | 持久 JSONL + kernel snap |
| **可发现** | server capabilities | `/.well-known/agent.json` | ACP Registry | 不需要 | A2A bridge | 不需要 | `agent_message.list_agents()` |
| **治理** | AAIF / LF | LF（独立 A2A 项目） | Zed + JetBrains | OpenAI 私有 | MS 私有 | Anthropic 私有 | PrimeIntellect 私有 |
| **跨厂商** | ✅ 万级 SDK | ✅ 150+ orgs | ✅ 25+ agents | ❌ OpenAI-only | ⚠️ 需 A2A | ❌ Anthropic-only | ❌ 本地内核 |
| **2026-08 活跃度** | 4 亿下载/月 | 22k stars | 9+ editors / 25+ agents | Beta | 1.0 GA | Mainstream | 14.5k stars / MIT |

### 3.7 三个关键问题的回答

**Q1. 哪个协议最接近"agent 直接发消息"?**
**A2A**——唯一明确定义 agent 为一等公民、跨组织 peer-to-peer 通信的协议。任务生命周期完整（submitted→working→input-required→auth-required→completed/failed/canceled）、Agent Card 描述身份+能力、"Opaque Execution" 原则（agent 自主决策不暴露内部工具）。MCP Tasks 扩展次之（同信任域 agent↔server，适合长任务轮询非对等协商）；ACP 不在 agent-to-agent 范畴（editor↔agent）。

**Q2. MCP / A2A / ACP 的分工?**
- **MCP** = Agent 调用外部工具/数据（client-server，agent 是 client）
- **A2A** = Agent 调用其他 Agent（peer-to-peer，跨信任域）
- **ACP** = 人类通过 Editor 调用 Agent（2 实体 1 协议）
- 决策规则（Oracle）："如果你能说出第二个 agent 并解释它的独立决策，用 A2A；如果'第二个 agent'只是同一模型的不同 prompt，那是一次工具调用。"

**Q3. prime-agent 与标准的关系——互补、不重叠、不冲突**
prime-agent 的 `agent_message` 是 **trust-boundary 内部**的 daemon-routed family-scope 消息总线，不属于任何开放协议；但已主动接入标准：① `--mode acp`（把自己暴露为 ACP agent，扩展能力放 `ai.primeintellect.prime-agent` _meta 命名空间）② MCP servers 作为工具源 ③ AGENTS.md 兼容。
**生态切入点**：可把 `agent_message.send` 暴露为 A2A Server（Agent Card + JSON-RPC endpoint）让子 sessions 进 A2A 网络；或反向用 A2A client 引入外部 agent 为 parent/sibling（代价：需重设计 family 边界）。**短期推荐：维持 nuclear family（安全上是 feature 非 gap），把 ACP 作为外部接入界面**。

---

## 4. 结论：prime-agent 的差异化定位

**不在"能不能跑多个 agent"（大家都能），而在三件事的组合**：

1. **本地 daemon + 持久 session**——区别于所有云端 daemon 方案（Amp Orbs/Devin/Kiro/Cursor）
2. **首类 A2A API**（`agent_message.send`）——区别于纯 subagent/纯 orchestrator 方案
3. **nuclear-family 显式作用域 + 保留可寻址子 agent**——区别于一次性 fan-out，且天然规避了 opencode 担心的 ACK 死循环（作用域受限 + 限流 + 排队上限）

**最接近的对手**：
- Claude Code Agent Teams（同样 A2A，但实验性、默认关闭、无 daemon）
- omp `hub`（同样 A2A，但进程内、无持久 session）
- Devin Managed Devins（同样 messaging，但云端、child 间不互发）
- Amp Orbs（同样 daemon 持久，但云端、A2A 文档化薄）

---

## 原始资料

- Claude Code: https://code.claude.com/docs/en/sub-agents · https://code.claude.com/docs/en/agent-teams · https://claude.com/blog/subagents-in-claude-code
- Codex: https://developers.openai.com/codex/concepts/subagents · https://developers.openai.com/codex/guides/agents-sdk · https://github.com/openai/codex/discussions/3898
- Antigravity: https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/ · https://github.com/google-antigravity/antigravity-cli
- Kimi: https://www.kimi.com/help/agent/agent-swarm · https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents.html
- opencode: https://opencode.ai/docs/agents/ · https://github.com/anomalyco/opencode/issues/19999
- omp/pi: https://omp.sh/ · https://github.com/can1357/oh-my-pi · https://pi.dev/
- Cursor: https://cursor.com/docs/agent/agents-window · https://cursor.com/changelog/04-24-26
- Devin: https://cognition.com/blog/devin-can-now-manage-devins · https://cognition.com/blog/multi-agents-working/
- Kiro: https://kiro.dev/blog/one-agent/ · https://github.com/aws-samples/sample-kiro-cli-multiagent-development
- Amp: https://sourcegraph.com/amp · https://ampcode.com/
- Zed: https://zed.dev/blog/parallel-agents
- prime-agent 源码（本地克隆）: `packages/coding-agent/src/core/agent-messages.ts` · `src/modes/daemon/daemon-mode.ts` · `docs/long-running-agents.md`
- 实测记录：双会话 daemon 常驻 + send_message 互发成功（A→B "hello from agent A" 送达确认）
