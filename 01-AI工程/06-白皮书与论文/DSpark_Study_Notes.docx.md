# DSpark_Study_Notes.docx

> **自动转换视窗** (原文件: `DSpark_Study_Notes.docx`)


DSpark

Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation

DeepSeek x Peking University | June 2025

DSpark 深度学习笔记

大模型推理加速框架详解

资料来源：DeepSeek / DeepSpec GitHub · 论文 arxiv:2606.19348

目录

一、背景：大模型推理的「挤牙膏」困境

2026年6月，DeepSeek与北京大学团队联合发布了论文《DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation》，提出了一套新的大模型推理加速框架。DSpark已经进入DeepSeek-V4-Flash preview和DeepSeek-V4-Pro preview的生产服务系统，替代此前的MTP-1方案。

1.1 问题本质：自回归生成的速度瓶颈

主流语言模型生成文本时，基本采用autoregressive（自回归）方式。模型每生成一个新token，都需要做一次以前文为条件的前向计算。输出越长，解码步骤越多，延迟也越容易累积。

对于实时聊天、多轮Agent workflow、代码助手这类高交互场景，生成速度会直接影响用户体验，也会影响GPU利用率。

1.2 推测解码（Speculative Decoding）概述

推测解码的思路可以用一个比喻理解：让一个「小模型」先写草稿，再让「大模型」快速审稿。

流程如下：

Draft Stage（草稿阶段）：系统先用一个轻量级 draft model（草稿模型）生成一串候选token。

Verification Stage（验证阶段）：再由真正负责输出质量的 target model（目标模型）一次性验证这些候选token。

通过验证的token会被接受；一旦某个位置被拒绝，后面的候选token全部作废，target model再生成一个修正token。

由于验证阶段可以并行完成，推测解码可以在不改变target model输出分布的前提下提高生成速度。更直观地说，它想让大模型一次前向计算确认更多token，而不是每次只确认一个。

二、已有方案及其局限性

2.1 Autoregressive Draft Model（自回归草稿模型）

代表方案：Eagle3。它像正常语言模型一样，一个token接一个token地生成候选内容。

优点：前后关系更自然，候选质量较高。

缺点：draft model自己写草稿时也要一步一步来，候选token越多，draft阶段越慢。为了控制延迟，通常不能做得太深，因此第一个token的预测能力受限。

2.2 Parallel Draft Model（并行草稿模型）

代表方案：DFlash。它可以一次性生成多个候选token，速度很快。

优点：生成速度快，适合生成较长的candidate block。

缺点：candidate block内部的token之间缺少足够的依赖关系。容易出现Multi-Modal Collision（多模态碰撞），即将多条续写路径混在一起，生成前后不一致的组合（如“of problem”而非“of course”）。

2.3 Suffix Decay（后缀衰减）现象

并行草稿模型开头几个token往往还不错，但越往后，候选token被target model接受的概率下降越快。论文把这种现象称为suffix decay。

核心矛盾：推测解码的问题已经不只在于能不能一次生成更多token，还在于哪些 token值得交给target model验证。

三、DSpark 核心创新

DSpark的思路可以概括为两件事：草稿要写得更像样，审稿要更会挑重点。具体包含三大创新组件：

3.1 Semi-Autoregressive Architecture（半自回归架构）

这是DSpark在生成侧的核心创新。它保留parallel draft model的主干，让大部分计算仍然一次完成；同时在输出端加入一个轻量级顺序模块（Sequential Module），让后面的token能参考前面已经采样出来的token。

可以理解为：前面用并行方式快速铺开候选，后面再用一个很轻的顺序模块检查相邻token的衔接关系。

3.1.1 两种 Sequential Head

关键效果：2层DSpark已经超过5层DFlash，说明轻量级顺序建模比单纯增加并行层数更有效。

3.2 Confidence-Scheduled Verification（基于置信度调度的验证）

这是DSpark在验证侧的核心创新。系统会给每个候选位置预测一个confidence score（置信度分数）。这个分数表示：在前面的token都已经被target model接受的情况下，当前位置继续被接受的概率有多高。

校准效果：DSpark的置信度头将校准误差从3-8%降低到约1%，提供了可靠的置信度估计。

3.3 Hardware-Aware Prefix Scheduler（硬件感知前缀调度器）

调度器根据三个因素动态决定每个请求该验证多少token：

当前系统负载：GPU空闲时验证更多token，繁忙时验证更少token

每个候选位置的置信度：低置信度的token会被过滤掉

引擎在不同 batch size 下的吞吐曲线（SPS(B)）：通过一次性启动时的profiling获得

这也是DSpark相比传统推测解码更接近真实生产环境的地方：它不只追求单次生成更多候选token，也会根据系统负载调整验证预算。

四、技术架构详解

4.1 两阶段生成流程

DSpark将草稿生成分为两个阶段：

第一阶段：Parallel Backbone（以DFlash为主干）一次性产生所有位置的基础logits。这保证了生成速度。

第二阶段：Sequential Head在每个位置采样前，添加一个依赖于前缀的偏置项。只查看立即前缀的一个token，通过低秩分解（rank 256）保持轻量。

延迟开销：在batch size 128的测试中，相比DFlash，DSpark的单轮延迟只增加0.2%至1.3%，但accepted length最多提升30%。

4.2 置信度头训练

DSpark训练了一个独立的confidence head，用于估计每个token的生存概率。该头的监督信号来自分析性的每位置接受率，确保校准误差从3-8%降低到约1%。

4.3 与MTP的关系

重要点： DSpark与Multi-Token Prediction（MTP）是互补关系，而非替代关系。MTP让模型在每一步预测多个未来token，已被证明在NVIDIA DGX Spark等硬件上可获得50-100%的加速。DSpark在MTP之上叠加了另一层：即使有MTP，验证步骤仍然是单次前向传播，通过推测解码接受的token是“免费的”。

五、实验结果

5.1 离线实验

实验设置：在Qwen3-4B、Qwen3-8B、Qwen3-14B和Gemma4-12B四个target model上测试DSpark，与autoregressive draft model Eagle3和parallel draft model DFlash对比。

评测场景：数学推理（GSM8K, MATH500, AIME25）、代码生成（MBPP, HumanEval, Live-CodeBench）、日常聊天（MT-Bench, Alpaca, Arena-Hard）。

5.1.1 Macro-Average Accepted Length（宏平均接受长度）

accepted length表示每一轮推测解码中，平均有多少token能被target model接受。这个数字越高，说明draft model写出的草稿越能被大模型认可，推理加速空间也越大。

5.1.2 不同任务差异显著

以Qwen3-4B为例，DSpark在不同任务上的平均accepted length差异明显：

启示：数学和代码更结构化，续写路径更稳定；聊天更开放，模型可能有很多种合理回答方式。因此，同样长度的候选token，在不同任务里的价值并不一样。固定verification length会浪费一部分计算资源。

5.1.3 Proposal Length 对比

随着proposal length（候选长度）从4增加到16，DSpark相对DFlash的优势继续扩大。在最长设置下，DSpark在数学、代码和聊天任务上分别领先DFlash 30%、26%和22%。

5.1.4 Confidence Threshold Sweep

论文在Qwen3-4B上做了confidence threshold sweep（置信度阈值扫描），即不断提高置信度门槛，观察系统会保留哪些token。

结论：门槛越高，系统过滤掉的低价值候选token越多，整体acceptance rate越高。聊天任务变化最明显，说明其不确定性最高，也最能从动态调度中获益。

六、生产环境部署

这是DSpark论文最关键的部分。DeepSeek在DeepSeek-V4-Flash preview和DeepSeek-V4-Pro preview的真实生产引擎中部署了DSpark，最大draft长度设为5，对比对象是此前的MTP-1生产基线。

6.1 为什么要替代 MTP-1

MTP-1只做单token预测，加速空间有限，但在高并发下比较安全。原因在于，静态multi-token draft虽然看起来一次生成更多token，但如果很多token最后被拒绝，反而会浪费target model的验证资源，拖累系统总吞吐。DSpark的意义在于，它让multi-token draft在真实线上流量中变得可控。

6.2 DeepSeek-V4-Flash 线上结果

关于661%：这个661%不应理解成所有常规场景都能获得6倍以上提升。更准确的理解是：在高交互、强SLA约束下，MTP-1已经很难继续维持服务能力，而DSpark把原本难以达到的性能区间打开了。

6.3 DeepSeek-V4-Pro 线上结果

6.4 动态调度策略

面对中等并发时，DSpark会把验证预算从MTP-1的静态2个token扩展到大约4-6个token，让每次前向计算产生更多有效输出。当并发继续升高、target model接近饱和时，DSpark会自动缩短验证长度，减少低置信度token对batch capacity的占用。

七、开源生态

DeepSeek宣布开源以下资源：

7.1 DeepSpec 代码库

仓库地址：https://github.com/deepseek-ai/DeepSpec

许可证：MIT License

支持算法：DSpark, DFlash, Eagle3

支持目标模型：Qwen3、Gemma4 等

功能：数据准备、草稿模型训练、推测解码评估

7.2 模型 Checkpoints

DeepSeek-V4-Flash-DSpark 和 DeepSeek-V4-Pro-DSpark 已在 Hugging Face 开放

关键特点：复用现有V4权重，仅附加DSpark draft模块，无需重新训练target model

7.3 使用场景

使用DeepSeek V4：直接附加DSpark模块，无需重新训练

使用其他开源模型：DeepSpec提供了针对Qwen3和Gemma4的训练框架

八、三种推测解码方案对比

九、关键启示与总结

9.1 推理优化已成为前沿实验室的一等交付物

深度学习的竞争已从纯粹的“训练更大模型”转向“把模型以更快、更便宜、更稳定的方式送到真实用户面前”。DeepSeek在约18个月内连续发布了sparse MoE、MTP、DSpark，每一个都是对推理效率的重大贡献。

9.2 DSpark 的核心哲学：“既要又要”

生成侧：保留parallel draft model的速度，同时补上autoregressive draft model的前后连贯性

验证侧：通过置信度调度和硬件感知前缀调度，动态调整验证预算

系统视角：不只追求单次生成更多候选token，也考虑系统负载和吞吐目标

9.3 大模型的尽头，是复杂的系统工程问题

推理加速已经不只是模型结构问题，也越来越是系统调度问题。单纯让draft model一次生成更多token，并不等于服务一定更快。候选Token的质量、通过率、验证长度、系统负载、吞吐目标......每一个变量都在极其微妙地互相牵扯。

9.4 开源对行业的意义

DeepSeek选择把这套生产环境里的加速经验开源，相当于把一部分真正能提高推理效率、降低服务成本的核心方法，无私分享给全行业。对于去中心化计算网络（如Akash、Render、io.net），如果能用相同硬件服务51-400%更多的请求，租用GPU时间的单位经济学将发生戏剧性变化。

9.5 未来方向

推理时优化成为一等交付物：前沿实验室不再把推理优化视为“事后想法”，而是与训练同等重要的核心交付

DSpark 可扩展性：已在Qwen、Gemma等非DeepSeek模型上验证，技术具有广泛适用性

与MTP互补：DSpark与MTP不是互斥关系，可以叠加使用，进一步提升推理效率

系统工程化趋势：大模型竞争进入更精细阶段，推理效率和成本优化同样决定AI产品的上限

十、参考资料

论文 PDF：https://github.com/deepseek-ai/DeepSpec/blob/main/DSpark_paper.pdf

DeepSpec 仓库：https://github.com/deepseek-ai/DeepSpec

DeepSeek-V3 Technical Report：https://arxiv.org/pdf/2412.19437v2

Eagle3 论文：https://arxiv.org/abs/2503.01840

DFlash 论文：https://arxiv.org/abs/2602.06036

Semi-Autoregressive Decoding for Efficient LLM Inference：ICLR 2025, OpenReview

Falcon (AAAI 2025)：Semi-autoregressive speculative decoding framework

MarkTechPost 报道：https://www.marktechpost.com/2026/06/27/deepseek-releases-dspark

Crypto Briefing 报道：https://cryptobriefing.com/deepseek-dspark-faster-inference/

DEV Community 分析：https://dev.to/max_quimby/dspark-open-weight-speed-without-a-cerebras-contract-1p0g


| --- | --- | --- |

| 类型 | 原理 | 优劣 |

| Markov Head（默认） | 仅建模相邻token之间的转移关系，使用低秩分解（rank 256）降低计算成本 | 计算成本低，部署更方便，即使词表很大也保持轻量 |

| RNN Head | 保留更长的块内历史信息 | 收益有限，复杂度更高 |





| --- | --- | --- |

| Target Model | vs Eagle3 | vs DFlash |

| Qwen3-4B | +30.9% | +16.3% |

| Qwen3-8B | +26.7% | +18.4% |

| Qwen3-14B | +30.0% | +18.3% |

| Gemma4-12B | 保持领先 | 保持领先 |





| --- | --- | --- |

| 任务类型 | Avg Accepted Length | 特点分析 |

| 数学推理 | 5.57 | 结构化程度高，续写路径稳定 |

| 代码生成 | 5.12 | 较为结构化，语法规则明确 |

| 日常聊天 | 3.49 | 开放式，模型可能有很多种合理回答方式 |





| --- | --- | --- | --- |

| 任务类型 | 原始Acceptance Rate | 高阈值Acceptance Rate | 提升 |

| 聊天任务 | 45.7% | 95.7% | +50.0% |

| 数学任务 | 76.9% | 92.5% | +15.6% |

| 代码任务 | 67.6% | 92.0% | +24.4% |





| --- | --- | --- |

| 服务目标 | DSpark vs MTP-1 总吞吐提升 | 单用户生成速度提升 |

| 80 token/s/user | 51% | 60-85% |

| 120 token/s/user（严格） | 661%（名义） | 显著提升 |





| --- | --- | --- |

| 服务目标 | DSpark vs MTP-1 总吞吐提升 | 单用户生成速度提升 |

| 35 token/s/user | 52% | 57-78% |

| 50 token/s/user（严格） | 406%（名义） | 显著提升 |





| --- | --- | --- | --- |

| 维度 | Eagle3 (AR Draft) | DFlash (Parallel Draft) | DSpark (Semi-AR Draft) |

| 生成方式 | 逐token自回归 | 一次性并行生成 | 并行主干 + 顺序头 |

| 草稿速度 | 较慢 | 快 | 快（仅+0.2-1.3%延迟） |

| 前缀质量 | 高 | 中（suffix decay） | 高 |

| 后缀质量 | 高（有块内依赖） | 低（无块内依赖） | 高（有块内依赖） |

| 置信度调度 | 无 | 无 | 有（硬件感知） |

| 生产部署 | 实验室为主 | 实验室为主 | 已在V4生产环境部署 |


