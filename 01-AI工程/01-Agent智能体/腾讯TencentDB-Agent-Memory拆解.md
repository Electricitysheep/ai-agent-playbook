# 腾讯云 TencentDB Agent Memory 拆解

> 团队级 AI Agent 记忆中枢。把散落的上下文（对话、文档、代码）变成四类**可治理、可共享、可装载**的记忆资产。
> 上游仓库：<https://github.com/TencentCloud/TencentDB-Agent-Memory>（MIT，Node ≥ 22.16）
> 一句话定位：RAG 回答"能搜到什么"，Team Memory 还回答"谁能用、哪个版本有效、该装给哪个 Agent"。

---

## 0. 为什么值得关注(上榜理由)

大厂正式下场做 **Agent 记忆基建** 的信号。痛点是：项目上下文每次要重讲、文档每个 Agent 都要从头读、
跑通的工作流下回还要重新摸索。记忆 = "让下一个 Agent 避免重造轮子的一切信息"。

```text
已有信息 → 可复用记忆资产 → 更少轮次 → 更少返工 → 更稳定结果
```

## 1. 四大记忆资产

| 资产 | 来源 | 作用 |
| :--- | :--- | :--- |
| **Chat Memory** | 对话 | 保留偏好、事实、决策、交互历史；理解用户跨会话一致 |
| **Skill** | 对话/工具调用 | 可复用工作流，不只是 prompt，带版本、资源文件、触发边界、执行步骤、校验规则 |
| **LLM-Wiki** | 文档 | 产品文档/设计规格/运维手册 → 结构化页面 + 链接图（灵感来自 Karpathy 的 LLM-resta wiki） |
| **Code-Graph** | 代码 | 索引符号、文件、调用关系、影响路径；改码前可找 callers/callees 做影响分析 |

冷启动友好：已有代码库自动生成 CodeGraph；已有文档生成 Wiki；已有对话自动抽 Skill + Chat Memory。

## 2. 技术核心

### 2.1 分层记忆（不存扁平记录）

| 层 | 内容 | 用途 |
| :--- | :--- | :--- |
| **L0** 原始对话 | 带全上下文 | 核实原文/时间戳/来源 |
| **L1** Atom | 从对话抽的事实 | 精确检索可执行信息 |
| **L2** Scenario | 按项目/场景组织的知识块 | 一键恢复工作上下文 |
| **L3** Core/Persona | 长期画像、稳定模式 | Agent 快速进入用户/团队上下文 |

检索也分层：平时 L2/L3 做快速 bootstrap；查具体事实时才 BM25 + 向量 + RRF 回退到 L1/L0，
再用条数 / token 预算 / 超时封顶，防止记忆撑爆上下文窗口。

### 2.2 资产不是全局 prompt，是 Agent 的"装载"（loadout）

- 四类资产统一注册为 **Memory Asset**；Memory Hub 用 **Fixed Binding + ACL** 决定能装给谁。
- 权限先按 Team / User / Agent / 可见性收敛，再按当前 query 检索。
- 切 Agent / 换框架只 re-equip，不需重训。

### 2.3 知识不整段注入，按需调用

- Wiki / CodeGraph 先通过 `/v3/tools/list` 发现能力，再 `/v3/tools/call` 取相关页面 / 源码 / 影响路径。
- 文档与代码成为记忆的一部分，但只在真正需要时才进上下文。

### 2.4 可见性与治理

| 可见性 | 语义 |
| :--- | :--- |
| `private` | 仅 Owner（连团队管理员也读不到） |
| `team` | 团队成员可读，Owner / Admin 管理 |
| `restricted` | 按 ACL 精确到人 / 角色 / Agent |
| `agent` | 定向装载给同团队内指定 Agent |

默认 private，共享是显式动作非默认泄漏。

## 3. 架构与部署

- 组件：**MemoryCore**（记忆引擎）+ **MemoryPanel/MemoryHub**（管理面板）+ **MemoryProxy**（接入层）+ **sdk**。
- 默认存储：本地 `SQLite + sqlite-vec`；可选腾讯云向量库 TCVDB。
- 支持：OpenClaw、Hermes、Claude Code、CodeBuddy、SDK。
- 一键部署：`deploy/global-images/start-all.sh`（需配两组 LLM 参数：memory 组 + proxy 组），面板 `http://localhost:8125`。
- 邀请承认：CodeGraph 借鉴 colbymchenry/codegraph；Skill 借 Hermes Agent；Wiki 灵感来自 Karpathy 的 LLM wiki。

## 4. Benchmark

| | 无记忆 | 有记忆 | 相对提升 |
| :--- | :---: | :---: | :---: |
| **PersonaMem** | 48% | **76%** | **+59%** |

PersonaMem 测的是 Agent 在长会话交互后能否正确理解并应用用户画像。

## 5. 与我司知识库体系的借鉴(思考区)

- **分层意识**：把原始摘录 → 单点知识 → 专题笔记 → 个人知识画像分四层管理，面试时可讲"我的知识积累就是模仿 L0→L3"。
- **Wiki 化**：`00_INDEX.md` 可升级为带关联关系的知识链接图。
- **Skill 化**：把反复使用的工作流（调研流程 / 月报生成 / 费曼复盘）固化为可复用 Skill。
- **落地评估**：团队级设计 + 需配置 LLM key 与多服务，单人知识管理用 Markdown + 这套分层思想更合算。

## 6. 面试考点速查

- RAG vs Agent Memory（表驱动回答）
- 如何给 Agent 做长期记忆？
- 长期记忆怎么防上下文爆炸？
- 记忆的可见性 / 权限如何设计（Share vs Privacy 平衡）？
- 如何评估记忆质量？（BM25+向量+RRF、PersonaMem 指标思路）