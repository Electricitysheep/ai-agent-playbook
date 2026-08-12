# 实验 02：TSFM 金融适配实测 —— Chronos 零样本 vs 随机游走/ARIMA

> 对应主题：`02_主题深度笔记/02_时序基础模型TSFM选型与微调.md`
> 关联论文：Re(Visiting) TSFM in Finance (arXiv 2511.18578)、
> Pretrained TSFMs for Financial Return Forecasting (arXiv 2606.27100)、英国央行 CCBS 实时评估
> 运行日期：2026-08-09 ｜ 状态：✅ 运行成功

## 目的

复现"金融数据上预训练 TSFM 零样本表现平平"的核心结论，用 Diebold-Mariano 检验
把 **Chronos-t5-small 零样本** 与 **随机游走 / ARIMA(1,1,0)** 做严格对比。

## 运行环境

- Windows 11 + Python 3.14.2（torch 2.11.0 CPU / transformers 4.52.4 / statsmodels 0.14.6 / yfinance 1.5.1）
- 数据：yfinance 拉取 5 只美股（AAPL/AMZN/GOOG/JPM/META）近 3 年日线（753 交易日）
- 模型：amazon/chronos-t5-small（T5, 46M 参数, CPU 推理）
  - ⚠ 注意：Chronos 已从 transformers 官方移除（Amazon 许可证），本实验用 `chronos_manual.py`
    手动实现 MeanScaleUniformBins tokenizer + T5 采样生成（权重从 HF 下载 ~80MB）

## 运行命令

```bash
python main.py
```

（首次运行下载模型权重；CPU 上 20 rolls × 5 股票 × 3 模型约 10-20 分钟）

## 协议设计

- **滚动原点（rolling-origin）**：每次预测只用当时可得的历史（200 日窗口），
  更接近生产研究而非随机 train/test 分割（对应 2606.27100 的方法论）
- **预测目标**：未来 5 日价格
- **评估**：RMSE / MAPE + Diebold-Mariano 检验（Newey-West 稳健方差，滞后 h-1）
- **模型**：
  1. Naive（随机游走，last value）
  2. ARIMA(1,1,0) 滚动估计
  3. Chronos-t5-small 零样本（20 样本采样均值）

## 结果摘要（2026-08-09 运行）

| 股票 | RMSE Naive | RMSE ARIMA | RMSE Chronos | DM(Chronos vs Naive) | p 值 |
|---|---|---|---|---|---|
| AAPL | 5.65 | 5.67 | 28.22 | +4.64 | 0.000 |
| AMZN | 6.59 | 6.57 | 26.48 | +4.18 | 0.000 |
| GOOG | 10.64 | 10.66 | 59.50 | +2.45 | 0.014 |
| JPM | 6.61 | 6.61 | 37.81 | +4.43 | 0.000 |
| META | 17.28 | 17.29 | 82.88 | +2.98 | 0.003 |

**结论：5/5 只股票上 Chronos 零样本显著差于随机游走（DM 均为正、4 只 p<0.01）。**
ARIMA 与随机游走几乎持平（日频价格近随机游走）。

## 关键发现

1. **零样本 TSFM 在日频价格预测上不是银弹**——与 2511.18578（零样本/微调都差、需从金融数据
   从头预训练）和英国央行实时评估（只有 TimeGPT 稳定接近基准）结论一致。
2. **数据泄漏警示**：评估集与预训练集重叠会夸大准确率 47-184%（paperswithbacktest 综述，
   2026）；本实验用 2026 年数据 + 2024 年预训练模型，重叠风险低。
3. **工程细节**：Chronos 对未归一化价格会输出极端值（GOOG 初次 RMSE=6,080,026），
   真实部署必须有价格 clip guard（本实验 clip 到 [0.5×min, 1.5×max] 后 RMSE=59.5）。
4. **局限**：本实验是零样本、日频、5 只股票的小规模验证；微调后表现可能不同（英国央行发现
   微调平均只赢 27%，但 TimeGPT 微调赢 58%——模型间差异大）。

## 文件清单

- `main.py`：主实验（滚动原点 + 3 模型 + DM 检验）
- `chronos_manual.py`：Chronos 手动推理实现（tokenize → T5 采样 → decode）+ 自检
- `data_cache.pkl`：缓存行情
- `result_summary.pkl`：结果序列化
