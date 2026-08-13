# 🤖 Agent 智能体（源码级调研）

> ⭐ 本库最厚的核心板块：16 篇深度调研，全部标注**证据来源分级**（官方文档 / 社区逆向 / 本机实测）

## 调研地图

### A2A 协议与生态（2026-08 最新）

| 报告 | 核心结论 |
|------|---------|
| [主流 Agent 的 Agent-to-Agent 能力对比](./20260812_主流Agent的Agent-to-Agent能力对比调研报告.md) | 🏆 14 家对比：仅 4 家支持 agent 直接互发消息，大多数是 hub-and-spoke |
| [A2A 协议与 MCP-bridge 生态现状](./20260812_A2A协议与MCP-bridge生态现状_调研报告.md) | 核实 A2A 实为 v1.0.1（无 v1.2），Agent-DID 是未合并 PR |
| [Agent-to-Agent 调研综合结论](./20260812_Agent-to-Agent调研_综合结论.md) | 该借鉴（wait_any 竞态原语/身份不可伪造）与该避免（idle pings）清单 |

### 源码级架构拆解

| 报告 | 亮点 |
|------|------|
| [Claude Code Agent Teams 源码深挖](./20260812_ClaudeCode_AgentTeams与DynamicWorkflows_源码级深挖.md) | 🔬 三层证据：官方文档 + 社区逆向 + 本机二进制；邮箱+flock 机制、SendMessage 身份不可伪造 |
| [Devin 多 Agent 消息架构](./20260812_Devin多Agent消息架构与权限模型_调研报告.md) | manager 经 MCP server 注入消息、child 间拓扑禁通信、三层权限模型 |
| [omp hub IPC 并发模型深挖](./20260812_omp_hub与task工具IPC并发模型深挖_深度调研报告.md) | 三层 IPC：进程内 IrcBus + AsyncJobManager + 跨进程 daemon broker |
| [腾讯 TencentDB-Agent Memory 拆解](./腾讯TencentDB-Agent-Memory拆解.md) | 数据库 Agent 的记忆实现 |

### Harness 与自我进化

| 报告 | 亮点 |
|------|------|
| [LongHorizon-Harness 技术架构分析](./20260806_LongHorizon-Harness技术架构分析.md) | 高德 ML 的 long-horizon agent harness |
| [Agent 自我进化 Harness 深度检索](./20260806_Agent自我进化Harness深度检索报告.md) | 自我进化 agent 的架构模式 |
| [LongHorizon-Harness MEA 整合蓝图](./LongHorizon-Harness_MEA_自我进化整合蓝图_20260806.md) | 多智能体进化的设计蓝图 |

### 基础与课程

- [Coding Agents 101 阅读摘要](./Coding_Agents_101_阅读摘要.docx.md)
- [CS146S 斯坦福 AI 教学总结](./CS146S斯坦福大学ai教学总结.docx.md) + [详细学习](./CS146S课程内容详细学习.docx.md)
- [AI 代码评审技术指南](./AI代码评审技术指南-摘要笔记.docx.md)
- [AI 代码助手团队落地方案](./AI代码助手团队落地方案.docx.md)

---

## 推荐阅读路径

```
新手入口：Coding Agents 101 → CS146S
核心进阶：主流 Agent A2A 对比 → Claude Code 源码深挖 → Devin 架构
前沿追踪：A2A 协议现状 → LongHorizon-Harness → 自我进化 Harness
```

**证据分级说明**：每篇报告的结论都标注来源层级（L1 官方文档 / L2 社区逆向 / L3 本机实测），L3 为最高可信度。
