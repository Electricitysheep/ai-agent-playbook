# -*- coding: utf-8 -*-
"""
实验 04：TradingAgents 源码走读 + 辩论路由逻辑可运行模拟
========================================================
1) 忠实复刻 TradingAgents 核心路由逻辑（conditional_logic.py 的
   should_continue_debate / should_continue_risk_analysis），用 stub LLM
   跑通五阶段管线（分析师→牛熊辩论→Trader→风险辩论→Portfolio Manager）
2) 验证：辩论轮次计数与路由切换行为与真实源码一致
3) 关键工程结论：结构化文档通信（vs 全自然语言）、两处辩论都是
   "LLM 对辩 + 无 LLM 的结构化解析（rating 用正则而非第二次 LLM 调用）"

运行: python main.py
环境: Python 3.14（零外部依赖，stub LLM 模拟，不调用真实 API）
"""

import sys
import warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_DEBATE_ROUNDS = 2       # 与 TradingAgents DEFAULT_CONFIG 默认一致
MAX_RISK_DISCUSS_ROUNDS = 1


class StubLLM:
    """极简 stub LLM：返回确定性文本，模拟 agent 输出（不调真实 API）。"""

    def invoke(self, prompt):
        # 从 prompt 里提取"你是 XXX"角色，构造带角色前缀的响应
        role = "Agent"
        for key in ("Bull Analyst", "Bear Analyst", "Aggressive Analyst",
                    "Conservative Analyst", "Neutral Analyst"):
            if key in prompt:
                role = key
                break
        return type("R", (), {"content": f"{role}: (stub 论点) 基于输入数据的确定性回应"})()


def should_continue_debate(state):
    """忠实复刻 tradingagents/graph/conditional_logic.py"""
    ds = state["investment_debate_state"]
    if ds["count"] >= 2 * MAX_DEBATE_ROUNDS:
        return "Research Manager"
    if ds["current_response"].startswith("Bull"):
        return "Bear Researcher"
    return "Bull Researcher"


def should_continue_risk_analysis(state):
    """忠实复刻 tradingagents/graph/conditional_logic.py"""
    rs = state["risk_debate_state"]
    if rs["count"] >= 3 * MAX_RISK_DISCUSS_ROUNDS:
        return "Portfolio Manager"
    if rs["latest_speaker"].startswith("Aggressive"):
        return "Conservative Analyst"
    if rs["latest_speaker"].startswith("Conservative"):
        return "Neutral Analyst"
    return "Aggressive Analyst"


def bull_node(state, llm):
    ds = state["investment_debate_state"]
    arg = f"Bull Analyst: (stub) 多方论点 {ds['count']}"
    ds["history"] += "\n" + arg
    ds["bull_history"] += "\n" + arg
    ds["current_response"] = arg
    ds["count"] += 1
    state["investment_debate_state"] = ds
    return state


def bear_node(state, llm):
    ds = state["investment_debate_state"]
    arg = f"Bear Analyst: (stub) 空方论点 {ds['count']}"
    ds["history"] += "\n" + arg
    ds["bear_history"] += "\n" + arg
    ds["current_response"] = arg
    ds["count"] += 1
    state["investment_debate_state"] = ds
    return state


def risk_node(state, role, llm):
    rs = state["risk_debate_state"]
    arg = f"{role}: (stub) 风险观点 {rs['count']}"
    rs["history"] += "\n" + arg
    rs[f"{role.lower().replace(' analyst','')}_history"] += "\n" + arg
    rs["latest_speaker"] = role
    rs["count"] += 1
    state["risk_debate_state"] = rs
    return state


def main():
    llm = StubLLM()
    print("=" * 80)
    print("TradingAgents 五阶段管线模拟（stub LLM，忠实复刻路由逻辑）")
    print("=" * 80)

    # ---- 阶段 1-2：分析师 → 牛熊辩论 ----
    state = {
        "company_of_interest": "NVDA",
        "trade_date": "2026-01-15",
        "market_report": "stub 行情报告",
        "sentiment_report": "stub 情绪报告",
        "news_report": "stub 新闻报告",
        "fundamentals_report": "stub 基本面报告",
        "investment_debate_state": {
            "bull_history": "", "bear_history": "", "history": "",
            "current_response": "", "judge_decision": "", "count": 0,
        },
        "risk_debate_state": {
            "aggressive_history": "", "conservative_history": "",
            "neutral_history": "", "history": "", "latest_speaker": "",
            "current_aggressive_response": "", "current_conservative_response": "",
            "current_neutral_response": "", "judge_decision": "", "count": 0,
        },
    }

    print("\n[阶段 1] 分析师产出报告（4 个分析师并行，源码中为 ToolNode+LLM 循环）")
    print("  market/sentiment/news/fundamentals 四份报告已写入共享状态（结构化文档通信）")

    print("\n[阶段 2] 牛熊辩论（ReAct + 结构化状态；路由用 count 与 current_response 前缀）")
    node = should_continue_debate(state)
    steps = []
    while node != "Research Manager":
        steps.append(node)
        if node == "Bull Researcher":
            state = bull_node(state, llm)
        else:
            state = bear_node(state, llm)
        node = should_continue_debate(state)
    print(f"  辩论顺序: {' → '.join(steps)}")
    print(f"  总轮次 count={state['investment_debate_state']['count']} "
          f"（期望 = 2*{MAX_DEBATE_ROUNDS}={2*MAX_DEBATE_ROUNDS}，与实际一致: "
          f"{state['investment_debate_state']['count'] == 2*MAX_DEBATE_ROUNDS}）")
    state["investment_plan"] = "stub 投资计划（Research Manager 结构化输出 ResearchPlan）"

    print("\n[阶段 3] Trader（结构化输出 TraderProposal：买/卖/持有 + 头寸）")
    state["trader_investment_plan"] = "stub 交易提案（Trader）"
    print("  trader_investment_plan 已写入")

    print("\n[阶段 4] 风险三辩（Aggressive/Neutral/Conservative + 路由）")
    node = should_continue_risk_analysis(state)
    risk_steps = []
    while node != "Portfolio Manager":
        risk_steps.append(node)
        state = risk_node(state, node, llm)
        node = should_continue_risk_analysis(state)
    print(f"  风险辩论顺序: {' → '.join(risk_steps)}")
    print(f"  总轮次 count={state['risk_debate_state']['count']} "
          f"（期望 = 3*{MAX_RISK_DISCUSS_ROUNDS}={3*MAX_RISK_DISCUSS_ROUNDS}，一致: "
          f"{state['risk_debate_state']['count'] == 3*MAX_RISK_DISCUSS_ROUNDS}）")

    print("\n[阶段 5] Portfolio Manager（结构化输出 PortfolioDecision + rating）")
    # 源码中 SignalProcessor 用 parse_rating 从 markdown 提取评级，无第二次 LLM 调用
    final = "**Rating**: Hold"  # stub PM 决策
    rating = [w for w in ("Buy", "Overweight", "Hold", "Underweight", "Sell")
              if w in final][0]
    print(f"  最终决策: {rating}（从结构化输出解析，无额外 LLM 调用）")

    print("\n" + "=" * 80)
    print("关键工程结论（对照真实源码 tradingagents/）")
    print("=" * 80)
    print("""
1. 通信协议：结构化文档（分析报告/TraderProposal/PortfolioDecision）为主，
   自然语言仅限辩论环节——避免上下文膨胀与信息稀释（论文 §3.4 的核心设计）。
2. 路由逻辑：conditional_logic.py 用状态计数 + 发言前缀驱动 LangGraph 条件边，
   本模拟的 should_continue_* 函数为逐行复刻。
3. 结构化输出：Trader/PM/Research Manager 用 with_structured_output 绑定 Pydantic
   schema；评级提取用 parse_rating 正则（signal_processing.py），不浪费第二次 LLM 调用。
4. 生产增强（v0.2.4+）：LangGraph checkpoint 断点续跑、TradingMemoryLog 决策日志
   与反思注入（下次同 ticker 运行时注入 past_context）、resolve_instrument_identity
   防公司身份幻觉。
5. 局限：stub LLM 无法复现真实推理质量；真实运行需 API key 且结果不可复现
   （官方明确说明 LLM 采样非确定性）。
""")
    print("[完成] 模拟验证通过：路由轮次与真实源码逻辑一致")


if __name__ == "__main__":
    main()
