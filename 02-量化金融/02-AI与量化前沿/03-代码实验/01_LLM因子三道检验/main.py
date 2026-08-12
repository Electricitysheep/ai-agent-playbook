# -*- coding: utf-8 -*-
"""
实验 01：LLM 因子挖掘的"三道检验"落地管道
=========================================
模拟 Chain-of-Alpha / Alpha-GPT 的 生成→评估→筛选 闭环，用真实 A 股日线数据
对一组"LLM 生成的候选因子"执行：IC/ICIR → 衰减测试 → 互补性检查，
最后给出"通过/淘汰"决策（对应 Chain-of-Alpha 的 Score=[S,C,E,D] 四维评分）。

不调真实 LLM（无 API key），用公式化候选池模拟 LLM 输出——检验环节 100% 真实。

运行: python main.py
环境: Python 3.14 / pandas 3.0.3 / numpy / yfinance（联网拉数据）
"""

import sys
import warnings
warnings.filterwarnings("ignore")
import os
import numpy as np
import pandas as pd
import yfinance as yf

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CACHE = os.path.join(OUT_DIR, "data_cache.parquet")
IC_THRESHOLD = 0.02        # 平均 IC 通过阈值
ICIR_THRESHOLD = 0.25      # ICIR 通过阈值（时间稳定性）
CORR_CAP = 0.6             # 与已入选因子最大允许相关性（互补性）
HORIZONS = [1, 5, 10, 20]  # 衰减测试持有期（交易日）

TICKERS = [
    "600519.SS", "601318.SS", "600036.SS", "000858.SZ", "601899.SS",
    "600030.SS", "000333.SZ", "601166.SS", "600900.SS", "000651.SZ",
    "601012.SS", "600276.SS", "002594.SZ", "600887.SS", "601888.SS",
    "000568.SZ", "600309.SS", "601088.SS", "600585.SS", "000001.SZ",
]


def load_data(force=False):
    """拉 20 只大盘股近 2 年日线，缓存 parquet。返回 date×symbol 的 close/volume 矩阵。"""
    if os.path.exists(DATA_CACHE) and not force:
        d = pd.read_pickle(DATA_CACHE)
        print(f"[数据] 缓存加载: {d['close'].shape}")
        return d
    closes, volumes = {}, {}
    for t in TICKERS:
        try:
            raw = yf.download(t, period="2y", interval="1d", progress=False, auto_adjust=True)
            if raw.empty:
                continue
            closes[t] = raw["Close"].squeeze()
            volumes[t] = raw["Volume"].squeeze()
        except Exception as e:
            print(f"  [跳过] {t}: {str(e)[:60]}")
    close = pd.DataFrame(closes).sort_index()
    volume = pd.DataFrame(volumes).reindex(close.index).sort_index()
    out = {"close": close, "volume": volume}
    pd.to_pickle(out, DATA_CACHE)
    print(f"[数据] 拉取完成: {close.shape}，{close.shape[1]} 只股票")
    return out


# ----------------------- 2. 候选因子池（模拟 LLM 输出） -----------------------
# 每个因子 = (名称, 描述, 计算函数[close矩阵, volume矩阵 → 因子矩阵])
# 刻意混入：2 个"无经济学逻辑"因子 + 1 个"前视伪造"因子（用当日收益构造）

def f_mom20(c, v):
    return c.pct_change(20)

def f_rev5(c, v):
    return -c.pct_change(5)

def f_vol20(c, v):
    return -c.pct_change().rolling(20).std()

def f_vwap_dev(c, v):
    # 用 close 自身近似 VWAP 偏离（简化版）
    return c / c.rolling(20).mean() - 1

def f_corr_pv(c, v):
    return c.pct_change().rolling(20).corr(v.pct_change())

def f_amt_trend(c, v):
    return v.rolling(5).mean() / v.rolling(60).mean()

def f_high_low(c, v):
    amp = (c.rolling(20).max() - c.rolling(20).min()) / c
    return -amp

def f_noise_mom(c, v):
    """模拟"隔日动量"：无逻辑的公式拼接，理应无效。"""
    return (c.pct_change(2) - c.pct_change(1)).shift(1)

def f_lookahead(c, v):
    """前视伪造因子：直接用当日收益率——与标签同源，IC 必虚高。"""
    return c.pct_change()

FACTOR_POOL = [
    ("mom20", "20日动量", f_mom20),
    ("rev5", "5日反转", f_rev5),
    ("vol20", "20日波动率(负)", f_vol20),
    ("vwap_dev", "VWAP偏离", f_vwap_dev),
    ("corr_pv", "量价相关性20日", f_corr_pv),
    ("amt_trend", "量能趋势5/60", f_amt_trend),
    ("high_low", "振幅因子(负)", f_high_low),
    ("noise_mom", "隔日动量(模拟噪声)", f_noise_mom),
    ("lookahead", "前视伪造因子", f_lookahead),
]


# ----------------------- 3. 三道检验 -----------------------

def panel_ic(factor_df, fwd_ret_df):
    """逐日截面 IC：每行 = 一天，因子列 与 未来收益列 的 Pearson 相关。
    前视纪律：因子用 t 日值，收益用 t→t+h 已错位的矩阵。"""
    ics, rank_ics = [], []
    for d in factor_df.index:
        f = factor_df.loc[d]
        r = fwd_ret_df.loc[d]
        m = f.notna() & r.notna()
        if m.sum() < 5:
            continue
        ics.append(np.corrcoef(f[m], r[m])[0, 1])
        rank_ics.append(f[m].rank().corr(r[m].rank()))
    ics, rank_ics = pd.Series(ics), pd.Series(rank_ics)
    return {
        "ic": ics.mean(),
        "icir": ics.mean() / ics.std() if ics.std() > 0 else 0.0,
        "rank_ic": rank_ics.mean(),
        "rank_icir": rank_ics.mean() / rank_ics.std() if rank_ics.std() > 0 else 0.0,
        "n_days": len(ics),
    }


def make_fwd_ret(close, h):
    """未来 h 日收益矩阵：ret_t = close_{t+h}/close_t - 1（h 日滚动）。"""
    return close.shift(-h) / close - 1


def decay_curve(factor_df, close):
    """衰减测试：IC 随持有期 h 变化。"""
    return {h: panel_ic(factor_df, make_fwd_ret(close, h))["ic"] for h in HORIZONS}


# ----------------------- 4. 主流程 -----------------------

def main():
    d = load_data()
    close, volume = d["close"], d["volume"]

    print(f"\n[因子] 计算 {len(FACTOR_POOL)} 个候选因子（模拟 LLM 输出）...")
    factors = {}
    for name, desc, fn in FACTOR_POOL:
        try:
            factors[name] = fn(close, volume)
        except Exception as e:
            print(f"  [因子失败] {name}: {str(e)[:80]}")
            factors[name] = pd.DataFrame(np.nan, index=close.index, columns=close.columns)

    print("\n" + "=" * 80)
    print("检验 1：IC / RankIC / ICIR（持有期 h=1 日）")
    print("=" * 80)
    rows = []
    for name, desc, _ in FACTOR_POOL:
        r = panel_ic(factors[name], make_fwd_ret(close, 1))
        r.update({"name": name, "desc": desc})
        rows.append(r)
    result = pd.DataFrame(rows).set_index("name")
    print(result[["desc", "ic", "icir", "rank_ic", "rank_icir", "n_days"]].round(4).to_string())

    print("\n" + "=" * 80)
    print("检验 1b：前视陷阱演示——lookahead 因子在 h=0（同日标签）的 IC")
    print("=" * 80)
    la = factors["lookahead"]
    same_day_ret = close.pct_change()
    ic0 = panel_ic(la, same_day_ret)["ic"]
    ic1 = panel_ic(la, make_fwd_ret(close, 1))["ic"]
    print(f"  h=0（因子与同日收益比）: IC={ic0:.4f}  ← 虚高假象")
    print(f"  h=1（因子与次日收益比）: IC={ic1:.4f}  ← 正确错位后的真实值")
    print("  ⚠ 结论：若回测框架把因子当日的收益也算进去，任何'动量类'因子都会伪造高 IC。")

    print("\n" + "=" * 80)
    print("检验 2：衰减测试（IC 随持有期变化；有效因子应随时间衰减）")
    print("=" * 80)
    decay_df = pd.DataFrame({name: decay_curve(factors[name], close)
                             for name, _, _ in FACTOR_POOL}).T
    print(decay_df.round(4).to_string())

    print("\n" + "=" * 80)
    print("检验 3：互补性 + 最终筛选（仿 Chain-of-Alpha Score=[S,C,E,D]）")
    print("=" * 80)
    # 互补性：逐股-逐日 stacked 因子值的相关矩阵
    corr_matrix = pd.DataFrame({
        name: factors[name].stack() for name, _, _ in FACTOR_POOL
    }).corr()
    print("因子相关矩阵：")
    print(corr_matrix.round(2).to_string())

    selected, rejected = [], {}
    order = result.sort_values("icir", ascending=False).index
    for name in order:
        r = result.loc[name]
        reasons = []
        if abs(r["ic"]) < IC_THRESHOLD:
            reasons.append(f"IC={r['ic']:.3f}<{IC_THRESHOLD}")
        if abs(r["icir"]) < ICIR_THRESHOLD:
            reasons.append(f"ICIR={r['icir']:.2f}<{ICIR_THRESHOLD}")
        if name == "lookahead":
            reasons.append("⚠ 前视陷阱：因子与预测收益同源，IC 虚高——正确检验必须 t→t+h 错位")
        if reasons:
            rejected[name] = "; ".join(reasons)
            continue
        if selected:
            max_c = max(abs(corr_matrix.loc[name, s]) for s in selected)
            if max_c > CORR_CAP:
                rejected[name] = f"与已选因子最高相关 {max_c:.2f} > {CORR_CAP}（冗余）"
                continue
        selected.append(name)

    print(f"\n✅ 通过 {len(selected)} 个: {selected}")
    print("❌ 淘汰:")
    for k, v in rejected.items():
        print(f"   - {k}: {v}")

    # 分层回测（仅演示管道正确性）：前1/3 - 后1/3 日频多空
    print("\n" + "=" * 80)
    print("附加：入选因子等权组合 前1/3-后1/3 日频多空（不含成本，仅演示）")
    print("=" * 80)
    if selected:
        combo = sum(factors[s].rank(axis=1) for s in selected) / len(selected)
        fwd1 = make_fwd_ret(close, 1)
        daily = []
        for day in combo.index:
            f, r = combo.loc[day], fwd1.loc[day]
            m = f.notna() & r.notna()
            if m.sum() < 10:
                continue
            ff, rr = f[m], r[m]
            k = max(1, int(len(ff) / 3))
            daily.append(ff.nlargest(k).index.map(lambda s: rr[s]).mean()
                         - ff.nsmallest(k).index.map(lambda s: rr[s]).mean())
        daily = pd.Series(daily).dropna()
        if len(daily) > 10:
            cum = (1 + daily).prod()
            sharpe = daily.mean() / daily.std() * np.sqrt(252) if daily.std() > 0 else 0
            print(f"  样本天数 {len(daily)} | 累计多空 {cum-1:.2%} | 年化Sharpe(粗) {sharpe:.2f}")
            print("  ⚠ 仅验证管道正确性，不代表因子实盘有效（未计成本/未样本外）。")

    pd.to_pickle({
        "ic_table": result[["ic", "icir", "rank_ic", "rank_icir"]].round(4),
        "decay_table": decay_df.round(4),
        "corr_matrix": corr_matrix.round(3),
        "selected": selected,
        "rejected": rejected,
    }, os.path.join(OUT_DIR, "result_summary.pkl"))
    print("\n[完成] 结果已存 result_summary.pkl")


if __name__ == "__main__":
    main()
