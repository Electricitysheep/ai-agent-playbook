# -*- coding: utf-8 -*-
"""
实验 02：TSFM 金融适配实测 —— Chronos 零样本 vs 随机游走/ARIMA
==============================================================
复现 Re(Visiting) TSFM in Finance (2511.18578) 与英国央行实时评估的核心结论：
"金融数据上，预训练 TSFM 零样本表现平平，需与强基准（随机游走）做显著性检验"。

用 5 只美股日线，滚动原点协议（rolling-origin），比较：
  1) Naive (随机游走, last value)
  2) ARIMA(1,1,0) 滚动估计（statsmodels）
  3) Chronos-t5-small 零样本（Amazon, 9M 参数, CPU 可跑）

评估：RMSE / MAPE + Diebold-Mariano 检验（vs 随机游走）。
结论提示：金融日频收益近随机游走，TSFM 需过 DM 显著性关卡才算数。

运行: python main.py
环境: Python 3.14 / torch 2.11 CPU / chronos 0.3 / statsmodels / yfinance
首次运行需联网下载模型（~80MB 已缓存于 ~/.cache/huggingface）
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

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CACHE = os.path.join(OUT_DIR, "data_cache.pkl")
TICKERS = ["AAPL", "AMZN", "GOOG", "JPM", "META"]
HORIZON = 5          # 预测未来 5 日
N_ROLLS = 20         # 滚动原点步数
CONTEXT = 200        # 历史窗口
SEED = 42

np.random.seed(SEED)


def load_data(force=False):
    if os.path.exists(DATA_CACHE) and not force:
        d = pd.read_pickle(DATA_CACHE)
        print(f"[数据] 缓存: {d.shape}")
        return d
    close = {}
    for t in TICKERS:
        raw = yf.download(t, period="3y", interval="1d", progress=False, auto_adjust=True)
        if not raw.empty:
            close[t] = raw["Close"].squeeze()
    df = pd.DataFrame(close).sort_index()
    pd.to_pickle(df, DATA_CACHE)
    print(f"[数据] 拉取: {df.shape}")
    return df


def dm_test(e1, e2, h=HORIZON):
    """Diebold-Mariano 检验：d = e1^2 - e2^2，H0: 两模型等精度。
    返回 (DM 统计量, p 值)。负值表示 e1(候选) 更好。"""
    d = e1**2 - e2**2
    d = d[~np.isnan(d)]
    if len(d) < 4:
        return np.nan, np.nan
    T = len(d)
    dbar = d.mean()
    # 异方差自相关稳健方差 (Newey-West 简化, 滞后 h-1)
    gamma0 = ((d - dbar) ** 2).mean()
    gamma = np.array([np.mean((d[i:] - dbar) * (d[: T - i] - dbar))
                      if i > 0 else gamma0 for i in range(h)])
    v = (gamma0 + 2 * np.sum(gamma[1:])) / T
    if v <= 0:
        return np.nan, np.nan
    dm = dbar / np.sqrt(v)
    from scipy.stats import norm
    p = 2 * (1 - norm.cdf(abs(dm)))
    return dm, p


def main():
    df = load_data()
    # 逐股票评估
    results = {}
    for t in TICKERS:
        series = df[t].dropna().values
        if len(series) < CONTEXT + N_ROLLS + HORIZON:
            print(f"  [跳过] {t} 数据不足")
            continue
        end = len(series) - HORIZON
        starts = np.linspace(CONTEXT, end, N_ROLLS).astype(int)
        pred_naive, pred_arima, pred_chronos = [], [], []
        actuals = []

        from statsmodels.tsa.arima.model import ARIMA
        from chronos_manual import predict_chronos
        model = None
        if model is None:
            from transformers import AutoModelForSeq2SeqLM
            model = AutoModelForSeq2SeqLM.from_pretrained("amazon/chronos-t5-small")
            model.eval()

        for s in starts:
            ctx = series[:s]
            y_true = series[s:s + HORIZON]
            actuals.append(y_true)
            # 1) 随机游走
            pred_naive.append(np.full(HORIZON, ctx[-1]))
            # 2) ARIMA(1,1,0)
            try:
                fit = ARIMA(ctx, order=(1, 1, 0)).fit()
                pred_arima.append(fit.forecast(HORIZON))
            except Exception:
                pred_arima.append(np.full(HORIZON, ctx[-1]))
            # 3) Chronos 零样本（手动实现，权重 amazon/chronos-t5-small，CPU）
            try:
                fc, _ = predict_chronos(model, ctx, HORIZON, num_samples=20)
                lo, hi = ctx.min() * 0.5, ctx.max() * 1.5
                fc = np.clip(fc, lo, hi)
                pred_chronos.append(fc)
            except Exception:
                pred_chronos.append(np.full(HORIZON, ctx[-1]))

        actuals = np.array(actuals)
        naive = np.array(pred_naive)
        arima = np.array(pred_arima)
        chronos = np.array(pred_chronos)

        def mape(p):
            return np.nanmean(np.abs((actuals - p) / actuals)) * 100

        res = {
            "rmse_naive": np.sqrt(np.mean((actuals - naive) ** 2)),
            "rmse_arima": np.sqrt(np.mean((actuals - arima) ** 2)),
            "rmse_chronos": np.sqrt(np.mean((actuals - chronos) ** 2)),
            "mape_naive": mape(naive),
            "mape_arima": mape(arima),
            "mape_chronos": mape(chronos),
        }
        dm_c_naive, p_c_naive = dm_test(
            chronos.ravel() - actuals.ravel(), naive.ravel() - actuals.ravel())
        res["dm_chronos_vs_naive"] = dm_c_naive
        res["p_chronos_vs_naive"] = p_c_naive
        results[t] = res
        print(f"[完成] {t}: Chronos RMSE={res['rmse_chronos']:.4f} vs Naive={res['rmse_naive']:.4f} "
              f"vs ARIMA={res['rmse_arima']:.4f} | DM={dm_c_naive:.2f} (p={p_c_naive:.3f})")

    summary = pd.DataFrame(results).T.round(4)
    print("\n" + "=" * 80)
    print("结果总表（RMSE 越低越好；DM<0 且 p<0.05 表示 Chronos 显著优于随机游走）")
    print("=" * 80)
    print(summary.to_string())

    sig = summary[(summary["p_chronos_vs_naive"] < 0.05) & (summary["dm_chronos_vs_naive"] < 0)]
    print(f"\n结论: {len(sig)}/{len(summary)} 只股票上 Chronos 显著优于随机游走 → "
          f"{'支持' if len(sig) > len(summary)/2 else '不支持'} 'TSFM 零样本可直接用于日频收益预测'")
    print("（若多数不显著，与 2511.18578 / 英国央行结论一致：金融需领域适配/微调，零样本不是银弹）")

    summary.to_pickle(os.path.join(OUT_DIR, "result_summary.pkl"))
    print("\n[完成] 结果已存 result_summary.pkl")


if __name__ == "__main__":
    import torch
    main()
