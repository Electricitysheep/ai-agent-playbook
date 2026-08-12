# -*- coding: utf-8 -*-
"""
实验 11：LLM-MCTS 因子搜索骨架（stub 版，还原东吴研报方法论）
=================================================================
还原东吴证券 LLM-MCTS 可解释因子迭代框架（2026-06-23 研报）的核心结构，
用"规则生成器"代替真实 LLM（无 API key），验证 MCTS 搜索框架本身是否有效：

1) Seed 化：以真实因子为根节点（mom20/rev5/vol20 等 6 个基础因子）
2) MCTS 闭环：选择(UCT) → 扩展(规则生成器模拟 LLM 生成候选) → 评测(真实数据 IC)
   → 回传(reward 沿父链更新)
3) 双层验证：样本内选型 + 样本外仅验证（东吴"样本外不反选"铁律）
4) 结果：MCTS 搜索能否找到优于原始 Seed 的因子变体？与"随机生成"基线对比

数据：yfinance A 股（复用实验 09 的 55 只股票池），真实行情
说明：规则生成器 = 对父因子公式做"语义化改写"（窗口/算子/方向组合），
      模拟 LLM 生成候选的过程；真实 LLM 版本只需替换生成器（见 README 扩展说明）。

运行: python main.py
环境: Python 3.14 / yfinance / pandas / numpy
"""

import sys
import warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import math
import numpy as np
import pandas as pd
import yfinance as yf

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CACHE = os.path.join(OUT_DIR, "data_cache.pkl")
SEED_NAMES = ["mom20", "rev5", "vol20", "vwap_dev", "amt_trend", "high_low"]
N_ITER = 30          # MCTS 迭代轮数
N_CANDIDATES = 6     # 每轮扩展生成的候选数
IS_END = "2025-06-30"  # 样本内截止
HORIZON = 5

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


# ---------------- 因子定义（6 个 Seed + 规则变体） ----------------

def make_factor(name, window=20, sign=1):
    """返回一个因子函数：输入 close 矩阵 → 输出因子矩阵。窗口/方向参数化。"""
    def f(close):
        w = max(2, window)
        if name == "mom20":
            return sign * close.pct_change(w)
        if name == "rev5":
            return -sign * close.pct_change(w)
        if name == "vol20":
            return -sign * close.pct_change().rolling(w).std()
        if name == "vwap_dev":
            return sign * (close / close.rolling(w).mean() - 1)
        if name == "amt_trend":
            return sign * (close.rolling(5).mean() / close.rolling(w).mean())
        if name == "high_low":
            return -sign * (close.rolling(w).max() - close.rolling(w).min()) / close
        raise ValueError(name)
    return f


def factor_desc(fn_meta):
    """把因子元信息转成可读描述（模拟 LLM 输出的'解释'）。"""
    name, w, s = fn_meta
    direction = "正向" if s > 0 else "反向"
    return f"{name}(窗口={w},{direction})"


def rule_generator(parent_meta, rng):
    """规则生成器：模拟 LLM 围绕父因子生成候选（窗口 ± 变化、方向翻转、算子替换）。
    返回候选因子元信息列表 [(name, window, sign), ...]。"""
    candidates = []
    base_name, base_w, base_s = parent_meta
    for _ in range(3):
        w_new = max(3, base_w + int(rng.integers(-8, 9)))
        s_new = base_s * (1 if rng.random() > 0.3 else -1)
        candidates.append((base_name, w_new, s_new))
    for _ in range(3):
        other = rng.choice([n for n in SEED_NAMES if n != base_name])
        w_new = int(rng.integers(5, 30))
        s_new = 1 if rng.random() > 0.5 else -1
        candidates.append((other, w_new, s_new))
    return candidates


def compute_ic(factor_fn, close, end_date):
    """样本内 IC（截止 end_date，h=5）。返回平均 IC。"""
    f = factor_fn(close.loc[:end_date])
    ret = close.loc[:end_date].shift(-HORIZON) / close.loc[:end_date] - 1
    ics = []
    for d in f.index:
        ff, rr = f.loc[d], ret.loc[d]
        m = ff.notna() & rr.notna()
        if m.sum() < 15:
            continue
        ics.append(np.corrcoef(ff[m], rr[m])[0, 1])
    return float(np.mean(ics)) if ics else 0.0


def compute_ic_oos(factor_fn, close, start_date="2025-07-01"):
    """样本外 IC（start_date 之后）。"""
    f = factor_fn(close.loc[start_date:])
    ret = close.loc[start_date:].shift(-HORIZON) / close.loc[start_date:] - 1
    ics = []
    for d in f.index:
        ff, rr = f.loc[d], ret.loc[d]
        m = ff.notna() & rr.notna()
        if m.sum() < 15:
            continue
        ics.append(np.corrcoef(ff[m], rr[m])[0, 1])
    return float(np.mean(ics)) if ics else 0.0


# ---------------- MCTS 核心 ----------------

class MCTSNode:
    def __init__(self, meta, parent=None):
        self.meta = meta          # (name, window, sign)
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0.0
        self.best_ic = -1.0

    @property
    def ucb(self):
        if self.visits == 0:
            return float("inf")
        exploit = self.total_reward / self.visits
        explore = 1.4 * math.sqrt(math.log(max(self.parent.visits, 1)) / self.visits)
        return exploit + explore


def mcts_search(close, seed_meta, n_iter=N_ITER, n_cand=N_CANDIDATES, seed=42):
    rng = np.random.default_rng(seed)
    root = MCTSNode(seed_meta)
    best_node, best_ic = root, compute_ic(make_factor(*seed_meta), close, IS_END)
    root.best_ic = best_ic
    ic_cache = {}

    for it in range(n_iter):
        # 选择：从根出发按 UCB 选到叶子
        node = root
        while node.children:
            node = max(node.children, key=lambda c: c.ucb)
        # 扩展：生成候选
        candidates = rule_generator(node.meta, rng)[:n_cand]
        for meta in candidates:
            ic = ic_cache.get(meta)
            if ic is None:
                ic = compute_ic(make_factor(*meta), close, IS_END)
                ic_cache[meta] = ic
            child = MCTSNode(meta, parent=node)
            child.best_ic = ic
            node.children.append(child)
            # 回传
            reward = max(ic, 0.0)
            cur = child
            while cur is not None:
                cur.visits += 1
                cur.total_reward += reward
                cur = cur.parent
            if ic > best_ic:
                best_ic, best_node = ic, child
    return best_node, best_ic, ic_cache


def random_search_baseline(close, n_candidates=180, seed=7):
    """基线：随机生成同样数量的因子（不经过 MCTS 引导），取最优 IC。"""
    rng = np.random.default_rng(seed)
    best_ic, best_meta = -1.0, None
    for _ in range(n_candidates):
        name = rng.choice(SEED_NAMES)
        w = int(rng.integers(3, 30))
        s = 1 if rng.random() > 0.5 else -1
        meta = (name, w, s)
        ic = compute_ic(make_factor(*meta), close, IS_END)
        if ic > best_ic:
            best_ic, best_meta = ic, meta
    return best_meta, best_ic


def main():
    close = load_data()
    print(f"[行情] {close.shape[0]} 天 × {close.shape[1]} 只（样本内 ≤{IS_END}）")

    print("\n" + "=" * 78)
    print("Seed 因子基线（样本内 IC）")
    print("=" * 78)
    seed_best = None
    for name in SEED_NAMES:
        meta = (name, 20, 1)
        ic = compute_ic(make_factor(*meta), close, IS_END)
        print(f"  {name:<10} IC={ic:+.4f}")
        if seed_best is None or ic > seed_best[1]:
            seed_best = (meta, ic)
    print(f"  最优 Seed: {factor_desc(seed_best[0])} IC={seed_best[1]:+.4f}")

    print("\n" + "=" * 78)
    print(f"MCTS 搜索（{N_ITER} 轮 × {N_CANDIDATES} 候选/轮）")
    print("=" * 78)
    best_node, best_ic, cache = mcts_search(close, seed_best[0])
    print(f"  MCTS 最优: {factor_desc(best_node.meta)} 样本内 IC={best_ic:+.4f}")
    ic_oos = compute_ic_oos(make_factor(*best_node.meta), close)
    print(f"  样本外 IC（东吴'样本外仅验证不反选'）: {ic_oos:+.4f}")

    print("\n" + "=" * 78)
    print("基线对比：随机生成 vs MCTS")
    print("=" * 78)
    rand_meta, rand_ic = random_search_baseline(close, n_candidates=N_ITER * N_CANDIDATES)
    print(f"  随机基线最优: {factor_desc(rand_meta)} IC={rand_ic:+.4f}")
    print(f"  MCTS 最优:    {factor_desc(best_node.meta)} IC={best_ic:+.4f}")
    delta = best_ic - seed_best[1]
    print(f"  MCTS 相对最优 Seed 提升: {delta:+.4f}")

    print("\n" + "=" * 78)
    print("结论与局限")
    print("=" * 78)
    print("""
1. MCTS 用 UCB 引导搜索方向（exploit 高分节点 + explore 未访问节点），
   理论上比均匀随机更聚焦——本实验对比两者在相同候选预算下的最优 IC。
2. 规则生成器是 LLM 的占位：真实 LLM 版本只需替换 rule_generator 为
   '读父节点公式+评测反馈→生成带金融假说的公式'（东吴研报方法）。
3. 局限：样本内 IC 选择本身有过拟合风险（东吴靠'样本外不反选'+去重控制）；
   本实验仅验证 MCTS 框架，因子有效性需更大面板+DSR 复核。
""")
    pd.to_pickle({"seed_best": seed_best, "mcts_best": (best_node.meta, best_ic, ic_oos),
                  "random_best": (rand_meta, rand_ic)},
                 os.path.join(OUT_DIR, "result.pkl"))
    print("[完成] 结果已存 result.pkl")


if __name__ == "__main__":
    main()
