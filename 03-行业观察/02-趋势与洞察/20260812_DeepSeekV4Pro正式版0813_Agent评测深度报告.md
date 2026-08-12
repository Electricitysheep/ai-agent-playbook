# 20260812_DeepSeekV4Pro正式版0813_Agent评测深度报告

> 检索日期：2026-08-12 ｜ 类型：深度调研报告 ｜ 可信度：官方口径 A / 第三方口径 B / 传闻 C（逐条标注）
> 本版 v4（2026-08-12）：**新增官方 V4-Pro-0813 Agent 成绩单（用户提供官方图表 + 与官方模型卡交叉核验）**，该表为 0813 正式版的 Agent 评测核心数据。

## 我能讲出来的版本（5 行）

1. **V4-Pro-0813 正式版 2026-08-12 发布，多渠道确认**：①DeepSeek 官方 API 文档模型名已更新至 DeepSeek-V4-Pro-0813；②Vercel AI Gateway changelog（8-12 07:00 UTC）确认 `deepseek-v4-pro-0813` 新权重上线；③**官方发布了 0813 的 Agent 成绩单图表**（DeepSeek logo，标题"DeepSeek V4 Pro 正式版模型在 Agent 相关评测集上的表现以及其他前沿模型的对比"）——官方更新日志页尚未同步该条目，但成绩单已以图表形式发布。
2. **官方 0813 Agent 成绩单（核心）**：Terminal-Bench 2.1 **87.9**（反超 Opus-4.8 的 85.0，逼近 Fable 5 的 88.0）、DeepSWE **62.7**（反超 Opus-4.8 的 58.0）、Cybergym **83.3**（反超 Opus-4.8 的 78.3）、AutomationBench **31.8**（全场第一，超 Fable 5 的 29.1）、HLE w/ tools **60.0**（反超 Opus-4.8 的 57.9）、DSBench-FullStack 71.1（与 Opus-4.8 71.6 打平）。
3. **相对预览版是质变**：Terminal-Bench 72.1→87.9（+15.8）、DeepSWE 12.8→62.7（+49.9）、Cybergym 52.7→83.3（+30.6）、DSBench-Hard 31.1→67.2（+36.1）——"Flash-0731 式后训练"在 Pro 规模上复刻且增益更大，**V4-Pro-0813 已成为 Agent 基准上的真正前沿选手**。
4. **独立口径仍待跟进**：AA v4.1.1（8-06 方法版）对 V4-Pro 的 45 分测的是预览版构建，0813 的独立评测（AA/arena/Vals）尚未出分；官方 0813 表为 DeepSeek Harness 自测口径，需独立复现。
5. 性价比维持碾压：输出 $0.87/M、缓存命中输入 $0.004/M（-99%）；8-6 官方已预告正式版落地后整体涨价。

## 原始资料（检索来源）

- **官方 0813 Agent 成绩单图表**：用户提供截图（DeepSeek 官方发布，含 logo；各列与官方 Flash-0731 模型卡交叉核验一致）；官方更新日志 https://api-docs.deepseek.com/updates 尚未同步该条目
- **Vercel AI Gateway changelog（0813 权重上线实据，2026-08-12）**：https://vercel.com/changelog/deepseek-v4-pro-now-runs-updated-weights-on-ai-gateway
- DeepSeek 官方 API 文档（Your First API Call）：https://api-docs.deepseek.com/ ；Flash-0731 官方模型卡：https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731
- **Artificial Analysis v4.1.1（独立口径，测预览版）**：https://artificialanalysis.ai/models/deepseek-v4-pro ｜ https://artificialanalysis.ai/providers/deepseek ｜ https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-1-1
- CAISI / NIST 独立评测（2026-05-01）：https://www.nist.gov/news-events/news/2026/05/caisi-evaluation-deepseek-v4-pro
- IT之家 / 财新 / 36氪 / 凤凰网 / 科创板日报 / 华尔街见闻；The New Stack / TechTimes / yage.ai DeepSWE 审计

---

## 1. 事件时间线

| 时间 | 事件 | 可信度 |
|---|---|---|
| 2026-04-24 | DeepSeek-V4 预览版发布并开源：V4-Pro（1.6T/49B 激活）与 V4-Flash（284B/13B 激活），均 1M 上下文、MIT 协议 | A（官方） |
| 2026-07-24 | 旧模型名 `deepseek-chat` / `deepseek-reasoner` 正式停用 | A |
| 2026-07-31 | **V4-Flash-0731 正式版** API 公测：9 项 Agent 基准"远超 V4-Pro-Preview"；原生 Responses API、适配 Codex；开源权重当日上 HF | A |
| 2026-08-05 | 官方公告：近期整体上调 API 定价，"预计涨幅较大"；峰谷计费落地（北京工作日 9-12、14-18 高峰翻倍） | A |
| 2026-08-06 | AA 发布智能指数 v4.1.1（评测构成转向 Agent 负载）；Claude Opus 5=63 居首 | A |
| **2026-08-12** | **V4-Pro-0813 正式版发布，三渠道实据**：①API 文档模型名更新；②Vercel AI Gateway 确认新权重上线；③**官方发布 0813 Agent 成绩单图表**（用户提供，交叉核验为真） | A（三实据） |

---

## 2. 模型规格速览

| 项 | DeepSeek-V4-Pro | DeepSeek-V4-Flash |
|---|---|---|
| 总参数量 | **1.6T**（当前最大开源权重） | 284B |
| 激活参数量 | 49B | 13B |
| 上下文 / 最大输出 | 1M / 384K | 1M / 384K |
| 架构 | MoE + CSA/HCA 混合注意力 + mHC + Muon；1M 下 FLOPs 为 V3.2 的 27%、KV 缓存 10% | 同左 |
| 推理模式 | Non-think / High / Max | 同左 |
| 许可证 | MIT | MIT |
| Agent 适配 | Claude Code、OpenClaw、OpenCode、CodeBuddy | 同左 + Codex + 原生 Responses API |

---

## 3. 核心：官方 V4-Pro-0813 Agent 成绩单（2026-08-12 发布）

![DeepSeek V4 Pro 0813 官方 Agent 成绩单（1920×1026，点击可放大）](20260812_deepseek-v4-pro-0813_official_agent_scorecard.png)

> 上图即官方原图（DeepSeek logo，标题"DeepSeek V4 Pro 正式版模型在 Agent 相关评测集上的表现以及其他前沿模型的对比"）。下方为同数据的文字版表格（便于检索/复制）。**核验说明**：图中 Flash-0731 / Flash-Preview / Pro-Preview / Opus-4.8 各列与官方 Flash-0731 模型卡逐项一致（Terminal-Bench 82.7/61.8/72.1、DeepSWE 54.4/7.3/12.8、Toolathlon 70.3/49.7/55.9、DSBench 系列等全部对上），确认官方口径。HLE 与 Fable 5 列为新增对比。评测为 DeepSeek Harness（未发布）自测，max 档、temp=1.0、top_p=0.95。

| 基准（Agent 类） | **V4-Pro-0813** | Flash-0731 | Pro-Preview | Flash-Preview | Opus-4.8 | Fable 5 (w/ fallback) |
|---|---|---|---|---|---|---|
| HLE（无工具 / 带工具，Pass@1） | **42.7 / 60.0** | 37.8 / 51.5 | 37.7 / 48.2 | 34.8 / 45.1 | 49.8 / 57.9 | 53.3 / 63.0 |
| Terminal-Bench 2.1（终端操作） | **87.9** 🏆 | 82.7 | 72.1 | 61.8 | 85.0 | 88.0 |
| NL2Repo（NL→完整代码仓库） | 61.5 | 54.2 | 38.5 | 39.4 | **69.7** | — |
| Cybergym（网络安全攻防） | **83.3** 🏆 | 76.7 | 52.7 | 38.7 | 78.3 | 83.1 |
| DeepSWE（真实仓库修 issue） | **62.7** 🏆 | 54.4 | 12.8 | 7.3 | 58.0 | 70.0 |
| Toolathlon-Verified（多工具编排） | 74.1 | 70.3 | 55.9 | 49.7 | **76.2** | 77.9 |
| Agents' Last Exam | **25.7** 🏆 | 25.2 | 16.5 | 15.8 | 25.7 | — |
| AutomationBench (Public) | **31.8** 🏆 | 25.1 | 12.8 | 10.8 | 27.2 | 29.1 |
| DSBench-FullStack（内部全栈） | 71.1 | 68.7 | 41.8 | 37.0 | 71.6 | **77.2** |
| DSBench-Hard（内部难题） | 67.2 | 59.6 | 31.1 | 25.8 | **71.7** | 68.3 |

> 🏆 = 该行对比中 V4-Pro-0813 领先或并列 Opus-4.8（表中 Opus-4.8 与 Fable 5 之外的对比对象）。

### 3.1 读表结论

1. **0813 相对预览版是质变**：后训练把 Pro 的 Agent 能力整体抬升一个量级——Terminal-Bench +15.8、DeepSWE +49.9（12.8→62.7）、Cybergym +30.6、DSBench-Hard +36.1、DSBench-FullStack +29.3、NL2Repo +23.0、Toolathlon +18.2。**"Flash-0731 式后训练"在 Pro 规模上复刻且增益更大**，Preview 与 0813 之间几乎是两个模型。
2. **对 Opus-4.8：多数 Agent 基准反超**——Terminal-Bench 2.1（87.9 vs 85.0）、Cybergym（83.3 vs 78.3）、DeepSWE（62.7 vs 58.0）、AutomationBench（31.8 vs 27.2）、HLE w/ tools（60.0 vs 57.9）五胜；DSBench-FullStack 打平（71.1 vs 71.6）；仅 NL2Repo（61.5 vs 69.7）、Toolathlon（74.1 vs 76.2）、DSBench-Hard（67.2 vs 71.7）仍落后。
3. **对 Fable 5（当前闭源顶级）**：Terminal-Bench 2.1 仅差 0.1（87.9 vs 88.0）、Cybergym 打平（83.3 vs 83.1）、**AutomationBench 反超（31.8 vs 29.1）**、DSBench-Hard 接近（67.2 vs 68.3）；但 DeepSWE（62.7 vs 70.0）、DSBench-FullStack（71.1 vs 77.2）、HLE（42.7 vs 53.3）、Toolathlon（74.1 vs 77.9）仍有明显差距——**仓库级长程编码与超难推理是剩余缺口**。
4. 保留口径警示：官方表为 DeepSeek Harness 自测（该框架尚未发布），AA 对 Flash-0731 的独立重测比官方低 3.7 分（79 vs 82.7）——**0813 的绝对分数需独立复现后才有最终结论**，但相对趋势（预览版→0813 质变）可信。

---

## 4. 独立口径参照：AA v4.1.1（测的是预览版构建）

> ⚠️ AA 尚未评测 0813 构建；下表 V4-Pro 分数 = 预览版构建。AA v4.1.1（8-06）含 9 项评测，Agent 类（GDPval-AA v2 20% + Terminal-Bench 2.1 16% + τ³-Banking 14%）合计占 50%。

| 模型（推理档位） | AA 智能指数 | 备注 |
|---|---|---|
| Claude Opus 5 | **63** | 闭源第一（当前不可用） |
| Kimi K3 (max) | **57** | 开源权重第一 |
| Claude Opus 4.8 (max) | 56 | 当前可用闭源最强 |
| GPT-5.5 (xhigh) | 55 | — |
| **DeepSeek V4 Flash-0731 (max)** | **52** | 开源第二；单任务成本 $0.03 |
| GPT-5.6 Luna (max) / GLM-5.2 (max) | 51 | — |
| Gemini 3.6 Flash (high) | 50 | — |
| **DeepSeek V4 Pro (max，预览版)** | **45** | #6/101；单任务成本 $0.05 |
| DeepSeek V4 Pro (high) | 44 | — |
| DeepSeek V4 Pro（非思考） | 32 | — |

**Agent 专项（AA 独立实测 Flash-0731）**：GDPval-AA v2 = **1559 Elo**（开源第二，Kimi K3=1687）；Terminal-Bench 2.1 = **79%**（官方自报 82.7，差 3.7 分即官方 vs 独立口径差异的实证）；τ³-Banking = 31.1%。

**对 0813 的预期**：Flash-0731 靠后训练把 AA 指数 40→52（+12）；官方成绩单显示 0813 在 Agent 基准上的跃升幅度大于 Flash（DeepSWE 12.8→62.7 vs Flash 7.3→54.4）——**0813 的 AA 指数有望显著高于预览版的 45**，待 AA 出分验证。

---

## 5. 其他第三方评测（针对预览版/Flash 的历史口径）

| 评测方 | 结果 | 可信度 |
|---|---|---|
| **Vals AI**（Vibe Code Benchmark） | 4 月：V4 系开源权重第一，击败 Gemini-3.1-Pro；较 V3.2 约 10 倍跃升 | B |
| **Arena.ai**（人类盲测） | 4 月：V4-Pro 代码竞技场开源第 3/综合第 14；8 月：V4-Flash-High 1586 分重塑 Frontend Code Arena（总榜第 7、开源第 3） | B |
| **CAISI / NIST**（2026-05-01，预览版） | V4-Pro（max）整体落后美国前沿约 8 个月（IRT Elo 800 vs GPT-5.5 1260）；PortBench 44%、CTF 32% | A（政府机构） |
| **yage.ai**（DeepSWE 独立审计，2026-05-28，预览版） | 无污染 DeepSWE：V4-Pro 仅 8%（GPT-5.5 70%）；验证器假阳性 8.5% vs DeepSWE 0.3%——官方 80.6% 与独立 8% 的落差主要来自验证器与自家 harness | B（独立审计） |
| **The New Stack**（实测，2026-08-10） | Flash 正式版 vs Pro 预览版：前两任务平手、优化任务 Flash 更激进（1.83x vs 1.06x）；Flash 3 倍 token 但账单几乎相同（$0.09 vs $0.10） | B（一手实测） |

---

## 6. 定价与性价比

| 模型 | 输入 $/M（缓存未命中） | 输入 $/M（缓存命中） | 输出 $/M | AA 单任务成本 |
|---|---|---|---|---|
| V4-Pro | $0.435（¥3） | **$0.004（-99%）** | $0.87（¥6） | $0.05 |
| V4-Flash 正式版 | $0.14（¥1） | $0.0028（¥0.02，98% 折扣） | $0.28（¥2） | $0.03 |
| Claude Opus-4.8（参照） | ~$3 | — | $25 | $1.78 |
| GPT-5.5 xhigh（参照） | ~$2.5 | — | ~$15 | $0.99 |

> 高峰时段（北京工作日 9-12、14-18）V4 系翻倍；8-6 官方公告正式版落地后整体涨价，涨幅"较大"。按 AA 单任务成本，V4-Pro 仍比 Opus-4.8 便宜约 35 倍——**0813 在多数 Agent 基准反超 Opus-4.8 的同时维持 1/35 的成本，是当前"性能/价格"比最强的 Agent 底座**。

---

## 7. 能力画像总结（2026-08-12 最新口径）

### ✅ 优势（有强证据）
- **Agent 基准全面逼近/反超闭源顶级（0813 官方口径）**：Terminal-Bench 2.1 87.9（>Opus-4.8，≈Fable 5）、Cybergym 83.3、DeepSWE 62.7、AutomationBench 31.8 全场第一、HLE w/ tools 60.0
- **后训练质变**：相对预览版全项大幅跃升（DeepSWE +49.9、DSBench-Hard +36.1），Agent 能力从此前的"中上游"进入"前沿"区间
- **性能/价格比全行业最强**：1/35 成本 + 多数 Agent 基准反超 Opus-4.8；缓存命中输入 -99%
- **1M 上下文 + 效率架构**：FLOPs 27%、KV 10%；生态绑定 Claude Code / OpenClaw / OpenCode / CodeBuddy / Codex

### ⚠️ 短板 / 待验证
- **仓库级长程编码仍是最大缺口**：NL2Repo（61.5 vs 69.7）、DSBench-Hard（67.2 vs 71.7）、DeepSWE 对 Fable 5（62.7 vs 70.0）
- **超难推理仍落后**：HLE 无工具 42.7 vs Fable 5 53.3 / Opus-4.8 49.8
- **官方自测口径待独立复现**：DeepSeek Harness 未发布；AA 对 Flash 的独立重测比官方低 3.7 分，0813 需同样打折
- **AA 指数（预览版 45）远未反映 0813**：0813 的 AA 独立评分预计数日内出炉，届时才能校准官方 vs 独立差距
- 事实性幻觉率高（AA-Omniscience 口径，预览版）；思考模式 token 消耗大（预览版评测 1.8 亿 tokens）

---

## 8. 研判与启示

1. **V4-Pro-0813 是"Flash-0731 后训练路线"在 Pro 规模的成功复刻，且增益更大**：官方成绩单显示 Agent 能力已进入前沿区间（反超 Opus-4.8 多数基准、逼近 Fable 5）。**8 月最重要的模型事件已落地，方向与 7-31 Flash 预告一致。**
2. **剩余缺口有明确的清单**：仓库级长程编码（NL2Repo/DSBench-Hard）与超难推理（HLE）——这两项正是 CAISI/yage 独立审计此前指出的"真实能力差距"所在，说明独立审计的批评方向是对的，但 0813 已大幅缩小该差距。
3. **评测口径教训依然成立**：官方自测（自家 Harness）vs 独立复测（AA 低 3.7 分、yage 低至 8%）——看 Agent 跑分必须三问：谁测的？什么 harness？验证器假阳性多少？0813 的官方分数应视为"上界"，独立复现后才有最终结论。
4. **对个人学习路径的落点**：Agent 能力（Terminal-Bench / DeepSWE / GDPval-AA / Cybergym）已是新标尺；V4 系与 Claude Code / OpenCode / OpenClaw 深度绑定，`02_AI工程/01_Agent智能体` 方向可直接以 V4-0813 + OpenCode 为实践底座；"官方 vs 独立评测"双口径对比与"性能/价格比"框架可直接用于求职面试选型方法论。

---

## 附：待验证清单（后续跟进）

- [x] **识别用户截图**：确认为 DeepSeek 官方 V4-Pro-0813 Agent 成绩单（logo+标题+与官方 Flash-0731 卡交叉核验一致）
- [ ] 官方更新日志同步 0813 条目（当前仍止于 7-31 Flash）；官方中文公告（微信公众号/App）原文
- [ ] **AA/arena/Vals 对 0813 构建的独立评测**（预计数日内出分）——重点看 AA 智能指数是否如预期从 45 升至 50 上下
- [ ] DeepSeek Harness 正式发布——发布后官方 Agent 数字才可独立复现
- [ ] 8-6 公告的新定价方案正式通知（涨幅与峰谷细则）
