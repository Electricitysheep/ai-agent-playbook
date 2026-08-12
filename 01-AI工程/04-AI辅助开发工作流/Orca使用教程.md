# Orca 使用教程

> 基于你机器的实际安装状态编写：Orca v1.4.135+，安装于 `C:\Users\24835\AppData\Local\Programs\Orca\Orca.exe`，主代理已选定 Claude Code 并自动挂好 hooks。
> 更新日期：2026-07-12

## 1. Orca 是什么、在你工作流里的定位

Orca（stablyai/orca）是**多 agent 编排驾驶舱**——一个桌面 GUI，让你在一个界面里并排跑多个终端编码 agent（Claude Code、Codex、Gemini CLI、omp 等 30+ 种），每个 agent 在**隔离的 git worktree** 里工作，互不踩脏。

你的定位：**驾驶舱**。Claude Code 是主代理，Orca 负责任务分发、并行对比、统一监控和订阅用量看板。

## 2. 你机器上已就绪的部分

- **Claude Code hooks 已挂**：`~/.claude/settings.json` 的 `UserPromptSubmit` / `Stop` / `StopFailure` 三个钩子指向 `~/.orca/agent-hooks/claude-hook.cmd`（超时 10s）——这是 Orca 感知 Claude Code 活动状态（运行中/完成/失败）的机制，**不要手动删**，否则 Orca 面板里看不到 Claude 的状态。
- **16 个 agent 钩子脚本就绪**：`~/.orca/agent-hooks/` 下有 claude / codex / gemini / antigravity / cursor / copilot / grok / kimi / droid / devin 等的 hook 脚本，接入新 agent 时 Orca 会自动使用。
- **数据目录**：`%APPDATA%\Orca\`（profiles、orchestration.db 编排数据库、claude-accounts、daemon 后台进程、E2EE 密钥对——移动端同步用）。

## 3. 核心概念

| 概念 | 含义 |
|---|---|
| **Worktree** | 每个任务/agent 一个隔离的 git 工作树，并行改代码不互相污染 |
| **Agent 线程** | 一个 agent 在一个 worktree 里的一次任务执行，有运行/完成/未读状态 |
| **编排** | 把同一个提示词同时分发给多个 agent，各自独立做，最后对比择优 |

## 4. 基本工作流

1. **打开仓库**：把你的项目（如 kairos）加入 Orca。
2. **创建任务**：写提示词 → 选 agent（默认 Claude Code）→ Orca 自动建 worktree 并启动 agent。
3. **并行对比**（Orca 的招牌玩法）：同一提示分发给最多 5 个 agent（比如 Claude Code + omp + Gemini），各自在自己的 worktree 里实现，完成后并排对比 diff，挑最好的合并。
4. **审查**：内嵌 diff 注释器，直接在改动上写反馈发回给 agent，不用切窗口。
5. **合并**：选中满意的 worktree 结果合入主分支。

## 5. 值得用的特色功能

- **用量监控**：面板显示 Claude / Codex 的订阅用量和限额重置时间——配合 `omp usage` 就是你的双看板。
- **Quick Open**：跨 worktree / 文件 / agent 全局搜索跳转。
- **Design Mode**：在内嵌 Chromium 窗口里点选页面元素，HTML/CSS/截图自动进提示词——调前端（如 workflow-designer）时特别顺手。
- **拖拽**：文件、图片直接拖进提示框。
- **通知 + 未读标记**：agent 完成任务弹通知；忙的时候标未读，回头处理。
- **终端分割**：内置终端支持无限分割、滚动历史持久化。
- **Computer Use**：允许 agent 操作桌面应用（谨慎开）。
- **移动同伴 App**：手机上监控/操控 agent（E2EE 密钥对就是为这个生成的）。

## 6. 与 Claude Code / omp 的分工建议

| 场景 | 用什么 |
|---|---|
| 深度单任务（架构改造、复杂修复） | Claude Code 直接干（Orca 里或终端里都行） |
| 不确定方案好坏 | Orca 并行分发：Claude Code + omp(Antigravity 池) 各做一版，对比 |
| 批量小任务、实验性尝试 | omp / opencode（免费池），Orca 统一监控 |
| 前端调样式 | Orca Design Mode + 任一 agent |

## 7. 注意事项

- Orca 的 hook 超时是 10 秒——如果你的 Claude Code 某天启动变慢，先检查是不是 hook 脚本卡住。
- `orchestration.db` 和 profiles 在 `%APPDATA%\Orca`，重装系统前备份这个目录即可保留全部任务历史。
- Worktree 会占磁盘：定期在 Orca 里清理已合并/废弃的 worktree（agent 侧的残留可用 `omp worktree` 和 `git worktree prune` 清）。
