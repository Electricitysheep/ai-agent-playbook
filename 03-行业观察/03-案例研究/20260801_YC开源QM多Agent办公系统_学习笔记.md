# YC 开源 QM：多 Agent 办公系统的架构拆解与个人体系对照（学习笔记）

> 归档日期 2026-08-02 · 主题：YC 于 2026-07-31 开源的 multi-agent 办公系统 QM
> 一手资料为主：官网 https://qm.ycombinator.com/ · 仓库 https://github.com/yc-software/qm
> 对照底稿：02_AI工程/05_AI辅助开发工作流/多Agent工作流手册_v1.md（v1.3）

---

## 我能讲出来的版本（5 行）

1. 
2. 
3. 
4. 
5. 

---

## 一、QM 是什么

QM（Quartermaster，船上管后勤的军需官——官网注脚原话："the person on a ship who coordinates belowdecks to keep things in order"，来源：https://qm.ycombinator.com/）是 Y Combinator 开源的 **multiplayer agent harness**，一句话定位："A multiplayer agent harness for work. In Slack and on the web."（来源：https://raw.githubusercontent.com/yc-software/qm/main/README.md）

**发布事实（已核实）**：
- 仓库创建 2026-07-29，MIT 协议，抓取时刻（2026-08-02）6,262 stars（来源：GitHub API repos/yc-software/qm）
- 首个公开 release v0.1.2 于 2026-07-31 00:06 UTC 发布，当天连发 v0.1.3 / v0.1.4（来源：GitHub API releases）
- HN 讨论 2026-07-31 18:04 UTC 上首页，658 分 / 155 评论（来源：https://news.ycombinator.com/item?id=49126604，经 hn.algolia.com API 核实标题/分数/评论数，未逐条读评论）
- 官方称可与 Pi / OpenCode / Codex / Claude Code 任选其一驱动同一核心（README 原话："Pi, OpenCode, Codex, and Claude Code all drive the same core"，且仓库 src/harness/ 下确有 pi-harness.ts / opencode-harness.ts / codex-harness.ts / claude-harness.ts 四个适配器，来源：README + GitHub 文件树）

**它解决的问题**：大多数 agent 是"个人助理"式设计，硬套到整家公司会迅速变复杂（README 原话："Most agents are designed like personal assistants. You can make one work for a whole company, but it quickly gets complex."）。QM 为 startup 设计：**每个员工和每个房间（频道/群聊/项目）各自有独立的 memory、文件、keychain 视角、权限、crons、web apps 和持久 sandbox**（来源：README）。

**官网的演进叙事**（来源：https://qm.ycombinator.com/）：
1. 第一代：一个 Ruby 写的 agent loop + 能访问内部数据的工具，第一天就有用但能力有限；后来扩展出 crons 和 webhook triggers；
2. OpenClaw 发布把他们推向新方向；
3. 为员工 provision 了 **50+ 个 Hermes 个人助理 agent**，管理这个规模的 fleet 变得有挑战；
4. 想要"Hermes 的灵活 + 第一代系统的简单"，且想自己托管，于是有了 QM。

**OpenClaw 是什么（补一句定位）**：官网说的 "fleet of OpenClaw-like agents" 里的 OpenClaw，是 OpenClaw Foundation（非营利）维护的开源**个人** AI 助手，跑在用户自己的设备上，可接 Slack/Discord/Telegram/WhatsApp 等 20+ 平台（来源：https://github.com/openclaw/openclaw 、https://openclaw.ai/，定位已核实）。所以 QM 的目标翻译过来是：**把"人手一个 OpenClaw 式个人助理"这件事，按组织规模管起来**——每个人一个、每个房间一个，但统一身份、统一权限、统一审计。

**官方列举的典型用法**（README "What you can do with it" 节，来源：README）：跨内部笔记/邮件/文档/数据库/网页统一检索；从"公司大脑"取信息；构建内部应用并发布给对的人；**学你的写作口吻，然后定时 triage 收件箱（带标签和回信草稿）**；在现有仓库里跑测试、开 PR、盯 CI、查系统日志；在共享频道里跟踪项目、发更新和 follow-up。→ 这些是 YC 用 QM 做事的场景参照，其中"学口吻 + 定时处理收件箱"与"频道里跟项目"是最有 YC 味的两个。

⚠️ **需人工核实的点**：你给的已知事实里"覆盖会计、法务、活动、工程"——我 grep 过 README 全文，**一手 README 并未逐部门列举**；该表述来自媒体转述（https://enterprisedna.co/resources/ai-pulse/ai-pulse-2026-08-01-y-combinator-open-sourced-qm-the-multiplayer-agent-harness-i/ 与 https://valueaddvc.com/pulse/y-combinator-qm-open-source-agent-harness-2026），官网只说"especially helpful for work-related tasks"。内部是否真在跑这四个部门，**未能获取一手确认，需人工核实**。

**社区反响（二手，谨慎引用）**：HN 前排 658 分 / 155 评论（2026-07-31，来源：https://news.ycombinator.com/item?id=49126604）。逐条评论分数没拿到（Algolia items API 不返回子评论分数），抓到的较热评论文本大意：①"一个 AI 项目要求人写 PR、还明令别用 AI 扩写提案，挺讽刺"（@john_strinlai，针对 CONTRIBUTING.md 的 human-written 规则）；②"看起来像是 YC 为了不在 Buzz 面前丢地盘而 rush 出来的内部工具"（@josht，"Buzz" 具体指哪家未核实）；③"不如直接用 Hermes/OpenClaw，或 Tasklet/Prajvis"（@argssh）；④"行业有 AI psychosis 了"（@Drupon，同样针对 CONTRIBUTING）。这些只当氛围参考，不代表事实，正式引用前请回 HN 逐条核实。

---

## 二、架构拆解

### 2.1 组件关系图

README 自带一张 mermaid 架构图（来源：README Architecture 节），转写成 ASCII：

```
┌──────────────────────── QM 部署（跑在 operator 自己的云账号）────────────────────────┐
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐        │
│  │ Headless Core（TypeScript on Node + Fastify HTTP）                        │        │
│  │   API · identity · policy · scheduler · audit                            │        │
│  │   ┌──────────────────────────────────────────────────────────────┐       │        │
│  │   │ Agent Loop：harness 抽象（可换，不绑定厂商）                   │       │        │
│  │   │   Pi / OpenCode / Codex / Claude Code → 同一核心               │       │        │
│  │   └──────────────────────────────────────────────────────────────┘       │        │
│  │   triggers：交互触发(mention/DM/消息) · cron · webhook · monitor(变化才跑)│       │        │
│  └──────────────┬──────────────────────────────────────────────────┬─────────┘        │
│                 │                                                  │                  │
│   ┌─────────────▼───────────┐                    ┌─────────────────▼─────────────┐    │
│   │ Postgres 持久层           │                    │ 每 scope 一个持久 sandbox       │    │
│   │ sessions · memory · 队列  │                    │ 文件 · 工具 · keychain 视角      │    │
│   │ grants · audit · runs     │                    │ 已登录服务（OAuth token 注入）    │    │
│   │ 幂等 · 交付                │                    │ execute 工具在此隔离执行，装了的 │    │
│   └───────────────────────────┘                    │ 工具会一直在（durable）           │    │
│                                                    └───────────────────────────────┘    │
│                                                                                       │
│  surface 插件（都挂在 core 的 HTTP API 上，可选）：web UI · admin 面板 · 公开 portal     │
│  Slack = 可选 in-process 插件（Bolt 实现，core 用 service client 直接驱动并监督）       │
│  connectors（OAuth 一次性同意链接，admin 启用）：Google Workspace · Dropbox · Linear ·  │
│     GitHub/GitLab · Google Drive/Sheets · 浏览器会话                                  │
│  skills：scope 持有 · 按 grant 共享 · admin 门控晋升 org 级 · 可从 git 仓库导入 pack    │
│  web apps：自定义内部应用，发布给指定人，capability link 授权                          │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

**scope 体系**（"每人每房间"的展开）：

```
Org scope（org 级 notebook，仅 admin 可写，全 org 每场对话都会 recall）
 ├─ 每人个人 scope（DM：自己的 memory / 文件 / keychain 视图 / sandbox / crons）
 ├─ 每 Slack 频道 / 群聊 scope（频道自己的 notebook；成员可见）
 └─ 每项目 scope（project：项目专属记忆 + 文件 + web app）
核心安全目标：阻止跨 scope 的 read / write / delivery；凭据只在授权 scope 内；
每个 action 按 principal + scope 归因审计（来源：SECURITY.md）
```

### 2.2 各组件分别解决什么问题

**Headless core（API · identity · policy · scheduler）**：所有 turn 都过一个中央核心，核心不绑定任何一家模型/前端。"Every substrate (harness, session store, sandbox, memory) sits behind an interface, so production implementations swap in via one wiring file."（README）→ 解决**厂商锁定与组件可替换性**。源码佐证：src/wiring.ts、src/harness/harness-router.ts。**模型层同样可换**：src/model/model-catalog.ts 注册了 anthropic / openai / openrouter / pi 四类模型供应商，web UI 测试里还出现过 OpenRouter 接入（plugins/web-ui/test/openrouter-turn.test.ts）→ 连模型供应商都不绑定，这与我的体系"多入口不同厂"的思路同构。

**Postgres 持久层**：sessions、memory、queue 全落库；run 存储、任务队列、幂等、审计全部有 postgres-* 实现（src/runs/postgres-run-store.ts、src/cron/job-queue.ts、src/delivery/postgres-delivery-store.ts 等）。AGENTS.md 的工程铁律："Anything an operator or the system reads back later must live in a durable store, never RAM alone." → 解决**后台任务/多实例下状态丢失**（core 蓝绿双实例部署，进程内 Map 每次部署就没了）。

**每 scope 一个持久 sandbox**：agent 只有一个小而固定的工具面，其中 `execute` 在 scope 自己的隔离 sandbox 里跑命令——"its durable computer, where installed tools stay installed"（README）。后端可换：本地 docker、AWS ECS Fargate + Lambda MicroVM（sandbox 后端叫 sprites）、Fly Machines（来源：cli/README.md + src/sandbox/ 下有 local-sandbox.ts / aws-sandbox.ts / sprites-sandbox.ts / docker-exec.ts）。→ 解决**隔离执行 + 环境持久化**：装一次工具，之后每次 run 还在。

**triggers（crons / webhooks / monitors / 交互）**：README features 说 "Background work. Crons and watches run work while nobody's watching."。代码里 `BackgroundWakeTrigger = "cron" | "webhook" | "monitor"`（src/types.ts），provenance.ts 里 WAKE_TRIGGERS = {cron, webhook, monitor}，部署目录示例里 webhook 的 surface/origin 是 `"webhook"/"automation"`（docs/deploy-directory.md）。cron 有 store/scheduler/job-queue 三件套（src/cron/）；monitor（watch）带 pattern + cursor，轮询到变化才触发（src/monitors/monitor-store.ts）；交互触发（mention/DM/消息）走 run-trigger（src/triggers/run-trigger.ts）。→ 分别解决：**定时活、外部系统推事件、盯变化、人叫**四类启动方式。官网还提到 webhook triggers 早在其第一代 Ruby harness 就有——所以 webhook 是 QM 触发模型的一等公民（官网 + 代码双重证据）。

**memory（分 scope 笔记本，不是共享池）**：⚠️ 注意，"shared memory"在 QM 里并不存在一个公共池——准确说法是 **per-scope notebook** + 三种共享手段：①房间本身就是共享 scope（频道有频道自己的 notebook）；②org-wide notebook（仅 admin 可写，全 org 每场对话自动 recall）；③跨房间写入走 self-API 且带权限校验（公共频道任何内部成员可写；私密频道/群聊必须是成员，403 拦截）。memory 是 typed tool 而非文件："Memory is NOT a file…the tool is the one real path"，每 turn 自动 recall + 事后自动提取，另有 search / remember / read / rewrite（curate）动作（来源：skills-seed/memory/SKILL.md + src/memory/strategies/ 下有 per-turn / consolidation / scratch-promote / agent-only 四种策略）。→ 解决**记忆按边界组织 + 防串味 + 可净化**。

**connectors（OAuth 一次性同意链接）**：admin 先启用 provider；用户点一次性 consent link 连接，agent 永远看不到/不代输密码；token 以环境变量形式注入**该用户自己的 sandbox**（如 `$VAULT_TOKEN_GMAIL_GOOGLEAPIS_COM`，来源：skills-seed/google-workspace/SKILL.md）。connector 实现集中在 src/connectors/（oauth.ts、consent-link.ts、connector-client-store.ts、browser-session-store.ts）。技能库里已有 google-workspace、dropbox、linear、github-gitlab、google-drive-sheets 等（skills-seed/ 目录）。浏览类连接器另有供应商抽象（browse 技能支持 browserbase / kernel 两种后端，skills-seed/browse/providers/）。→ 解决**SaaS 数据的按人授权接入**：凭据不出用户自己的 scope，且浏览器执行也可换后端。

**安全 posture 三档 + 预声明命令策略**：Strict（每个工具调用都暂停等人工审批，除两个无副作用收尾）/ **Auto（默认，classifier 先筛 provenance 标注的外部数据与工具结果再进模型，可接自己的 screening proxy）** / Dangerous（不筛不暂停）。另有 predeclared command policy——对递归删除、破坏性 SQL 等硬拒绝，**Dangerous 档也生效**（README Security 节）。人在环审批直接发生在 Slack 里（源码 src/slack/approval-cards.ts），Strict 档的"每步暂停"就是通过这类审批卡片完成的。→ 解决**组织级风险偏好收敛 + 最低兜底线**。

**web apps / skills / admin**：web apps 把自定义内部应用发布给指定人，capability link 是 bearer 授权（SECURITY.md 明示这是"deliberate exception"）；skills 按 scope 持有、可 grant 共享、admin 门控晋升、可 git 导入 pack；admin 面板管 org 级配置、安全 posture、可用 harness 与模型（README Features）。→ 解决**把 agent 能力产品化地分发给组织成员**。

### 2.3 部署形态：一个部署 = 一组服务

QM 不是一个单体，而是一组服务（来源：deploy/README.md 的 Topology 节）：

- **Public portal 是唯一公网入口**：负责 OIDC 认证，并反向代理私有网络里的 web UI 与 admin 面板；
- **Core、Postgres、agent computers（各 scope 的 sandbox）全部私有**，不暴露公网；
- **Slack 走 outbound Socket Mode 在 core 进程内运行**——所以 Slack 不需要任何入站端口；
- **auth broker**（内置的邮箱一次性链接登录）：部署时 CLI 生成签名密钥与 portal 的 client 凭据并接线；它本身也是私有服务，portal 只转发它的两条浏览器路由（`/idp/`），token/userinfo/JWKS 调用留在内网；想去掉它换外部 IdP（如 Slack OIDC）就删 `"auth"`；
- **Connector 的 OAuth client 与 Slack bot token 从 admin connector URL 录入**，密文存持久存储、永不落 deployment 目录；agent 只向用户广告 admin 已启用的 connector。

→ 这条拓扑回答了一个之前没写清的点：**QM 的"可选插件"不是说能拆掉核心功能，而是核心(headless)+全部数据面都在私有网络里，对外只开 portal 一个口**——这比个人工具"一个进程跑在本机"是完整一档的组织级安全模型。

### 2.4 为什么"每人每房间独立 memory/权限/sandbox"是单人工具解决不了的

回答你的第二个问题。单人 agent 工具（Claude Code / OpenCode / Codex 在个人机器上跑）的默认模型是：**一个进程、一份上下文、一套凭据、一个本机/单容器环境**。QM 按 scope 隔离解决的是这五类单人工具做不到的事：

1. **多用户并发不互相污染**：多个员工同时用，各改各的 workspace，"work independently without affecting each other"（README）。单进程 agent 服务多人必然上下文互踩、文件冲突。
2. **数据保密边界**：法务/财务/人事数据不能互相可见。SECURITY.md 把"阻止跨 scope 的 read/write/delivery"列为核心安全目标。一个拿全公司权限的单体 agent，一次 prompt injection 或误操作就能读全库。
3. **凭据最小化**：每个人的 OAuth token 只 materialize 进自己的 sandbox；keychain 按 scope 有独立视图；凭据的 owner / audience / 一次性或常驻 / 过期 / 撤销 / 审计由 core 强制执行（SECURITY.md：grant 引擎）。单人工具里所有凭据混在一台机器上。
4. **团队记忆**："公司脑"不是一个人的记忆，而是按房间/项目组织的 notebook；跨房间写入都要过权限校验。单人工具没有"房间"这个中间层。
5. **无人值守执行 + 归因审计**：cron/webhook/monitor 在没人盯的时候跑，且每个动作都有 principal + scope 归因。本地 agent 没有"谁、在哪个 scope、干了什么"的归因层，也就无法回答"这是谁授权的改动"。

一句话：**单人工具解决"一个人怎么把活干完"；scope 体系解决"很多人一起用且各不越界、出事可追责"**——第二维是组织才有的维度。

### 2.5 工程与发布纪律（YC 的软件文化信号，值得单独抄走）

这是 QM 代码库自己定的规矩（来源：仓库根 AGENTS.md，CLAUDE.md 是它的软链接）：

- **零注释铁律**："The standard is zero comments"——不写解释性注释/docblock/TODO，用命名、结构和测试表达意图，理由写进 commit/PR 描述；
- **修复要全仓扫同类**：发现一个 bug/反模式，grep 全仓库同模式一起修，不许只修报告的那一处；
- **Durable by default**：任何之后要读回的状态（audit/日志/队列/配置）必须落 Postgres，进程内 Map 只配当缓存——因为 core 蓝绿部署、多实例，内存状态等于每次部署就丢；
- **禁止作者自审**：合 main 前必须派一个没看过你写代码的独立评审 agent，且"green CI 不等于 review"；评审深度按 blast radius（看调用方数量，不是文件数）定；
- **前端改动必须截图**进 PR；
- 发布链：npm 包带 provenance 证明、`.npmrc` 强制新包版本 7 天冷却期防供应链投毒、release 由 CI 从 main 触发并签图（来源：cli/README.md + SECURITY.md Dependency cooldown）。

其中"零注释""独立评审""durable-by-default"这三条，正好是你知识库 09_测试与工程规范 想补的信号，可直接进工程实践清单。

---

## 三、对照我的多 agent 体系

我的体系（据 多Agent工作流手册_v1.md v1.3）：**5 个 agent 入口**（Claude Code 主刀 / omp 快手 / Antigravity IDE 手 / opencode 流水线 / Kimi CLI 长文手）+ **Orca 宿主**（任务总线 / 并行引擎 / 审查工作台 / 注意力管理器 / 观测面板）+ **21 条路由** + 六种并行拓扑 + deny 规则（rm -rf* / git push*）。

**逐组件对照**：

| QM 组件 | 我的体系现状 | 差距 | 可借鉴动作 |
|---|---|---|---|
| harness 抽象（4 个 harness 驱动同一核心） | 5 入口按路由分工，理念一致 | 我是"一个任务挑一个入口"，QM 是"多个 harness 服务同一核心" | 保持；"同题多方案（拓扑②）必须不同厂"与 QM 的 harness-router 同构，手册第五节已写对 |
| 每 scope 独立 sandbox + 持久环境 | Orca worktree 做文件级隔离 | worktree 只是 git 检出，不是独立环境；工具安装不持久 | 轻量版：每个项目给独立 env/缓存目录；重活才起 docker |
| per-scope notebook（typed memory） | 各 agent 自带 memory，互不可见、无共享 | 没有"项目级记忆"这一层 | 见启发 1 |
| triggers：cron / webhook / monitor | 第七节有 cron/scheduled task | 缺 webhook 与 monitor（变化才触发） | 见启发 2 |
| posture 三档 + 预声明命令策略 | 有 deny 硬规则 | 是"黑名单"而非"按任务类型分档" | 危险类任务（删库/推送/发信）显式走 strict 档，其余 auto |
| 审计 / attribution | Orca 有 orchestration.db 任务历史 | 记录的是任务而非"哪个 agent 在哪个 scope 干了什么" | 见启发 3 |
| 持久化队列 + 幂等 | 后台任务靠 Orca 挂着 | 状态在内存，易丢 | 长任务关键状态落盘（手册 v1.3 已强调类似纪律） |
| connectors（OAuth 授权即插即用） | agent-reach 15 平台 + MCP | 无"按 scope 的凭据视图" | 凭据按项目分环境变量，不全局混用 |

**三个核心洞察**：

1. **QM 的"多人"维度我不需要，但"多 scope"维度可以直接降维**。把 QM 的"人/房间/项目"映射到我的"项目/主题"：每个项目一份独立记忆、独立 env、独立沙箱——这正好补上手册里 worktree 视野盲区（2026-07-25 演练踩到的坑）之后的下一层：**文件隔离有了，记忆隔离没有**。
2. **QM 的工程纪律是个人体系的质量模板**：小固定工具面 + execute 进沙箱、一切读回的状态必须落盘、一切动作可审计、供应商可换——和手册第七节"观测→沉淀→自动化"复利哲学同构，但 QM 把它做成了硬约束而不是习惯。我的体系目前最缺的是"审计"这一条。
3. **触发模型补全自动化的最后一环**：手册第七节有定时（cron），QM 的 watch/monitor（盯一个数据源，变化才触发）+ webhook（外部事件推入）正好是我体系里没有的两类触发器。

---

## 四、不该照搬的部分

**QM 里 YC 特有、个人开发者不该照搬的**：

1. **组织级治理全套**：admin 面板、grants 引擎、org-wide notebook、skill 晋升门控、全链路 audit——都是为"多用户 + 分级权限"设计的。个人单用户跑这套是纯开销，没有可隔离的"别人"。
2. **50+ 员工的 fleet 运维**：官网明说"管理 50+ Hermes 的挑战"直接催生了 QM。我的规模是 5 入口，fleet 生命周期管理（provision/回收/配额）不存在。
3. **每 scope 常驻计算的基础设施**：每个员工/房间一个持久 VM/sandbox + RDS + 对象存储 + egress proxy + 蓝绿部署（来源：cli/README.md、deploy/ 目录结构）。个人用本地 docker sandbox 即可。
4. **Slack 深度依赖**：QM 的默认协作叙事全部围绕 Slack——bot 进频道、群聊里的 agent、Slack 审批卡片、Slack SSO 免邮箱入职（来源：cli/templates/deployment/references/slack.md）。README 强调 Slack 和 web UI 都是**可选插件**、core 本身无 surface，但"频道记忆/群聊协作"这类核心场景没有 Slack 就退化成纯 web 单聊。个人没有 Slack workspace，等于砍掉一半产品形态。
5. **OAuth connector 生态 + email onboarding**：面向组织工作流（员工入职连接 Gmail/Linear/Dropbox）。个人用现成 MCP 即可。
6. **供应链工程**：npm provenance、7 天依赖冷却（SECURITY.md Dependency cooldown）、private fork 流程——面向多人维护的开源项目，个人仓库不需要。

**三个门槛**（分别回答你问题里的成本/规模/Slack）：

- **成本门槛**：部署在 operator 自己的云账号（AWS ECS Fargate + RDS + Lambda MicroVM，或 Fly Machines + Postgres）。⚠️ 官方 README/cli 文档**未公布任何价格**，具体账单**未能获取，需人工核实**；但从架构上可确定：每个 scope 一个常驻计算环境 + 托管数据库 + 按员工数×日常使用量计费的模型 API，是**组织级账单**，不是一个个人开发者"装上就跑"的玩具级成本。
- **组织规模门槛**：设计目标明确是 startup/团队。多用户、多房间、需要权限边界时，隔离才有意义；单用户场景"每人独立 workspace"没有对应物。规模下限至少是"有几个人要同时用，且数据要互相保密"。
- **Slack 门槛**：产品名本身就带着 Slack（"In Slack and on the web"）。没有 Slack workspace：bot 进不了频道、频道记忆用不了、Slack SSO 用不了（可退回 email-gated onboarding，slack.md 明确说 bot 与 SSO 可分开/可不要）——能用，但用到的只是 web 单聊 + 后台任务的降级形态。

---

## 五、对本知识库的启发

1. **给多Agent工作流手册加一条"项目级记忆"路由（对标 QM 的 per-scope notebook）**：在每个 Orca worktree / 项目根目录维护一份 `MEMORY.md`（或并入 CLAUDE.md），并在路由表加一条：*涉及项目背景的问题，先读目标项目的 MEMORY.md 再回答，禁止凭全局印象跨项目套答案*。落地成本极低（一个文件 + 一条规则），直接补上"文件隔离有了、记忆隔离没有"的缺口。

2. **把第七节自动化层从"cron 一种"扩成"三类触发器"（对标 BackgroundWakeTrigger）**：cron 已有；补 ①webhook——给 knowledge-notes / paper-to-practice 仓库配 push webhook，推送即触发知识库整理（路由 18）；②watch——写一个"盯数据源、变化才进任务队列"的轮询脚本（如每周日归档仪式前盯一个订阅源/指标）。每周五复盘时只处理"变化了的东西"，而不是全量重扫。

3. **给 Orca 任务总线加"最小审计"一行（对标 QM 的 attribution）**：每个后台任务结束时自动 append 一条 `{时间, agent, worktree, 动作概要, 结果}` 到任务日志（现有 orchestration.db 之外的 `audit.log`，或复用任务历史）。周五复盘扫一遍 = QM 全量审计的个人降级版，也为面试讲"可观测与可归因"留实证。

---

## 附：来源与核实状态

**一手来源（已抓取核实）**：
- 官网全文：https://qm.ycombinator.com/ —— 定位、演进叙事、OpenClaw 对比、名字由来 ✓
- README 全文：https://raw.githubusercontent.com/yc-software/qm/main/README.md —— 架构图、scope 模型、posture 三档、harness 列表、部署方式 ✓
- 仓库元数据（GitHub API）：https://github.com/yc-software/qm —— 2026-07-29 创建、MIT、6,262 stars（2026-08-02 抓取）、releases v0.1.2~v0.1.4 均在 07-31 ✓
- SECURITY.md：威胁模型、grant/凭据语义、已知限制清单、依赖冷却 ✓
- cli/README.md + docs/getting-started.md + docs/deploy-directory.md：部署目录、AWS/Fly 后端、webhook surface 示例 ✓
- cli/templates/deployment/references/slack.md：Slack bot 与 SSO 的双 App 模型、可去 Slack 化的边界 ✓
- 源码文件清单与关键文件（GitHub API + 文件内容抓取）：src/harness/*（4 个 harness）、src/triggers/run-trigger.ts 与 provenance.ts（cron/webhook/monitor）、src/monitors/monitor-store.ts、src/memory/strategies/、src/connectors/、src/sandbox/*、skills-seed/memory·connect-apps·google-workspace SKILL.md ✓
- deploy/README.md + deploy/stacks/README.md：部署服务拓扑（portal 唯一公网口、core/Postgres/sandbox 私有、Slack outbound Socket Mode、auth broker 走 /idp/ 转发）✓
- src/model/model-catalog.ts（anthropic/openai/openrouter/pi 四类供应商）、src/slack/approval-cards.ts（Slack 审批卡片）、skills-seed/browse/providers/（browserbase/kernel 两种浏览器后端）—— 文件存在且关键内容已核实 ✓

**二手来源（仅佐证，未深读全文）**：
- HN：https://news.ycombinator.com/item?id=49126604 —— 658 分/155 评论，2026-07-31 ✓（Algolia API 核实标题/分数/评论数；评论文本抓取了几条高分段大意见"社区反响"，但 items API 不返回单条分数，未逐条核实）
- OpenClaw 定位：https://github.com/openclaw/openclaw 、https://openclaw.ai/ —— 开源个人 AI 助手、OpenClaw Foundation 非营利维护、接 20+ 平台 ✓（定位已核实，其内部架构未深读）
- enterprisedna.co、valueaddvc.com、explainx.ai、yeyupiaoling.cn 的解读 —— "覆盖会计/法务/活动/工程"等描述来自这批转述，**与一手 README 未逐部门列举的事实存在出入，需人工核实后再引用** ⚠️

**未能获取 / 需人工核实**：
- 官方无任何成本/定价数据；每员工常驻 sandbox 的云账单量级 ⚠️ 估算，未核实
- "QM 在 YC 内部实际跑会计/法务/活动/工程"的一手确认 ⚠️ 未核实
- webhook 的完整公开接入形态：src/api/routes/ 下无独立 webhook 路由文件，webhook 以 BackgroundWakeTrigger 类型（src/types.ts）+ deployment 配置（docs/deploy-directory.md 的 surface:"webhook"/origin:"automation"）+ admin origins 标签（"Webhook monologue"）形式存在，具体如何从外部打到系统 ⚠️ 未能逐行核实
- HN 评论的完整逐条内容与分数、"Buzz" 竞品具体指谁 ⚠️ 未核实
- OpenClaw 的内部架构/与 QM 的差异 ⚠️ 未深读（仅核实定位）
