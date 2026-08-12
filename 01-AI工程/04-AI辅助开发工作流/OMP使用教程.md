# omp (Oh My Pi) 使用教程

> 基于你机器的实际安装状态编写：omp v16.4.6（bun 全局包），已登录 Google Antigravity + OpenCode Go 两个 OAuth 源。
> 更新日期：2026-07-12

## 1. omp 在你工作流里的定位

omp 是终端 AI 编码代理（类似 Claude Code），在你的三车道体系里承担**廉价/免费池车道**：

| 车道 | 工具 | 额度来源 |
|---|---|---|
| 主力 | Claude Code（官方） | Claude Pro（**只在官方 CLI 用**，防封号红线） |
| 免费池 | **omp** | Antigravity 日配额（Google/Anthropic/OpenAI 三池）+ OpenCode Go（$12/5h、$30/周、$60/月） |
| 批量并行 | opencode + oh-my-openagent | OpenCode Go + 百炼 |

**红线提醒**：不要在 omp 里 `/login anthropic` 登录你的 Claude Pro 账号。要用 Claude 系模型，走 Antigravity 池（`omp usage` 里的 "Usage (Anthropic)" 那一条就是它，和你的 Claude Pro 账号无关）。

## 2. 账号与配额（你已完成登录）

```bash
omp usage                    # 全部账号限额总览（你目前两池都是 0% 使用）
omp usage -p anthropic       # 只看某个 provider
omp usage --history -d 7     # 最近 7 天的小时级用量快照
omp stats                    # 本地使用统计
```

当前状态：Antigravity 三池（OpenAI/Google/Anthropic）每日重置、全部闲置；OpenCode Go 月度仅用 $0.09/$60。

## 3. 日常使用

### 启动

```bash
omp                          # 交互式 TUI
omp "重构这个函数"            # 带初始提示启动
omp @notes.md @shot.png "解释这段" # @ 前缀附加文件/图片
omp -p "列出 src 下所有 .ts"  # 非交互：执行完退出（适合脚本）
```

**注意**：在家目录 `~` 直接启动会被自动切到临时目录（你 sessions 里那条 `--C--tmp--` 就是这么来的）。**在项目目录里启动**，或加 `--allow-home`。会话按启动目录关联，换目录后 `-c` 找不到之前的会话。

### 模型切换

```bash
omp --model opus             # 模糊匹配模型名
omp --model gemini-3-pro
```

- TUI 内：`/model` 面板选择；`Ctrl+P` 在模型间循环（可用 `--models claude-sonnet,deepseek` 限定循环列表）
- 你的模型分层（2026-07-12 两轮 bench + 使用习惯校准后定稿，全部走 Antigravity 池）：
  - `default`: gemini-3.5-flash（日常主力，1.2s 起答/207 TPS——default 角色是高频短交互，延迟优先；比原来的 ds-v4-flash 快 2.5 倍且不花钱池）
  - `smol`: gemini-3.5-flash（与 default 同款，无所谓）
  - `slow`: claude-opus-4-6（深度推理——Claude 池只有 Google 池约 1/30 大小，专门留给刀刃）
  - `plan`: gemini-3.1-pro:high（1M 上下文规划；3.1-pro 必须带 :low/:high 思考档，否则报 Budget 0 错误）
  - 复杂编码任务临时升档：`Ctrl+P` 或 `/model` 切 gemini-3.1-pro:low（112 TPS，首 token 约 6s）
  - OpenCode Go 池（kimi-k2.7-code/minimax-m3/deepseek 等）留给批量并行和超长输出，手动 `--model` 调用
- 思考等级：`--thinking off|low|medium|high|max|auto`（你配置为 auto）

### 会话管理

```bash
omp -c                       # 继续本目录最近一次会话
omp -c "接着上次继续"
omp -r                       # 弹出会话选择器
omp -r <ID前缀>              # 直接恢复指定会话
omp --no-session             # 临时会话，不落盘
omp --export <session.jsonl> # 会话导出为 HTML（可分享）
```

会话文件在 `~/.omp/agent/sessions/`。

## 4. 值得用的特色功能

- **`/review`** — 并行审查员做代码审查，P0-P3 分级（配合你的 PR 工作流）
- **子代理** — 并行隔离任务，返回结构化结果；`omp agents` 管理
- **`--advisor`** — 第二个模型旁观每一步并注入提醒（重要改动时开）
- **`/collab view`** — 生成只读浏览器链接，把会话实时分享给别人看
- **网页搜索** — 你已配置 `webSearch: gemini`；`omp search` 可测试搜索链
- **`omp commit`** — 生成提交信息 + 更新 changelog
- **`omp bench`** — 同一提示对比多个模型的首 token 延迟和吞吐（选默认模型前跑一次很值）
- **`omp worktree`** — 管理 agent 自建的 git worktree（`~/.omp/wt`）
- **`omp models`** — 列出/搜索全部可用模型
- **LSP + DAP** — 内置 IDE 级重命名/诊断/符号导航，原生调试器驱动（lldb/dlv/debugpy），Windows 原生无需 WSL

## 5. 配置

| 文件 | 用途 | 你的现状 |
|---|---|---|
| `~/.omp/agent/config.yml` | 主配置（modelRoles、theme、webSearch） | 四角色 Antigravity 分层（备份在 config.yml.bak-20260712） |
| `~/.omp/agent/mcp.json` | MCP 服务器 | 空（禁用了 zai-mcp-server、chrome-devtools） |
| `~/.omp/agent/models.yml` | 自定义 provider / 回退链 | 未创建 |
| `~/.omp/agent/sessions/` | 会话存储 | 基本为空 |

omp 会**自动继承** `.claude/`、`.cursor/`、`AGENTS.md` 等 8 种现有配置格式的规则/技能/MCP 定义——你在 Claude Code 里积累的 skills 和规则大多不用迁移。

模型角色分层（建议按第 6 节优化）：

```bash
omp --smol <快模型> --slow <推理模型> --plan <规划模型>
# 或写进 config.yml 的 modelRoles: {default, smol, slow, plan}
```

### 多配置隔离

```bash
omp --profile work --alias omp-work   # 建独立 profile 并生成 shell 快捷命令
```

auth、会话、设置、缓存全部隔离——适合把"个人实验"和"正式项目"分开。

## 6. 速查表

| 想做什么 | 命令 |
|---|---|
| 看全部账号配额 | `omp usage` |
| 续上次会话 | `omp -c` |
| 挑历史会话 | `omp -r` |
| 换模型 | `/model` 或 `Ctrl+P` 或 `--model xx` |
| 代码审查 | `/review` |
| 升级 | `omp update` |
| 测速对比模型 | `omp bench` |
| 生成 commit | `omp commit` |
| 清理存储 | `omp gc` |
