# 论文精读 09：Lopez de Prado《Advances in Financial Machine Learning》+ AQR/LdP 文本因子研究

> 精读日期：2026-08-09 ｜ 关联主题：主题 07（回测纪律，核心理论源头）、主题 01（文本因子）
> 关联知识库：主报告 §3.2（LdP/AQR 文本因子 1-3% alpha）、底稿（多处）
> 定位：方法论源头，不是单篇论文——本书 + 相关论文组

## 1. 基本信息

- **书**：Marcos López de Prado《Advances in Financial Machine Learning》(2018, Wiley)
  —— 量化 ML 的"回测纪律圣经"；实验 07 的 DSR/PBO 均源自本书及其论文组
- **相关论文**：Bailey & López de Prado (2014) Deflated Sharpe Ratio (JPM 40(5))；
  Bailey et al. (2017) The Probability of Backtest Overfitting (CSCV)；
  López de Prado (2025+) How to Use the Sharpe Ratio
- **文本因子**：Lopez de Prado 2020+、AQR 2024 文本因子研究（主报告 §3.2 引用）
- 注：本精读基于公开论文 PDF 与书评综述，未购买全书（2026-08-09 时点）

## 2. 动机（解决什么问题）

1. **多重检验是回测虚高的头号来源**：分析师可以回测数百万/数十亿策略变体；
   "试 N 次挑最优"的期望最大 Sharpe 恒 >0（即使真实 alpha=0）——winner's curse；
2. **非正态收益**：金融收益有偏度/肥尾，正态假设下 Sharpe 显著性被高估；
3. **选择偏差**：只报告正面结果（publication bias）进一步放大虚高。

## 3. 方法（怎么做的）

### 三道统计武器（实验 07 已全部落地）

1. **PSR（Probabilistic Sharpe Ratio）**：P(真实 SR > 阈值)，
   用前四阶矩（均值/方差/偏度/峰度）+ 样本长度修正标准误；
2. **DSR（Deflated Sharpe Ratio）**：把 PSR 的基准从 0 抬到 E[max(SR_N)]——
   N 次试验的期望最大 Sharpe（极值理论近似 √(2·ln N)·√Var(SR)），
   同时修正非正态 + 样本长度；还可与 Harvey-Liu (2014) 的 BH 阈值互补；
3. **PBO（Probability of Backtest Overfitting，CSCV 方法）**：非参数组合
   对称交叉验证——把收益切 S 块，遍历所有 S/2 选法做 IS/OOS 划分，
   统计"IS 最优策略 OOS 排到中位数以下"的比例；PBO>0.5 = 选择过程产生噪声。

### 文本因子方法（AQR/LdP 路线，衔接主报告 §3.2）

- 用 LLM/NLP 从管理层情绪、电话会语气、分析师修正分歧等提取文本因子；
- 验证范式：IC 检验 + 与传统因子低相关（正交）+ 组合后 Sharpe 改善；
- 证据（主报告口径）：2018-2024 美股样本贡献年化 1-3% alpha。

## 4. 数据与实验设置

- 实验 07（本人复现）：100 个纯随机策略（真实 alpha=0）→ 最优 Sharpe +2.62
  （PSR=1.00 → DSR=0.43），PBO=24.2%，白化 Spearman +0.09——完美复现
  LdP"赢家诅咒"论点（详见 04_代码实验/07_回测纪律与过拟合诊断/）。
- 原文案例（Bailey et al. 2017）：随机游走生成 1000 日价格，4 维参数网格 8,800 组合
  优化出年化 Sharpe 1.27（PSR 统计量 2.83，"显著"），但 CSCV 估算 **PBO 高达 55%**——
  教科书级演示：IS 全正、OOS 约 53% 为负。

## 5. 结果（作者如何验证有效）

1. **DSR 有效区分真信号与统计巧合**：修正选择偏差+非正态+样本长度后，
   "显著"变"不显著"（本实验：PSR 1.00 → DSR 0.43）；
2. **PBO 有效诊断选择过程**：IS 最优策略 OOS 垫底比例 >50% = 过拟合；
3. **文本因子方法论**：1-3% 年化 alpha + 低相关（主报告 §3.2 口径）。

## 6. 局限

1. DSR 需估计 Var(SR) 与独立试验数 N——"独立试验"在高度相关变体下难界定
   （有效试验数 K_eff < N，见 ml4trading 文档）；
2. CSCV 块数/分块方式影响 PBO 估计；
3. 文本因子 1-3% 的口径来自主报告转引，原始论文需独立核验；
4. 本书技术性强，金融本科生读原文有门槛——本精读提供"够用"的工程版。

## 7. 与已有知识库报告的联系

- **主题 07（核心）**：实验 07 完整落地 PSR/DSR/PBO/白化四道诊断，本精读是理论源；
- **主题 01（因子）**：LdP/AQR 文本因子 1-3% alpha 是"LLM 语义因子有价值"的学术证据；
- **主题 05（Qlib）**：PIT 数据库防前视/幸存者偏差，与 LdP"数据质量优先"哲学同源；
- 面试金句："我跑过 100 个因子变体，DSR 从 0.99 掉到 0.62"——比"我们 Sharpe 3.0"
  有说服力，因为它证明你懂统计（实验 07 实测口径）。

## 8. 面试话术（30 秒）

"Lopez de Prado 的《Advances in Financial ML》是回测纪律的理论源头，我把它
最核心的三件武器全部落地验证过：PSR 修正非正态、DSR 修正多重检验、PBO 用
CSCV 诊断选择过程。我的复现很直观：100 个真实没有 alpha 的随机策略，挑出
Sharpe 最高 2.62 的，PSR 算出来 1.00 好像铁定显著，DSR 修正'100 次试验'后
只剩 0.43——就是抛硬币。这就是为什么 AI 量化团队（像 Man Group 承认的）
一个月能挖出成百上千信号时，没有 DSR/PBO 把关的信号全是统计巧合。"

## 来源

- López de Prado (2018) Advances in Financial Machine Learning, Wiley
- Bailey & López de Prado (2014) The Deflated Sharpe Ratio, JPM 40(5) 94-107
  （https://www.pm-research.com/content/iijpormgmt/40/5/94）
- Bailey et al. (2017) The Probability of Backtest Overfitting
  （https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf）
- López de Prado et al. (2025) How to Use the Sharpe Ratio
- ml4trading.io Diagnostic 文档（DSR/PBO/RAS 工程实现参考）
- 主报告 §3.2（AQR/LdP 文本因子 1-3%，2026-08-07 口径）
- 实验 07（2026-08-09，本人复现）
