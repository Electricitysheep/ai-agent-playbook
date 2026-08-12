# 05. 端到端 AI 量化管线（Qlib + RD-Agent）

> 对应实验：`04_代码实验/05_Qlib_PIT数据库与幸存者偏差/`（✅ 已运行）
> 关联：主报告 §3.3 ｜ 底稿 C3 ｜ 主题 01（LLM 因子）、主题 07（回测纪律）
> 完成日期：2026-08-09

## 5.1 是什么（30 秒版）

Qlib 是微软开源的 AI 量化平台（arXiv 2009.11189），覆盖"数据处理→因子→模型→回测→组合"
全链路，核心资产是 **point-in-time (PIT) 数据库**（每个时点只提供当时可知的数据，杜绝
前视与幸存者偏差）。RD-Agent(Q)（arXiv 2505.15155，NeurIPS 2025）是微软在其上构建的
**数据为中心的多智能体自动研究框架**：五单元闭环（Specification 设定 → Synthesis 提假设 →
Implementation 用 Co-STEER 写代码 → Validation 回测 → Analysis 用 bandit 选方向），
让"因子挖掘 + 模型优化"自动化、可累积、可解释。

## 5.2 为什么重要（行业证据）

- **RD-Agent(Q) 实证**（arXiv 2505.15155，NeurIPS 2025）：
  - **成本 <$10**（LLM API 开销）即可达到约 **2 倍于经典因子库的年化收益**，且**少用 70% 因子**；
  - 联合优化（因子+模型）下 o3-mini 达 IC 0.0532 / ARR 14.21% / IR 1.74，显著超 Alpha158/TRA 基线；
  - 超过 SOTA 深度时序模型（更小资源预算下）。
- **中国市场落地**：主报告 §3.3——国内出现"36 个 Loop 触发 11 次 SOTA 更新"案例；
  融量 AlphaMind 让 6 个国产大模型 20 轮迭代挖换手率反转因子（2026-05-08，二手待核）；
  东吴证券从"优化"升级为"生成"范式（2026-01）。RD-Agent 是国内 AI 因子自动化的事实标准之一。
- **Qlib 生态**：qrun 一行命令跑完整工作流；LightGBM+Alpha158 官方示例 IR 1.997（无成本）/
  1.444（含成本）；PIT 数据库 2022-03 引入（GitHub PR #343）后成为回测纪律的参考实现。

## 5.3 怎么做（方法步骤 + 关键点 + 踩坑点）

### Qlib 全链路（qrun 工作流，官方配置示例）

```
数据(provider_uri=~/.qlib/qlib_data/cn_data, market=csi300)
  → 特征(Alpha158DL + StaticDataLoader 载入预计算因子 parquet ← LLM 因子接入点)
  → 归一化(RobustZScoreNorm/Fillna/CSZScoreNorm)
  → 训练(GeneralPTNN / LightGBM，train 2008-2014 / valid 2015-2016 / test 2017-2020)
  → 回测(TopkDropoutStrategy，top50 随机丢 5，含成本/滑点)
  → 记录(SignalRecord/SigAnaRecord/PortAnaRecord)
```

### LLM 因子如何插进 Qlib（RD-Agent 官方做法）

RD-Agent(Q) 用 **nested data loader** 组合两类特征：
```yaml
# 官方 quant_agent_fin.rst 配置
features:  # 嵌套：Alpha158 工程特征 + LLM 生成因子
  - class: ...Alpha158DL        # 经典 158 个工程特征（RESI5/WVMA5/RSQR5/KLEN...）
  - class: ...StaticDataLoader  # 载入 LLM 因子 parquet (combined_factors_df.parquet)
```

### RD-Agent(Q) 五单元闭环（数据为中心，因子-模型联合优化）

```
[Specification] 根据优化目标动态设定 goal-aligned prompts
[Synthness]     从历史结果的知识森林长出新因子/模型假设 → 映射为可执行任务
[Implementation] Co-STEER 代码生成 agent（CoT + 图结构知识库）
[Validation]    因子去重（与 SOTA 库 IC_max ≥ 0.99 判冗余剔除）→ Qlib 回测
[Analysis]      统一指标评估 + multi-armed bandit 调度器选下一步方向
      ↑___________________ 循环（持续、自主、知识累积）___________________|
```

### 踩坑点（面试高频）

1. **PIT 是回测真实性的地基**：不修 PIT，后面所有因子/模型结论都建立在幻觉上
   （本实验量化：仅剔除退市股就虚高 +6.8% 累计收益）。
2. **LLM 因子必须过去重**：RD-Agent 用 IC_max ≥ 0.99 与 SOTA 因子库判冗余——对应
   Chain-of-Alpha 的 Diversity 维度（主题 01），两道检验殊途同归。
3. **自动化的过拟合风险**：循环越多，越容易对回测区间过拟合——RD-Agent 依赖
   bandit 调度器 + 严格样本外（test 2017-2020 独立于 fit 2008-2014），但仍需
   walk-forward 复核（主题 07）。
4. **环境兼容**：Qlib 官方仅支持 Python ≤3.12（本机 3.14 无法安装 pyqlib，见实验记录）；
   生产用 Docker 或 Linux 环境。

## 5.4 真实数字（标注来源与口径）

| 数字 | 来源 | 口径 |
|---|---|---|
| 成本 <$10 → 2× 年化收益、少用 70% 因子 | arXiv 2505.15155（NeurIPS 2025） | 真实市场回测，LLM API 成本 |
| o3-mini 联合优化：IC 0.0532 / ARR 14.21% / IR 1.74 | arXiv 2505.15155 | CSI 300，2017-2020 测试期 |
| LightGBM+Alpha158 官方示例：IR 1.997（无成本）/1.444（含成本） | Qlib GitHub 官方示例 | qrun 默认工作流 |
| 36 Loop 触发 11 次 SOTA 更新 | 主报告 §3.3（二手） | 国内团队案例 |
| 本实验：幸存者偏差虚高 +6.8% 累计收益（年化 2.82% vs 5.19%） | 实验 05（2026-08-09） | 30 只 A 股 3 年，模拟 10 只退市 |

## 5.5 我的可复现实验（做了什么/结果/结论）

**实验 05：PIT 数据库 + 幸存者偏差量化**（✅ 运行成功，2026-08-09）
- **做了什么**：pyqlib 在 Python 3.14 无 wheel（官方仅支持 ≤3.12，**运行失败原因已记录**），
  改用等价实验：拉 30 只 A 股大盘股 3 年日线，模拟 10 只"退市股"（死亡前 6 个月收益最低，
  死亡点后数据缺失），对比 PIT 等权组合（每时点用可知截面）vs 幸存者组合（剔除退市股）。
- **结果**：PIT 年化 2.82%（累计 +8.35%）vs 幸存者年化 5.19%（累计 +15.75%）——
  **幸存者偏差虚高 +6.8% 累计收益**，Sharpe 从 0.17 虚高到 0.31。
- **结论**：仅"剔除退市股"一项就足以系统性扭曲回测——Qlib PIT 数据库的工程意义
  得到量化验证；与实习"杜绝未来函数"直接呼应。局限：模拟退市、等权组合不含成本。

## 5.6 面试话术

**30 秒故事**：
"我研究微软 Qlib + RD-Agent 的端到端管线，核心是 point-in-time 数据库——每个时点
只提供当时可知的数据。我做了个量化验证：30 只 A 股里模拟 10 只退市，用'今天还活着
的股票'回测过去，收益虚高 6.8%、Sharpe 从 0.17 虚高到 0.31——这就是幸存者偏差。
RD-Agent 在上面做了自动化闭环：五单元循环（设定→假设→Co-STEER 写代码→回测→bandit 选方向），
实测不到 10 美元 LLM 成本就能达到经典因子库 2 倍年化、少用 70% 因子。我实习里做的
7462 万行管道和'杜绝未来函数'的纪律，在 Qlib 里就是 PIT 数据库的设计——工程直觉
和理论框架对上了。"

**3 个数字**：
1. **+6.8%**：我实测幸存者偏差虚高的累计收益
2. **2× / 70%**：RD-Agent 相对经典因子库的年化提升与因子数量节省（成本 <$10）
3. **IC 0.0532 / IR 1.74**：RD-Agent 联合优化在 CSI 300 测试期的成绩

**可能的追问与应答**：
- Q：PIT 数据库具体怎么实现？
  A：数据按 (instrument, datetime) 存，带 update_time 字段；查询时加 `<= 该时点` 过滤，
  因子值只有 update_time 之后才可见。成分股列表同样 PIT 化（用"那天实际是成分股"的股票）。
- Q：RD-Agent 会不会过拟合？
  A：会，这是自动化的头号风险。它的防线：严格样本外划分（fit 2008-2014 / test 2017-2020）、
  bandit 调度器控制探索方向、因子去重（IC_max≥0.99 剔除）；但我面试时会强调仍需
  walk-forward 和实盘模拟复核（主题 07），自动化放大的是"发现效率"，不是"验证豁免"。
- Q：LLM 因子怎么进 Qlib？
  A：nested data loader：Alpha158DL（工程特征）+ StaticDataLoader（LLM 因子 parquet）
  拼接成特征集，走同一套归一化→训练→回测管道——LLM 产出的是"特征列"，不是"结论"，
  这保证了可检验性（IC/衰减/互补性三道检验在进库前完成，见主题 01）。

## 来源清单

- arXiv 2505.15155 R&D-Agent-Quant（NeurIPS 2025，https://arxiv.org/abs/2505.15155）
- Qlib GitHub（https://github.com/microsoft/qlib，PIT PR #343 2022-03；qrun 示例结果）
- RD-Agent GitHub + quant_agent_fin.rst 配置（https://github.com/microsoft/RD-Agent）
- arXiv 2009.11189 Qlib: An AI-oriented Quantitative Investment Platform
- 主报告 §3.3（2026-08-07）、底稿 C3（2026-08-07）
- 实验 05 main.py / README.md（2026-08-09）
- ⚠ pyqlib 安装失败记录：Python 3.14 无 wheel，官方支持 ≤3.12（2026-08-09）
