# -*- coding: utf-8 -*-
"""
实验 13：多因子合成 —— LightGBM 集成 vs IC 加权 vs 等权（walk-forward 内评估）
=================================================================================
衔接 RD-Agent 的"Alpha Integration"环节（主题 05）与主题 01 的因子合成：
用真实 A 股数据比较三种因子合成方式的样本外表现：

1) 等权合成：所有因子 z-score 后等权平均（简单基线）
2) IC 加权合成：按各因子近期 IC 加权（时序自适应）
3) LightGBM 合成：ML 学习因子→收益的非线性映射

评估：统一在 walk-forward 滚动窗口内做（每窗口训练/计算权重 → OOS 预测一次），
输出各方法的样本外 IC 与分层多空——**合成方式的质量差异 + 过拟合诊断**。

数据：yfinance A 股（复用实验 09/12 的股票池）
运行: python main.py
环境: Python 3.14 / lightgbm / yfinance / pandas / numpy
"""

import sys
import warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import numpy as np
import pandas as pd
import yfinance as yf
from lightgbm import LGBMRegressor

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CACHE = os.path.join(OUT_DIR, "data_cache.pkl")
HORIZON = 5
WINDOW_IS = 180
WINDOW_OOS = 60

TICKERS = [
    "601318.SS", "600036.SS", "601166.SS", "600030.SS", "000001.SZ",
    "600519.SS", "600887.SS", "601888.SS", "000858.SZ", "600809.SS",
    "002594.SZ", "601012.SS", "002415.SZ", "600585.SS", "601899.SS",
    "600900.SS", "000333.SZ", "002475.SZ", "600309.SS", "600031.SS",
    "601857.SS", "600028.SS", "601088.SS", "600019.SS", "601225.SS",
]


def load_data(force=False):
    if os.path.exists(DATA_CACHE) and not force:
        return pd.read_pickle(DATA_CACHE)
    closes = {}
    for t in TICKERS:
        try:
            raw = yf.download(t, period="3y", interval="1d", progress=False, auto_adjust=True)
            if not raw.empty:
                closes[t] = raw["Close"].squeeze()
        except Exception:
            pass
    close = pd.DataFrame(closes).sort_index()
    pd.to_pickle(close, DATA_CACHE)
    print(f"[数据] 拉取完成: {close.shape}")
    return close


def make_features(close):
    ret = close.pct_change()
    return {
        "mom20": close.pct_change(20),
        "rev5": -close.pct_change(5),
        "vol20": -ret.rolling(20).std(),
        "vwap_dev": close / close.rolling(20).mean() - 1,
        "amt_trend": close.rolling(5).mean() / close.rolling(60).mean(),
        "high_low": -(close.rolling(20).max() - close.rolling(20).min()) / close,
    }


def build_panel(close, feats):
    rows = []
    fwd = close.shift(-HORIZON) / close - 1
    for date in close.index:
        for sym in close.columns:
            c = close.loc[date, sym]
            fr = fwd.loc[date, sym]
            if pd.isna(c) or pd.isna(fr):
                continue
            fvals = {name: feats[name].loc[date, sym] for name in feats}
            if any(pd.isna(v) for v in fvals.values()):
                continue
            rows.append({"date": date, "symbol": sym, **fvals, "fwd_ret": fr})
    return pd.DataFrame(rows)


def ic(pred, actual):
    if len(pred) < 10:
        return 0.0
    return float(np.corrcoef(pred, actual)[0, 1])


def zscore_series(s):
    std = s.std()
    return (s - s.mean()) / std if std > 0 else s * 0


def synth_equal(panel, is_dates, test):
    """等权：各因子 z-score 后平均（权重用 IS 的均值和标准差，OOS 只应用）。"""
    feats_cols = [c for c in panel.columns if c not in ("date", "symbol", "fwd_ret")]
    means, stds = {}, {}
    is_data = panel[panel["date"].isin(is_dates)]
    for c in feats_cols:
        means[c], stds[c] = is_data[c].mean(), is_data[c].std()
    pred = np.zeros(len(test))
    for c in feats_cols:
        if stds[c] > 0:
            pred += (test[c].values - means[c]) / stds[c]
    return pred / len(feats_cols)


def synth_ic_weighted(panel, is_dates, test):
    """IC 加权：按各因子在 IS 内的 IC 加权（正 IC 才保留）。"""
    feats_cols = [c for c in panel.columns if c not in ("date", "symbol", "fwd_ret")]
    is_data = panel[panel["date"].isin(is_dates)]
    weights = {}
    for c in feats_cols:
        w = ic(is_data[c].values, is_data["fwd_ret"].values)
        weights[c] = max(w, 0.0)
    if sum(weights.values()) == 0:
        return np.zeros(len(test))
    pred = np.zeros(len(test))
    for c in feats_cols:
        if weights[c] > 0:
            pred += weights[c] * (test[c].values - is_data[c].mean())
    return pred / sum(weights.values())


def synth_lgb(panel, is_dates, test):
    """LightGBM：学习因子→收益的非线性映射。"""
    feats_cols = [c for c in panel.columns if c not in ("date", "symbol", "fwd_ret")]
    is_data = panel[panel["date"].isin(is_dates)]
    model = LGBMRegressor(n_estimators=50, max_depth=3, learning_rate=0.05,
                          random_state=42, verbose=-1)
    model.fit(is_data[feats_cols], is_data["fwd_ret"])
    return model.predict(test[feats_cols])


def run_walkforward(panel, synth_fn):
    dates = sorted(panel["date"].unique())
    preds, actuals, log = [], [], []
    for i in range(0, len(dates) - WINDOW_IS - WINDOW_OOS + 1, WINDOW_OOS):
        is_dates = dates[i:i + WINDOW_IS]
        oos_dates = dates[i + WINDOW_IS:i + WINDOW_IS + WINDOW_OOS]
        if len(oos_dates) < 20:
            break
        test = panel[panel["date"].isin(oos_dates)]
        p = synth_fn(panel, is_dates, test)
        preds.extend(p)
        actuals.extend(test["fwd_ret"].values)
        log.append((str(oos_dates[0])[:10], ic(p, test["fwd_ret"].values)))
    return np.array(preds), np.array(actuals), log


def report(name, pred, actual, log):
    print(f"\n  {name}")
    print(f"  {'窗口起点':<12} {'OOS IC':>8}")
    for start, oos_ic in log:
        print(f"  {start:<12} {oos_ic:+8.4f}")
    print(f"  综合 OOS IC = {ic(pred, actual):+.4f}（n={len(pred)}）")
    df = pd.DataFrame({"pred": pred, "ret": actual}).dropna()
    k = max(1, len(df) // 3)
    ls = df.nlargest(k, "pred")["ret"].mean() - df.nsmallest(k, "pred")["ret"].mean()
    print(f"  分层多空日均 = {ls*100:.3f}%")


def main():
    close = load_data()
    feats = make_features(close)
    panel = build_panel(close, feats)
    print(f"[面板] {len(panel)} 行（{panel['date'].nunique()} 天 × {panel['symbol'].nunique()} 只）")
    print(f"[设置] IS {WINDOW_IS} 天 / OOS {WINDOW_OOS} 天，walk-forward 内评估三种合成")

    print("\n" + "=" * 78)
    print("三种因子合成方式（统一 walk-forward 评估）")
    print("=" * 78)

    for name, fn in [("等权合成", synth_equal), ("IC 加权合成", synth_ic_weighted),
                     ("LightGBM 合成", synth_lgb)]:
        pred, actual, log = run_walkforward(panel, fn)
        report(name, pred, actual, log)

    print("\n" + "=" * 78)
    print("结论（面试要点）")
    print("=" * 78)
    print("""
1. 三种合成方式代表三种复杂度：等权（无学习）、IC 加权（线性自适应）、
   LightGBM（非线性学习）——对应 RD-Agent/Chain-of-Alpha 的"因子集成"环节。
2. 观察点：
   - LightGBM 在 OOS 上若劣于简单加权 → 因子本身预测力弱时，ML 学到的是噪声
     （与实验 12 的 IS 高/OOS 低同源——ML 需要更强的因子信号才不虚）
   - IC 加权若优于等权 → 因子间预测力差异显著，自适应权重有价值
3. 工程要点：所有合成的均值/标准差/权重都只在 IS 上估计、OOS 只应用——
   泄漏的合成（用全样本统计）会系统性高估 OOS 表现（见主题 07）。
4. 局限：25 只小面板 + 6 因子；生产需更多因子 + DSR/PBO + 行业中性化。
""")
    pd.to_pickle({"panel_n": len(panel)}, os.path.join(OUT_DIR, "result.pkl"))
    print("[完成]")


if __name__ == "__main__":
    main()
