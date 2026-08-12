# 实验 04：TradingAgents 源码走读 + 辩论路由逻辑可运行模拟

> 对应主题：`02_主题深度笔记/04_多智能体交易框架源码精读.md`
> 源码：TauricResearch/TradingAgents（GitHub, 96.8k stars, Apache-2.0），clone 于 2026-08-09
> 论文：arXiv 2412.20138（Xiao/Sun/Luo/Wang）
> 运行日期：2026-08-09 ｜ 状态：✅ 运行成功

## 目的

1. 源码走读：TradingAgents 五阶段管线（分析师→牛熊辩论→Trader→风险辩论→PM）的真实实现
2. 逐行复刻 `conditional_logic.py` 的辩论路由逻辑，用 stub LLM 跑通全管线
3. 验证路由轮次与真实源码一致，提炼可面试的工程结论

## 运行环境

- Windows + Python 3.14（零外部依赖，stub LLM 模拟，不调真实 API）
- 运行命令：`python main.py`（秒级）

## 源码走读要点（真实源码，2026-08-09 clone）

| 模块 | 路径 | 职责 |
|---|---|---|
| 主图 | `tradingagents/graph/trading_graph.py` | TradingAgentsGraph：LLM 初始化（deep/quick 双模型）、ToolNode 工具分配、checkpoint、memory log |
| 图组装 | `tradingagents/graph/setup.py` | LangGraph StateGraph：13+ 节点、条件边（analyst→tools 循环、辩论轮次路由） |
| 路由逻辑 | `tradingagents/graph/conditional_logic.py` | 辩论/风险辩论轮次控制（本实验逐行复刻） |
| 状态传播 | `tradingagents/graph/propagation.py` | 初始状态（InvestDebateState/RiskDebateState 结构化） |
| 分析师 | `tradingagents/agents/analysts/` | market/social/news/fundamentals 四角色，ReAct 提示 + ToolNode |
| 牛熊研究者 | `tradingagents/agents/researchers/` | bull/bear 辩论节点，读共享状态写辩论历史 |
| 研究经理 | `tradingagents/agents/managers/research_manager.py` | 结构化输出 ResearchPlan（五档评级） |
| Trader | `tradingagents/agents/trader/trader.py` | 结构化输出 TraderProposal（买/卖/持有+头寸） |
| 风险三辩 | `tradingagents/agents/risk_mgmt/` | Aggressive/Neutral/Conservative 三角色 |
| PM | `tradingagents/agents/managers/portfolio_manager.py` | 结构化输出 PortfolioDecision，注入 past_context（记忆） |
| 信号解析 | `tradingagents/graph/signal_processing.py` | parse_rating 正则提取评级，无第二次 LLM 调用 |

## 模拟结果（2026-08-09 运行）

```
[阶段 2] 牛熊辩论顺序: Bull → Bear → Bull → Bear（count=4 = 2×max_debate_rounds ✓）
[阶段 4] 风险辩论顺序: Aggressive → Conservative → Neutral（count=3 = 3×max_risk_discuss_rounds ✓）
[阶段 5] PM 最终决策: Hold（从结构化输出解析）
```

路由逻辑验证：`should_continue_debate`（count≥2×N→Research Manager；current_response 前缀切换
Bull/Bear）与 `should_continue_risk_analysis`（count≥3×N→PM；latest_speaker 前缀轮换三角色）——
均与真实源码逐行一致。

## 关键工程结论

1. **结构化文档通信为主、自然语言辩论为辅**：分析报告/TraderProposal/PortfolioDecision 都是
   Pydantic schema 绑定的结构化输出，避免上下文膨胀与信息稀释（论文核心设计）。
2. **双 LLM 配置**：deep_think_llm（复杂推理：研究经理/PM）vs quick_think_llm（数据检索：分析师）。
3. **记忆与反思**：TradingMemoryLog 持久化决策日志，下次同 ticker 运行注入 past_context
   （含上次实现收益与反思）——跨轮学习的工程实现。
4. **生产健壮性**（v0.2.4+）：LangGraph checkpoint 断点续跑、resolve_instrument_identity
   防公司身份幻觉、ticker path-traversal 加固、Windows UTF-8 修复。
5. **局限**：stub LLM 不产生真实推理；官方明确"回测结果不可复现、非投资建议"——
   该框架是研究脚手架，不是可上线策略。

## 文件清单

- `main.py`：五阶段管线模拟（逐行复刻路由逻辑 + stub LLM）
- 源码 clone 位于 `C:\Users\24835\AppData\Local\Temp\opencode\ta_src`（可删除）
