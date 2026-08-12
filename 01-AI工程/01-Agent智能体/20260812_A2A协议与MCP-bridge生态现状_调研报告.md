# 方向 D 调研报告:A2A 协议与 MCP bridge 生态现状

## 摘要

本报告针对 Google 发起、现已移交 Linux Foundation AAIF 治理的 A2A（Agent2Agent）协议，在 2026-08 时点的生态现状与安全状态进行了深度核实，并回答了五个专属问题：(1) Agent Card 签名与域绑定机制；(2) 安全缺陷清单逐项核实；(3) MCP Tasks 扩展（SEP-1686/2663）与 A2A 的边界与合并前景；(4) 社区"ticketing > chat"论点；(5) prime-agent 接入 A2A 的可行性方案。

核心结论（先读）：

1. **不存在 A2A v1.2**。A2A 核心规范最新版本为 **v1.0.1**（v1.0.0 于 2026-03-12 发布，首个稳定生产版；v1.0.1 于 2026-05-26 仅修 bug）。问题 1 中"Agent-DID + DNS TXT 域绑定"实为 **PR #1496（A2A-IDF 提案）**，截至 2026-08 **未合并**。规范内已落地的只有：JWS 签名 Agent Card（RFC 7515 + RFC 8785 规范化）+ TLS 证书域绑定。
2. **安全缺陷核实**：prompt injection 无防护 → **仍开放**；无 consent state → **部分修复**（v1.0 新增 `TASK_STATE_AUTH_REQUIRED`，但授权语义明确下放实现）；无 token TTL 强制 → **仍开放**（规范明文"不定义 scope/validity/revocation"）。2026-06 最新论文（arXiv 2606.28690，AgentThread）证实"只有 1 个协议在实践中强制执行安全相关控制，且没有任何协议为跨协议行为分配强制责任"。
3. **MCP Tasks vs A2A**：SEP-1686/2663 编号**核实无误**且均为 Final。MCP Tasks 已在 2026-07-28 从核心规范移出为独立扩展 `io.modelcontextprotocol/tasks`。边界 = MCP 管 agent↔tool（客户端-服务器），A2A 管 agent↔agent（对等、跨厂商、不透明）。**无合并公告**，但双方同属 AAIF，存在软性趋同信号。
4. **ticketing > chat**：社区结论为"**chat 是表象层，ticket 是基座层**"。A2A 自身就区分 Message（琐碎交互）与 Task（有状态长任务）。对 prime-agent 的 auto/steer/follow_up 三种投递模式有直接映射意义。
5. **prime-agent 接入 A2A**：**可行，但建议走"桥接守护进程"模式而非直接暴露 nuclear family**。最小路径 = 发布 Agent Card + 实现 4 个核心方法（SendMessage/GetTask/ListTasks/CancelTask）+ 把 `agent_message.send` 包装为 A2A Task。nuclear family 是本地遏制边界，A2A 是跨信任域模型——二者通过"外部对等体作为一等但隔离的主体 + 显式 opt-in"共存。

---

## 1. 总览:时间线与生态现状

### 1.1 时间线（已核实）

| 时间 | 事件 |
|---|---|
| 2025-04-09 | Google 发布 A2A，约 50 家发布伙伴 |
| 2025-06-23 | Google 在 Open Source Summit NA（丹佛）将 A2A 捐给 Linux Foundation |
| 2025-07-30 | v0.3.0：well-known URI 从 `agent.json` 改为 `agent-card.json`；AgentCard 新增 `signatures` 字段 |
| 2025 年末 | IBM 竞争标准 ACP 并入 A2A（终结标准之争） |
| 2025-11-11 | AWS Bedrock AgentCore Runtime 宣布 A2A 支持（SigV4 + OAuth 2.0，端口 9000） |
| 2025-12-09 | Linux Foundation 成立 AAIF（Agentic AI Foundation）：Anthropic 捐 MCP、OpenAI 捐 AGENTS.md、Block 捐 goose；AWS/Anthropic/Block/Bloomberg/Cloudflare/Google/Microsoft/OpenAI 为白金成员 |
| 2026-03-12 | **v1.0.0 发布**（首个稳定生产版）：Signed Agent Cards、多租户、PKCE、Device Code、移除 Implicit/Password OAuth、§13 Security Considerations 章节 |
| 2026-04-09 | 一周年：LF 新闻稿宣布 **150+ 组织**、Azure AI Foundry / Copilot Studio / AWS / Google 原生集成、AP2 支付协议（60+ 组织） |
| 2026-05-26 | v1.0.1（bugfix，无安全语义变化） |
| 2026-07-28 | MCP 规范 2026-07-28 版：Tasks 移出核心，成为官方扩展（SEP-2663） |

### 1.2 采用现实（可信度分级）

| 事实 | 状态 | 证据 |
|---|---|---|
| 150+ 组织"支持"A2A | ✅ 数字属实，但**统计口径是"发布 Agent Card + SDK 接入"**，非跨组织自主委派 | LF 新闻稿（2026-04-09）；dreaming.press 分析 |
| A2A 进入三大云（Google ADK / Azure AI Foundry / AWS Bedrock AgentCore） | ✅ 已确认 | LF 新闻稿；AWS ML Blog（2025-11-11） |
| IBM ACP 并入 A2A | ✅ 已确认 | dreaming.press（2026-06-30） |
| v1.0 生产可用 | ✅ 已确认 | Google Open Source Blog（2026-04-16） |
| "企业生产部署（供应链/金融/保险/IT 运维）" | ⚠️ **无具名企业、无指标**——营销级声明 | LF 新闻稿原文无具体案例 |
| **Claude Code / Codex 原生支持 A2A** | ❌ **均未原生实现**，仅有第三方桥（a2a-bridge、codex-claude-bridge、synapse-a2a、a2acode） | 各桥接项目 README 明言"neither tool supports A2A natively" |
| 跨厂商自主发现+委派在生产中普遍 | ❌ 仍罕见——常见形态是单厂商内（Vertex↔Vertex）或已签合同的双公司 | dreaming.press 采用现实分析 |

> **一句话**：A2A 是真实、中立的、版本化的应用层协议，一年内完成了标准合并（ACP→A2A）与云平台嵌入；但 150 这个数字衡量的是"声明支持"，不是"自主信任的跨组织任务委派"。真正的障碍不是消息格式，而是信任、身份、结算——所以生态下一步建的是**签名 Agent Card**（身份）和 **AP2**（结算）。

---

## 2. 问题 1:A2A v1.2 的 Agent Card 签名 + 域绑定如何工作？

### 2.1 ⚠️ 前提修正:没有 A2A v1.2

A2A 核心规范发布过的 tag 只有：v0.1.0 → v0.2.x → v0.3.0 → **v1.0.0（2026-03-12）→ v1.0.1（2026-05-26）**。不存在 v1.1/v1.2。

"v1.2" 在生态中唯一出现的位置是 **A2A-IDF（Agent Identity Framework）自身路线图**的版本号（v1.1 = vouching attestations，v1.2 = federated revocation）——那是**分层扩展的版本，不是 A2A 核心版本**。

### 2.2 规范内已落地的机制（A2A v1.0，§4.4 + §8.4）

**Agent Card**：JSON 元数据文档，公开 agent 的身份、能力、技能、端点与认证要求。公开 agent **必须**发布在 `https://{domain}/.well-known/agent-card.json`（RFC 8615 well-known，§14.3 已注册 IANA）。

**签名（§8.4，可选 MAY 非 MUST）**：

```
AgentCard.signatures[] = AgentCardSignature {
    protected: string   // base64url(JSON 保护头),含 alg/typ/kid/jku
    signature: string   // base64url(签名字节)
    header:    struct   // 可选非保护头
}
```

验证流程（§8.4.3，客户端 MUST 六步）：
1. 从 `signatures[]` 取一个签名；
2. 通过 `kid` +（可选）`jku` 或本地信任密钥库取公钥；
3. 按 §5.7 proto 字段存在性语义移除默认值属性；
4. **排除 `signatures` 字段本身**（防循环依赖）；
5. 用 RFC 8785（JCS）对剩余 JSON 规范化（字段字典序、无空白）；
6. 用 RFC 7515（JWS）验证签名。

关键：签名证明"谁签了卡片"，**不证明卡片内容无害**（恶意 agent 可以签自己的坏卡片）。规范还规定：过期/吊销密钥 MUST NOT 用于验证；多签名支持密钥轮换；公钥 SHOULD 经 HTTPS 获取。

**域绑定（现状）**：v1.0 核心规范**只有 TLS 证书验证**（§7.2 SHOULD）——Agent Card 通过 WebPKI 绑定到托管域，`jku` 指向的 JWKS 提供密钥但**不提供密钥↔域名的密码学绑定**。

### 2.3 提案中的机制:Agent-DID + DNS TXT（PR #1496，未合并）

**A2A-IDF（PR #1496，2026-02 提出，open）** 通过 Agent Card 的 `extensions[]` 机制（§4.6）分层实现三级身份验证：

| 级别 | 名称 | 证明什么 | 证据 |
|---|---|---|---|
| 0 | SELF_ASSERTED | agent 用自己的密钥签了自己的卡片 | RFC 9421 + Ed25519，对照声明的 `keyid` 验签 |
| 1 | **DOMAIN_VERIFIED** | 域运营者绑定该密钥 | **DNS TXT `_a2a-identity.<domain>`** 公布 keyid；TTL ≤ 300s（2026-05-11 加入规范指导） |
| 2 | ORGANIZATION_VERIFIED | 可信第三方背书 | `attestations[]` 数组中 ≥1 条由验证方信任的 issuer 签名 |

**Level 1 绑定机制**：

```
DNS TXT: _a2a-identity.example.com  IN  TXT  "v=A2AID1; k=<base64url-ed25519-pubkey>; kid=<key-id>"
Agent Card: https://example.com/.well-known/agent-card.json
```

验证合成（三层叠加）：
1. HTTPS 获取卡片 → TLS 证书验证 WebPKI 绑定到 `example.com`；
2. 解析 DNS TXT `_a2a-identity.example.com` → 证明 **DNS 区运营者**（通常是域名注册人）认可该密钥；
3. 组合：TLS 证明卡片来自 example.com 的 Web 服务器，DNS TXT 证明区运营者说"这把密钥是 example.com 的 agent 密钥"。

吊销机制（SHOULD/MAY）：JWKS 移除、DNS TXT 更新（受 TTL 限制）、`.well-known/a2a-revocations.json` 通知端点。

**注意**：PR #1496 明确**拒绝强制 W3C DID/VC**（"对当前生态过于复杂"）。`did:webvh` 来自独立的社区项目 Agent-DID（edisonduran/agent-did，RFC-001，2026-05-08），与 A2A-IDF 是平行方案。其他竞争提案：#1829 Envoys（RFC 9421 逐消息签名，非逐卡片）、#1511（did:webvh + vouch 链）、#2043（DANE/DNSSEC 锚定 SPKI）、`did:agent:`（EVM 锚定）。

### 2.4 小结表

| 特性 | A2A 核心 v1.0 | A2A-IDF 提案（PR #1496） |
|---|---|---|
| `/.well-known/agent-card.json` | MUST（§8.1） | 继承 |
| TLS（HTTPS） | MUST（§7.1） | 继承 |
| 验证服务器 TLS 证书 | SHOULD（§7.2） | 继承 |
| JWS 签名 Agent Card | **MAY**（§8.4） | 拟改为生产环境 MUST |
| 验证已签名卡片 | SHOULD（§8.4.3） | 拟改 MUST |
| DNS TXT `_a2a-identity` 域绑定 | —（规范无） | 拟 Level 1+ MUST |
| 第三方 attestation | —（规范无） | 拟 MAY（Level 2） |

---

## 3. 问题 2:安全缺陷清单逐项核实

### 3.1 判定总表

| # | 缺陷（grith.ai 2026-03-20，针对 v1.0） | 2026-08 状态 | 证据 |
|---|---|---|---|
| a | **Prompt injection 无防护** | **🔴 仍开放** | Issue #22 以"与协议无关，由各实现处理"关闭；§13 无语义载荷防护；arXiv 2606.28690 证实 |
| b | **无 consent state** | **🟡 部分修复** | v1.0 新增 §7.6 `TASK_STATE_AUTH_REQUIRED`，但 §7.6.4 明文把授权 scope/validity/revocation 下放实现 |
| c | **无 token TTL 强制** | **🔴 仍开放** | §7.6.4 明文"不定义 scope、representation、validity、或 revocation 语义"；arXiv 2602.11327v2 证实 |
| d | Agent Card 签名为可选（MAY） | 🔴 仍开放（v1.0 保持 MAY） | §8.4；A2A-IDF 拟改 MUST 但未合并 |
| e | Opaque Execution 无法审查工具调用 | 🔴 设计使然，规范未变 | §设计原则 |
| f | 无 tool call 评估门 | 🔴 仍开放 | 协议层无策略评估点 |
| g | 授权实现自定义 | 🔴 仍开放 | §13.1 要求每个操作授权，但机制留给实现 |
| h | 多轮 session smuggling（Unit 42 PoC） | 🔴 仍可复现 | 规范未增加对话级注入防护 |
| i | Agent Card 投毒（"agent in the middle"） | 🔴 仍开放 | 签名只验 issuer，不验内容良性 |
| j | 路线图不覆盖上述缺口 | 🔴 路线图仍聚焦治理/SDK/测试 | a2a-protocol.org/latest/roadmap/ |

### 3.2 三项核心声明的详细核实

**(a) Prompt injection —— 仍开放（高置信）**

维护者立场未变（Issue #22，2025-06-23 关闭，标注 enhancement 未实现）：
> "Not relevant to the protocol, up to individual implementations to handle"

最权威的近期确认：arXiv 2606.28690（AgentThread，2026-06-27 提交）——对 5 个协议做形式化安全分析，发现 **35 项规范级发现、80 项实现测试、30 项仅组合出现的失败**，且"**只有 1 个协议在实践中强制执行安全相关控制，没有任何协议为跨协议行为分配强制责任**"。

**(b) Consent state —— 部分修复（高置信）**

v1.0 新增 §7.6 "In-Task Authorization"：
- agent 侧 MUST：把 TaskState 置为 `TASK_STATE_AUTH_REQUIRED` 并附 TaskStatus 说明（§7.6.1）；
- client 侧可以：回复协商/纠正/拒绝，或联系人类/其他 agent 履行授权（§7.6.2）。

但 §7.6.4 明确封顶：
> "The A2A protocol does not define the scope, representation, validity, or revocation semantics of the authorization decision or credential obtained in response to this state."

即：协议定义了**请求授权的信号**，但"用户到底同意了啥"的语义完全不在协议内。且 §7.6.3 承认链式凭证会"向链上每个参与的 agent 暴露凭证"——consent 范围在多 agent 链上不被强制。

**(c) Token TTL —— 仍开放（高置信）**

- 规范 §13.4：凭证 SHOULD 定期轮换、SHOULD 实现吊销——全是 SHOULD；
- §7.6.4 明文下放；
- arXiv 2602.11327v2（2026-04-17，v1.0 发布之后）原文：
> "A2A uses OAuth 2.0 for authentication; however, it does not impose strict expiration durations of tokens for sensitive operations."

### 3.3 v1.0 实际新增的安全机制（正面清单）

| 机制 | 章节 | 版本 | 对应缺陷 |
|---|---|---|---|
| Agent Card JWS 签名（RFC 7515 + RFC 8785） | §4.4.7 + §8.4 | v0.3.0 → v1.0 正式化 | 身份（部分） |
| mTLS 安全方案 | §4.5.6 | v0.3.0 | 认证选项 |
| PKCE 强制（Authorization Code） | §4.5.8 | v1.0 | 代码拦截 |
| Device Code flow（RFC 8628） | §4.5.10 | v1.0 | 受限客户端 |
| 移除 Implicit + Password OAuth | §4.5 | v1.0 | 令牌泄露向量 |
| `TASK_STATE_AUTH_REQUIRED` | §7.6 | v1.0 | consent（部分） |
| 推送通知 SSRF 防护（私网 IP 黑名单） | §13.2 | v1.0 | webhook 类 |
| 多租户 + 操作级授权范围强制 | §3.6.2 + §13.1 | v1.0 | 枚举泄露 |
| 首个规范性 §13 Security Considerations | §13 | v1.0 | 框架 |

**元发现**：grith.ai 文章发布于 v1.0.0 后 8 天；此后 5 个月内的两篇学术分析（2602.11327v2、2606.28690）均得出相同结论。**AAIF 社区截至 v1.0.1 未关闭这三项核心缺口**。且 A2A 仓库 GitHub Security Advisories 为 **0 条**。

---

## 4. 问题 3:MCP Tasks 扩展（SEP-1686/2663）vs A2A

### 4.1 SEP 编号核实 ✅ 无误

| 字段 | SEP-1686 | SEP-2663 |
|---|---|---|
| 标题 | Tasks | Tasks Extension |
| 状态 | **Final**（Standards Track） | **Final**（Extensions Track） |
| 创建 | 2025-10-20 | 2026-04-27 |
| 作者 | Surbhi Bansal, Luca Chang（Amazon） | Luca Chang, Caitie McCaffrey（MCP Agents WG） |

**现状（2026-08）**：MCP 规范 2026-07-28 版 changelog 明言——"把实验性 tasks 从核心协议移入官方扩展 `io.modelcontextprotocol/tasks`（SEP-2663）"。即 **MCP Tasks 已不再是核心规范的一部分**，而是独立扩展（参考实现：github.com/modelcontextprotocol/ext-tasks）。

### 4.2 两代 Tasks 设计的差异

| | SEP-1686（原核心版，已废弃） | SEP-2663（现行扩展） |
|---|---|---|
| Task ID | **客户端生成**（`_meta.task.taskId`） | **服务器生成** |
| 创建触发 | 客户端每请求 opt-in | **服务器每请求自行决定**返回 CreateTaskResult |
| 方法 | `tasks/get`、`tasks/result`（阻塞）、`tasks/list`、`tasks/delete` | `tasks/get`（内联 result/error）、`tasks/update`（client→server 输入）、`tasks/cancel` |
| 状态 | 7 态（含 submitted/unknown） | **5 态**：`working`、`input_required`、`completed`、`failed`、`cancelled` |
| 推送 | 无（靠 SSE 旁路） | `notifications/tasks` over `subscriptions/listen`（SEP-2575） |
| 资源管理 | `keepAlive` | `ttlMs` + `pollIntervalMs` |
| 支持 tasks 的方法 | tools/call、resources/read、prompts/get、sampling | **仅 `tools/call`** |
| 客户端托管 task | 允许 | 移除（SEP-2260 禁止服务器主动请求） |

### 4.3 任务模型对比表

| 维度 | MCP Tasks（SEP-2663） | A2A v1.0 Tasks |
|---|---|---|
| 位置 | 独立扩展 `io.modelcontextprotocol/tasks` | **核心协议** |
| 治理 | MCP 项目（LF/AAIF） | AAIF/LF |
| 传输 | JSON-RPC over Streamable HTTP / stdio | JSON-RPC 2.0、gRPC、HTTP+JSON/REST（三绑定等价） |
| 状态数 | 5 | **8**（submitted/working/input_required/**auth_required**/completed/failed/canceled/rejected） |
| 轮询 | `tasks/get` | `GetTask` + `ListTasks`（游标分页） |
| 取消 | `tasks/cancel`（协作式） | `CancelTask` |
| 重连/订阅 | 无（重新轮询） | `SubscribeToTask`（重连 SSE） |
| 推送通知 | `notifications/tasks`（单向往客户端推全量 DetailedTask） | webhook `PushNotificationConfig`（JWT/JWKS 认证） |
| 流式 | 无内建（客户端轮询） | `SendStreamingMessage`（SSE：TaskStatusUpdateEvent + TaskArtifactUpdateEvent） |
| 中途输入 | `tasks/get` → inputRequests → `tasks/update` | streaming 事件（input_required/auth_required 状态） |
| 多轮上下文 | 无 | `contextId` 分组 |
| 工件模型 | 内联在 result | 一等 `Artifact`，chunked streaming（append/lastChunk） |
| 幂等 | 范围外 | §3.3.1 操作级幂等规则 |
| 多租户 | 无 | 原生 `tenant` 字段 |
| 签名/信任 | OAuth 2.1 + RFC 8707 | Agent Card JWS + mTLS |

### 4.4 边界在哪里？

双方官方表述完全一致：**MCP = agent↔tool（客户端-服务器、单 host、结构化无状态调用）；A2A = agent↔agent（对等、不透明、跨厂商、有状态多轮）**。

- A2A v1.0 公告："MCP inside agents, A2A between agents."
- A2A 官方对比页（topics/a2a-and-mcp/）：Tools/Resources 是"有明确结构化输入输出、通常无状态的基元"；Agents 是"能推理、规划、用多工具、跨长交互维持状态的自主系统"。
- Oracle 决策矩阵的判别测试："**如果你能说出第二个 agent 的名字并解释它的独立决策，用 A2A；如果'第二个 agent'只是同一模型换了个 prompt，那是工具调用。**"

### 4.5 会不会合并？—— 无合并公告，但有四个软性趋同信号

1. **同一治理伞**：A2A 与 MCP 都归 Linux Foundation AAIF。AAIF 工作组的名字本身就覆盖跨协议地带："Workflows & Process Integration"（handoff 协议、角色定义、状态保证）、"Identity & Trust"（委托协议、跨域身份、权限流）。
2. **MCP Tasks 的自定位**：ext-tasks 仓库描述明言"为 MCP 协议提供 tasks 扩展参考，支持**长运行操作，如 Agent 通信**"——即 MCP 有意覆盖 A2A 用例空间的一部分。
3. **扩展机制趋同**：MCP 走 SEP-2133 URI 扩展 + `server/discover`；A2A 走 AgentCard `extensions[]` URI 声明——同一套"URI 声明 + 能力协商"词汇。
4. **官方桥接模式**：A2A 文档给出"A2A agent 的技能暴露为 MCP 资源/工具"的标准桥接范式。

**判断**：合并不是技术问题而是治理问题。两者同属 AAIF，理论上可通过 "Workflows & Process Integration" 工作组出台跨协议 handoff 标准。但截至 2026-08 没有任何公告；工程上更可能的路径是**桥接与分层共存**（A2A agent 背后用 MCP 调工具），而非协议合并。

---

## 5. 问题 4:"ticketing > chat"论点与对 prime-agent 投递模式的启发

### 5.1 社区论点综合

**结论："chat 是表象层，ticket 是基座层。"** 支持者与论据：

| 论据 | 出处 |
|---|---|
| chat 隐喻"大约 30 秒就烧断保险丝"——延迟变成认知囚禁；用户约 12s 就切走，即使 agent 最终完成也会放弃会话 | tianpan.co《Async Agents Need an Inbox, Not a Chat》（2026-04-23） |
| "不要把 chat log 当作 agent 状态机"——消息描述交互，持久操作状态需要显式域对象与转移；transcript 应是工作的视图而非记录 | dev.to/markin（2026-08-06）；cmdop |
| 即使 chat 前端生产化也变成 ticket：Cloudflare 把 Think 的聊天轮次包进 SQLite-backed 提交行（pending→running→completed/aborted/skipped/error）+ 幂等键 | Cloudflare think-durable-submissions.md |
| worker 死亡/重试重复副作用/审计追溯 → 需要 checkpoint、saga 补偿、append-only 证据日志 | Cloudflare fibers、Temporal/Restate、Salesforce 分布式持久队列（2026-04-09，5x 扩规模）、OpenAI Symphony（Linear 作为 agent 控制平面，PR +500%）、CHAP（arXiv 2606.09751） |

**反方论点（chat 仍有位置）**：
1. 亚秒级 UX 反馈——单模型轮次内（≤几秒）流式 token 就是正确基元；
2. 双向对话/实时上下文——"tax preparation agent 需要和你一起把方案聊出来"，100 个工具调用的建模不现实（A2A 工程师 HN 原话：**"Talk to an agent as an agent"**）；
3. 启动/探索类小任务——写 ticket 比提问更费事；
4. 单次模型推理期间的流式本身没问题——问题在把 chat 基元当作多步、多分钟、多参与方工作的单位。

**A2A 自身就是范例**：`SendMessage` 返回 Message（琐碎交互，SSE 流"恰好一个 Message 然后关闭"）或 Task（有状态长任务）；规范明言 Message 仅用于"不需要长运行处理或复杂状态管理"的交互。**协议内部已经内置了 ticketing-over-chat 的分层**。

### 5.2 对 prime-agent auto/steer/follow_up 的启发

prime-agent 官方语义（prime-agent/packages/coding-agent/docs/long-running-agents.md）：

```python
receipt = await agent_message.send(
    "message text",
    receiver_role="sibling",   # parent / sibling / child（nuclear family）
    receiver_name="api-reviewer",
    mode="auto",               # auto | steer | follow_up
)
print(receipt["deliveryStatus"])   # "delivered" | "queued"
```

| 模式 | 官方语义 | 本质 | 对应生态模式 |
|---|---|---|---|
| `auto` | 目标忙则 steer，闲则立即投递 | 智能自适应交付 | A2A push notification / 立即投递 |
| `steer` | **故意把消息注入进行中的工作** | 侵入式中断 | 高风险跨信任域操作；只在家庭内可接受 |
| `follow_up` | **等目标当前工作结束再投递** | 排队/票据语义 | **与 A2A Task 模型原生一致**（working→completed 生命周期） |

**启发清单**：
1. **follow_up 就是原生 ticket 语义**——A2A 的 Task 状态机（submitted→working→completed）与 `delivered`/`queued` receipt 一一对应。prime-agent 若做 A2A 桥，follow_up 应映射为普通 Task 排队，zero-friction。
2. **steer 是唯一跨信任域危险模式**——"注入进行中的工作"在 A2A 跨厂商语境下等同于不可控的会话劫持（Unit 42 session smuggling 的利用面）。**steer 应被 A2A 桥默认禁止或降级**，仅保留家庭内使用。
3. **auto 映射为投递策略而非新协议语义**——它是路由器行为（忙/闲探测），在 A2A 侧表现为：Task 在服务器端排队（idle 目标）vs 直接工作（busy 目标被 steer 的等价物，需显式 opt-in）。
4. **receipt 语义可映射到 Task 状态**：`delivered` → completed（带 artifact=receipt）；`queued` → working/submitted（带预计投递信息）。
5. 若按 ticketing-first 重设计，prime-agent 应把"消息"视为 Task 的附属视图（transcript 是视图，Task 是记录）——与社区"chat as presentation, ticket as substrate"一致。

---

## 6. 问题 5:prime-agent 接入 A2A 的可行性

### 6.1 prime-agent 现状盘点（已核实）

- **模型**：daemon 常驻 worker（resident session worker）+ supervisor 路由 + 持久 JSONL transcript + IPython kernel。
- **消息 API**：`agent_message.send(message, receiver_role, receiver_name, mode)`；`agent_message.list_agents()`；`send("all", ...)` 仅广播给家庭名册（family roster）。
- **nuclear family**：只允许 parent/sibling/child 之间互发；daemon 派生 sender 身份并强制消息大小/速率/待投递队列上限。
- **deliveryStatus**：`delivered`（到达空闲目标上下文）/ `queued`（接受待后续投递）。
- **进程隔离**：daemon 进程隔离是"生命周期与故障隔离"，**非安全沙箱**——worker 以客户端相同 OS 权限运行。这点对 A2A 暴露有直接安全含义。

### 6.2 结论:可行，但推荐"桥接守护进程"模式而非直接暴露

**核心矛盾**：nuclear family 是**本地遏制边界**（同机 daemon 强制、同家庭名册、进程级身份派生）；A2A 是**跨信任域模型**（对等、不透明、跨厂商、对方可恶意/可违约/可破产）。直接把 `agent_message.send` 暴露给公网 A2A 客户端 = 把一个信任模型建立在另一个之上，中间缺一层策略边界。

**推荐架构：A2A 桥接守护进程（A2A Bridge Daemon）**

```
┌─────────────────────────────────────────────────────────┐
│ 公网（跨厂商 A2A peers）                                  │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│   │ Agent B  │   │ Agent C  │   │ 未知 X   │  ← 不可信  │
│   └────┬─────┘   └────┬─────┘   └────┬─────┘           │
└───────┼───────────────┼──────────────┼─────────────────┘
        │  HTTPS + JWS Agent Card + 认证 + 限流/配额/审计
┌───────▼───────────────▼──────────────▼─────────────────┐
│ A2A Bridge Daemon（独立进程，与 prime daemon 隔离）       │
│  · 发布 Agent Card（技能=send/steer/follow_up，白名单）   │
│  · 实现:SendMessage/GetTask/ListTasks/CancelTask        │
│  · 策略层:allowlist、steer 降级、配额、审计日志           │
│  · 外部对等体 = 一等但隔离的"外部 sibling"身份             │
└───────────────────────┬─────────────────────────────────┘
        │ 内部 IPC（受信，复用 daemon 的 UDS/命名管道）
┌───────▼─────────────────────────────────────────────────┐
│ prime-agent daemon                                       │
│  · nuclear family 不变（parent/sibling/child 原生）       │
│  · bridge 注入的外部 peer 作为显式 opt-in 的隔离角色       │
└─────────────────────────────────────────────────────────┘
```

**nuclear family 与 A2A 跨域模型的共存方案**：
1. **外部对等体降级为"外部 sibling"**：A2A peer 经桥接进入后，被赋予一个受限的 sibling 角色（可发消息、可收 follow_up），**永远拿不到 parent/child 权限**；不能 spawn、不能读家庭名册。
2. **显式 opt-in**：每个 agent 必须显式声明"接受来自外部 A2A peer 的任务"，默认关闭（与 `/goal`、`/autonomous` 的显式创建原则一致）。
3. **steer 默认禁用**（见 5.2）：外部 peer 的 `steer` 请求被桥降级为 `follow_up` 或拒绝。
4. **策略独立于协议**：桥接层的 allowlist/配额/审计不依赖 A2A 规范（规范授权本来就实现自定义 §7.6.4）——这正好符合 A2A "security enforcement 是别人的问题"的架构现实。

### 6.3 最小实现路径（把 `agent_message.send` 暴露为 A2A Server）

**Step 1 — 发布 Agent Card**（最小可用）：
```json
{
  "name": "prime-agent-fleet",
  "description": "PrimeIntellect RLM agent family bridge",
  "version": "1.0.0",
  "skills": [
    {"id": "send_message", "name": "send", "description": "Deliver a message to a named agent (mode: auto|follow_up)"}
  ],
  "capabilities": {"streaming": false, "pushNotifications": false, "extensions": []},
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "securitySchemes": {"apiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"}}
}
```
位置：`https://{bridge-host}/.well-known/agent-card.json`。

**Step 2 — 实现 4 个核心方法**（JSON-RPC 2.0 over HTTP，最快路径；gRPC/REST 等价绑定后续可加）：
- `SendMessage` → 内部调 `agent_message.send(...)`；返回 **Task**（而非 Message）以承载生命周期；
- `GetTask` → 查 `deliveryStatus`/内部任务状态，映射到 A2A TaskState；
- `ListTasks` → 按 contextId/状态过滤（用 daemon 的任务台账）；
- `CancelTask` → 内部对已排队消息撤销（幂等）。

**Step 3 — 状态映射**（ticketing-first，与问题 4 结论一致）：

| A2A TaskState | prime-agent 语义 |
|---|---|
| `submitted` | 消息已入 daemon 待投递队列 |
| `working` | 目标 agent 正在处理（receipt=queued 且目标忙碌） |
| `completed` | receipt=delivered，artifact=送达回执 |
| `failed` | 目标不存在/超限/被策略拒绝（role 不在家庭名册） |
| `rejected` | allowlist/steer 降级拒绝 |
| `input_required` / `auth_required` | 桥接策略层要求人类批准（可选扩展） |

**Step 4 — 安全基线**（呼应问题 2 的缺陷清单）：
- 认证：API key 起步，升级 OAuth 2.0 Authorization Code + PKCE（v1.0 已强制 PKCE）；
- **自签/托管短 TTL token**，桥内强制 5-15 分钟过期（补偿协议无 TTL 强制）；
- **steer 语义拒绝**：外部请求的 `mode=steer` → 403 或降级 follow_up；
- prompt injection：把 Agent Card 的 skill 描述视为不可信输入，**不将外部任务文本拼入系统提示**（外部输入只进入 user turn 且经显式边界标注）；
- 审计：全量记录入 daemon 的 JSONL（复用现有持久化）。

### 6.4 否决理由清单（什么时候不该做）

1. **若目标只是让本机两个 agent 通信**——A2A 是过度设计；nuclear family + daemon IPC 已经做了，且更快更安全（Oracle 矩阵："一个 agent 加一组工具是 MCP 问题，不是 A2A 问题"）。
2. **若没有真实跨厂商对等体**——当前采用现实是"桥接项目为了存在而存在"（a2a-bridge README 明言 Claude Code/Codex 都不原生支持 A2A）。为接入而接入 = 为 A2A 增加任务生命周期管理而没有收益。
3. **若把 `agent_message.send` 直接暴露**（不做桥接进程、不做 allowlist、不降级 steer）——等于把本地遏制边界（nuclear family）的信任外借给公网，且 A2A 协议本身不提供 prompt injection/TTL/consent 保护（问题 2 已核实），风险不可接受。
4. **若团队没有能力维护信任层**——跨组织 agent 协作的真实障碍是身份、授权、结算、追责（问题 1.2）。桥接项目要当 B2B 集成做，不是当 web 请求做。

### 6.5 最终建议

**做，但做"窄而安全"的版本**：A2A Bridge Daemon + 4 方法最小面 + follow_up-first 语义 + steer 禁用 + 短 TTL token + 全量审计。**在桥接层把安全当项目主体（90% 工作量），协议调用是简单的 10%**——这正是 A2A 一年采用现实教给所有人的一课（dreaming.press：签名、支付、身份才是下一年的主题）。

---

## 7. 一手来源与可信度标注

### A2A 官方
1. **A2A 核心仓库**（https://github.com/a2aproject/A2A）· 高（官方源码，25.3k stars）
2. **A2A 规范 v1.0.1**（https://github.com/a2aproject/A2A/blob/0a43195/docs/specification.md，§7.6.4 / §8.4 / §13）· 高（官方规范）
3. **A2A CHANGELOG**（https://github.com/a2aproject/A2A/blob/main/CHANGELOG.md）· 高（版本事实）
4. **A2A 规范站点**（https://a2a-protocol.org/latest/specification/）· 高
5. **A2A PR #1496 A2A-IDF**（https://github.com/a2aproject/A2A/pull/1496）· 中（未合并提案）
6. **A2A 安全公告页**（https://github.com/a2aproject/A2A/security/advisories）· 高（0 条）
7. **Issue #22 Prompt Injection**（https://github.com/a2aproject/A2A/issues/22）· 高（维护者立场）
8. **Linux Foundation 一周年新闻稿**（https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year）· 高（官方，含营销成分）
9. **Google Open Source 博客周年文**（https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html）· 高

### 安全分析
10. **grith.ai《A2A 零 prompt injection 防护》**（https://grith.ai/blog/a2a-protocol-zero-defenses-prompt-injection）· 中（供应商视角，但引 Red Hat/Unit 42/Semgrep/Trustwave/Solo.io 原文）
11. **arXiv 2602.11327**（MCP/A2A/Agora/ANP 威胁建模，12 项协议级风险）· 高（同行评审前论文）
12. **arXiv 2606.28690**（AgentThread 形式化组合安全分析：35 spec 发现/80 测试/30 组合失败）· 高（最新，2026-06-27）
13. **arXiv 2505.12490**（Improving Google A2A Protocol：consent/token 批评的源头）· 高
14. **Red Hat A2A 安全增强指南**（https://developers.redhat.com/articles/2025/08/19/how-enhance-agent2agent-security）· 高
15. **Unit 42: Agent Session Smuggling**（https://unit42.paloaltonetworks.com/agent-session-smuggling-in-agent2agent-systems/）· 高
16. **Semgrep A2A 安全工程师指南**（https://semgrep.dev/blog/2025/a-security-engineers-guide-to-the-a2a-protocol/）· 高

### MCP Tasks
17. **SEP-1686**（https://modelcontextprotocol.io/seps/1686-tasks.md）· 高（Final）
18. **SEP-2663**（https://modelcontextprotocol.io/seps/2663-tasks-extension.md）· 高（Final）
19. **MCP 规范 2026-07-28 changelog**（https://modelcontextprotocol.io/specification/2026-07-28/changelog.md）· 高
20. **ext-tasks 仓库**（https://github.com/modelcontextprotocol/ext-tasks）· 高（官方参考实现）
21. **MCP Tasks 扩展概览**（https://modelcontextprotocol.io/extensions/tasks/overview.md）· 高

### 采用现实与决策框架
22. **dreaming.press《A2A at One Year》**（https://dreaming.press/posts/a2a-protocol-at-one-year-adoption-reality.html）· 中（AI 作者+人工审校，分析质量高）
23. **Oracle《The Agent Communication Matrix》**（https://blogs.oracle.com/developers/the-agent-communication-matrix-when-mcp-a2a-and-plain-rest-each-win · Medium 镜像 https://medium.com/oracledevs/the-agent-communication-matrix-when-mcp-a2a-and-plain-rest-each-win-e60562e34657）· 中（厂商博客，决策框架实用）
24. **tianpan.co《Async Agents Need an Inbox, Not a Chat》**（https://tianpan.co/blog/2026-04-23-async-agents-inbox-not-chat）· 中
25. **dev.to/markin《Do not use the chat log as your agent state machine》**（https://dev.to/markin/do-not-use-the-chat-log-as-your-agent-state-machine-4pbf）· 中
26. **Cloudflare think-durable-submissions.md**（https://github.com/cloudflare/agents/blob/main/design/think-durable-submissions.md）· 高（官方设计文档）
27. **Salesforce 分布式持久队列工程文**（https://engineering.salesforce.com/building-a-distributed-persistent-queue-that-scaled-ai-workloads-5x-under-llm-rate-limits/）· 高（官方工程博客）
28. **AWS Bedrock AgentCore A2A 公告**（https://aws.amazon.com/blogs/machine-learning/introducing-agent-to-agent-protocol-support-in-amazon-bedrock-agentcore-runtime/）· 高

### prime-agent
29. **prime-agent long-running-agents.md**（https://github.com/PrimeIntellect-ai/prime-agent/blob/main/packages/coding-agent/docs/long-running-agents.md）· 高（官方文档，agent_message.send 语义唯一权威来源）
30. **prime-agent 仓库**（https://github.com/PrimeIntellect-ai/prime-agent）· 高（14.7k stars）
31. **wq-challenge/prime-agent-poc 脚本**（本地工作区，RPC 模式 JSON stdin/stdout 协议实证）· 高（本地实证）

---

## 8. 结论清单（Do's / Don'ts）

**Do's**
1. 写报告/做方案时先说清"A2A 无 v1.2"——这是最常见的错误前提。
2. 安全评估以 arXiv 2606.28690（2026-06）为最新基准，而不是 2026-03 的 grith.ai 文章。
3. prime-agent 接入 A2A 走"桥接守护进程 + 4 方法最小面 + follow_up-first"。
4. 把安全当项目主体（allowlist/短 TTL/steer 禁用/审计），协议调用是简单 10%。
5. MCP 与 A2A 按分层理解：MCP inside agents, A2A between agents。

**Don'ts**
1. 不要称"v1.2 的 Agent-DID + DNS TXT 绑定"为规范事实——它是未合并提案（PR #1496）。
2. 不要把 A2A 的"150+ 组织"解读为跨厂商生产协作普遍化。
3. 不要指望协议层提供 prompt injection/TTL/consent 保护——它明确不是安全强制层。
4. 不要把 nuclear family 直接暴露给公网 A2A peer——先降级为隔离的"外部 sibling"。
5. 不要对 A2A 默认开放 `steer`（注入进行中工作）——跨信任域等同会话劫持面。
