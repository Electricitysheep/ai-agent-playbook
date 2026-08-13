# 主 Master 编排 Agent 提示词 v2（带确切 Orca 命令）

> 用法：整段复制给主 master 的 agent（opencode/omp 均可）。本版**内嵌全部 orca 命令**，
> 编排 agent 只做参数替换和结果收集，不再需要自行推断如何调用 Orca。

---

```
# 任务：用 Orca 编排 4 个并行调研 Agent

你是编排 agent。用下面的**确切命令**为 4 个方向各建一个 Orca worktree、
各派一个 agent 做深度调研、收集结果、汇总归档。全程用 Windows 侧的
orca CLI（不要用 Git Bash 之外的猜测）。

## 0. 前置：定位 orca CLI

在 Windows 侧执行（Git Bash 里）：
```
ORCA="/c/Users/24835/AppData/Local/Programs/Orca/resources/bin/orca"
"$ORCA" status --json
```
确认 ok=true 后再继续。若失败，报告错误并停止，不要换工具。

## 1. 先读输入材料（用 Read 工具）

- 任务包：`C:/Users/24835/实习积累知识集合/02_AI工程/01_Agent智能体/20260812_Agent-to-Agent调研任务包_4方向.md`
- 背景报告：`C:/Users/24835/实习积累知识集合/02_AI工程/01_Agent智能体/20260812_主流Agent的Agent-to-Agent能力对比调研报告.md`

任务包里已有【方向 A/B/C/D】四个完整 prompt。你的工作是分发它们，不重写。

## 2. 为 4 个方向各建一个 Orca worktree（用确切命令）

对每个方向执行（把 <TASK_NAME> 和 <PROMPT_FILE> 换成实际值）：

```
ORCA="/c/Users/24835/AppData/Local/Programs/Orca/resources/bin/orca"
"$ORCA" worktree create \
  --repo id:4e74899b-c396-4952-8159-9b05f6ba6839 \
  --name <TASK_NAME> \
  --no-parent \
  --agent <AGENT_ID> \
  --prompt "<该方向的完整 prompt 文本>" \
  --json
```

4 个方向的参数表（**AGENT_ID 默认用 `opencode`**——已实测可用；
如果某个 id 报错，用 terminal create + send 的两步法替代）：

| 方向 | TASK_NAME | AGENT_ID | 调研内容 |
|---|---|---|---|
| A | agent2a-claude-teams | opencode | Claude Code Agent Teams + Dynamic Workflows |
| B | agent2a-omp-hub | opencode | omp hub + task 工具 |
| C | agent2a-devin | opencode | Devin Managed Devins |
| D | agent2a-a2a | opencode | A2A 协议 + prime-agent 接入 |

> 命令执行要点（来自 orca-cli 官方指南）：
> - `--no-parent` 表示独立顶层任务，不要基于当前分支
> - `--agent` 在 worktree 首个终端启动 agent；`--prompt` 发送初始任务
> - `--agent` 单独使用会**保持在后台**，不会阻塞你的编排流程
> - 如果 `--agent` 参数报错，用两步法：
>   ```
>   "$ORCA" worktree create --repo id:4e74899b-... --name <TASK_NAME> --no-parent --json
>   "$ORCA" terminal create --worktree <返回的完整worktreeId> --command "<agent命令>" --json
>   "$ORCA" terminal send --terminal <handle> --text "<prompt>" --enter --json
>   ```
> - 每个 worktree 的 id 是 `<repoId>::<worktreePath>` 完整值，不要截断

## 3. 子 agent 的 prompt 来源

每个方向的完整 prompt 就在任务包里（含一手来源清单 + 专属问题 + 输出要求）。
把对应方向的 prompt 原文作为 `--prompt` 的值传进去。
子 agent 的产出要求：报告写到该 worktree 根目录 `report.md`，中文，≥10 一手来源。

## 4. 收集结果（4 个都建完后）

用 `"$ORCA" worktree list --json` 和 `"$ORCA" terminal list --json` 查看各
worktree 状态。全部完成后，用 Read 读取 4 份 report.md。

## 5. 汇总 + 归档

1. 汇总成综合结论报告：
   - 4 个方向要点提炼（每个 5-8 条）
   - 跨方向对比：谁最接近 prime-agent？谁最值得借鉴？
   - "该借鉴/该避免"总清单
   - 对 prime-agent 未来方向的判断（是否接 A2A / 借鉴 Claude Teams / 学习 Devin）
2. 归档到：`C:/Users/24835/实习积累知识集合/02_AI工程/01_Agent智能体/20260812_Agent-to-Agent调研_综合结论.md`
   遵循知识库格式：费曼门槛（5 行）置顶 + 原始资料清单
3. 在 `C:/Users/24835/实习积累知识集合/00_INDEX.md` 变更日志加一行（参照 v2.9 格式）

## 6. 验收标准

- [ ] 4 个 worktree 各有一份 report.md，来源可追溯（≥10 一手来源/方向）
- [ ] 综合结论已归档，含跨方向对比 + 借鉴清单
- [ ] 00_INDEX.md 已更新
- [ ] 4 个方向并行执行（不是串行等待）

## 7. 约束

- 不要重写任务包里的 prompt——原样分发
- 不要用 `orca orchestration task-create`（那是协调者跟踪状态，不适合本任务）
- 子 agent 报告必须中文，含可信度标注
- 完成后报告：4 个 worktree 的产出路径 + 综合报告路径
```
