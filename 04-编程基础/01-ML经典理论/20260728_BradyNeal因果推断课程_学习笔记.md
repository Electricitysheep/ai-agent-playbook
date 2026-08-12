# Introduction to Causal Inference — Brady Neal 因果推断免费课程（ML 视角）

> **课程主页**：https://www.bradyneal.com/causal-inference-course
> **作者**：Brady Neal（Mila / 因果推断与机器学习）
> **性质**：免费公开课（非学分），从机器学习视角讲因果推断，融合流行病学/经济学/政治学等多学科视角
> **整理日期**：2026-07-28 · **类型**：学习笔记（课程资源导航）
> **先修要求**：本科级概率论（唯一硬要求）；统计/ML 概念会在用到时现场补

---

## 我能讲出来的版本（5 行·费曼门槛）

1. 因果推断的核心难题：**根本问题是我们永远观测不到同一个体的反事实**——用了药的人和没用药的人不是同一批人，直接比均值就掉进混杂（confounding）的坑。
2. 两套主流语言：Rubin 的**潜在结果框架**（potential outcomes，定义 ATE/CATE 等估计目标）和 Pearl 的**结构因果模型 + 因果图**（SCM/DAG，用图表达变量间因果结构）。
3. 识别的核心招式：**后门调整**（backdoor，阻断混杂路径）与前门调整、*do*-演算——把"因果量"翻译成"可用观测数据计算的统计量"。
4. 估计的两条腿：随机实验是金标准；观测数据靠 IV（工具变量）、双重差分（DiD）、合成控制、断点回归（RDD）、敏感性分析对付未观测混杂；ML 负责估计异质性处理效应（CATE，如广义随机森林）。
5. 前沿方向：因果发现（从数据学因果图）、可迁移性（transportability，结论跨人群/环境是否成立）、反事实与中介分析、因果表征学习（Bengio 方向）。

---

## 课程资源总入口

| 资源 | 链接 |
|------|------|
| 课程主页 | https://www.bradyneal.com/causal-inference-course |
| 主课 YouTube 播放列表 | https://www.youtube.com/playlist?list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0 |
| 嘉宾讲座播放列表 | https://www.youtube.com/playlist?list=PLoazKTcS0RzZ1SUgeOgc6SWt51gfT80N0 |
| **教材 ICI 草稿 PDF**（前十章，持续更新） | https://www.bradyneal.com/Introduction_to_Causal_Inference-Dec17_2020-Neal.pdf |
| 课程 Slack 讨论区 | https://join.slack.com/t/causalcourse/shared_invite/zt-qpomuitc-WRYfcbeUNb9UACJN2U~kGw |
| 选书指南（哪本因果推断书适合你） | https://www.bradyneal.com/which-causal-inference-book |
| 反馈表单 | https://docs.google.com/forms/d/e/1FAIpQLSfoDk_PftCTD5aSqz7TP_MG8heIw0wSH4OVEkIsSvCaLgSsXw/viewform |

> ⚠️ Slides 在 Adobe Acrobat 中显示异常，用其他 PDF 阅读器打开。
> 📌 教材 PDF 如需离线存档，可下载至 `07_原始文献/99_英文PDF资料/`（PDF 不入 git）。

---

## 课程大纲（15 周 · 视频 + Slides + 阅读）

> Slides 均为 `https://www.bradyneal.com/slides/` 下的 PDF；视频均来自主播放列表。

| 周 | 主题 | 视频 | Slides | 教材章节 |
|----|------|------|--------|----------|
| W1 | 动机 / 课程预览 / 课程信息 | [Video](https://www.youtube.com/watch?v=CfzO4IEMVUk&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=1) · [课程信息](https://www.youtube.com/watch?v=xj-tzrm5Src&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=6) | [Slides](https://www.bradyneal.com/slides/1%20-%20A%20Brief%20Introduction%20to%20Causal%20Inference.pdf) | Ch.1 |
| W2 | **潜在结果** Potential Outcomes + 完整估计示例 | [Video](https://www.youtube.com/watch?v=q8x9aetyok0&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=8) | [Slides](https://www.bradyneal.com/slides/2%20-%20Potential%20Outcomes.pdf) | Ch.2 |
| W3 | **图模型** Graphical Models | [Video](https://www.youtube.com/watch?v=Go4EkHN_PcA&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=19) | [Slides](https://www.bradyneal.com/slides/3%20-%20The%20Flow%20of%20Association%20and%20Causation%20in%20Graphs.pdf) | Ch.3 |
| W4 | **后门调整** + 结构因果模型 SCM | [Video](https://www.youtube.com/watch?v=dB8r4Afmobo&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=28) | [Slides](https://www.bradyneal.com/slides/4%20-%20Causal%20Models.pdf) | Ch.4 |
| W5 | 随机实验 / **前门调整** / ***do*-演算** / 图识别 | [Video](https://www.youtube.com/watch?v=z91LnTDyhtI&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=37) | [Slides](https://www.bradyneal.com/slides/5%20-%20Identification.pdf) | Ch.5-6 |
| W6 | **估计** Estimation + 🎤 Susan Athey 嘉宾：异质处理效应 | [Video](https://www.youtube.com/watch?v=YzcOYU-s2t4&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=42) · [嘉宾讲座](https://www.youtube.com/watch?v=oZoizsX3bts&list=PLoazKTcS0RzZ1SUgeOgc6SWt51gfT80N0&index=7) | [Slides](https://www.bradyneal.com/slides/6%20-%20Estimation.pdf) | Ch.7 |
| W7 | 未观测混杂 / 边界 / **敏感性分析** | [Video](https://www.youtube.com/watch?v=IXNMYqUsBBQ&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=47) | [Slides](https://www.bradyneal.com/slides/7%20-%20Unobserved%20Confounding.pdf) | Ch.8 |
| W8 | **工具变量** Instrumental Variables | [Video](https://www.youtube.com/watch?v=Mco16tUSA-U&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=53) | [Slides](https://www.bradyneal.com/slides/8%20-%20Instrumental%20Variables.pdf) | Ch.9 |
| W9 | **双重差分** DiD + 🎤 Alberto Abadie 嘉宾：合成控制 | [Video](https://www.youtube.com/watch?v=tT8xLRS_cRQ&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=58) · [嘉宾讲座](https://www.youtube.com/watch?v=nKzNp-qpE-I&list=PLoazKTcS0RzZ1SUgeOgc6SWt51gfT80N0&index=11) | [Slides](https://www.bradyneal.com/slides/9%20-%20Difference-in-Differences.pdf) | Ch.10 |
| — | 休息周（无课） | — | — | 复习旧阅读 |
| W10 | **因果发现**（观测数据）+ 🎤 Jonas Peters 嘉宾 | [Video](https://www.youtube.com/watch?v=lVE-4deFe7c&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=62) | [Slides](https://www.bradyneal.com/slides/10%20-%20Causal%20Discovery%20from%20Observational%20Data.pdf) | Ch.11 |
| W11 | **因果发现**（干预数据） | [Video](https://www.youtube.com/watch?v=de2ODel8F1k&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=69) | [Slides](https://www.bradyneal.com/slides/11%20-%20Causal%20Discovery%20from%20Interventions.pdf) | Ch.12 |
| W12 | **迁移学习 / 可迁移性** Transportability | [Video](https://www.youtube.com/watch?v=JNq4oCV9C5k&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=77) | [Slides](https://www.bradyneal.com/slides/12%20-%20Transfer%20Learning%20and%20Transportability.pdf) | Ch.13 |
| W13 | 🎤 **Yoshua Bengio 嘉宾：因果表征学习** | [嘉宾讲座](https://www.youtube.com/watch?v=rKZJ0TJWvTk&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=80) | [Slides](https://www.bradyneal.com/slides/Yoshua_Bengio_Guest_Talk_Towards_Causal_Representation_Learning.pdf) | — |
| W14 | **反事实 + 中介分析** Counterfactuals & Mediation | [Video](https://www.youtube.com/watch?v=f8PEpthLlN4&list=PLoazKTcS0Rzb6bb9L508cyJ1z-U9iWkA0&index=81) | [Slides](https://www.bradyneal.com/slides/14%20-%20Counterfactuals%20and%20Mediation.pdf) | Ch.14 |

**四场嘉宾讲座（均值得单独看）**：Susan Athey（斯坦福，CATE/GRF）、Alberto Abadie（MIT，合成控制）、Jonas Peters（因果发现）、Yoshua Bengio（因果表征学习）。

---

## 阅读小组论文清单（按周/主题）

> 课程配套 weekly reading group（≤15 人讨论制）。以下论文按主题组织，可作为每周延伸阅读；全部开放获取。

**W2 潜在结果**
- [Does obesity shorten life? (Hernán & Taubman, 2008)](https://www.nature.com/articles/ijo200882)
- [Does Obesity Shorten Life? Or is it the Soda? (Pearl, 2018)](https://ftp.cs.ucla.edu/pub/stat_ser/r483-reprint.pdf)

**W3 图模型与 SCM**
- [On the Interpretation of do(x) (Pearl, 2019)](https://www.degruyter.com/view/j/jci.2019.7.issue-1/jci-2019-2002/jci-2019-2002.xml)
- [Quantifying causal influences (Janzing et al., 2012)](https://arxiv.org/abs/1203.6502)
- [Trygve Haavelmo and the Emergence of Causal Calculus (Pearl, 2014)](https://ftp.cs.ucla.edu/pub/stat_ser/r391.pdf)

**W5 随机实验 / 前门 / do-演算**
- [Single World Intervention Graphs: A Primer (Richardson & Robins, 2013)](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.644.1881&rep=rep1&type=pdf)
- [The Paper of How: Front-Door Criterion (Bellemare & Bloem, 2019)](http://marcfbellemare.com/wordpress/wp-content/uploads/2019/08/BellemareBloemFDCAugust2019.pdf)
- [On Pearl's Hierarchy and the Foundations of Causal Inference (Bareinboim et al., 2020)](https://causalai.net/r60.pdf)

**W6 估计与 CATE**
- [Estimating individual treatment effect (Shalit et al., 2017)](https://arxiv.org/abs/1606.03976)
- [Adapting Neural Networks for Treatment Effects (Shi, Blei, Veitch, 2019)](https://arxiv.org/abs/1906.02120)
- [Generalized Random Forests (Athey et al., 2019)](https://arxiv.org/abs/1610.01271)
- [Meta-learners for HTE (Künzel et al., 2017)](https://arxiv.org/abs/1706.03461)

**W7 敏感性分析**
- [Making sense of sensitivity (Cinelli & Hazlett, 2019)](https://rss.onlinelibrary.wiley.com/doi/full/10.1111/rssb.12348)
- [Sense and Sensitivity Analysis (Veitch & Zaveri, 2020)](https://arxiv.org/abs/2003.01747)
- [Sensitivity Analysis in Non-Experimental Prevention Research (Liu et al., 2013)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3800481/)
- [Sensitivity Analysis of Linear SCMs (Cinelli et al., 2019)](http://proceedings.mlr.press/v97/cinelli19a.html)

**W8-9 IV / RDD / DiD / 合成控制**
- [Improving Causal Inference: Natural Experiments (Dunning, 2007)](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.883.6034&rep=rep1&type=pdf)
- [Alternative Causal Inference Methods in Population Health (Mattay et al., 2019)](http://paa2019.populationassociation.org/uploads/190202)
- [Deep IV (Hartford et al., 2017)](http://proceedings.mlr.press/v70/hartford17a/hartford17a.pdf)
- [Regression Discontinuity Designs in Economics (Lee & Lemieux, 2010)](https://www.princeton.edu/~davidlee/wp/RDDEconomics.pdf)

**W10 因果发现（无实验）**
- [Inferring causation from time series (Runge et al., 2019)](https://www.nature.com/articles/s41467-019-10105-3)
- [Distinguishing Cause from Effect (Mooij et al., 2016)](https://jmlr.org/papers/v17/14-518.html)
- [Do-calculus when the True Graph Is Unknown (Hyttinen et al., 2015)](https://www.cs.helsinki.fi/u/mjarvisa/papers/hyttinen-eberhardt-jarvisalo.uai15.pdf)
- [Review of Causal Discovery Methods (Glymour et al., 2019)](https://www.frontiersin.org/articles/10.3389/fgene.2019.00524/full)
- [Invariant prediction (Peters, Bühlmann & Meinshausen, 2016)](https://rss.onlinelibrary.wiley.com/doi/10.1111/rssb.12167)
- [Nonlinear causal discovery with ANMs (Hoyer et al., 2008)](https://papers.nips.cc/paper/3548-nonlinear-causal-discovery-with-additive-noise-models.pdf)
- [Causal Discovery from Nonstationary Data (Huang et al., 2020)](https://arxiv.org/abs/1903.01672)

**W11 因果发现（有实验）**
- [Experiment Selection for Causal Discovery (Hyttinen et al., 2013)](https://jmlr.csail.mit.edu/papers/v14/hyttinen13a.html)
- [Greedy Learning of Interventional MECs (Hauser & Bühlmann, 2012)](https://arxiv.org/abs/1104.2808)
- [Learning Equivalence Classes under Interventions (Yang et al., 2018)](https://arxiv.org/abs/1802.06310)
- [Joint Causal Inference from Multiple Contexts (Mooij et al., 2020)](https://www.jmlr.org/papers/volume21/17-123/17-123.pdf)

**W12 可迁移性与迁移学习**
- [External Validity: Transportability (Pearl & Bareinboim, 2014)](https://ftp.cs.ucla.edu/pub/stat_ser/r400-reprint.pdf)
- [A causal framework for distribution generalization (Christiansen et al., 2020)](https://arxiv.org/abs/2006.07433)
- [Causal inference and the data-fusion problem (Bareinboim & Pearl, 2016)](https://www.pnas.org/content/113/27/7345)
- [On Causal and Anticausal Learning (Schölkopf et al., 2012)](https://icml.cc/2012/papers/625.pdf)
- [Domain Adaptation under Target and Conditional Shift (Zhang et al., 2013)](http://proceedings.mlr.press/v28/zhang13d.html)
- [Multi-Source Domain Adaptation: A Causal View (Zhang et al., 2015)](https://mingming-gong.github.io/papers/AAAI_MULTI.pdf)
- [Invariant Models for Causal Transfer Learning (Rojas-Carulla et al., 2016)](http://www.jmlr.org/papers/volume19/16-432/16-432.pdf)
- [Domain Adaptation as Inference on Graphical Models (Zhang et al., 2020)](https://arxiv.org/abs/2002.03278)
- [Domain Adaptation via Invariant Conditional Distributions (Magliacane et al., 2018)](https://arxiv.org/abs/1707.06422)

**W14 反事实 / 中介 / 路径特异效应**
- [Causal Mediation Effects (Imai et al., 2010)](https://imai.fas.harvard.edu/research/files/mediation.pdf)
- [Identifiability of Path-Specific Effects (Avin et al., 2005)](https://ftp.cs.ucla.edu/pub/stat_ser/r321-ijcai05.pdf)
- [Interpretation and Identification of Causal Mediation (Pearl, 2014)](https://ftp.cs.ucla.edu/pub/stat_ser/r389.pdf)

**因果表征学习**
- [Visual Causal Feature Learning (Chalupka et al., 2015)](http://www.its.caltech.edu/~fehardt/papers/CPE_UAI2015.pdf)
- [Discovering causal signals in images (Lopez-Paz et al., 2017)](https://arxiv.org/abs/1605.08179)
- [Invariant Risk Minimization (Arjovsky et al., 2019)](https://arxiv.org/abs/1907.02893)

---

## 建议学习路径（结合本库闭环法）

1. **路径**：W1→W9 是核心（潜在结果→图模型→后门→do-演算→估计→IV/DiD），每周 1 视频 + 对应教材章节，约 9 周；W10+（因果发现/迁移/表征）按兴趣选学。
2. **测试**：每周用「考官模式」自测该周概念（什么是后门准则？IV 的三个假设？DiD 平行趋势？）。
3. **压缩**：学完 W9 后做一页速查表（识别策略 × 假设 × 适用场景矩阵），放入 `05_求职面试/07_闪卡与速查/`。
4. **量化联动**：IV/DiD/合成控制/RDD 直接是量化金融与计量面试弹药，与 `03_量化金融/` 互补。
5. **提问渠道**：对应 YouTube 视频评论区（作者工作日每天看）；邮件主题加 `[Causal Course]`。

---

*收录于 01_编程基础/06_ML经典理论 · 来源：https://www.bradyneal.com/causal-inference-course · 2026-07-28 整理*
