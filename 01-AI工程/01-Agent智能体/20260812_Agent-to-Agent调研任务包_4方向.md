# 多 Agent 调研任务包 — Agent-to-Agent 通信深度调研（4 方向）

> 分发给 4 个并行 agent。每个方向一个 prompt，已内置一手来源清单与专属问题。
> 背景（所有 agent 共用）：prime-agent（PrimeIntellect 开源 RLM agent）实现首类 agent-to-agent 通信：
> `agent_message.send(role, name, mode)` + daemon 协调 + nuclear-family 作用域（只能发给 parent/sibling/child）。
> 已实测：双会话 daemon 常驻 + send_message 互发成功。参考文档：
> https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/docs/long-running-agents.md

---

## 方向 A：Claude Code Agent Teams + Dynamic Workflows 源码级深挖

**任务**：Claude Code 的 Agent Teams（实验性，默认关闭）和 Dynamic Workflows 是最接近 prime-agent A2A 的官方实现。深挖其源码与设计限制。

**一手来源**：
- https://code.claude.com/docs/en/agent-teams
- https://code.claude.com/docs/en/workflows
- https://code.claude.com/docs/en/cross-session-messaging
- https://claude.com/blog/subagents-in-claude-code
- https://claude.com/blog/introducing-dynamic-workflows-in-claude-code
- 社区源码分析：https://decodeclaude.com/teams-and-swarms/ · https://www.claudecodecamp.com/p/claude-code-agent-teams-how-they-work-under-the-hood · https://github.com/openedclaude/claude-reviews-claude/blob/main/architecture/08-agent-swarms.md

**专属问题**：
1. Agent Teams 的文件邮箱机制（~/.claude/teams/{name}/inboxes/）与 flock 并发控制——为什么选文件而非 IPC/socket？
2. SendMessage 工具的身份验证：如何确认消息来自另一个 Claude 会话而非用户？（跨会话消息被标记为"来自其他 Claude session，非你本人"）
3. 权限委托链路：teammate 无交互终端时 permission_request/permission_response 如何经 leader 中转？
4. 已知限制：session 恢复、任务协调、shutdown 行为、headless（-p）模式下 mailbox 投递缺陷
5. **对 prime-agent 的借鉴清单**：哪些设计该抄？哪些是它该避免的（如 idle pings 占满 inbox、headless 投递 bug）？

---

## 方向 B：omp `hub` + `task` 工具实现深挖

**任务**：omp（can1357/oh-my-pi，pi 的 TypeScript fork）的 `hub` 工具（message live agents + supervise）是最接近 prime-agent A2A 的开源实现。深挖其 IPC 与并发模型。

**一手来源**：
- https://omp.sh/ · https://github.com/can1357/oh-my-pi
- 源码分析：https://deepwiki.com/can1357/oh-my-pi/12.2-task-delegation
- pi（上游）：https://pi.dev/ · https://github.com/earendil-works/pi

**专属问题**：
1. `hub` 的完整 API：message live agents、wait/cancel background jobs、supervise 长进程——底层 IPC 是什么（socket？stdio？）？
2. `task` 工具的并发模型：Semaphore + mapWithConcurrencyLimit 的实现细节；与 prime-agent 的 daemon worker 进程模型有何本质区别？
3. `orchestrate` 关键字（等价 Claude ultracode）如何触发多阶段并行 subagent 合同？
4. 生命周期：omp 的 AsyncJobManager 跑后台任务，但为何"不是系统级 daemon"？它与 prime-agent 的"session 整体搬进 worker 进程"差在哪？
5. **对 prime-agent 的借鉴清单**：hub 的监督模式（supervise）与 task 的并发控制，哪些值得吸收？

---

## 方向 C：Devin Managed Devins 的 messaging 架构与权限模型

**任务**：Devin（Cognition）是云端 managed multi-agent 的标杆：manager Devin 拆任务给子 Devin（各自独立 VM），支持 mid-task 消息注入。深挖其 messaging 与权限。

**一手来源**：
- https://cognition.com/blog/devin-can-now-manage-devins
- https://cognition.com/blog/multi-agents-working/
- https://cognition.com/blog/devin-fusion
- https://cognition.ai/blog/multi-agents-working/

**专属问题**：
1. manager→child 消息注入的实现：mid-task 指令/上下文/纠错如何传进子 Devin 的独立 VM？
2. 权限模型：manager 如何管理子 Devin 的 tool 权限？子 Devin 之间能否通信？（官方说 child 间不互发，验证并解释为何）
3. "Schedule messages to itself"：Devin 的自我调度机制（follow-ups/checkpoints）如何实现持久化？
4. Walden Yan 2025 年的"Don't Build Multi-Agents"到 2026 年"受控多 agent 可行"的转变——技术依据是什么？他们踩了什么坑（cross-agent communication 需要专门训练）？
5. **对 prime-agent 的借鉴清单**：云端 VM 隔离 vs prime-agent 本地 worker 的取舍；child 间禁通信 vs prime-agent sibling 通信的设计差异

---

## 方向 D：A2A 协议与 MCP bridge 生态现状

**任务**：A2A（Google → Linux Foundation AAIF）是唯一"跨厂商 agent 互信"标准，但 Claude Code/Codex 都未原生实现。深挖 A2A 现状、安全缺陷、以及 prime-agent 接入的可行性。

**一手来源**：
- https://github.com/a2aproject/A2A
- https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year
- https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html
- 安全批判：https://grith.ai/blog/a2a-protocol-zero-defenses-prompt-injection · arXiv 2602.11327 · arXiv 2606.28690
- 采用现实：https://dreaming.press/posts/a2a-protocol-at-one-year-adoption-reality.html
- 决策框架：https://blogs.oracle.com/developers/the-agent-communication-matrix-when-mcp-a2a-and-plain-rest-each-win

**专属问题**：
1. A2A v1.2 的 Agent Card 签名 + 域绑定（Agent-DID + DNS TXT）如何工作？
2. 安全缺陷清单核实：prompt injection 无防护、无 consent state、无 token TTL 强制——哪些已被修复、哪些仍开放？
3. MCP Tasks 扩展（SEP-1686/2663）vs A2A：两者在"agent 通信"上的边界在哪里？会不会合并？
4. 社区"ticketing > chat"论点：异步任务票 vs 同步消息，哪种更适合 agent 协作？对 prime-agent 的 auto/steer/follow_up 投递模式有何启发？
5. **prime-agent 接入 A2A 的可行性**：把 `agent_message.send` 暴露为 A2A Server 的最小实现路径？nuclear family 边界如何与 A2A 的跨域模型共存？给出具体方案或否决理由

---

## 通用输出要求（4 个方向都适用）

- Markdown 报告，含：文本架构图、关键代码/文档引用（带 URL）、与 prime-agent 的逐项对比表、明确的"该借鉴/该避免"清单
- 一手来源 ≥10 个，标注可信度（官方文档=高，社区分析=中，未核实=低）
- 长度 2500-4000 字，结构清晰
- 每节结论必须可追溯到来源，禁止臆测
