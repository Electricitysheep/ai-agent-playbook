# 论文精读 02：Fin-R1（arXiv 2503.16252）

> 精读日期：2026-08-09 ｜ 关联主题：主题 08（论文组）、主题 01（因子）、主题 06（另类数据）
> 关联知识库：主报告 §3.2、底稿 C2 ｜ 代码：https://github.com/SUFE-AIFLM-Lab/Fin-R1（700+ stars）

## 1. 基本信息

- **标题**：Fin-R1: A Large Language Model for Financial Reasoning through Reinforcement Learning
- **作者**：Zhaowei Liu 等（上海财经大学 SUFE-AIFLM-Lab + 财跃星辰）
- **发布**：2025-03-20（v1，至 v5）｜ 领域：cs/金融
- **模型**：Qwen2.5-7B-Instruct 基座 + SFT + GRPO（7B 参数）

## 2. 动机（解决什么问题）

金融 LLM 三大挑战：
1. **数据碎片化**：金融数据跨法律/经济/量化域，单一来源不够；
2. **推理不透明**：现有金融 LLM 黑箱，无法审计；
3. **业务泛化弱**：模型难迁移到真实业务场景（合规检查、智能投顾）。

**核心主张**：小模型（7B）+ 两阶段训练（SFT→RL）即可达到大模型级的金融推理能力。

## 3. 方法（怎么做的）

**两阶段流水线**：
1. **数据构建**：Fin-R1-Data——60,091 条高质量 CoT 样本，从多个权威基准蒸馏+两轮筛选
   （DeepSeek-R1 蒸馏；筛选标准：术语重叠度、推理步骤≥3、逻辑一致性、内容多样性等），
   覆盖 FinCorpus/FinQA/ConvFinQA/TFNS/Ant_Finance 等；
2. **训练**：
   - **SFT**：学"先思考再回答"，跨法律/经济/量化域推理；
   - **GRPO**（Group Relative Policy Optimization，PPO 的高效变体，无需价值网络）：
     双奖励 = 格式奖励（约束可解释结构）+ 准确率奖励；另引入 Qwen2.5-Max 模型验证器
     修正正则奖励偏差。

**关键发现（消融）**：单独 GRPO（Fin-R1-Zero）输出不连贯（67.8 分）；单独 SFT（Fin-R1-SFT）
71.9 分；SFT+GRPO 组合达 75.2——两阶段缺一不可。

## 4. 数据与实验设置

- **训练数据**：Fin-R1-Data 60,091 条 CoT（FinQA 2948 / ConvFinQA 2000 / TFNS 2451 / Ant_Finance 1548 / FinCorpus 29288 等）
- **评测基准**：FinQA / ConvFinQA / Ant_Finance / TFNS / Finance-Instruct-500K
- **基线**：DeepSeek-R1(671B)、Qwen2.5-32B/14B/7B、DeepSeek-R1-Distill 系列

## 5. 结果（作者如何验证有效）

| 模型 | 参数量 | FinQA | ConvFinQA | Ant_Finance | TFNS | Fin-Instruct | 平均 |
|---|---|---|---|---|---|---|---|
| **Fin-R1** | **7B** | **76.0** | **85.0** | 81.0 | 71.0 | 62.9 | **75.2** |
| DeepSeek-R1 | 671B | 71.0 | 82.0 | 90.0 | 78.0 | 70.0 | 78.2 |
| Qwen2.5-32B-Instruct | 32B | 72.0 | 78.0 | 84.0 | 77.0 | 58.0 | 73.8 |
| DeepSeek-R1-Distill-Llama-70B | 70B | 68.0 | 74.0 | 84.0 | 62.0 | 56.0 | 69.2 |
| Qwen2.5-7B-Instruct | 7B | 60.0 | 66.0 | 85.0 | 68.0 | 49.0 | 65.6 |

- **平均 75.2 分排名第二**（仅次 671B 的 DeepSeek-R1 78.2，差 3 分），
  **比同规模 SOTA 高 17+ 分**，比 70B 蒸馏模型高 6 分；
- **FinQA（76.0）与 ConvFinQA（85.0）双第一**；
- **"100 倍参数差距"论据**：7B 达到 671B 的 96% 表现——小模型路线可部署性强。

## 6. 局限

1. **基准是"推理题"而非"交易收益"**：FinQA/ConvFinQA 是表格数值推理，不直接等于可交易 alpha——
   与主报告"LLM 选股要怀疑"的提醒呼应；
2. 蒸馏自 DeepSeek-R1——上游模型错误会继承；
3. 评测为静态基准，无实盘/回测验证；
4. 中文金融场景为主，跨市场泛化未验证。

## 7. 与已有知识库报告的联系

- 主报告 §3.2：Fin-R1 列为"金融推理 SOTA，兼顾准确性与可解释性"——证据链的第 2 篇；
- 主题 01（因子）：Fin-R1 的"格式奖励"与因子挖掘的"结构化输出"同哲学——
  约束模型输出可解析、可审计；
- 主题 06（另类数据）：Fin-R1 数据蒸馏方法（两轮筛选+模型验证器）与情绪因子
  的"标签质量决定上限"（SFI 24-69）呼应；
- 主题 07（回测纪律）：Fin-R1 验证的是"推理能力"而非"交易有效性"——面试时要区分
  这两个概念，这是加分项。

## 8. 面试话术（30 秒）

"Fin-R1 用 7B 小模型达到 671B 大模型 96% 的金融推理表现：60,091 条从 DeepSeek-R1
蒸馏的 CoT 数据，SFT 注入推理能力，GRPO 强化学习用格式+准确率双奖励优化。
关键消融：只用 RL 不行（输出不连贯），只用 SFT 差 3 分，两阶段组合 75.2 分
碾压所有同规模模型、FinQA/ConvFinQA 双第一。但我面试会主动指出它的边界：
这是'推理题'的 SOTA，不是'交易收益'的证明——把推理能力和 alpha 能力分开，
这正是我理解 AI 量化的成熟度所在。"

## 来源

- arXiv 2503.16252（https://arxiv.org/abs/2503.16252，2025-03-20）
- GitHub SUFE-AIFLM-Lab/Fin-R1（https://github.com/SUFE-AIFLM-Lab/Fin-R1）
- HuggingFace SUFE-AIFLM-Lab/Fin-R1
