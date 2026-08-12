# 实验 08：行情数据工程实战 —— Pandas/Polars 双引擎 SBS 对齐 + 加速基准

> 对应主题：`02_主题深度笔记/10_行情数据工程实战.md`
> 衔接：用户实习故事（7462 万行分钟级行情、Pandas/Polars 双引擎对齐、6→54 因子、5-10 倍加速）
> 运行日期：2026-08-09 ｜ 状态：✅ 运行成功（含诚实修正）

## 目的

复现并验证用户实习核心方法：双引擎 SBS 对齐（0 误差重合）、Polars 加速、
parquet 因子存储——用可复现实验支撑简历数字。

## 运行环境

- Windows + Python 3.14（pandas 3.0.3 / polars 1.40.1 / numpy 2.4.6 / yfinance 1.5.1）
- 运行命令：`python main.py`（Part A 需联网拉分钟数据）

## 三部分结果（2026-08-09 运行）

### Part A：真实数据 SBS 对齐 ✅

- 5 只美股（AAPL/MSFT/NVDA/JPM/TSLA）5 天 1 分钟真实数据，9750 行
- 6 个因子（mom60/vol60/vwap_dev/rsi14/dd60/corr_pv）pandas 与 polars 各算一遍
- **最大绝对误差 0.00e+00（round(8) 截断口径）——双引擎 0 误差重合**
- 关键修复：vwap_dev 的"当日 VWAP"pandas 用 `groupby(date).transform(mean)`、
  polars 用 `.mean().over(["symbol", truncate("1d")])`——**必须定义一致才能对齐**，
  否则误差 5.6e-3（跨日滚动 vs 按日分组）

### Part B：1200 万行加速基准（合成数据）✅ 诚实报告

- 合成 30 只 × 250 天 × 1600 分钟 = **1200 万行**（仅用于引擎性能，不用于因子结论）
- pandas 2.84s vs polars 0.72s = **3.9x 加速**（3 个简单滚动因子）
- 诚实结论：本机 3.9x；实习中 5-10x 来自更大规模 + 54 因子复杂度 + polars 惰性求值，
  **加速比随任务复杂度上升**——不夸大实测数字

### Part C：parquet 因子存储 ✅

- 200 万行因子写入 zstd parquet：0.93s，文件 74.4 MB
- 全列读取 0.18s vs 仅 3 列 0.09s（列裁剪 1.9x）
- parquet 列式存储 + zstd 压缩 = 生产因子库标准范式

## 踩坑记录（面试可直接讲）

1. **MultiIndex 非唯一索引**：yfinance 分钟数据可能有重复时间戳（跨日界/盘前盘后），
   pandas `setitem` 时 `reindex` 抛 `Index._join_level on non-unique index`——
   修复：加载时 `drop_duplicates` + 因子计算用 dict 构造 DataFrame（位置对齐）；
2. **双引擎定义一致性**：同一因子两引擎必须用相同数学定义（按日分组 vs 跨日滚动），
   否则 SBS 对齐必失败——这是"对齐方法论"的核心；
3. **诚实报告**：实测 3.9x 就写 3.9x，不套用实习的 5-10x——面试讲"我复现过"比
   "我听说"可信。

## 文件清单

- `main.py`：三部分完整实现
- 无缓存文件（Part A 数据每次拉取；Part C 临时文件运行后删除）
