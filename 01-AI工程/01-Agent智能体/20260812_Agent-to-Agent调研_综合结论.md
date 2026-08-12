# 20260812_Agent-to-Agent调研_综合结论

> **日期**：2026-08-12
> **方式**：Orca 编排 4 个并行调研 agent(方向 A Claude Teams / B omp hub / C Devin / D A2A),各产出独立报告后综合
> **背景**：实测 prime-agent 的 agent-to-agent 通信后,深挖 4 个最接近的实现,为 prime-agent 设计取舍提供依据

---

## 我能讲出来的版本(5 行)

1. **Claude Code Agent Teams 是"文件邮箱"派**:~/.claude/teams/{name}/inboxes/ 纯 JSON 文件 + flock 锁,不用 IPC/socket——因为要跨进程、可审计、崩溃安全;SendMessage 是唯一通信工具,身份由系统注入不可伪造。
2. **omp hub 是"三层 IPC 前门"**:消息(进程内 IrcBus)+ 后台任务(AsyncJobManager Promise Map)+ 长进程监督(跨进程 daemon broker,Unix socket/Windows pipe + token)——监督不是独立命令,是 launch 家族。
3. **Devin 是"manager-child 单向"派**:manager 通过 Devin MCP server 向子会话注入消息、读子 trajectory 纠偏;child 之间**拓扑上就没有通信通道**(不是权限黑名单),且模型没被训练过跨 agent 发消息。
4. **A2A 规范现状**:核心规范是 v1.0.1(不存在 v1.2),Agent-DID+DNS 域绑定只是未合并的 PR #1496;安全缺陷(prompt injection 无防护、token TTL 无强制)仍开放。
5. **prime-agent 的独特定位被 4 份报告共同确认**:它是唯一"本地 daemon worker 进程 + 首类 A2A API + nuclear-family 显式作用域"的组合,该组合在 2026-08 主流 agent 中无直接对标。

---

## 1. 四方向要点提炼

### 方向 A：Claude Code Agent Teams(报告 22K 字符,三层证据 L1文档/L2社区/L3本机二进制)

- **文件邮箱机制**:`~/.claude/teams/{name}/inboxes/{agent}.json`,纯 JSON + lockfile 并发控制(指数退避重试)。选文件而非 IPC/socket 的原因:跨进程(各 teammate 独立)、崩溃安全(磁盘持久)、可审计(cat 文件即可调试)、无 daemon/端口/服务发现。
- **SendMessage 身份验证**:消息被标记为"来自另一个 Claude session,非用户本人";teammate 不能代用户审批权限、不能中继绕过检查(agent 间消息在 auto 模式下被视为不可信输入)。
- **权限委托链路**:teammate 无交互终端 → permission_request 写 leader 邮箱 → leader 提示用户 → permission_response 回写 → teammate 继续。plan 审批同理。
- **已知限制**:headless(-p)模式下 mailbox 投递缺陷(消息 read:false,投递循环不工作);idle pings 每 2-4 秒刷屏占满 inbox;shutdown 是 request/response 协议逐 agent 确认。
- **对 prime-agent 的借鉴**:
  - ✅ 借鉴:文件邮箱的"可审计性"思想(harness 状态用 JSON 落盘可查)、身份不可伪造(daemon 从 session 元数据推导 sender)、权限委托模式
  - ❌ 避免:idle pings 刷屏(应加节流/合并)、headless 投递缺陷(需要显式的离线投递测试)、纯文件邮箱的低效(prime-agent 用 daemon socket 更好)

### 方向 B：omp hub + task(报告 13.8K 字符,源码级 A 档)

- **hub 三层结构**:①进程内 IrcBus 邮箱总线(消息)②AsyncJobManager Promise Map(后台任务,maxRunningJobs=15,结果保留 5 分钟)③跨进程 daemon broker(长进程监督,Unix socket/Windows pipe + token 认证)。12 个 op 分三族,supervise 是 launch 家族的一部分。
- **task 并发模型**:每会话一个可热调整的 Semaphore(abort-aware acquire、就地 resize、0=无限)+ mapWithConcurrencyLimit worker 池(fail-fast、abort 返回部分结果)。**与 prime-agent 的本质区别:并发单位是协程级交错 vs 进程级隔离**。
- **orchestrate 隐藏机制**:不是 slash 命令,是小写散文边界匹配后把 10 条规则 + 7 步工作流(Ingest→Plan→Dispatch→Verify→Commit→Advance→Final verify)追加到当条用户消息。
- **生命周期**:AsyncJobManager 是进程内单例,"后台"只意味着不阻塞当前轮次;进程退出全 cancel——恢复靠 JSONL 工件重扫成 parked 行,是"复活"不是"接着跑"。**prime-agent 才是真 daemon**(supervisor + 每 root session tree 一个 worker 进程 + IPython kernel,socket 协议、detach/attach、崩溃恢复)。
- **对 prime-agent 的借鉴**:
  - ✅ 统一 wait 三方竞态(jobs↔消息↔超时,先到先返回+丢消息保护)→ daemon 协议层加 wait_any 命令
  - ✅ 智能轮询阶梯 [5s,10s,30s,60s,300s] + 60s 空闲重置 → 适配 RPC/daemon 客户端
  - ✅ abort-aware Semaphore acquire(abort 时从队列 splice 掉 waiter)→ 防取消残留 waiter
  - ✅ Semaphore 就地 resize + queued job 不占槽 → 热更新并发上限

### 方向 C：Devin Managed Devins(报告 20K 字符)

- **三阶段演进**:2024-09 MultiDevin(1 manager + ≤10 worker)→ 2025-06 "Don't Build Multi-Agents"唱衰 → 2026-03/04 Managed Devins 重装,收敛为"map-reduce-and-manage":写操作单线程,并行 agent 只贡献智能不贡献动作。
- **manager→child 消息注入 = Devin MCP server**:manager 调用 devin_session_create/interact/events/gather 等工具,把指令/纠错作为消息投进子会话事件流;manager 还能读 child 完整 trajectory(事件日志)纠偏,不是实时看屏幕。
- **child 间禁通信的真正原因**:拓扑上没这个通道(child 唯一对外工具面是 Devin MCP 且作用域是自己的会话)+ 模型没被训练过"跨 agent 发消息"。**不是权限黑名单,是架构决定**。
- **权限模型三层**:①独立 VM(secrets 按 VM 最小化,brain 在 Cognition 侧)②API 层 bypass_approval 按 session + service-user RBAC(ManageOrgSessions/ImpersonateOrgSessions)③ACU 预算限制算力。
- **对 prime-agent 的借鉴**:
  - ✅ 写操作单线程(map-reduce-and-manage)——并行 agent 贡献智能,写入收敛到单点,避免冲突
  - ✅ manager 读完整 trajectory 纠偏(审计思想)
  - ⚖️ sibling 通信差异:Devin 因模型能力未到选择拓扑禁用 peer 协商;prime-agent 选择把 nuclear-family 消息作为一等公民——这是**赌模型会学会 A2A** vs **等模型学会再开**的策略分歧

### 方向 D：A2A 协议(报告 24K 字符,深度核实)

- **规范现状修正**:核心规范是 **v1.0.1**(v1.0.0 于 2026-03-12,v1.0.1 于 2026-05-26 修 bug);**不存在 v1.2**;Agent-DID+DNS TXT 域绑定是未合并的 PR #1496。已落地:JWS 签名 Agent Card(RFC 7515 + RFC 8785)+ TLS 证书域绑定。
- **安全缺陷核实**:prompt injection 无防护 → 仍开放;无 consent state → 部分修复(v1.0 新增 TASK_STATE_AUTH_REQUIRED 但语义下放);无 token TTL 强制 → 仍开放。2026-06 论文(arXiv 2606.28690)证实"只有 1 个协议强制执行安全控制,没有任何协议为跨协议行为分配强制责任"。
- **MCP Tasks vs A2A**:SEP-1686/2663 均为 Final;MCP Tasks 已移出核心为独立扩展 io.modelcontextprotocol/tasks。边界 = MCP 管 agent↔tool, A2A 管 agent↔agent。无合并公告,但同属 AAIF 有软性趋同信号。
- **ticketing > chat**:chat 是表象层,ticket 是基座层。A2A 自身区分 Message(琐碎)与 Task(有状态长任务)。对 prime-agent 的 auto/steer/follow_up 有直接映射意义。
- **prime-agent 接入 A2A**:可行,建议走"**桥接守护进程**"模式而非直接暴露 nuclear family。最小路径 = 发布 Agent Card + 实现 4 个核心方法(SendMessage/GetTask/ListTasks/CancelTask)+ 把 agent_message.send 映射到 A2A SendMessage,family 边界由桥接层解释而非直接暴露。

---

## 2. 跨方向对比：谁最接近 prime-agent？谁最值得借鉴？

| 维度 | Claude Teams | omp hub | Devin | A2A 标准 | **prime-agent** |
|---|---|---|---|---|---|
| 消息传输 | 文件邮箱+flock | IrcBus+daemon broker | Devin MCP server | HTTP/JSON-RPC/gRPC | **本地 daemon socket** |
| 通信拓扑 | 团队内 peer | 进程内 bus | manager→child 单向 | 跨厂商 peer | **nuclear-family peer** |
| 身份验证 | 系统注入不可伪造 | token 认证 | service-user RBAC | Agent Card 签名 | **daemon 从 session 推导** |
| 并发模型 | 独立进程 | 协程级 | 独立 VM | 跨组织 | **worker 进程级** |
| 持久性 | 文件持久 | 进程内,退出即失 | 云端 VM | 服务端 task store | **daemon worker + JSONL 恢复** |
| 是否本地 daemon | ❌ | ⚠️ 部分 | ❌ 云端 | N/A | **✅ 唯一本地 daemon** |
| 实验/生产 | 实验性,默认关闭 | 生产 | 生产 | 生产(v1.0.1) | 生产(MIT) |

**结论**：
- **最接近的架构**:Claude Agent Teams(peer 通信 + 身份不可伪造)和 omp hub(IPC 抽象 + 监督)
- **最值得借鉴的机制**:omp 的 wait_any 竞态原语 + 智能轮询阶梯;Devin 的"写操作单线程 + 读 trajectory 纠偏";Claude 的身份注入与权限委托
- **prime-agent 独占**:本地 daemon + worker 进程 + 崩溃恢复——这是唯一"本地第一"的完整 A2A 实现

---

## 3. "该借鉴/该避免"总清单

### 该借鉴(按优先级)

1. **wait_any 三方竞态原语**(omp)——daemon 协议层加 wait_any 命令,统一 jobs/消息/超时等待
2. **智能轮询阶梯 [5s,10s,30s,60s,300s]**(omp)——适配 RPC 客户端,避免烧模型轮次
3. **abort-aware Semaphore acquire**(omp)——防取消残留 waiter
4. **写操作单线程 + 并行只贡献智能**(Devin)——避免并行写入冲突
5. **manager 读完整 trajectory 纠偏**(Devin)——审计思想
6. **身份由系统注入不可伪造**(Claude)——daemon 已实现,保持
7. **消息与 Task 分层**(A2A)——区分琐碎交互与有状态长任务,映射 auto/steer/follow_up

### 该避免

1. **idle pings 刷屏**(Claude)——加节流/合并
2. **headless 投递缺陷**(Claude)——需显式离线投递测试
3. **纯文件邮箱的低效**(Claude)——daemon socket 已更优,不必退回
4. **进程内"后台任务"假持久**(omp)——退出即失,需真 daemon
5. **child 拓扑禁通信的过度保守**(Devin)——模型在进步,family-scope 通信是正确赌注,但需限流防 ACK 循环
6. **协议层不定义安全**(A2A)——安全必须实现层负责,不能指望协议

---

## 4. 对 prime-agent 未来方向的判断

1. **短期(维持)**:继续 nuclear-family + daemon 方案,不加 A2A 标准接入。理由:本地场景无跨厂商需求,A2A 安全缺陷未解决,且 family-scope 是安全 feature。
2. **中期(补原语)**:实现 wait_any 竞态原语 + 智能轮询阶梯(吸收 omp),这是当前最缺的编排能力。
3. **长期(可选桥接)**:若要跨厂商协作,走"桥接守护进程"模式——发布 Agent Card + 实现 A2A 核心方法,SendMessage 映射到 agent_message.send,family 边界由桥接层解释。
4. **持续(测试)**:**headless/daemon 投递的离线回归测试**(Claude 踩过坑),确保 RPC/print 模式下 agent_message 可靠投递。

---

## 原始资料

- 四方向独立报告(各含一手来源清单):
  - `20260812_ClaudeCode_AgentTeams与DynamicWorkflows_源码级深挖.md`
  - `20260812_omp_hub与task工具IPC并发模型深挖_深度调研报告.md`
  - `20260812_Devin多Agent消息架构与权限模型_调研报告.md`
  - `20260812_A2A协议与MCP-bridge生态现状_调研报告.md`
- 背景: `20260812_主流Agent的Agent-to-Agent能力对比调研报告.md`
- 任务包: `20260812_Agent-to-Agent调研任务包_4方向.md`
- 编排: `20260812_Agent-to-Agent编排提示词_v2.md`
