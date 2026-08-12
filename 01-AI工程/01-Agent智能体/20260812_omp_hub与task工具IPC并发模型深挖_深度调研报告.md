# 20260812_omp hub与task工具IPC并发模型深挖_深度调研报告

> 2026-08-12 · 方向 B：omp（can1357/oh-my-pi）`hub` + `task` 工具实现深挖
> 目标读者：正在设计 prime-agent A2A / 多 agent 编排层的人（即未来的自己）
> 可信度分级：A 档——源码级（`parallel.ts`/`job-manager.ts`/`irc/bus.ts`/`task/index.ts`/`docs/tools/task.md` 全文 + `tools/hub/` 五文件 librarian 源码分析，固定提交 `06aecdd5`）；prime-agent 侧为官方架构文档，未读其源码

---

## 我能讲出来的版本(5 行)

1. omp 的 `hub` 不是单工具而是**三层 IPC 的单一前门**：消息（进程内 IrcBus 邮箱总线）、后台任务（进程内 AsyncJobManager Promise Map）、长进程监督（跨进程 daemon broker，Unix socket/Windows pipe + token 认证）——12 个 op 分三族，`supervise` 只是动词不是命令，监督就是 `launch` 家族。
2. `task` 并发 = 每会话一个可热调整的 `Semaphore`（abort-aware acquire、就地 resize、0=无限） + `mapWithConcurrencyLimit` worker 池（fail-fast、abort 返回部分结果）；与 prime-agent 的本质区别是**并发单位**：协程级交错 vs 进程级隔离。
3. `orchestrate` 是**隐藏系统通知**而非 slash 命令：小写散文边界匹配后把 10 条规则 + 7 步工作流（Ingest→Plan→Dispatch→Verify→Commit→Advance→Final verify）追加到当条用户消息，强制"阶段完成不是 yield 点、不相交工作必须同消息并行、子代理永不验证"。
4. AsyncJobManager 是进程内单例（maxRunningJobs=15、结果保留 5 分钟、owner 路由投递带指数退避），"后台"只意味着不阻塞当前轮次；进程退出全 cancel——恢复靠 JSONL 工件重扫成 `parked` 行，是"复活"不是"接着跑"。prime-agent 才是真 daemon：supervisor + 每 root session tree 一个 worker 进程 + IPython kernel，socket 协议、detach/attach、崩溃恢复。
5. 对 prime-agent 最值得吸收的三件：统一 wait 三方竞态（jobs↔消息↔超时先到先返回 + 丢消息保护）、abort-aware Semaphore（防取消残留收缩并发）、orchestrate 合同的"验证所有权唯一"与"并行强制"规则。

---

## 原始资料

- omp 官网: https://omp.sh/ · 仓库: https://github.com/can1357/oh-my-pi（分析固定提交 `06aecdd5`）
- DeepWiki 源码分析: https://deepwiki.com/can1357/oh-my-pi/12.2-task-delegation · 12.4-async-jobs-and-background-execution
- 源码文件（raw.githubusercontent.com/can1357/oh-my-pi/06aecdd5/）：
  - `packages/coding-agent/src/task/parallel.ts`（全文）
  - `packages/coding-agent/src/async/job-manager.ts`（全文）
  - `packages/coding-agent/src/irc/bus.ts`（全文）
  - `packages/coding-agent/src/task/index.ts`、`docs/tools/task.md`
  - `packages/coding-agent/src/tools/hub/{index,types,messaging,jobs,launch}.ts`（librarian 源码级分析）
  - `packages/coding-agent/src/modes/orchestrate.ts`、`prompts/system/orchestrate-notice.md`
- 上游 pi: https://pi.dev/ · https://github.com/earendil-works/pi
- 对照 prime-agent: https://github.com/PrimeIntellect-ai/prime-agent（`packages/coding-agent/docs/{architecture,long-running-agents,rpc,rlm}.md` + 官方博客 2026-08-05）

---

## 0. 先修事实：三项目同源，路线分叉

- **pi（earendil-works）本身就是 TypeScript/Bun 单仓**（`@earendil-works/pi-*` 包），不是 Rust 项目。**omp 不是"把 pi 改写成 TS"，而是 fork 后把包作用域改为 `@oh-my-pi/*` 的活跃分支**（源码里 import 全是 `@oh-my-pi/pi-utils` 等）。
- **prime-agent（PrimeIntellect-ai）也是 pi 生态 fork**（其 RPC 文档仍引用 `@earendil-works/pi-coding-agent` 内部实现）。
- 三者同源但走上相反路线：**omp 保持单进程，把进程内编排做到极致**（hub/IRC/task/async jobs）；**prime-agent 走向多进程 daemon**（supervisor + worker + IPython kernel）。这个对照贯穿第 4 题。

---

## 1. Q1：`hub` 完整 API 与底层 IPC

### 1.1 模块结构与 API 面

`hub` 是 5 文件模块 `packages/coding-agent/src/tools/hub/`：

| 文件 | 职责 |
|---|---|
| `index.ts` | `HubTool` 类：op 路由、per-op 审批、统一 `wait` 竞态 |
| `types.ts` | `HubOp` 12 值联合 + `HubDetails` 判别联合结果类型 |
| `messaging.ts` | `send`/`inbox`/`list`/`wait(from)` → IrcBus |
| `jobs.ts` | `cancel`/`jobs`/`wait(ids)` → AsyncJobManager |
| `launch.ts` | `start`/`ps`/`logs`/`stop`/`restart`/`describe` + 进程 `send`/`wait` → daemon broker |

**12 个 op，三个家族**：

```
hub op:
  messaging:  send(to|"all", message, await?, replyTo?) | wait(from?) | inbox(peek?) | list
  jobs:       jobs | cancel(ids) | wait(ids | timeoutMs)   ← 无参 wait 兜底
  processes:  start(name, application, args, cwd, pty, ready, restart, persist, detached)
              | ps | logs(name, lines, head, grep, follow, cursor)
              | stop | restart | describe
              | send(name, text|keys|signal) | wait(name, for:"ready"|"exit", pattern)
```

- `approval` 分级：`wait/inbox/list/jobs/cancel/ps/logs/describe` 及 peer `send` 为 **read**；`start/stop/restart` 与进程 stdin `send` 为 **exec**。
- 工具摘要原文：*"Message peer agents, control background jobs, **and supervise long-running processes**"*。
- `start` 的关键字段：`ready: {log?, port?, host?, timeout?}`（就绪条件可组合：log 正则 **或/且** TCP port）、`restart: 'no'|'on-failure'|'always'`、`persist`（活到最后一个 omp 客户端退出）/`detached`（活到所有进程退出，强制无 PTY）。

### 1.2 底层 IPC：不是单一机制，是**三层**

| 层 | op 家族 | IPC 原语 | 进程边界 |
|---|---|---|---|
| ① 消息 | send/inbox/list/wait(from) | `IrcBus.global()` — 进程内 pub/sub 邮箱 + waiter 队列 | 同进程 |
| ② 后台任务 | jobs/cancel/wait(ids) | `AsyncJobManager` — 进程内全局单例，`Map<id, AsyncJob>`（纯 Promise） | 同进程 |
| ③ 长进程 | start/ps/logs/stop/restart/describe | `daemonClientForProject(cwd)` → 跨进程 Unix socket / Windows named pipe + `broker.token` 认证 | 独立 broker 进程 |

**① IrcBus**（`irc/bus.ts` 全文已读）：进程内 mailbox，每 agent 邮箱上限 100 条。`send` **永不阻塞**等收件人回复，按收件人状态机路由：

```
parked  → AgentLifecycleManager.ensureLive 复活（outcome: "revived"）
idle    → 唤醒真实 turn（"woken"）
busy    → deliverIrcMessage 非打断旁注，下一步边界注入（"injected"）
aborted / advisor → 直接 failed（aborted 不可复活；advisor 是只读观察行）
```

- 投递成功的消息**不留邮箱**（已进收件人上下文，避免二次投递）；仅投递失败才缓冲，供后续 `wait`/`inbox` 取。
- 回复是收件人的真实 turn，发送方用 `wait(from:)` 观察。特例：收件人 mid-turn 无法到达步进边界（如同步 task spawn 中）且 `send await:true` 时，生成**临时旁路自动回复**，防止发送方干等超时。
- 广播 `to:"all"` 只覆盖 running+idle peer（**不复活 parked**）；定向 send 会复活 parked。

**③ 跨进程监督**：`launch/client.ts` 持有一条**持久** socket 连接（`CONNECT_TIMEOUT_MS=10_000`），完成通知经 `onCompletion(owner, sink)` 回传——所以 `start` 一个长进程后 omp 客户端退出，broker 仍能继续跑并把结果送回。

### 1.3 统一 `wait`：三方竞态（全设计最精巧的一点）

`#executeWait` 用 `Promise.race` 同时竞态三个 leg：

```ts
runningJobs.map(j => j.promise)     // leg 1: 运行中 job promise
+ bus waiter（无超时 IrcBus.wait）   // leg 2: 收件消息
+ window timer（timeoutMs 或智能轮询阶梯）// leg 3: 时间窗
```

- **"先到先返回"而非"全部完成才返回"**——模型可反复重发 wait 续等。
- **防丢消息**：`Promise.race` 之后**重新 await bus leg**，保证被消费的消息即使与 job 结算同帧也能赢——job 结果会自投递，被出队的消息丢不得。
- 智能轮询阶梯 `POLL_WAIT_LADDER_MS = [5s, 10s, 30s, 60s, 300s]`：连续重轮询（60s 内）逐级退避，干完活回来重置到地板——避免 wait 烧模型轮次。

### 1.4 cancel 的双路径（jobs + jobless agent 恢复）

`executeCancel` 对每个 id 依次尝试：
1. `manager.cancel(id, ownerFilter)`——job 存在且 running → 真 abort；
2. job 已结算但底层 subagent 注册还活着（预算中止的 keep-alive 僵尸，issue #6315）→ `cancelAgentRegistration`：abort live session + `lifecycle.release(id)`——这是 jobless subagent 的唯一 kill 路径；
3. 否则返回 `not_found` / `already_completed`。

跨 agent kill 双层拒绝：`manager.cancel` 校验 `ownerId` 匹配；`cancelAgentRegistration` 校验 `ref.parentId === ownerId`。

---

## 2. Q2：`task` 并发模型 vs prime-agent daemon worker

### 2.1 Semaphore（`parallel.ts` 全文已读）

- `max<=0` 或非有限 → **无限并发**（对应 `task.maxConcurrency=0` 的 "Unlimited" 语义，issue #3305）。
- `acquire(signal)` **abort-aware**：等待者带 AbortSignal 排队，abort 时把自己从队列 `splice` 掉——否则被放弃的 waiter 会被后续 `release` 唤醒，**永久收缩有效并发**（issue #3464 评审反馈）。
- `release()` 只在低于上限时 admit 下一个；`resize(max)` **就地调整**（非换实例）：提高上限立即放行排队者，降低上限让在途持有者自然排空。
- 用法：`TaskTool` 每会话一个 `#spawnSemaphore`，**每次 acquire/release 前从热设置 `task.maxConcurrency` resize**——会话中途改设置对已排队工作立即生效。

### 2.2 mapWithConcurrencyLimit（worker 池模式）

```ts
limit = clamp(floor(concurrency) 或 items.length, 1, items.length)
// worker 循环: nextIndex++ 抢任务（原子取号）
// 内部 AbortController; workerSignal = AbortSignal.any([外部signal, 内部])
// fail-fast: 首个非 abort 错误 → 内部 abort + rejectFirst + throw
// abort 时: 返回 {results(部分), aborted:true}; 完成的保留, 进行中的自行处理, 未开始的 undefined
// 结果按输入顺序排列（index 写入）
```

另有 `mapWithConcurrencyLimitAllSettled` 变体：不 fail-fast，rejection 按输入位置捕获，已启动的 sibling 全部 settle 后才返回（task 批量执行用此变体，signal 驱动取消）。

### 2.3 调度绑定

- `task.batch` 默认开，wire 形状 `{context, tasks[]}`——context 是必填共享背景，渲染进每个 subagent 的 system prompt。
- 每个 item 注册一个 `type:"task"` 的 AsyncJob（`queued:true` + `ownerId=调用方`），job body 先 acquire 信号量、`markRunning()` 后执行。**queued 状态不占执行槽**——大 batch 不会饿死其他 job 注册。
- `task.agentIdleTtlMs` 默认 420_000ms（7 分钟）：结束的 subagent → `idle`（保留 live session）→ `adopt` 计时 → park（dispose session 但保留 JSONL）→ 被消息/复活。
- 子代理必须走隐藏 `yield` 工具收尾：最多 3 次提醒，最后一次强制 `toolChoice=yield`；软预算 200 请求（1.5× 强制 yield）；`maxRecursionDepth` 限递归。

### 2.4 与 prime-agent 的本质区别

| 维度 | omp | prime-agent |
|---|---|---|
| 并发单位 | **协程**（Promise，单进程事件循环交错） | **进程**（每 root session tree 一个 worker + IPython kernel 子进程） |
| 故障域 | 进程内共享——一个 subagent 崩 = 全崩 | 进程隔离——worker 崩溃由 supervisor 从 JSONL + kernel 快照恢复 |
| 生命周期边界 | 随主进程；"后台"= 不阻塞当前轮次 | daemon 独立于终端；detach 后 resident worker 继续 |
| 执行引擎 | `createAgentSession` 同进程直接调 | RLM：模型唯一工具是持久 IPython kernel，subagent = 递归 `prime-agent` 实例 |
| 并行度 | 单线程（真并行只有 IO 等待） | 真多进程并行 |

一句话：omp 的"并行"是**事件循环内交错**（省进程开销、共享内存、无隔离）；prime-agent 是**操作系统级进程**（隔离、可恢复、每 session 完整进程栈）。两者都明言：进程隔离是生命周期/故障用的，**不是安全沙箱**。

---

## 3. Q3：`orchestrate` 关键字如何触发多阶段并行合同

位置：`modes/orchestrate.ts` + `prompts/system/orchestrate-notice.md`。

### 3.1 触发机制

- **不是 slash 命令**（旧版 `/orchestrate` 已移除）。`magicKeywordRegex("orchestrate")`——**必须小写、散文边界**（`orchestrated`/`Orchestrate`/`orchestrate.ts` 均不触发；测试覆盖大小写/空白/fenced-code/inline-code/标点邻接）。
- 命中后把 `ORCHESTRATE_NOTICE`（隐藏 system-notice）**追加到那条用户消息**，仅当轮生效。
- 编辑器内 teal→violet 渐变高亮（hue 150→280，14 档）。
- 开关：`magicKeywords.orchestrate`（默认 true）；同类关键字：`ultrathink`、`workflow`。

### 3.2 合同内容（10 条规则 + 7 步 workflow）

```
Ingest → Plan → Dispatch → Verify → Commit → Advance → Final verification
```

1. **阶段完成不是 yield 点**——同一轮内直接启动下一阶段，直到全部可验证完成或真正 `[blocked]`；
2. 分发前**全量枚举**工作面（引用到的 audit/plan/checklist 全展开成 todo）；"大多数/重要项"算失败；
3. **最大并行**：不相交范围必须一次消息内多个 `task` 调用；只派一个 subagent 前先找并行机会或改为内联；仅当产出合同（类型/schema/共享模块）被下一步消费时才串行；
4. 每个 task 自包含（共享零上下文）：≤3–5 个显式目标路径（禁 glob）、变更的 API/模式、边界用例、可观察验收标准；
5. 阶段间必须验证（`bun check`/`bun test`/`lsp diagnostics`）；红树不许推进、不许宣称完成；
6. 只按请求或仓库惯例 commit；绝不提交红树；
7. 子代理做错 → 派修正型 subagent 指明差距，**绝不默默内联修**；
8. **禁 scope creep/shrink**：不许加未请求工作，不许把未完成改标 "follow-up"/"v1"/"MVP"；
9. **子代理永不验证/lint/format**——验证所有权唯一归 orchestrator，阶段边界验证一次（防 formatter 竞态）；
10. trivial 机械改动内联做（`edit`/`write`），只在实质/可并行时才 offload——成本-收益门控。

**关键点**：orchestrate 驱动的是 `task` 工具，**不是 `hub`**；`hub` 只作为轮询便利（"async results / hub wait"）出现。hub = 编排的观察/消息面，task = 执行面。

---

## 4. Q4：AsyncJobManager 为何"不是系统级 daemon"

`async/job-manager.ts` 全文已读，铁证是**进程内全局单例**：

```ts
static #instance: AsyncJobManager | undefined;   // static 单例，随进程生灭
readonly #jobs = new Map<string, AsyncJob>();    // 纯内存
DEFAULT_MAX_RUNNING_JOBS = 15;
DEFAULT_RETENTION_MS = 5 * 60 * 1000;            // 结果保留 5 分钟后驱逐
```

不是 daemon 的四个原因（也是与 prime-agent 的分水岭）：

1. **内存态，无进程边界**：job = Promise + AbortController，`dispose()` 一到全部 `cancelAll(ASYNC_JOB_MANAGER_SHUTDOWN_REASON)`。"后台" = 不阻塞当前模型轮次（yield 后 `subagent-async-pending.md` 提示仍在跑），**绝不超越进程存活**。
2. **恢复 ≠ 继续运行**：会话重开后 Hub 扫描持久化工件（`<id>.jsonl`）把历史 subagent 变成 **`parked` 行**——是从磁盘"复活"可再消息的会话壳，不是接着跑。
3. **生命周期状态机在进程内**：`idle → adopt(7min TTL) → parked → revive`，进程退出即终结；"Main" 永不 park。
4. **投递是 owner-routed 进程内回调**：`registerDeliverySink(ownerId, sink)`，指数退避（500ms→30s 带 jitter）；无 live sink → dead-letter（结果文本保留到驱逐）——跨 agent 投递被架构性杜绝。

### 4.1 vs prime-agent 架构对照（官方文档已确认）

```
prime-agent:
  TUI/CLI client ──"local daemon protocol"(socket)──▶ Daemon supervisor ──▶ Session worker 进程
                                                          │（routing · attachments · 崩溃恢复）
                                                          ▼
                                    worker = AgentSessionRuntime + Scheduler
                                             + Root IPython kernel + RLM 子进程树
```

- **client 只拥有渲染/输入，不拥有执行**；supervisor 拥有发现/路由/worker 健康/跨 agent 消息；
- 每个 worker 进程拥有一个 root session tree；detach 后 resident worker 继续持有队列/调度/kernel/后代/持久状态；worker 或 supervisor 重启可从 JSONL + kernel 快照恢复；
- 调度面（heartbeat/cron/goal/autonomous）全部注入同一 session queue，与人工 prompt 走同一条执行管道。

**差在哪一句话**：omp 把"后台"做进**进程内事件循环**（Promise + 单例 Map + owner 路由回调），prime-agent 把"后台"做进**操作系统**（daemon 进程 + worker 进程 + socket 协议 + 磁盘快照恢复）。前者部署即单进程 CLI、零 IPC 成本；后者换来 detach/attach、崩溃恢复、跨会话持续执行——代价是 supervisor 进程栈、协议、序列化/重放。

---

## 5. Q5：对 prime-agent 的借鉴清单

### 值得吸收（按性价比排序）

| # | omp 机制 | 为什么值得 | 落地建议 |
|---|---|---|---|
| 1 | **统一 wait 三方竞态**（jobs ↔ 消息 ↔ 超时，先到先返回 + 丢消息保护） | prime-agent 已有 daemon 消息 + 后台任务，缺"等任意一方先到"的单一原语 | daemon 协议层加 `wait_any` 命令 |
| 2 | **智能轮询阶梯** `[5s,10s,30s,60s,300s]` + 60s 空闲重置 | 轮询烧模型轮次；阶梯让紧轮询自动退避 | 适配到 RPC/daemon 客户端轮询 |
| 3 | **abort-aware Semaphore acquire**（abort 时从队列 splice 掉 waiter） | 防取消残留 waiter 永久收缩并发——有并发限制队列的系统都会踩此坑 | 直接吸收 `parallel.ts` 的 `acquire(signal)` |
| 4 | **Semaphore 就地 resize + queued job 不占槽** | 热更新上限 + 大 batch 不饿死其他任务 | 映射到 worker 池上限动态调整 |
| 5 | **ownerId 作用域 cancel/list**（manager 层 + registry 层双重校验父 id） | 子代理 teardown 不误杀父任务；prime-agent 的 family roster 已有血缘概念 | cancel 前校验 `ref.parentId === ownerId` |
| 6 | **orchestrate：阶段边界验证所有权唯一**（子代理永不验证，orchestrator 验证一次） | 防 formatter 竞态 + 红树推进；对齐 autonomous mode 的 quality gates | 写进 autonomous 策略提示 |
| 7 | **orchestrate：并行强制规则**（不相交工作必须同消息并行、禁串行） | 直击 agent 默认串行/偷懒模式 | 进 prime-agent 系统提示 |
| 8 | **launch 的 ready 组合条件**（log 正则 + TCP port）+ restart 策略 | supervisor 已有进程管理基础，缺"可验证启动合同" | 加到 supervisor 进程规范 |
| 9 | **Hub 的 parked 复活语义**（消息 parked agent = 自动 revive + 注入） | prime-agent retained subagent 已实现类似物，核对语义对齐 | 复核现有实现 |

### 不要照搬 / 注意差异

1. **omp 的 wait 是"轮询+事件"混合，不是真 push**——prime-agent 的 daemon 有真 push 通道，只需吸收"先到先返回"语义，不必回退成轮询。
2. **omp 的进程内模型故障域小**——`maxRunningJobs=15` + 信号量是单进程妥协，**不要**当特性抄回去；prime-agent 已用进程隔离解决。
3. **没有独立 `supervise` op**——"supervise"只是工具摘要的动词，监督就是 `launch` 家族；要 supervise 语义直接做成 supervisor 固有职责即可。
4. **hub 不 spawn 子代理**——spawn 走 task，hub 只管消息与观察。职责分离值得保留（避免一个工具既派活又管活的混乱）。

---

## 6. 方法学与可信度

- **源码级**：`parallel.ts` / `job-manager.ts` / `irc/bus.ts` / `task/index.ts` / `docs/tools/task.md` 为全文精读；`tools/hub/` 五文件与 `orchestrate.ts`/`orchestrate-notice.md` 为 librarian 子代理源码分析（含逐函数路由、schema 字段、测试名佐证）。
- **固定提交** `06aecdd5`（DeepWiki 最后索引时间 2026-08-12），避免 main 分支漂移。
- **prime-agent 侧**：官方 `packages/coding-agent/docs/{architecture,long-running-agents,rpc,rlm}.md` + 2026-08-05 官方博客，**未读源码**——借鉴清单中涉及 prime-agent 现有能力的判断（family roster、retained subagent、autonomous gates）需落地前以源码复核。
- **局限**：未能对 omp 做本地克隆实证（Windows 环境克隆超时），IPC 行为描述基于源码推演；"三项目同源"的判断基于包名/文档引用，未经 git 历史验证。
