# 02. 时序基础模型（TSFM）选型与微调

> 对应实验：`04_代码实验/02_TSFM金融适配实测/`（✅ 已运行）
> 关联：底稿 D1 ｜ 主报告 §1（数据/因子层）｜ 论文精读清单：2511.18578
> 完成日期：2026-08-09

## 5.1 是什么（30 秒版）

TSFM（Time Series Foundation Models）= 在大规模异构时序上预训练的基础模型，
如 Google TimesFM-2.5、Amazon Chronos-2、Salesforce MOIRAI-2、Nixtla TimeGPT-2。
它们像 LLM 之于文本一样，试图让"预测任意时序"零样本可用。
**但金融是 TSFM 最难的应用场景**：噪声大（低信噪比）、非平稳（结构突变）、收益近随机游走。
2025-2026 多个独立研究（arXiv 2511.18578、arXiv 2606.27100、英国央行实时评估）的一致结论：
**零样本/微调在金融上表现平平，从金融数据"从头预训练"才有实质提升；TSFM 是有用的"先验"，不是"alpha 引擎"。**

## 5.2 为什么重要（行业证据）

- **Re(Visiting) TSFM in Finance**（arXiv 2511.18578，Rahimikia/Ni/Wang，2025-11-23）：
  首个 TSFM 金融全市场综合实证。用多市场日超额收益大样本评估零样本/微调/从头预训练：
  **开箱即用的预训练 TSFM 在零样本和微调设置下表现差；在金融数据上从头预训练的模型取得
  实质性的预测与经济效益提升**——领域适配的价值被量化验证（来源：arXiv 2511.18578）。
- **Pretrained TSFMs for Financial Return Forecasting**（arXiv 2606.27100，2026-06-25）：
  5 只美股（AAPL/AMZN/GOOG/JPM/META）× 10 个任务，等上下文预算 + 滚动原点协议：
  预训练 TSFM 拿下 8/10 任务胜，MOIRAI-2 和 TimesFM-2.5 平均排名最强；
  **但 Diebold-Mariano 检验仅 2/10 任务显著优于随机游走**（Chronos@AMZN、MOIRAI-2@GOOG）；
  iTransformer 在 META 两个任务上都赢——特定资产的本地监督学习仍可击败通用预训练；
  结论："TSFM 是降低开发成本的有用先验，但不是统计可靠的 alpha 引擎"（来源：arXiv 2606.27100）。
- **英国央行（SNB 附属研究）实时评估**（CCBS MPC, 2026-06）：每日宏观/金融序列实时滚动评估：
  仅 TimeGPT 稳定接近基准（median relRMSFE 1.047 vs BVAR 0.994）；**微调 vs 零样本配对对比中
  微调仅 27% 胜率**（TimeGPT 例外：58%）——微调在金融上甚至会过拟合（来源：Bank of England
  演示文稿 2026-06）。
- **TimesFM 金融微调实践**（Preferred Networks 技术博客，2025）：微调 SOTA 时序模型 TimesFM
  用于金融数据，损失与准确率显著优于传统模型——微调范式有效（来源：tech.preferred.jp）。
- **Marconi et al. (2025)**：TTM/Chronos 在美债收益率、EURUSD 波动率、股票价差三个任务上，
  预训练模型**少用 3-10 年数据**即可达到可比精度；但 3 个任务中 2 个传统专业模型仍打平或更好
  （来源：paperswithbacktest 综述转引）。
- **数据泄漏警示**：TSFM 评估若测试集与预训练语料重叠，准确率会被夸大 **47-184%**
  （来源：paperswithbacktest 综述，2026）——评估 TSFM 必须确认测试数据不在其训练语料中。

## 5.3 怎么做（方法步骤 + 选型决策 + 踩坑点）

### 四选一决策表（截至 2026-08）

| 模型 | 架构 | 预训练规模 | 金融适配度 | 适用场景 |
|---|---|---|---|---|
| TimesFM 2.5 (Google) | decoder-only transformer + 连续 patch embedding | 1000 亿+时间点（含合成） | 中（需微调） | 单变量日频、Google Cloud/BigQuery 生态 |
| Chronos-2 (Amazon) | T5 encoder-decoder + token 化（量化桶） | 大规模 + 合成选项 | 中（需微调） | 概率预测（输出分布）、5 档大小（9M-710M）、CPU 可跑 |
| MOIRAI-2 (Salesforce) | decoder-only + MoE + any-variate attention | LOTSA 270 亿观测、9 领域 | 中高（多变量首选） | **多资产组合**（股票间相关）、任意变量数 |
| TimeGPT-2 (Nixtla) | encoder-decoder（商业） | 含金融/经济数据 | **高（唯一在央行评估中稳定接近基准）** | 商业 API、agentic forecasting、私有化部署 |
| Lag-Llama / TTM / MOMENT | 变体 | 金融数据少 | 低 | 有更强替代时不推荐 |

**关键选型经验**：
1. 预训练语料含金融/经济数据的模型表现更好（英国央行：TimeGPT/Bolt/Chronos-2 强于 TTM/Lag-Llama，
   后者金融语料极少）；
2. 多变量场景用 MOIRAI-2（原生 any-variate attention），单变量快速原型用 Chronos-Bolt（9M，
   300+ 预测/秒）；
3. **永远先跑基准**：金融上必须过"随机游走/ARIMA + Diebold-Mariano"关卡，否则一切都是噪声。

### 标准评估协议（本实验已落地）

```python
# 1) 滚动原点：每次预测只用当时可得的历史（无前视）
starts = np.linspace(CONTEXT, len(series)-H, N_ROLLS).astype(int)
# 2) 候选 vs 随机游走：DM 检验（Newey-West 稳健方差）
d = (e_cand**2 - e_naive**2)          # 每步误差平方差
v = (gamma0 + 2*sum(gamma[1:h])) / T  # 异方差自相关稳健方差
dm = d.mean() / sqrt(v); p = 2*(1-norm.cdf(|dm|))
# 3) 判定：DM<0 且 p<0.05 才算"显著优于随机游走"
```

### 微调范式（当零样本不够时）

- **LoRA/Adapter 轻量微调**（FinGPT 数据为中心 + LoRA 范式，主报告 §2）；
- **从金融数据从头预训练**（2511.18578 结论：比微调更好，但要更多算力与数据）；
- 微调需防过拟合：英国央行实测微调平均只赢零样本 27%（TimeGPT 58% 例外）。

### 踩坑点（面试高频）

1. **收益 vs 价格**：直接预测价格（非平稳）几乎必败；应预测收益/超额收益（2511.18578 用超额收益）。
2. **数据泄漏**：预训练语料重叠夸大 47-184%——查模型训练集是评估第一关。
3. **信噪比幻觉**：RMSE 低几个百分点 ≠ 可交易 alpha；必须过 DM 显著性关卡（2606.27100 实测
   8/10 胜率但仅 2/10 显著）。
4. **未归一化价格**：Chronos 对高价位输出极端值（本实验 GOOG 初次 RMSE=6,080,026），
   部署必须有价格 clip guard。
5. **微调不是万能**：金融上微调可能引入过拟合；TimeGPT 是少数据微调仍赢的例外。

## 5.4 真实数字（标注来源与口径）

| 数字 | 来源 | 口径 |
|---|---|---|
| 预训练 TSFM 零样本/微调在金融上表现差；从头预训练才有实质提升 | arXiv 2511.18578（2025-11-23） | 多市场日超额收益 |
| 预训练 TSFM 8/10 任务胜；但 DM 检验仅 2/10 显著优于随机游走 | arXiv 2606.27100（2026-06-25） | 5 美股 × 10 任务，rolling-origin |
| 微调 vs 零样本：微调仅 27% 胜率（TimeGPT 例外 58%） | 英国央行 CCBS（2026-06） | 日频宏观/金融序列实时评估 |
| TimeGPT median relRMSFE 1.047 vs BVAR 0.994 / 随机游走 1.000 | 英国央行 CCBS（2026-06） | 22 变量 × 4 家族 |
| 评估集与预训练集重叠夸大准确率 47-184% | paperswithbacktest 综述（2026） | 多研究元分析 |
| 预训练模型少用 3-10 年数据达到可比精度 | Marconi et al. 2025 | 美债/EURUSD/价差 3 任务 |
| **本实验：5/5 只股票 Chronos 零样本显著差于随机游走**（DM 全正，4 只 p<0.01） | 实验 02（2026-08-09） | 5 美股日线，200 日上下文，h=5 |
| 本实验：ARIMA 与随机游走几乎持平（RMSE 相差 <1%） | 实验 02 | 同上 |
| 本实验：Chronos 对 GOOG 未 clip 时 RMSE=6,080,026 → clip 后 59.5 | 实验 02 | 同上 |
| TimeGPT-2 宣称最高 60% 准确率提升；Nixtla 获 $16M A 轮 | Nixtla 官方博客（2025-2026） | 厂商口径，需独立验证 |

## 5.5 我的可复现实验（做了什么/结果/结论）

**实验 02：TSFM 金融适配实测**（✅ 运行成功，2026-08-09）
- **做了什么**：5 只美股（AAPL/AMZN/GOOG/JPM/META）753 交易日日线，滚动原点协议
  （200 日上下文、预测 h=5、20 个原点），对比 Naive / ARIMA(1,1,0) / Chronos-t5-small 零样本，
  用 DM 检验判定显著性。Chronos 用 `chronos_manual.py` 手动实现（transformers 已移除 Chronos，
  自己实现 MeanScaleUniformBins tokenizer + T5 采样生成，含自检：线性趋势/正弦/随机游走行为符合直觉）。
- **结果**：**5/5 只股票 Chronos 零样本显著差于随机游走**（RMSE 为 Naive 的 4-5 倍；
  DM +2.45 ~ +4.64，4 只 p<0.01）。ARIMA 与 Naive 几乎持平（日频价格近随机游走）。
  工程发现：Chronos 对未归一化价格输出极端值（GOOG RMSE 6e6），加 clip guard 后 59.5。
- **结论**：零样本 TSFM 在日频价格预测上不是银弹——与 2511.18578 和英国央行结论一致；
  "TSFM 是有用先验、不是 alpha 引擎"在自己数据上得到验证。局限：零样本、日频、5 只股票；
  未测微调（微调是本主题的下一步）。

## 5.6 面试话术

**30 秒故事**：
"我做了一个 TSFM 金融适配的实证：用 5 只美股日线，滚动原点协议对比随机游走、ARIMA 和
Chronos-t5-small 零样本，用 Diebold-Mariano 检验判显著性。结果 5/5 只股票上 Chronos 零样本
都显著差于随机游走——这和 arXiv 2511.18578 还有英国央行的实时评估结论一致：TSFM 是好的
'先验'，但金融预测必须过随机游走关卡、必须领域适配。我还踩到一个真实工程坑：Chronos 对
未归一化价格会输出 600 万倍的 RMSE，必须有价格 clip guard。这个实验让我理解了为什么 2026
年行业说 TSFM 处于'金融适配期'。"

**3 个数字**：
1. **5/5**：我实测 Chronos 零样本在全部 5 只股票上显著差于随机游走
2. **8/10 vs 2/10**：2606.27100 中预训练 TSFM 任务胜率 8/10，但 DM 显著仅 2/10——胜率≠显著性
3. **27% vs 58%**：微调平均只赢零样本 27%，TimeGPT 例外 58%（英国央行）——模型间差异巨大

**可能的追问与应答**：
- Q：那 TSFM 到底能不能用？
  A：能用，但定位是"先验/特征提取器"而非"端到端预测器"：1) 少数据场景做 few-shot 起点；
  2) 预测目标用收益/超额收益而非价格；3) 必须过 DM 显著性关卡；4) 优先选预训练语料含金融的
  模型（TimeGPT/MOIRAI-2）；5) 有条件就从金融数据微调或从头预训练（2511.18578 证明更强）。
- Q：TimesFM 和 Chronos 怎么选？
  A：单变量快速原型 → TimesFM 2.5（连续 patch，Google 生态）或 Chronos-Bolt（9M、CPU 快）；
  多资产相关建模 → MOIRAI-2（原生 any-variate attention）；要概率分布 → Chronos-2（token 分布）。
  但任何选择都要先跑基准。
- Q：为什么微调在金融上反而更差？
  A：金融数据少、噪声大，微调容易过拟合到样本内噪声；英国央行实测微调只赢 27%。
  解决：少参数量微调（LoRA）、强正则化、严格样本外验证。
- Q：数据泄漏怎么防？
  A：查模型预训练语料是否含你的测试数据；用最新时段（2025-2026）数据做测试；
  对黑盒模型（TimeGPT）用时间戳错位检验。

## 来源清单

- arXiv 2511.18578 Re(Visiting) TSFM in Finance（https://arxiv.org/abs/2511.18578，2025-11-23）
- arXiv 2606.27100 Pretrained TSFMs for Financial Return Forecasting（https://arxiv.org/html/2606.27100，2026-06-25）
- Bank of England CCBS 演示稿 Real-Time Macroeconomic Forecasting with TSFMs（2026-06）
- paperswithbacktest: TimesFM vs Chronos vs MOIRAI 对比 + TSFM 金融挑战（https://paperswithbacktest.com/，2026）
- Nixtla 官方博客 TimeGPT-2 公告（2025-2026）
- Preferred Networks TimesFM 金融微调博客（https://tech.preferred.jp/en/blog/timesfm/，2025）
- 底稿 D1（2026-08-07）、主报告 §1
- 实验 02 main.py / chronos_manual.py / README.md（2026-08-09）
