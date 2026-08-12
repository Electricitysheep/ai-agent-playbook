# -*- coding: utf-8 -*-
"""
实验 05：Point-in-Time 数据库为什么重要 —— 幸存者偏差量化演示
=============================================================
Qlib 的核心设计之一是 point-in-time (PIT) 数据库：每个时点只提供"当时可知"的数据，
杜绝幸存者偏差与前视。本实验用真实 A 股数据量化"幸存者偏差"的危害：

1) 拉取 30 只 A 股大盘股 3 年日线
2) 模拟"退市"：按"死亡前 6 个月累计收益最低"标记 1/3 股票为退市股
   （真实世界规律：退市前往往持续下跌），死亡点后数据缺失
3) 视角 A（PIT，正确）：每时点等权持有"当时有数据"的全部股票
   ——退市股死亡前仍被持有，其亏损被如实计入
4) 视角 B（幸存者，错误）：整个回测只持有最终存活的股票
   ——等价于"用今天还活着的股票回测过去"，退市股亏损被系统性剔除
5) 对比两视角累计收益 → 量化幸存者偏差的虚高幅度

运行: python main.py
环境: Python 3.14 / pandas / yfinance（联网拉数据）
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

TICKERS = [
    "600519.SS", "601318.SS", "600036.SS", "000858.SZ", "601899.SS",
    "600030.SS", "000333.SZ", "601166.SS", "600900.SS", "000651.SZ",
    "601012.SS", "600276.SS", "002594.SZ", "600887.SS", "601888.SS",
    "000568.SZ", "600309.SS", "601088.SS", "600585.SS", "000001.SZ",
    "002415.SZ", "601668.SS", "600028.SS", "000002.SZ", "601857.SS",
    "600104.SS", "002475.SZ", "601688.SS", "600690.SS", "002230.SZ",
]


def load_data(force=False):
    """拉 30 只 A 股大盘股 3 年日线 close，返回 date×symbol 矩阵。"""
    if os.path.exists(DATA_CACHE) and not force:
        d = pd.read_pickle(DATA_CACHE)
        print(f"[数据] 缓存加载: {d.shape}")
        return d
    closes = {}
    for t in TICKERS:
        try:
            raw = yf.download(t, period="3y", interval="1d", progress=False, auto_adjust=True)
            if not raw.empty:
                closes[t] = raw["Close"].squeeze()
        except Exception:
            pass
    df = pd.DataFrame(closes).sort_index()
    pd.to_pickle(df, DATA_CACHE)
    print(f"[数据] 拉取完成: {df.shape}，{df.shape[1]} 只股票")
    return df


def make_deaths(close, frac=1 / 3):
    """模拟退市：按'死亡前 6 个月累计收益最低'标记退市股（真实退市股生前跑输），
    死亡点后数据缺失。返回 (masked 矩阵, dead 列表, death_point)。"""
    death_point = int(len(close) * 0.66)
    lookback = close.iloc[death_point - 120:death_point]
    perf = lookback.iloc[-1] / lookback.iloc[0] - 1
    n_dead = int(len(close.columns) * frac)
    dead = list(perf.nsmallest(n_dead).index)
    masked = close.copy()
    masked.loc[masked.index[death_point:], dead] = np.nan
    return masked, dead, death_point


def ew_portfolio_pit(masked):
    """PIT 视角：每时点等权持有'当时有数据'的股票，返回日收益序列。"""
    ret = masked.pct_change().clip(-0.10, 0.10)
    n = masked.notna().sum(axis=1)
    port = (ret * masked.notna()).sum(axis=1) / n.replace(0, np.nan)
    return port.dropna()


def ew_portfolio_survivor(masked, dead):
    """幸存者视角：整个回测只持有非退市股（退市股被完全排除）。"""
    alive = masked.drop(columns=dead)
    return ew_portfolio_pit(alive)


def report(name, pnl):
    if len(pnl) < 20:
        return
    cum = (1 + pnl).prod()
    ann_ret = (1 + pnl).prod() ** (252 / len(pnl)) - 1
    vol = pnl.std() * np.sqrt(252)
    sharpe = ann_ret / vol if vol > 0 else 0
    print(f"  {name:<30} 年化 {ann_ret:>7.2%} | 年化Sharpe {sharpe:>5.2f} | 累计 {cum-1:>7.2%}")


def main():
    close = load_data()
    masked, dead, death_point = make_deaths(close)
    print(f"\n[模拟] 标记 {len(dead)}/{close.shape[1]} 只股票为退市（死亡前 6 个月收益最低）:")
    print(f"  {list(dead)}")
    print(f"  死亡点 = 第 {death_point}/{len(close)} 个交易日（{close.index[death_point].date()}）")

    print("\n" + "=" * 78)
    print("对比：PIT 等权组合 vs 幸存者等权组合（真实数据，3 年）")
    print("=" * 78)
    pit = ew_portfolio_pit(masked)
    surv = ew_portfolio_survivor(masked, dead)
    report("PIT（每时点可知截面）", pit)
    report("幸存者偏差（剔除退市股）", surv)

    if len(pit) > 20 and len(surv) > 20:
        bias = (1 + surv).prod() / (1 + pit).prod() - 1
        print(f"\n  >>> 幸存者偏差造成的累计收益虚高: {bias*100:+.1f}%")
        print("  （正值 = 幸存者视角虚高；退市股死亡前跑输越多，虚高越明显）")

    print("\n" + "=" * 78)
    print("Qlib PIT 数据库对应关系（供面试叙述）")
    print("=" * 78)
    print("""
Qlib 的 point-in-time 设计（GitHub PR #343, 2022-03）：
1. 数据按 (instrument, datetime) 存储，带 'update_time' 字段——因子值只有在
   update_time 之后才可用，天然杜绝未来函数；
2. 成分股列表也是 PIT 的：回测某天用"那天实际是成分股"的股票，
   而不是"今天还是成分股"的股票（本实验的视角 A vs B 之差就是幻觉量）；
3. 实测意义：本实验显示，仅'剔除退市股'这一项就足以系统性扭曲回测收益，
   不修 PIT，后面所有因子/模型结论都建立在幻觉之上。
""")


if __name__ == "__main__":
    main()
