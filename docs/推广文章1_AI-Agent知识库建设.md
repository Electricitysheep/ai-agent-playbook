# 我如何用 8 个月构建一个 AI Agent × 量化知识库（106 篇笔记 + 16 个可运行实验）

> 首发建议：知乎专栏 → 掘金 → V2EX（提炼版）。文末链接已埋点。

---

## 从"收藏夹"到"弹药库"

8 个月前，我的 AI 学习方式是刷到好文章就扔进收藏夹。结果收藏了 300+ 篇，真用起来的不到 10 篇。

转折点是我开始实习做 AI 智能体开发。每天被 LangChain、RAG、Agent 架构淹没，我发现**收藏夹的尽头是焦虑，笔记的尽头才是能力**。

于是我把所有收藏拆解、重写、验证，变成了一套自己的知识库——**ai-agent-playbook**。

## 三个核心发现

### 1. Agent 源码拆解比看文档有用得多

市面上 90% 的 AI Agent 教程在讲概念，但真正理解一个 Agent，必须看它怎么工作。

我做了一批**源码级深挖**：
- **Claude Code Agent Teams**：邮箱 + flock 的消息机制、权限委托链路、headless 投递缺陷——全部来自本机二进制逆向
- **Devin 多 Agent 架构**：manager 经 MCP server 注入消息、child 间拓扑禁通信、三层权限模型
- **omp hub IPC 并发模型**：进程内 IrcBus + 跨进程 daemon broker 的三层结构

每篇调研都标注**证据来源分级**（官方文档 / 社区逆向 / 本机实测），拒绝二手转述。这是个人笔记库做不到的。

### 2. A2A 协议还在早期，但值得提前布局

我调研了 14 家主流 AI agent 的 Agent-to-Agent 能力，核心结论：

- "多 agent 并行"是主流标配（Claude/Codex/Kimi/Cursor 都有）
- 但 **"agent 间直接互发消息"只有 4 家支持**（prime-agent、Claude Code Agent Teams、Devin、omp）
- 大部分是 hub-and-spoke 编排模式
- A2A 标准协议已有 100+ 企业采用，但 Claude/Codex 均未原生实现

这意味着什么？**多 agent 协作是下一个爆发点，而现在布局的人很少。**

### 3. AI × 量化是几乎没人做的交叉点

我在量化金融方向做了全链路实践：LLM 因子挖掘 → 时序模型选型 → RL 最优执行 → 回测纪律 → 生产风控。

产出了 **16 个可运行代码实验**：
- LLM 因子三道检验管道（IC/ICIR/互补性）
- walk-forward 完整实现
- 生产风控叠加层模拟器
- 多因子合成

每个实验一个 `main.py` + 说明文档，clone 下来就能跑。

## 这套知识库的独特之处

| 维度 | 一般学习笔记 | ai-agent-playbook |
|------|------------|-------------------|
| 内容 | 收藏+摘抄 | 原创深度调研（源码级） |
| 证据 | 无来源 | 三层证据分级标注 |
| 可执行 | 纯文字 | 16 个可运行代码实验 |
| 更新 | 看心情 | 每周新增调研笔记 |
| 使用 | 只读 | Obsidian 库，克隆即用 |

## 开源邀请

我已经把整个知识库开源在 GitHub，**Obsidian 克隆即用**：

👉 **https://github.com/Electricitysheep/ai-agent-playbook**

如果你在学 AI Agent 或对 AI × 量化感兴趣，欢迎：
- ⭐ **Star**（让更多人看到）
- 📝 **提 Issue**（指出错误 or 建议新方向）
- 🤝 **PR 共建**（贡献你的笔记）

**Star 数会直接决定这套知识库能走多远——你的一个 star，就是它前进的动力。**

---

*本文由知识库内容提炼，原文见：[Agent-to-Agent 能力对比调研](https://github.com/Electricitysheep/ai-agent-playbook) | [AI×量化前沿笔记](https://github.com/Electricitysheep/ai-agent-playbook)*
