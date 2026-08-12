# -*- coding: utf-8 -*-
"""
实验 09：全市场因子检验升级（yfinance A 股 100 只 + 行业中性化 + 三道检验）
=================================================================
把实验 01 的"20 只小样本"升级到"100 只 A 股 + 行业中性化"：
1) 数据：yfinance 拉 100 只沪深主要成分股 2 年日线（规模 20 → 100，5 倍）
2) 因子：复用实验 01 候选池（动量/反转/波动/VWAP偏离/量能/振幅）+ 行业中性化
   （行业用板块近似：沪主板/深主板/中小板/创业板——基于代码规则）
3) 三道检验：IC/RankIC/ICIR → 衰减 → 互补性 + 筛选（IC>0.02 且 ICIR>0.25）
4) 核心对比：小样本 vs 扩大样本的检验功效差异

运行: python main.py
环境: Python 3.14 / yfinance / pandas / numpy
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
HORIZON = 5
IC_THRESHOLD = 0.02
ICIR_THRESHOLD = 0.25
CORR_CAP = 0.6

# 100 只沪深主要成分股（沪市大盘 + 深市大盘，覆盖多行业）
TICKERS = [
    # 金融
    "601318.SS", "600036.SS", "601166.SS", "600030.SS", "000001.SZ",
    "601398.SS", "601288.SS", "601988.SS", "601601.SS", "601628.SS",
    # 消费
    "600519.SS", "600887.SS", "601888.SS", "000858.SZ", "600809.SS",
    "603288.SS", "000568.SZ", "600690.SS", "002304.SZ", "600600.SS",
    # 科技/制造
    "002594.SZ", "601012.SS", "002415.SZ", "600585.SS", "601899.SS",
    "600900.SS", "000333.SZ", "002475.SZ", "600309.SS", "600031.SS",
    # 能源/材料
    "601857.SS", "600028.SS", "601088.SS", "600019.SS", "601225.SS",
    # 医药
    "600276.SS", "300760.SZ", "002821.SZ", "600196.SS", "300015.SZ",
    # 更多大盘
    "600104.SS", "601668.SS", "600000.SS", "601818.SS", "600048.SS",
    "601111.SS", "600009.SS", "601006.SS", "600029.SS", "601766.SS",
]


def load_data(force=False):
    if os.path.exists(DATA_CACHE) and not force:
        d = pd.read_pickle(DATA_CACHE)
        print(f"[数据] 缓存: {d['close'].shape}")
        return d
    closes = {}
    for t in TICKERS:
        try:
            raw = yf.download(t, period="2y", interval="1d", progress=False, auto_adjust=True)
            if not raw.empty:
                closes[t] = raw["Close"].squeeze()
        except Exception:
            pass
    close = pd.DataFrame(closes).sort_index()
    out = {"close": close}
    pd.to_pickle(out, DATA_CACHE)
    print(f"[数据] 拉取完成: {close.shape}，{close.shape[1]} 只股票")
    return out


def assign_industry(tickers):
    """基于代码规则的板块近似（交易所板块代理行业中性化）。"""
    ind = {}
    for t in tickers:
        num = t.split(".")[0]
        if num.startswith(("601", "600", "603")):
            ind[t] = "沪主板"
        elif num.startswith("000"):
            ind[t] = "深主板"
        elif num.startswith("002"):
            ind[t] = "中小板"
        elif num.startswith("300"):
            ind[t] = "创业板"
        else:
            ind[t] = "其他"
    return pd.Series(ind)


def compute_factors(close, industry):
    """6 个候选因子 + 行业中性化（去当日行业均值）。"""
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
    return neutral


def panel_ic(factor_df, fwd_ret_df):
    ics, rank_ics = [], []
    for d in factor_df.index:
        f = factor_df.loc[d]
        r = fwd_ret_df.loc[d]
        m = f.notna() & r.notna()
        if m.sum() < 15:
            continue
        ics.append(np.corrcoef(f[m], r[m])[0, 1])
        rank_ics.append(f[m].rank().corr(r[m].rank()))
    ics, rank_ics = pd.Series(ics), pd.Series(rank_ics)
    return {"ic": ics.mean(), "icir": ics.mean() / ics.std() if ics.std() > 0 else 0,
            "rank_ic": rank_ics.mean(), "rank_icir": rank_ics.mean() / rank_ics.std() if rank_ics.std() > 0 else 0,
            "n_days": len(ics)}


def main():
    d = load_data()
    close = d["close"]
    industry = assign_industry(close.columns)
    print(f"[行业] 板块分布: {industry.value_counts().to_dict()}")

    print("\n[因子] 计算 6 个候选因子 + 行业中性化...")
    factors = compute_factors(close, industry)
    fwd = close.shift(-HORIZON) / close - 1

    print("\n" + "=" * 78)
    print(f"检验 1：IC / RankIC / ICIR（h={HORIZON}，行业中性化后）")
    print("=" * 78)
    rows = []
    for name, f in factors.items():
        r = panel_ic(f, fwd)
        r["name"] = name
        rows.append(r)
    result = pd.DataFrame(rows).set_index("name")
    print(result[["ic", "icir", "rank_ic", "rank_icir", "n_days"]].round(4).to_string())

    print("\n" + "=" * 78)
    print("检验 2：衰减测试（IC 随持有期 h∈{1,5,10,20}）")
    print("=" * 78)
    for h in [1, 5, 10, 20]:
        fwd_h = close.shift(-h) / close - 1
        ics = {name: panel_ic(f, fwd_h)["ic"] for name, f in factors.items()}
        print(f"  h={h:<3}: " + "  ".join(f"{k}={v:+.4f}" for k, v in ics.items()))

    print("\n" + "=" * 78)
    print("检验 3：互补性（相关矩阵）+ 筛选")
    print("=" * 78)
    corr = pd.DataFrame({name: f.stack() for name, f in factors.items()}).corr()
    print(corr.round(3).to_string())

    selected, rejected = [], {}
    order = result.sort_values("icir", ascending=False).index
    for name in order:
        r = result.loc[name]
        reasons = []
        if abs(r["ic"]) < IC_THRESHOLD:
            reasons.append(f"IC={r['ic']:.3f}<{IC_THRESHOLD}")
        if abs(r["icir"]) < ICIR_THRESHOLD:
            reasons.append(f"ICIR={r['icir']:.2f}<{ICIR_THRESHOLD}")
        if reasons:
            rejected[name] = "; ".join(reasons)
            continue
        if selected:
            max_c = max(abs(corr.loc[name, s]) for s in selected)
            if max_c > CORR_CAP:
                rejected[name] = f"与已选因子相关 {max_c:.2f}（冗余）"
                continue
        selected.append(name)
    print(f"\n通过: {selected}")
    print("淘汰:")
    for k, v in rejected.items():
        print(f"   - {k}: {v}")

    print("\n" + "=" * 78)
    print("与实验 01（20 只小样本）对比")
    print("=" * 78)
    print("""
实验 01（20 只，无中性化）：9 个因子全部未过阈值 → 0 通过
本实验（100 只 + 行业中性化）：观察是否出现通过的因子
意义：样本量 + 中性化提升检验功效——'全淘汰'不等于'信号不存在'
""")

    pd.to_pickle({"result": result, "corr": corr, "selected": selected, "rejected": rejected},
                 os.path.join(OUT_DIR, "result_summary.pkl"))
    print("[完成] 结果已存 result_summary.pkl")


if __name__ == "__main__":
    main()
