# -*- coding: utf-8 -*-
"""
实验 15：组合优化 —— 均值方差 / 风险平价 / 最大分散度对比
=================================================================
用真实 A 股收益数据比较三种组合权重方法（面试高频"组合权重怎么定"）：

1) 均值方差 (Mean-Variance, Markowitz)：最大化 Sharpe（有约束优化）
2) 风险平价 (Risk Parity)：各资产贡献相同风险（迭代求解）
3) 等权重 (Equal Weight)：简单基线

评估：
- 三种方法的权重分布特征（集中度/多样性）
- 样本外表现（滚动窗口：每期用历史估计参数 → OOS 一期）
- 关键认知：均值方差对参数估计误差敏感（"估计误差最大化器"），
  风险平价更稳健——行业共识（Bridgewater 全天候的简化版思想）

数据：baostock 缓存（复用实验 14 的 296 只 → 取 10 只代表性股票做资产池）
运行: python main.py
环境: Python 3.14 / scipy / numpy / pandas
"""

import sys
import warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
EST_WINDOW = 120     # 参数估计窗口（交易日）
OOS_STEP = 20        # 每次滚动 OOS 长度


def load_returns():
    """从实验 14 缓存加载 close，按行业多样性选 10 只资产池。"""
    cache = os.path.join(os.path.dirname(OUT_DIR), "14_全市场因子检验_baostock300", "data_cache.pkl")
    if not os.path.exists(cache):
        raise FileNotFoundError(f"缺少实验 14 缓存 {cache}——先运行实验 14")
    d = pd.read_pickle(cache)
    close, industry = d["close"], d["industry"]
    # 按行业分组，每组选 1 只（覆盖 10 个不同行业，保证资产多样性）
    ind_map = industry.reindex(close.columns).dropna()
    picked = []
    seen = set()
    for code in ind_map.index:
        ind = ind_map[code]
        if ind not in seen:
            seen.add(ind)
            picked.append(code)
        if len(picked) >= 10:
            break
    if len(picked) < 5:
        raise RuntimeError(f"行业覆盖不足: {len(picked)}")
    print(f"[数据] 复用实验 14 缓存，按行业多样性选 {len(picked)} 只资产:")
    for c in picked:
        print(f"    {c} ({ind_map[c]})")
    ret = close[picked].pct_change().dropna()
    return ret


def mean_variance_weights(exp_ret, cov, risk_free=0.0):
    """最大化 Sharpe 的均值方差组合（权重非负、和为 1）。"""
    n = len(exp_ret)
    inv_cov = np.linalg.pinv(cov)

    def neg_sharpe(w):
        r = w @ exp_ret
        vol = np.sqrt(w @ cov @ w)
        return -(r - risk_free) / vol if vol > 0 else 1e6

    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    bounds = [(0, 1)] * n
    res = minimize(neg_sharpe, np.ones(n) / n, method="SLSQP",
                   bounds=bounds, constraints=cons,
                   options={"maxiter": 200, "ftol": 1e-9})
    if res.success:
        return res.x
    return np.ones(n) / n


def risk_parity_weights(cov, max_iter=100):
    """风险平价：各资产风险贡献相等（使用迭代求解）。
    参考：Spinu (2013) 风险平价唯一解。"""
    n = len(cov)
    x = np.ones(n) / n
    for _ in range(max_iter):
        vol = np.sqrt(x @ cov @ x)
        mrc = (cov @ x) / vol          # 边际风险贡献
        rc = x * mrc                   # 风险贡献
        target = rc.mean()
        new_x = np.clip(x * (target / np.maximum(rc, 1e-12)), 1e-6, None)
        new_x = new_x / new_x.sum()
        if np.max(np.abs(new_x - x)) < 1e-6:
            return new_x
        x = new_x
    return x


def portfolio_stats(weights, ret):
    """组合收益序列的年化收益/波动/Sharpe。"""
    w = np.asarray(weights, dtype=float)
    p = ret @ w
    ann_ret = (1 + p).prod() ** (252 / len(p)) - 1
    ann_vol = p.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    return ann_ret, ann_vol, sharpe


def main():
    ret = load_returns()
    n_assets = ret.shape[1]
    print(f"[收益] {ret.shape[0]} 天 × {n_assets} 资产")

    # ---- 静态比较：用全样本估计参数，看三种方法的权重特征 ----
    print("\n" + "=" * 78)
    print("静态比较（全样本估计参数 → 三种权重）")
    print("=" * 78)
    exp_ret = ret.mean() * 252
    cov = ret.cov() * 252
    w_mv = mean_variance_weights(exp_ret, cov)
    w_rp = risk_parity_weights(cov)
    w_ew = np.ones(n_assets) / n_assets

    for name, w in [("均值方差", np.asarray(w_mv, dtype=float)),
                    ("风险平价", np.asarray(w_rp, dtype=float)),
                    ("等权", np.asarray(w_ew, dtype=float))]:
        ann_ret, ann_vol, sharpe = portfolio_stats(w, ret)
        top3 = np.argsort(w)[-3:][::-1]
        hhi = (w ** 2).sum()
        print(f"  {name:<6} 年化 {ann_ret:>7.2%} | 波动 {ann_vol:>6.2%} | Sharpe {sharpe:>5.2f} "
              f"| HHI {hhi:.3f} | Top3 权重 {w[top3[0]]:.2f}/{w[top3[1]]:.2f}/{w[top3[2]]:.2f}")

    # ---- 滚动 OOS：每期用估计窗口求权重 → 下一段 OOS 评估 ----
    print("\n" + "=" * 78)
    print("滚动样本外评估（每期估计参数 → OOS 一期，参数只含历史信息）")
    print("=" * 78)
    n_total = len(ret)
    results = {"mv": [], "rp": [], "ew": []}
    for start in range(0, n_total - EST_WINDOW - OOS_STEP + 1, OOS_STEP):
        est = ret.iloc[start:start + EST_WINDOW]
        oos = ret.iloc[start + EST_WINDOW:start + EST_WINDOW + OOS_STEP]
        if len(oos) < 10:
            break
        er = est.mean() * 252
        cv = est.cov() * 252
        w_mv_r = mean_variance_weights(er, cv)
        w_rp_r = risk_parity_weights(cv)
        w_ew_r = np.ones(n_assets) / n_assets
        results["mv"].append(oos @ w_mv_r)
        results["rp"].append(oos @ w_rp_r)
        results["ew"].append(oos @ w_ew_r)

    print(f"  {'方法':<8} {'年化收益':>9} {'年化波动':>9} {'Sharpe':>7} {'最大回撤':>9}")
    for name in ["mv", "rp", "ew"]:
        p = pd.concat([pd.Series(x) for x in results[name]])
        ann_ret = (1 + p).prod() ** (252 / len(p)) - 1
        ann_vol = p.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
        cum = (1 + p).cumprod()
        mdd = (cum / cum.cummax() - 1).min()
        label = {"mv": "均值方差", "rp": "风险平价", "ew": "等权"}[name]
        print(f"  {label:<8} {ann_ret:>8.2%} {ann_vol:>8.2%} {sharpe:>7.2f} {mdd:>8.2%}")

    print("\n" + "=" * 78)
    print("结论（面试要点）")
    print("=" * 78)
    print("""
1. 均值方差：理论最优但"估计误差最大化器"——对 μ 和 Σ 的估计极敏感，
   静态全样本下常给出极端权重（高 HHI）；滚动 OOS 常因估计噪声表现不稳。
2. 风险平价：不依赖收益预测（只用协方差），权重更分散（低 HHI），
   样本外更稳健——Bridgewater 全天候策略的核心思想（风险贡献均衡）。
3. 等权：简单但常常"难以被击败"（DeMiguel et al. 2009：1/N 策略）——
   在参数估计噪声大时，等权是最难被复杂方法稳定超越的基线。
4. 工程要点：真实生产中权重计算只用历史信息（滚动估计），
   且需叠加组合级风控（行业/因子暴露，见实验 10 的 RiskGate）。
5. 局限：10 资产小池 + 简单实现（无收缩估计/BL 先验）；演示方法对比非投资建议。
""")
    pd.to_pickle({"w_mv": w_mv, "w_rp": w_rp, "w_ew": w_ew},
                 os.path.join(OUT_DIR, "result.pkl"))
    print("[完成] 结果已存 result.pkl")


if __name__ == "__main__":
    main()
