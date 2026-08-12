# -*- coding: utf-8 -*-
"""
实验 12：walk-forward 完整实现（滚动窗口训练-测试 + 过拟合对比）
================================================================
主题 07 的 walk-forward 理论落地为可运行代码，并回答三个面试高频点：

1) walk-forward 怎么做：滚动窗口"训练→冻结参数→OOS 只测一次→滚动前进"
2) walk-forward vs 单次 train/test 分割：为什么 walk-forward 更诚实
3) 过拟合对比：在样本内选最优参数的策略（无纪律）vs walk-forward 策略

数据：yfinance A 股（复用实验 09 的 55 只股票池），真实行情
模型：LightGBM（sklearn 接口），因子 = 6 个基础量价因子

运行: python main.py
环境: Python 3.14 / lightgbm 4.7 / sklearn / yfinance
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
WINDOW_IS = 180        # 每个窗口训练长度（交易日）
WINDOW_OOS = 60        # 每个窗口测试长度
MIN_TRAIN = 100

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
    """6 个基础量价因子（date×symbol 面板 → 扁平化特征矩阵）。"""
    ret = close.pct_change()
    feats = {
        "mom20": close.pct_change(20),
        "rev5": -close.pct_change(5),
        "vol20": -ret.rolling(20).std(),
        "vwap_dev": close / close.rolling(20).mean() - 1,
        "amt_trend": close.rolling(5).mean() / close.rolling(60).mean(),
        "high_low": -(close.rolling(20).max() - close.rolling(20).min()) / close,
    }
    return feats


def build_panel(close, feats):
    """展平成 (date, symbol, features..., fwd_ret) 长表。"""
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


def ic_series(pred, actual):
    if len(pred) < 10:
        return 0.0
    return float(np.corrcoef(pred, actual)[0, 1])


def walk_forward(panel):
    """滚动窗口：每个窗口在 IS 训练 LightGBM，OOS 预测一次，参数冻结。
    返回 (OOS 预测, OOS 实际, 窗口数, 每窗口 IS/OOS IC 记录)。"""
    dates = sorted(panel["date"].unique())
    oos_preds, oos_actuals = [], []
    window_log = []
    for i in range(0, len(dates) - WINDOW_IS - WINDOW_OOS + 1, WINDOW_OOS):
        is_dates = dates[i:i + WINDOW_IS]
        oos_dates = dates[i + WINDOW_IS:i + WINDOW_IS + WINDOW_OOS]
        if len(oos_dates) < 20:
            break
        train = panel[panel["date"].isin(is_dates)]
        test = panel[panel["date"].isin(oos_dates)]
        if len(train) < MIN_TRAIN:
            continue
        feats_cols = [c for c in train.columns if c not in ("date", "symbol", "fwd_ret")]
        model = LGBMRegressor(n_estimators=50, max_depth=3, learning_rate=0.05,
                              random_state=42, verbose=-1)
        model.fit(train[feats_cols], train["fwd_ret"])
        # IS IC：训练集内预测（有监督拟合，通常虚高）
        is_pred = model.predict(train[feats_cols])
        is_ic = ic_series(is_pred, train["fwd_ret"].values)
        pred = model.predict(test[feats_cols])
        oos_ic = ic_series(pred, test["fwd_ret"].values)
        window_log.append((str(oos_dates[0])[:10], is_ic, oos_ic))
        oos_preds.extend(pred)
        oos_actuals.extend(test["fwd_ret"].values)
    return np.array(oos_preds), np.array(oos_actuals), len(window_log), window_log


def no_discipline(panel):
    """无纪律基线：用全部历史训练一次，然后在最后一段测试（等效于单次分割+反复调参）。"""
    dates = sorted(panel["date"].unique())
    split = int(len(dates) * 0.8)
    train = panel[panel["date"] <= dates[split]]
    test = panel[panel["date"] > dates[split]]
    feats_cols = [c for c in train.columns if c not in ("date", "symbol", "fwd_ret")]
    model = LGBMRegressor(n_estimators=50, max_depth=3, learning_rate=0.05,
                          random_state=42, verbose=-1)
    model.fit(train[feats_cols], train["fwd_ret"])
    pred = model.predict(test[feats_cols])
    return pred, test["fwd_ret"].values


def report(name, pred, actual):
    ic = ic_series(pred, actual)
    # 分层多空：前 1/3 做多 - 后 1/3 做空
    df = pd.DataFrame({"pred": pred, "ret": actual}).dropna()
    k = max(1, len(df) // 3)
    long_ret = df.nlargest(k, "pred")["ret"].mean()
    short_ret = df.nsmallest(k, "pred")["ret"].mean()
    print(f"  {name:<32} IC={ic:+.4f} | 多空日均 {(long_ret-short_ret)*100:.3f}% | n={len(df)}")


def main():
    close = load_data()
    feats = make_features(close)
    panel = build_panel(close, feats)
    print(f"[面板] {len(panel)} 行样本（{panel['date'].nunique()} 天 × {panel['symbol'].nunique()} 只）")
    print(f"[设置] IS 窗口 {WINDOW_IS} 天 / OOS 窗口 {WINDOW_OOS} 天 / 预测 h={HORIZON}")

    print("\n" + "=" * 78)
    print("walk-forward（滚动窗口，参数冻结，OOS 只测一次）")
    print("=" * 78)
    pred_wf, actual_wf, n_win, window_log = walk_forward(panel)
    report(f"walk-forward ({n_win} 个窗口)", pred_wf, actual_wf)

    print("\n  每窗口 IS vs OOS IC（过拟合诊断：IS 高 OOS 低 = 曲线拟合）：")
    print(f"  {'窗口起点':<12} {'IS IC':>8} {'OOS IC':>8} {'OOS/IS':>8}")
    for start, is_ic, oos_ic in window_log:
        ratio = (oos_ic / is_ic) if abs(is_ic) > 1e-6 else float("nan")
        flag = " ⚠曲线拟合" if ratio < 0.5 else ""
        print(f"  {start:<12} {is_ic:+8.4f} {oos_ic:+8.4f} {ratio:>7.2f}{flag}")

    print("\n" + "=" * 78)
    print("无纪律基线（单次 80/20 分割 + 全历史训练）")
    print("=" * 78)
    pred_nd, actual_nd = no_discipline(panel)
    report("单次分割（样本外）", pred_nd, actual_nd)

    print("\n" + "=" * 78)
    print("结论（面试要点）")
    print("=" * 78)
    ic_wf = ic_series(pred_wf, actual_wf)
    ic_nd = ic_series(pred_nd, actual_nd)
    print(f"""
1. walk-forward 用 {n_win} 个独立 OOS 窗口验证（每窗口参数只在 IS 上选、冻结后测一次），
   覆盖多个市场 regime——比单次分割更诚实。
2. 对比：单次分割 IC={ic_nd:+.4f} vs walk-forward IC={ic_wf:+.4f}
   （若单次分割更高，说明它对某一时段过拟合；walk-forward 的指标更接近实盘预期）
3. 工程要点（Kiploks 实践）：
   - 预处理（归一化/去趋势）必须在 IS 上 fit、OOS 只应用——全局统计=泄漏
   - 每窗口结果 JSONL 持久化（窗口ID/参数/指标/版本）→ 可复现
   - 至少 3-5 个窗口才有统计意义；OOS Sharpe < 50% IS Sharpe = 曲线拟合
4. 局限：本实验因子/模型为演示配置；生产需更多因子 + DSR/PBO 复核。
""")
    pd.to_pickle({"wf": (pred_wf, actual_wf, n_win), "nd": (pred_nd, actual_nd)},
                 os.path.join(OUT_DIR, "result.pkl"))
    print("[完成] 结果已存 result.pkl")


if __name__ == "__main__":
    main()
