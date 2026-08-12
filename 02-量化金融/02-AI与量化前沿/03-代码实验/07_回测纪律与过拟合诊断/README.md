# 实验 07：多重检验与过拟合诊断 —— PSR / DSR / PBO / 白化检验

> 对应主题：`02_主题深度笔记/07_回测纪律与过拟合诊断.md`
> 关联文献：Lopez de Prado《Advances in Financial Machine Learning》、Bailey & Lopez de Prado (2014)
> Deflated Sharpe Ratio、Bailey et al. (2017) CSCV/PBO
> 运行日期：2026-08-09 ｜ 状态：✅ 运行成功

## 目的

用**纯随机数据**（真实 alpha=0）证明 Lopez de Prado 的核心论点：只要试的次数够多，
随机策略池里必然出现 Sharpe 高得吓人的"赢家"——它是选择偏差（winner's curse）的产物，
不是真 alpha。落地四道诊断：PSR / DSR / PBO / 白化检验。

## 运行环境

- Windows + Python 3.14 / numpy / scipy（纯 CPU，秒级）
- 运行命令：`python main.py`

## 实验设计

1. 生成 100 个"随机策略"：真实无 alpha（均值 0 的随机游走）+ 随机波动率模拟"不同策略"
2. 观察原始 Sharpe 分布与最优者（order statistic 效应）
3. PSR（概率夏普比）：单策略真实 SR>0 的概率（含偏度/峰度/样本长度修正）
4. DSR（去偏夏普比）：把 PSR 基准从 0 抬到 E[max(SR_N)]（N 次试验的期望最大）
5. PBO（回测过拟合概率，CSCV 非参数方法）：IS 最优策略 OOS 排到中位数以下的概率
6. 白化检验：IS/OOS 排名 Spearman 相关（真实策略应正相关，随机策略≈0）

## 结果摘要（2026-08-09 运行）

| 指标 | 数值 | 解读 |
|---|---|---|
| 100 个随机策略最优 Sharpe | **+2.618** | 真实 alpha=0！纯选择偏差 |
| PSR（未修正多重检验） | **1.000** | 看起来"铁定显著" |
| DSR（修正 N=100 次试验） | **0.428** | 修正后 = 抛硬币偏一点，不显著 |
| PBO（CSCV） | **24.2%** | 边界（健康 <25%） |
| 白化检验 Spearman | **+0.088 (p=0.382)** | IS/OOS 排名无关 = 纯白噪指纹 |

## 核心结论（面试可直接引用）

1. **赢家诅咒量化**：100 次试验能把纯噪声策略的 Sharpe 抬到 2.62——这就是为什么
   "AI 一个月发现成百上千信号"（Man Group 承认）时，DSR/PBO 是不可跳过的关卡。
2. **PSR → DSR 的落差是面试金句**：同一策略 PSR=1.00 但 DSR=0.43——"N 次试验挑最优"
   的事实让"显著"变"不显著"。
3. **白化检验是快速直觉**：IS 排名与 OOS 排名无关（r=0.088）→ 白噪。
4. **行业参照**：ARIA 实务"四门槛晋升"——walk-forward Sharpe 正 × PurgedKFold IC 达标 ×
   DSR>0.95 × PBO<0.25，全过才可实盘。

## 局限

- 随机策略用正态收益（真实收益偏度/峰度更高，DSR 修正更强）；
- CSCV 块数 10 为演示配置（论文建议更多块 + 多次随机分块取均值）；
- 本实验聚焦"多重检验"维度，walk-forward 的滚动窗口实现见主题笔记 07 5.3 节。

## 文件清单

- `main.py`：四道诊断完整实现
- `result.npz`：结果序列化
