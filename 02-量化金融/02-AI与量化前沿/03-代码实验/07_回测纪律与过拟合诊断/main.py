# -*- coding: utf-8 -*-
"""
实验 07：多重检验与过拟合诊断 —— PSR / DSR / PBO / 白化检验
=============================================================
面试最高频点：回测纪律。本实验用**纯随机数据**证明 Lopez de Prado 的核心论点：
"只要试的次数够多，随机策略池里必然出现一个 Sharpe 高得吓人的'赢家'——它是
选择偏差（winner's curse）的产物，不是真 alpha。"

实验内容（对应 Lopez de Prado 论文方法，全部可复现）：
1) 生成 100 个"随机策略"（真实无 alpha 的随机游走 + 随机参数）
2) 观察原始 Sharpe 分布：选最优者，Sharpe 必然虚高（order statistic 效应）
3) PSR（概率夏普比）：单个策略的真实 Sharpe > 0 的概率
4) DSR（去偏夏普比）：考虑 N 次试验后的概率——应显著低于 PSR
5) PBO（回测过拟合概率，CSCV 方法）：IS 最优策略 OOS 排到中位数以下的概率
6) 白化检验：IS/OOS 排名相关性 → 随机策略的 IS 排名与 OOS 排名无关

运行: python main.py
环境: Python 3.14 / numpy / scipy（纯 CPU）
"""

import sys
import warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import numpy as np
from scipy import stats

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(42)
N_TRIALS = 100      # 尝试的策略变体数（多重检验规模）
T = 500             # 每个策略的样本期（交易日，约 2 年）
S_BLOCKS = 10       # CSCV 的块数


def generate_strategy_returns(n_trials, T):
    """生成 n_trials 个随机策略的日收益：真实无 alpha（均值 0 的随机游走），
    每个策略有自己的噪声实现 + 随机波动率（模拟'不同策略'）。"""
    rets = np.zeros((n_trials, T))
    for i in range(n_trials):
        vol = RNG.uniform(0.005, 0.02)
        rets[i] = RNG.normal(0, vol, T)
    return rets


def sharpe(r, annualize=252):
    return r.mean() / r.std() * np.sqrt(annualize) if r.std() > 0 else 0.0


def psr(sh, T, sr_benchmark=0.0, skew=0.0, kurt=3.0):
    """Probabilistic Sharpe Ratio (Bailey & Lopez de Prado 2012)：
    P(真实 SR > SR_benchmark)。"""
    se = np.sqrt((1 - skew * sh + (kurt - 1) / 4 * sh**2) / (T - 1))
    if se == 0:
        return 1.0 if sh > sr_benchmark else 0.0
    return stats.norm.cdf((sh - sr_benchmark) / se)


def dsr(sh, T, n_trials, var_sr, skew=0.0, kurt=3.0):
    """Deflated Sharpe Ratio：把 PSR 的基准从 0 提升到 'N 次试验的期望最大 SR'。
    期望最大 SR 用极值理论近似：E[max] ≈ sqrt(2*log(N)) * (1/sqrt(T)) 的尺度修正，
    这里用论文的 Var(SR) 版本。"""
    if n_trials <= 1:
        sr0 = 0.0
    else:
        gamma = 0.5772  # Euler-Mascheroni
        sr0 = np.sqrt(2 * np.log(n_trials)) * np.sqrt(var_sr)
        sr0 += gamma / np.sqrt(2 * np.log(n_trials)) * np.sqrt(var_sr)
    return psr(sh, T, sr_benchmark=sr0, skew=skew, kurt=kurt)


def cscv_pbo(rets, s_blocks=S_BLOCKS):
    """Combinatorially Symmetric Cross-Validation (Bailey et al. 2017)：
    把每策略收益序列分成 S 块，遍历所有 S/2 选法做 IS/OOS 划分，
    统计 'IS 最优策略在 OOS 排到中位数以下' 的比例 = PBO。"""
    n, T = rets.shape
    block_len = T // s_blocks
    rets_cut = rets[:, :s_blocks * block_len]
    blocks = [rets_cut[:, b * block_len:(b + 1) * block_len] for b in range(s_blocks)]
    from itertools import combinations
    combos = list(combinations(range(s_blocks), s_blocks // 2))
    overfit = 0
    for iso in combos:
        oos_idx = [b for b in range(s_blocks) if b not in iso]
        is_ret = sum(blocks[b] for b in iso).sum(axis=1)  # 按块累加
        oos_ret = sum(blocks[b] for b in oos_idx).sum(axis=1)
        # IS 最优策略在 OOS 的排名
        best_is = np.argmax(is_ret)
        oos_rank = stats.rankdata(oos_ret)[best_is] / n  # 归一化排名
        if oos_rank < 0.5:
            overfit += 1
    return overfit / len(combos)


def whitening_test(rets):
    """白化检验：IS 前半段排名 vs OOS 后半段排名的 Spearman 相关。
    真实策略应正相关（排名保持）；随机策略应接近 0。"""
    half = rets.shape[1] // 2
    is_sh = np.array([sharpe(rets[i, :half]) for i in range(len(rets))])
    oos_sh = np.array([sharpe(rets[i, half:]) for i in range(len(rets))])
    rho, p = stats.spearmanr(is_sh, oos_sh)
    return rho, p


def main():
    print("=" * 78)
    print("生成 100 个随机策略（真实无 alpha）的日收益序列")
    print("=" * 78)
    rets = generate_strategy_returns(N_TRIALS, T)
    sh_all = np.array([sharpe(r) for r in rets])
    print(f"  原始 Sharpe 分布: 均值 {sh_all.mean():+.3f} | 标准差 {sh_all.std():.3f} | "
          f"最大 {sh_all.max():+.3f}")

    best_idx = np.argmax(sh_all)
    sh_best = sh_all[best_idx]
    r = rets[best_idx]
    skew = stats.skew(r)
    kurt = stats.kurtosis(r, fisher=False)  # 非超额峰度

    print("\n" + "=" * 78)
    print("赢家诅咒：'最优'策略的 Sharpe 与显著性")
    print("=" * 78)
    print(f"  N={N_TRIALS} 次试验中的最优 Sharpe = {sh_best:+.3f}（真实 alpha = 0）")
    p_psr = psr(sh_best, T, skew=skew, kurt=kurt)
    print(f"  PSR (概率夏普比, 基准=0)      = {p_psr:.3f}  ← 未修正多重检验")
    var_sr = np.var(sh_all)
    p_dsr = dsr(sh_best, T, N_TRIALS, var_sr, skew=skew, kurt=kurt)
    print(f"  DSR (去偏夏普比, N={N_TRIALS})  = {p_dsr:.3f}  ← 修正后")
    print(f"  → DSR 远低于 PSR: 考虑'N 次试验挑最优'后，这个 Sharpe 不再显著")
    print(f"  → 面试话术: 'Sharpe 1.5 是 1 次试验还是 100 次试验试出来的？后者毫无意义'")

    print("\n" + "=" * 78)
    print("PBO（回测过拟合概率，CSCV 方法）")
    print("=" * 78)
    pbo = cscv_pbo(rets)
    print(f"  PBO = {pbo:.1%}")
    if pbo > 0.5:
        print("  → IS 最优策略 OOS 排到中位数以下的概率 > 50%：选择过程纯噪声")
    print("  → 健康阈值: PBO < 0.25（Lopez de Prado 建议）；> 0.5 = 过拟合")

    print("\n" + "=" * 78)
    print("白化检验：IS/OOS 排名相关（真实策略应正相关）")
    print("=" * 78)
    rho, p_val = whitening_test(rets)
    print(f"  Spearman(IS 排名, OOS 排名) = {rho:+.3f} (p={p_val:.3f})")
    if abs(rho) < 0.1:
        print("  → 接近 0：IS 最优与 OOS 表现无关 = 纯白噪（随机策略的指纹）")
    print("  → 真实策略应有显著正相关（r>0.2 且 p<0.05），否则是噪声")

    print("\n" + "=" * 78)
    print("结论与面试要点")
    print("=" * 78)
    print(f"""
1. 100 个随机策略的最优 Sharpe 被'挑'到了 {sh_best:+.2f}，尽管真实 alpha=0——
   这是 order statistic（选择偏差），不是 alpha。试的次数越多，虚高越狠。
2. 三道防线（本实验全部落地）：
   - PSR：单个策略显著性的诚实度量（含偏度/峰度/样本长度修正）
   - DSR：把 PSR 的基准从 0 抬到 E[max(SR_N)]——N 越大门槛越高
   - PBO：选择过程本身的稳定性（CSCV 非参数，无模型假设）
3. 白化检验是快速直觉：IS/OOS 排名不相关 = 白噪。
4. 面试用法：'我跑过 100 个因子变体，DSR 从 0.99 掉到 0.62'——
   这比任何'我们 Sharpe 3.0'都有说服力，因为它证明你懂统计。
""")
    np.savez(os.path.join(OUT_DIR, "result.npz"),
             sh_all=sh_all, psr=p_psr, dsr=p_dsr, pbo=pbo, whitening_rho=rho)
    print("[完成] 结果已存 result.npz")


if __name__ == "__main__":
    main()
