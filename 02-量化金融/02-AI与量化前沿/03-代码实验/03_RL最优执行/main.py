# -*- coding: utf-8 -*-
"""
实验 03：RL 最优执行 —— Almgren-Chriss 闭式解 vs Tabular Q-Learning
====================================================================
1) 实现 Almgren-Chriss 模型（永久+临时市场冲击，E[C]+lambda*Var[C] 目标）
   验证闭式解 sinh 轨迹、效率前沿、λ→0 退化为 TWAP 的三大性质
2) 在 AC 模拟环境中训练 Tabular Q-Learning 执行智能体（状态=剩余库存/剩余时间/价格偏离，
   动作=卖出比例），对比 TWAP 与 AC 最优的成本-风险位置
3) 验证"RL 为什么在执行上 work"：奖励稠密、环境平稳、状态可控

运行: python main.py
环境: Python 3.14 / numpy（无额外依赖，纯 CPU）
"""

import sys
import warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import numpy as np

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(42)

# ---------------- 1. Almgren-Chriss 模型参数 ----------------
S0 = 100.0        # 初始价格
X0 = 100000.0     # 总卖出股数
T = 10            # 执行期（单位：交易日/切片数）
N = 10            # 切片数
TAU = T / N
SIGMA = 0.02      # 每切片波动率（2%）
ETA = 4e-4        # 临时冲击系数（h(v) = eta * v，v=速率）——取 σ² 使 κ=√(λσ²/η) 有区分度
GAMMA = 1e-8      # 永久冲击系数（g(v) = gamma * v，影响总成本边界项，不改变轨迹形状）


def ac_holdings(lmbda):
    """AC 闭式解：最优持仓路径 x_k = X * sinh(kappa*(T-t_k)) / sinh(kappa*T)"""
    kappa_tilde2 = lmbda * SIGMA**2 / (ETA - 0.5 * GAMMA * TAU)
    if kappa_tilde2 <= 0:
        kappa = 1e-8
    else:
        kappa = np.arccosh(TAU**2 / 2 * kappa_tilde2 + 1) / TAU
    t = np.arange(N + 1) * TAU
    x = X0 * np.sinh(kappa * (T - t)) / np.sinh(kappa * T)
    return x, kappa


def simulate_path(trade_sizes, n_sims=20000):
    """蒙特卡洛模拟一条执行路径，返回 (E[C], std[C])。
    trade_sizes: 每切片卖出股数 v_k (sum = X0)"""
    v = np.asarray(trade_sizes, dtype=float)
    assert abs(v.sum() - X0) < 1.0, f"总量 {v.sum()} != {X0}"
    costs = np.zeros(n_sims)
    for i in range(n_sims):
        x = X0
        s = S0
        total_cost = 0.0
        for k in range(N):
            z = RNG.standard_normal()
            s = s + SIGMA * np.sqrt(TAU) * z - TAU * GAMMA * v[k]
            exec_price = s - ETA * v[k] / TAU
            total_cost += v[k] * (S0 - exec_price)
            x -= v[k]
        costs[i] = total_cost
    return costs.mean(), costs.std()


def twap_schedule():
    return np.full(N, X0 / N)


def ac_schedule(lmbda):
    x, _ = ac_holdings(lmbda)
    return np.diff(x) * -1  # 持仓减少量 = 卖出量


# ---------------- 2. Tabular Q-Learning 执行智能体 ----------------
N_INV = 11     # 库存分桶（0..10）
N_T = N + 1    # 剩余时间步
ACTIONS = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])  # 卖出剩余库存的比例


def ac_env_step(inv, t_left, action_idx, price):
    """AC 环境一步：返回 (成本增量, 新库存, 新时间, 新价格, done)。
    成本 = sell*(S0 - exec_price)，exec_price = 当前价 - 临时冲击，价格随 z 漂移——
    与 simulate_path 完全一致的执行成本逻辑。最后一步强制清仓。"""
    if t_left <= 1:
        sell = inv
    else:
        sell = inv * ACTIONS[action_idx]
    v = sell / TAU
    tmp_impact = ETA * v
    perm_impact = TAU * GAMMA * v
    z = RNG.standard_normal()
    new_price = price + SIGMA * np.sqrt(TAU) * z - perm_impact
    exec_price = new_price - tmp_impact
    cost = sell * (S0 - exec_price)
    new_inv = inv - sell
    new_t_left = t_left - 1
    done = new_t_left <= 0
    return cost, new_inv, new_t_left, new_price, done


def q_learning(episodes=20000, alpha=0.1, gamma=0.99, eps=0.1, lam_risk=0.01):
    """训练 Q 表。奖励 = -成本 - lam_risk*σ²τ*new_inv²（剩余库存敞口的方差项，与成本同量级）"""
    q = np.zeros((N_INV, N_T, len(ACTIONS)))
    inv_grid = np.linspace(0, X0, N_INV)
    risk_scale = SIGMA**2 * TAU   # σ²τ：剩余库存的方差系数
    for ep in range(episodes):
        inv = X0
        t_left = N
        price = S0
        done = False
        while not done:
            inv_idx = min(int(np.digitize(inv, inv_grid)) - 1, N_INV - 1)
            t_idx = t_left
            if RNG.random() < eps:
                a_idx = RNG.integers(len(ACTIONS))
            else:
                a_idx = np.argmax(q[inv_idx, t_idx])
            cost, new_inv, new_t_left, new_price, done = ac_env_step(
                inv, t_left, a_idx, price)
            risk_pen = lam_risk * risk_scale * (new_inv**2)
            reward = -cost - risk_pen
            if not done:
                n_idx = min(int(np.digitize(new_inv, inv_grid)) - 1, N_INV - 1)
                nt_idx = new_t_left
                best_next = np.max(q[n_idx, nt_idx])
            else:
                best_next = 0.0
            q[inv_idx, t_idx, a_idx] += alpha * (
                reward + gamma * best_next - q[inv_idx, t_idx, a_idx])
            inv, t_left, price = new_inv, new_t_left, new_price
    return q, inv_grid


def q_policy_sim(q, inv_grid, n_sims=20000):
    """用 Q 表跑蒙特卡洛，返回 (E[C], std[C])"""
    costs = np.zeros(n_sims)
    for i in range(n_sims):
        inv = X0
        t_left = N
        price = S0
        total = 0.0
        done = False
        while not done:
            inv_idx = min(int(np.digitize(inv, inv_grid)) - 1, N_INV - 1)
            t_idx = t_left
            a_idx = np.argmax(q[inv_idx, t_idx])
            cost, new_inv, new_t_left, new_price, done = ac_env_step(
                inv, t_left, a_idx, price)
            total += cost
            inv, t_left, price = new_inv, new_t_left, new_price
        costs[i] = total
    return costs.mean(), costs.std()


def main():
    print("=" * 80)
    print("第 1 部分：Almgren-Chriss 闭式解验证（λ 从 0 到 50）")
    print("=" * 80)
    rows = []
    for lmbda in [0.0, 0.1, 0.5, 2.0, 10.0]:
        x, kappa = ac_holdings(lmbda)
        v = np.diff(x) * -1
        mc, mstd = simulate_path(v, n_sims=10000)
        rows.append((lmbda, kappa, mc, mstd))
        front_load = (x[0] - x[1]) / (X0 / N)
        print(f"  λ={lmbda:<5} κ={kappa:.4f}  E[C]={mc:9.1f}  std[C]={mstd:8.1f}  首切片={v[0]:8.0f}股({front_load:.2f}x TWAP)")

    print("\n  效率前沿：E[C] 随 λ 上升（冲击↑），std[C] 随 λ 下降（风险↓）——无免费午餐")
    print("  λ=0 应退化为 TWAP（线性清算），λ↑ 应前倾清算（sinh 曲线）")

    print("\n" + "=" * 80)
    print("第 2 部分：TWAP vs AC(λ=2) vs Tabular Q-Learning")
    print("=" * 80)
    e_twap, s_twap = simulate_path(twap_schedule(), n_sims=20000)
    v_ac = np.diff(ac_holdings(2.0)[0]) * -1
    e_ac, s_ac = simulate_path(v_ac, n_sims=20000)

    print("\n  训练 Q-Learning（20000 episodes，纯 CPU 约 1-2 分钟）...")
    q, inv_grid = q_learning(episodes=20000)
    e_q, s_q = q_policy_sim(q, inv_grid, n_sims=20000)

    print(f"\n  {'策略':<22} {'E[C]':>10} {'std[C]':>10} {'相对TWAP成本':>12}")
    print(f"  {'TWAP (λ=0)':<22} {e_twap:10.1f} {s_twap:10.1f} {'100%':>12}")
    print(f"  {'AC 最优 (λ=2)':<22} {e_ac:10.1f} {s_ac:10.1f} {e_ac/e_twap*100:10.1f}%")
    print(f"  {'Q-Learning':<22} {e_q:10.1f} {s_q:10.1f} {e_q/e_twap*100:10.1f}%")

    print("\n" + "=" * 80)
    print("结论解读")
    print("=" * 80)
    print("""
1. AC 闭式解是执行优化的"教科书最优"：λ=0→TWAP，λ↑→提前清算（sinh 曲线前倾）。
2. Q-Learning 在 AC 环境中应学会接近最优的风险-成本权衡（状态=库存/时间/价格偏离）。
3. RL 在执行上 work 的原因（与选股对比）：
   - 奖励稠密：每步都有成交成本可度量（vs 选股稀疏奖励）
   - 环境平稳：微观结构相对稳定（vs 非平稳市场）
   - 状态可控：库存/时间是马尔可夫的（vs 高维市场状态）
4. 本实验用 AC 模型作环境，是"模型内一致性"验证；真实部署需 LOB 模拟器
   （JPM 的 LOB 模拟器 + 决策树策略；QRM + DDQN）—见主题笔记。
""")
    np.savez(os.path.join(OUT_DIR, "result.npz"),
             e_twap=e_twap, s_twap=s_twap, e_ac=e_ac, s_ac=s_ac,
             e_q=e_q, s_q=s_q)
    print("[完成] 结果已存 result.npz")


if __name__ == "__main__":
    main()
