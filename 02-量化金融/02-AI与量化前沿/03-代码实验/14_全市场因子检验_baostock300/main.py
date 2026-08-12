# -*- coding: utf-8 -*-
"""
实验 14：全市场因子检验（baostock 300 只分层抽样 + 真实行业中性化）
=================================================================
实验 09 的生产级升级：从"55 只 + 板块近似"升级到"300 只 + 真实申万行业"：

1) 数据：baostock（免费无 token）拉 300 只分层抽样 A 股 2 年日线
   ——分层抽样保证 81 个申万行业全覆盖（比随机抽样更代表全市场）
2) 行业中性化：用 baostock 真实申万行业标签（实验 09 用板块近似，此处是真实版）
3) 三道检验：IC/RankIC/ICIR → 衰减 → 互补性 + 筛选
4) 对比：小样本(20) → 中样本(55+板块近似) → 本实验(300+真实行业)的检验功效递进

运行: python main.py
环境: Python 3.14 / baostock / pandas / numpy
"""

import sys
import time
import warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import numpy as np
import pandas as pd
import baostock as bs

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CACHE = os.path.join(OUT_DIR, "data_cache.pkl")
HORIZON = 5
IC_THRESHOLD = 0.02
ICIR_THRESHOLD = 0.25
CORR_CAP = 0.6


def load_universe():
    """从缓存加载 300 只分层抽样（universe_300.pkl，81 行业）。"""
    pkl = os.path.join(os.path.dirname(OUT_DIR), "universe_300.pkl")
    if not os.path.exists(pkl):
        raise FileNotFoundError(f"缺少 {pkl}——先运行 universe 构建脚本")
    df = pd.read_pickle(pkl)
    print(f"[股票池] 缓存加载: {len(df)} 只 / {df['industry'].nunique()} 个行业")
    return df


def load_prices(force=False):
    if os.path.exists(DATA_CACHE) and not force:
        d = pd.read_pickle(DATA_CACHE)
        print(f"[数据] 缓存: {d['close'].shape}")
        return d
    universe = load_universe()
    closes, ind_map = {}, {}
    t0 = time.time()
    lg = bs.login()   # 只登录一次，整个会话复用（避免每次 login 3.4s 开销）
    if lg.error_code != '0':
        raise RuntimeError(f"baostock login failed: {lg.error_msg}")
    for i, row in universe.iterrows():
        code, ind = row["code"], row["industry"]
        try:
            rs = bs.query_history_k_data_plus(
                code, "date,close", start_date="2024-01-01", end_date="2026-06-30",
                frequency="d", adjustflag="2")
            rows = []
            while (rs.error_code == '0') and rs.next():
                rows.append(rs.get_row_data())
            if len(rows) > 100:
                s = pd.Series({r[0]: float(r[1]) for r in rows if r[1] != ''})
                s.index = pd.to_datetime(s.index)
                closes[code] = s
                ind_map[code] = ind
        except Exception:
            pass
        if (i + 1) % 50 == 0:
            print(f"  进度 {i+1}/{len(universe)} ({time.time()-t0:.0f}s, 已得 {len(closes)} 只)", flush=True)
    bs.logout()
    close = pd.DataFrame(closes).sort_index()
    ind = pd.Series(ind_map)
    out = {"close": close, "industry": ind}
    pd.to_pickle(out, DATA_CACHE)
    print(f"[数据] 拉取完成: {close.shape}")
    return out


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
    return neutral


def panel_ic(factor_df, fwd_ret_df):
    ics, rank_ics = [], []
    for d in factor_df.index:
        f = factor_df.loc[d]
        r = fwd_ret_df.loc[d]
        m = f.notna() & r.notna()
        if m.sum() < 30:
            continue
        ics.append(np.corrcoef(f[m], r[m])[0, 1])
        rank_ics.append(f[m].rank().corr(r[m].rank()))
    ics, rank_ics = pd.Series(ics), pd.Series(rank_ics)
    return {"ic": ics.mean(), "icir": ics.mean() / ics.std() if ics.std() > 0 else 0,
            "rank_ic": rank_ics.mean(), "rank_icir": rank_ics.mean() / rank_ics.std() if rank_ics.std() > 0 else 0,
            "n_days": len(ics)}


def main():
    d = load_prices()
    close, industry = d["close"], d["industry"]
    print(f"[行情] {close.shape[0]} 天 × {close.shape[1]} 只（{industry.nunique()} 个真实申万行业）")

    print("\n[因子] 6 个候选因子 + 真实行业中性化...")
    factors = compute_factors(close, industry)
    fwd = close.shift(-HORIZON) / close - 1

    print("\n" + "=" * 78)
    print(f"检验 1：IC / RankIC / ICIR（h={HORIZON}，真实行业中性化）")
    print("=" * 78)
    rows = []
    for name, f in factors.items():
        r = panel_ic(f, fwd)
        r["name"] = name
        rows.append(r)
    result = pd.DataFrame(rows).set_index("name")
    print(result[["ic", "icir", "rank_ic", "rank_icir", "n_days"]].round(4).to_string())

    print("\n" + "=" * 78)
    print("检验 2：衰减测试")
    print("=" * 78)
    for h in [1, 5, 10, 20]:
        fwd_h = close.shift(-h) / close - 1
        ics = {name: panel_ic(f, fwd_h)["ic"] for name, f in factors.items()}
        print(f"  h={h:<3}: " + "  ".join(f"{k}={v:+.4f}" for k, v in ics.items()))

    print("\n" + "=" * 78)
    print("检验 3：互补性 + 筛选")
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
    print("检验功效递进对比（三个样本规模）")
    print("=" * 78)
    print("""
实验 01（20 只，无中性化）：0/9 通过
实验 09（55 只，板块近似）：0/6 通过（mom20 IC 0.008→0.019，接近阈值）
本实验（300 只，真实行业）：观察是否出现通过因子
意义：样本量 + 中性化质量共同决定检验功效
""")
    pd.to_pickle({"result": result, "corr": corr, "selected": selected},
                 os.path.join(OUT_DIR, "result_summary.pkl"))
    print("[完成]")


if __name__ == "__main__":
    main()
