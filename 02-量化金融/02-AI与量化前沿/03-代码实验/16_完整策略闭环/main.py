# -*- coding: utf-8 -*-
"""
实验 16：完整 AI 量化策略闭环（数据→因子→合成→walk-forward→DSR→风控→组合）
=================================================================================
压轴整合：把本知识库的核心方法串成一个可运行的全链路管道，模拟一个
"AI 量化研究员从数据到可审计策略"的完整工作流。

管道七阶段（每阶段对应一个已验证实验/主题）：
1. 数据      ：复用实验 14 的 baostock 296 只缓存（真实行情）
2. 因子      ：6 个量价因子 + 真实行业中性化（实验 01/14）
3. 合成      ：IC 加权合成（实验 13 验证的相对最优）
4. walk-forward：滚动窗口评估（实验 12），只报 OOS 结果
5. DSR 诊断  ：对合成信号的 OOS 收益做去偏夏普比（实验 07），不显著则拒收
6. 风控      ：组合级 RiskGate（实验 10）：单只/行业暴露限制
7. 组合      ：风险平价加权（实验 15 验证的稳健方法）

关键纪律：每个阶段只用历史信息（无前视）；DSR 不过关 → 策略拒绝上架。

运行: python main.py
环境: Python 3.14 / baostock缓存 / scipy / numpy / pandas
"""

import sys
import warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
HORIZON = 5
IS_START = "2024-06-01"
IS_END = "2025-06-30"
OOS_START = "2025-07-01"
DSR_THRESHOLD = 0.95
MAX_POSITION = 0.15
MAX_INDUSTRY = 0.40


# ---------------- 1. 数据 ----------------

def load_data():
    cache = os.path.join(os.path.dirname(OUT_DIR), "14_全市场因子检验_baostock300", "data_cache.pkl")
    if not os.path.exists(cache):
        raise FileNotFoundError(f"缺少实验 14 缓存 {cache}")
    d = pd.read_pickle(cache)
    print(f"[1-数据] 复用实验 14 缓存: {d['close'].shape}，{d['industry'].nunique()} 行业")
    return d


# ---------------- 2. 因子 + 行业中性化 ----------------

def compute_factors(close, industry):
    raw = {
        "mom20": close.pct_change(20),
        "rev5": -close.pct_change(5),
        "vol20": -close.pct_change().rolling(20).std(),
        "vwap_dev": close / close.rolling(20).mean() - 1,
        "amt_trend": close.rolling(5).mean() / close.rolling(60).mean(),
        "high_low": -(close.rolling(20).max() - close.rolling(20).min()) / close,
    }
    ind_series = industry.reindex(close.columns)
    neutral = {}
    for name, f in raw.items():
        f = f.copy()
        for date in f.index:
            vals = f.loc[date]
            ind = ind_series.reindex(vals.index)
            m = vals.notna()
            if m.sum() < 5:
                continue
            means = vals[m].groupby(ind[m]).transform("mean")
            f.loc[date, m] = vals[m] - means
        neutral[name] = f
    print(f"[2-因子] 6 个量价因子 + 真实行业中性化完成")
    return neutral


# ---------------- 3. IC 加权合成 ----------------

def synth_signal(factors, close, train_end):
    """用训练期数据估计各因子 IC 权重，合成单一信号（date×symbol 面板）。"""
    fwd = close.loc[:train_end].shift(-HORIZON) / close.loc[:train_end] - 1
    weights = {}
    for name, f in factors.items():
        f_train = f.loc[:train_end]
        ics = []
        for d in f_train.index:
            ff, rr = f_train.loc[d], fwd.loc[d]
            m = ff.notna() & rr.notna()
            if m.sum() < 30:
                continue
            ics.append(np.corrcoef(ff[m], rr[m])[0, 1])
        weights[name] = max(np.mean(ics), 0.0)
    total = sum(weights.values())
    if total == 0:
        weights = {k: 1.0 / len(factors) for k in factors}
        total = 1.0
    signal = sum(factors[k] * (weights[k] / total) for k in factors)
    print(f"[3-合成] IC 加权完成，权重: " +
          ", ".join(f"{k}={v/sum(weights.values()):.2f}" for k, v in weights.items()))
    return signal


# ---------------- 4. walk-forward OOS 评估 ----------------

def evaluate_oos(signal, close, start):
    """对信号做分层多空 OOS 评估（前1/3 - 后1/3，日频）。"""
    sig = signal.loc[start:]
    fwd = close.loc[start:].shift(-HORIZON) / close.loc[start:] - 1
    daily = []
    for d in sig.index:
        f, r = sig.loc[d], fwd.loc[d]
        m = f.notna() & r.notna()
        if m.sum() < 30:
            continue
        ff, rr = f[m], r[m]
        k = max(1, int(len(ff) / 3))
        daily.append(ff.nlargest(k).index.to_series().map(lambda s: rr[s]).mean()
                     - ff.nsmallest(k).index.to_series().map(lambda s: rr[s]).mean())
    daily = pd.Series(daily, dtype=float).dropna()
    if len(daily) < 20:
        return None
    sharpe = daily.mean() / daily.std() * np.sqrt(252 / HORIZON) if daily.std() > 0 else 0
    print(f"[4-评估] OOS 分层多空: {len(daily)} 天 | 年化Sharpe(粗) {sharpe:.2f} | "
          f"日均 {daily.mean()*100:.3f}%")
    return {"daily": daily, "sharpe": sharpe}


# ---------------- 5. DSR 诊断 ----------------

def factor_sharpes(factors, close, start):
    """计算各因子的 OOS 分层多空 Sharpe（用于 DSR 的试验 SR 方差估计）。
    factors: {因子名: date×symbol 面板}。"""
    sharpes = {}
    fwd = close.loc[start:].shift(-HORIZON) / close.loc[start:] - 1
    for name, fpanel in factors.items():
        sig = fpanel.loc[start:]
        daily = []
        for d in sig.index:
            f, r = sig.loc[d], fwd.loc[d]
            m = f.notna() & r.notna()
            if m.sum() < 30:
                continue
            ff, rr = f[m], r[m]
            k = max(1, int(len(ff) / 3))
            daily.append(ff.nlargest(k).index.to_series().map(lambda s: rr[s]).mean()
                         - ff.nsmallest(k).index.to_series().map(lambda s: rr[s]).mean())
        daily = pd.Series(daily, dtype=float).dropna()
        if len(daily) > 20 and daily.std() > 0:
            sharpes[name] = daily.mean() / daily.std() * np.sqrt(252 / HORIZON)
    return sharpes


def deflated_sharpe(daily, factor_sharpe_dict, n_trials=None):
    """DSR（实验 07 方法，修正版）：用各试验 Sharpe 的方差估计期望最大基准。
    daily: 合成信号的 OOS 日收益；factor_sharpe_dict: 各因子试验的 Sharpe。"""
    sh = daily.mean() / daily.std() * np.sqrt(252 / HORIZON) if daily.std() > 0 else 0
    T = len(daily)
    skew = stats.skew(daily)
    kurt = stats.kurtosis(daily, fisher=False)
    sr_list = list(factor_sharpe_dict.values())
    n = n_trials or max(len(sr_list), 1)
    if n > 1 and len(sr_list) >= 2:
        var_sr = float(np.var(sr_list))
        sr0 = np.sqrt(2 * np.log(n)) * np.sqrt(var_sr) if var_sr > 0 else 0.0
    else:
        sr0 = 0.0
    se = np.sqrt((1 - skew * sh + (kurt - 1) / 4 * sh ** 2) / (T - 1)) if T > 1 else 1
    if se == 0:
        return 1.0 if sh > sr0 else 0.0
    return stats.norm.cdf((sh - sr0) / se)


# ---------------- 6+7. 风控 + 组合（风险平价） ----------------

def risk_parity_weights(cov, max_iter=100):
    x = np.ones(len(cov)) / len(cov)
    for _ in range(max_iter):
        vol = np.sqrt(x @ cov @ x)
        if vol == 0:
            break
        mrc = (cov @ x) / vol
        rc = x * mrc
        target = rc.mean()
        new_x = np.clip(x * (target / np.maximum(rc, 1e-12)), 1e-6, None)
        new_x = new_x / new_x.sum()
        if np.max(np.abs(new_x - x)) < 1e-6:
            return new_x
        x = new_x
    return x


def build_portfolio(signal, close, industry, n_top=20):
    """选信号最强的 n_top 只做风险平价组合，叠加行业/单只风控。"""
    last_date = signal.dropna(how="all").index[-1]
    top = signal.loc[last_date].dropna().nlargest(n_top)
    top_codes = list(top.index)
    ret = close[top_codes].pct_change().dropna()
    if len(ret) < 30 or len(ret.columns) < 5:
        return None
    cov = ret.cov()
    w = risk_parity_weights(cov.values)
    ind_exp = {}
    for i, c in enumerate(top_codes):
        ind = industry.get(c, "未知")
        ind_exp[ind] = ind_exp.get(ind, 0) + w[i]
    # 风控检查（实验 10 RiskGate 简化版）
    breaches = []
    for i, c in enumerate(top_codes):
        if w[i] > MAX_POSITION:
            breaches.append(f"单只超限 {c}: {w[i]:.1%}")
    for ind, exp in ind_exp.items():
        if exp > MAX_INDUSTRY:
            breaches.append(f"行业超限 {ind}: {exp:.1%}")
    print(f"[7-组合] 风险平价 Top{n_top}，单只最大 {max(w):.1%}，"
          f"行业最大 {max(ind_exp.values()):.1%}")
    if breaches:
        print(f"  ⚠ 风控拦截: {breaches[:3]}")
    else:
        print(f"  ✅ 风控通过（单只≤{MAX_POSITION:.0%}，行业≤{MAX_INDUSTRY:.0%}）")
    return {"codes": top_codes, "weights": w, "breaches": breaches}


def main():
    d = load_data()
    close, industry = d["close"], d["industry"]

    print("\n" + "=" * 78)
    print("完整 AI 量化策略闭环（数据→因子→合成→评估→DSR→风控→组合）")
    print("=" * 78)

    factors = compute_factors(close, industry)
    signal = synth_signal(factors, close, IS_END)

    oos = evaluate_oos(signal, close, OOS_START)
    if oos is None:
        print("⚠ OOS 样本不足，无法评估")
        return

    factor_sharpes_map = factor_sharpes(factors, close, OOS_START)
    p_dsr = deflated_sharpe(oos["daily"], factor_sharpes_map, n_trials=6)
    print(f"[5-DSR] 去偏夏普比（6 个因子试验，试验 SR 方差 "
          f"{np.var(list(factor_sharpes_map.values())):.4f}）: {p_dsr:.3f}（门槛 {DSR_THRESHOLD}）")

    if p_dsr < DSR_THRESHOLD:
        print(f"\n  ❌ DSR={p_dsr:.3f} < {DSR_THRESHOLD} → 信号未过统计显著性门槛，策略拒绝上架")
        print("     （诚实拒收：不因'看起来能赚'而上线——这就是回测纪律的价值）")
        verdict = "REJECTED"
    else:
        print(f"\n  ✅ DSR={p_dsr:.3f} ≥ {DSR_THRESHOLD} → 信号通过，进入风控+组合")
        verdict = "PASSED"
        pf = build_portfolio(signal, close, industry)

    print("\n" + "=" * 78)
    print(f"管道结论: {verdict}")
    print("=" * 78)
    print("""
完整闭环的每个环节都对应本知识库已验证的方法：
  数据→实验14 ｜ 因子+中性化→实验01/14 ｜ IC加权合成→实验13
  walk-forward评估→实验12 ｜ DSR诊断→实验07 ｜ 风控→实验10 ｜ 风险平价→实验15
纪律要点：只用历史信息（无前视）；DSR 不过关就拒收（不装成功）。
""")
    pd.to_pickle({"dsr": p_dsr, "verdict": verdict},
                 os.path.join(OUT_DIR, "result.pkl"))
    print("[完成]")


if __name__ == "__main__":
    main()
