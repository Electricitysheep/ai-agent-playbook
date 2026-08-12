# -*- coding: utf-8 -*-
"""
实验 10：生产风控叠加层模拟器
=============================
把主题 11 的 risk_gate 扩展为完整的独立风控叠加层模拟器，验证核心工程原则：
"绝不让单个 LLM 幻觉直接 sizing 进组合"。

模拟场景（教学演示，非真实交易）：
1) 生成一个"LLM 信号生成器"：多数时候输出合理信号，偶尔输出"幻觉信号"
   （如"确信度 100%、建议满仓、无视一切约束"）——模拟 LLM 幻觉
2) 独立风控层逐信号检查：头寸/行业暴露/单笔限额/换手/熔断
3) 对比两条路径：
   a. 信号直连下单（无风控）——幻觉信号直接进组合
   b. 信号过风控叠加层——幻觉被拦截/降权
4) 输出：被拦截的幻觉信号数、组合风险指标对比

运行: python main.py
环境: Python 3.14 / numpy（零外部依赖）
"""

import sys
import warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import numpy as np

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(42)
N_STOCKS = 20
N_DAYS = 100
HALLUCINATION_RATE = 0.05   # 5% 幻觉信号率


class Portfolio:
    """组合状态：持仓 + 行业暴露 + 当日换手。"""

    def __init__(self, n_stocks=N_STOCKS):
        self.n_stocks = n_stocks
        self.positions = np.zeros(n_stocks)
        self.industry = RNG.integers(0, 5, n_stocks)
        self.daily_turnover = 0.0
        self.total_capital = 100_000_000.0

    def industry_exposure(self):
        tot = self.positions.sum()
        if tot == 0:
            return np.zeros(5)
        exp = np.zeros(5)
        for i in range(self.n_stocks):
            exp[self.industry[i]] += self.positions[i]
        return exp / tot


class RiskGate:
    """独立风控叠加层：只看约束，不看信号理由（与信号层完全解耦）。"""

    def __init__(self):
        self.constraints = {
            "max_position": 0.10,
            "max_industry": 0.30,
            "max_trade_value": 5_000_000,
            "max_turnover": 0.20,
        }
        self.reject_log = []

    def check(self, signal, portfolio, price):
        """返回 (通过?, 拒绝原因)。signal: {stock_idx, size_frac, confidence}"""
        reasons = []
        target_value = signal["size_frac"] * portfolio.total_capital
        if target_value > self.constraints["max_trade_value"]:
            reasons.append(f"单笔超限 {target_value/1e6:.1f}M")
        new_pos = portfolio.positions[signal["stock_idx"]] + target_value
        if new_pos / portfolio.total_capital > self.constraints["max_position"]:
            reasons.append(f"单只头寸超限 {new_pos/portfolio.total_capital:.1%}")
        tmp = portfolio.positions.copy()
        tmp[signal["stock_idx"]] += target_value
        exp = np.zeros(5)
        for i in range(portfolio.n_stocks):
            exp[portfolio.industry[i]] += tmp[i]
        if (exp / portfolio.total_capital).max() > self.constraints["max_industry"]:
            reasons.append(f"行业暴露超限 {(exp/portfolio.total_capital).max():.1%}")
        if portfolio.daily_turnover + target_value / portfolio.total_capital > self.constraints["max_turnover"]:
            reasons.append(f"换手超限 {portfolio.daily_turnover+target_value/portfolio.total_capital:.1%}")
        if reasons:
            self.reject_log.append(reasons)
            return False, reasons
        return True, []


def llm_signal_generator(day):
    """模拟 LLM 信号生成器：95% 合理信号，5% 幻觉信号。
    幻觉信号 = 确信度 100% + 目标仓位 50%（远超单笔 500 万限额，5000 万）。"""
    if RNG.random() < HALLUCINATION_RATE:
        stock = int(RNG.integers(0, N_STOCKS))
        return {"stock_idx": stock, "size_frac": 0.50, "confidence": 1.0,
                "is_hallucination": True}
    stock = int(RNG.integers(0, N_STOCKS))
    size = RNG.uniform(0.01, 0.03)
    return {"stock_idx": stock, "size_frac": size,
            "confidence": RNG.uniform(0.5, 0.9), "is_hallucination": False}


def simulate(with_risk_gate, seed=1):
    """跑 N_DAYS 天模拟。with_risk_gate=True 时信号过风控层。
    用独立 RNG（seed）保证两条路径生成完全相同的信号序列——公平对比。"""
    local_rng = np.random.default_rng(seed)
    global RNG
    RNG = local_rng
    pf = Portfolio()
    gate = RiskGate() if with_risk_gate else None
    hallucination_generated = 0
    hallucination_executed = 0
    rejected_hallucination = 0
    max_position_seen = 0.0
    for day in range(N_DAYS):
        pf.daily_turnover = 0.0
        n_signals = int(local_rng.integers(1, 4))
        for _ in range(n_signals):
            sig = llm_signal_generator(day)
            if sig["is_hallucination"]:
                hallucination_generated += 1
            if with_risk_gate:
                ok, _ = gate.check(sig, pf, 100.0)
                if not ok:
                    if sig["is_hallucination"]:
                        rejected_hallucination += 1
                    continue
            if sig["is_hallucination"]:
                hallucination_executed += 1
            target = sig["size_frac"] * pf.total_capital
            pf.positions[sig["stock_idx"]] += target
            pf.daily_turnover += sig["size_frac"]
            max_position_seen = max(max_position_seen,
                                    pf.positions.max() / pf.total_capital)
    return {"hallucination_generated": hallucination_generated,
            "hallucination_executed": hallucination_executed,
            "rejected_hallucination": rejected_hallucination,
            "max_position_seen": max_position_seen,
            "n_reject": len(gate.reject_log) if gate else 0}


def main():
    print("=" * 78)
    print("生产风控叠加层模拟器（LLM 幻觉拦截验证）")
    print("=" * 78)
    print(f"  参数: {N_STOCKS} 只股票 × {N_DAYS} 天 | 幻觉率 {HALLUCINATION_RATE:.0%}")
    print("  公平性: 两条路径用相同随机种子 → 生成完全相同的信号序列")

    no_risk = simulate(with_risk_gate=False, seed=1)
    with_risk = simulate(with_risk_gate=True, seed=1)

    print("\n" + "=" * 78)
    print("对比：信号直连下单（无风控） vs 信号过风控叠加层")
    print("=" * 78)
    print(f"  {'指标':<24} {'无风控':>12} {'有风控':>12}")
    print(f"  {'幻觉信号生成总数':<24} {no_risk['hallucination_generated']:>12} {with_risk['hallucination_generated']:>12}")
    print(f"  {'幻觉信号进入组合':<24} {no_risk['hallucination_executed']:>12} {with_risk['hallucination_executed']:>12}")
    print(f"  {'被风控拦截的幻觉':<24} {'—':>12} {with_risk['rejected_hallucination']:>12}")
    print(f"  {'组合最大单只头寸':<24} {no_risk['max_position_seen']:>10.1%} {with_risk['max_position_seen']:>10.1%}")
    print(f"  {'风控拒绝总次数':<24} {'—':>12} {with_risk['n_reject']:>12}")

    print("\n" + "=" * 78)
    print("结论")
    print("=" * 78)
    print(f"""
1. 无风控路径：{no_risk['hallucination_executed']} 个幻觉信号（各 5000 万，占净值 50%）直接进组合，
   最大单只头寸达 {no_risk['max_position_seen']:.1%}——单点风险敞口失控。
2. 有风控路径：幻觉信号 {with_risk['rejected_hallucination']}/{with_risk['hallucination_generated']} 被拦截，
   组合最大头寸被压在约束内（{with_risk['max_position_seen']:.1%} ≤ 10%）。
3. 工程原则验证：'绝不让单个 LLM 幻觉直接 sizing 进组合'——
   风控层不看信号理由（确信度 100% 也没用），只看约束。
4. 面试用法：此模拟演示'为什么独立风控是 LLM 进生产的必要条件'。
""")
    import json
    with open(os.path.join(OUT_DIR, "result.json"), "w", encoding="utf-8") as f:
        json.dump({"no_risk": no_risk, "with_risk": with_risk}, f, indent=2, ensure_ascii=False)
    print("[完成] 结果已存 result.json")


if __name__ == "__main__":
    main()
