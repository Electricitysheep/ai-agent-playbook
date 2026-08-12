# 英文 AI 工程实战资源补充清单

> AI 应用/Agent 开发工程师方向 | 2025-2026 年维护中
> 配合工程实践缺口清单使用
> 优先级: P0=立即用 / P1=1-3 月内 / P2=读研后

---

## 为什么这些资源对 AI 应用工程师重要

AI 应用工程师的核心竞争力 = **能调模型 + 能搭系统 + 能上线运维**。本清单覆盖从 LLM 微调(简历硬技能)、ML 理论(面试+读研先修)、容器化部署(Agent Infra 必备)、系统设计(RAG/Agent 平台架构)到测试工程(生产级代码质量)的完整闭环,全部选自 2025 年仍活跃维护的官方文档、高星 GitHub 仓库和权威课程。

---

## 1. LLM 微调 (SFT/LoRA) — P0(立即用,补简历硬技能)

### 资源 1: [HuggingFace TRL 官方文档](https://huggingface.co/docs/trl/index)
- **平台/作者**: HuggingFace / TRL Team
- **推荐理由**: TRL 是目前最标准的 RLHF/SFT/DPO/GRPO 全栈训练库,与 transformers 深度集成。2025 年已原生支持 GRPO(DeepSeek-R1 同款训练方法),是工业界和学术界的事实标准。
- **使用方式**: 直接阅读 Quickstart 和 Trainer API 文档,配合 Colab 示例跑通第一个 SFT 脚本。
- **优先级**: P0

### 资源 2: [LoRA: Low-Rank Adaptation of Large Language Models (论文 + 代码)](https://arxiv.org/abs/2106.09685)
- **平台/作者**: Microsoft Research / Edward J. Hu 等 (ICLR 2022)
- **推荐理由**: LoRA 是 LLM 微调的基石论文。理解它能让你在面试中讲清楚"为什么只训 0.1% 参数就能达到全量微调效果",并理解 rank、alpha、target_modules 等超参数背后的数学直觉。
- **使用方式**: 读论文 Section 1-4 + 附录 E;代码仓库 [microsoft/LoRA](https://github.com/microsoft/LoRA) (14K+ stars) 看 `loralib/` 实现。
- **优先级**: P0

### 资源 3: [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
- **平台/作者**: hiyouga / 社区 (37K+ stars, Apache 2.0)
- **推荐理由**: 支持 100+ 模型、SFT/DPO/PPO/GRPO 全方法、内置 WebUI (LlamaBoard)、可一键对接 Unsloth 后端加速。是 2025 年入门到生产最友好的微调框架,README 本身就是一份中文/英文双语的微调百科全书。
- **使用方式**: 精读 README → 用 WebUI 或 CLI 跑一个 7B QLoRA 示例 → 尝试自定义 dataset 模板。
- **优先级**: P0

### 资源 4: [Unsloth](https://github.com/unslothai/unsloth)
- **平台/作者**: Unsloth AI (23K+ stars)
- **推荐理由**: 通过手写 Triton Kernel 实现 2-5× 训练加速、70-80% VRAM 节省。在单卡(RTX 4090)上微调 7B/13B 模型的首选。2025 年已支持 GRPO 和多 GPU。
- **使用方式**: 从官方 Colab Notebook 开始,体验"同样的模型,VRAM 从 24GB 降到 8GB"的震撼;可与 LLaMA-Factory 组合使用。
- **优先级**: P0

### 资源 5: [Axolotl](https://github.com/axolotl-ai-cloud/axolotl)
- **平台/作者**: axolotl-ai-cloud (9K+ stars, Apache 2.0)
- **推荐理由**: YAML 配置驱动的训练框架,擅长多 GPU 分布式 (FSDP/DeepSpeed)、长上下文序列并行、完整 RLHF 流水线。适合团队协作和可复现实验。
- **使用方式**: 阅读 `examples/` 下的 YAML 配置,理解 `base_model`、`datasets`、`sequence_len`、`fsdp` 等字段。
- **优先级**: P1(团队/多卡场景再深入)

### 资源 6: [HuggingFace PEFT](https://github.com/huggingface/peft)
- **平台/作者**: HuggingFace
- **推荐理由**: LoRA/QLoRA/DoRA/IA³ 等参数高效微调方法的底层实现库。TRL、LLaMA-Factory 都依赖它。理解 PEFT 的 `LoraConfig` 和 `get_peft_model` 是调试微调问题的必备技能。
- **使用方式**: 阅读官方 Quicktour,手动给一个 `AutoModel` 注入 LoRA adapter。
- **优先级**: P0

---

## 2. ML 经典理论 (读研先修 + 面试推导) — P1

### 资源 1: [Stanford CS229: Machine Learning](https://cs229.stanford.edu/)
- **平台/作者**: Stanford / Andrew Ng (2025 Summer/Fall 持续开课)
- **推荐理由**: 面试中推导 SVM 对偶、逻辑回归梯度、偏差-方差分解的标准答案来源。2025 年课程已加入 Transformers 和 Agentic AI Guest Lecture,经典与前沿兼顾。
- **使用方式**: 下载 [main_notes.pdf](https://cs229.stanford.edu/main_notes.pdf) 系统阅读;配合 SEE 视频 (see.stanford.edu) 复习关键 Lecture。
- **优先级**: P1

### 资源 2: [DeepLearning.AI 课程](https://www.deeplearning.ai/courses/)
- **平台/作者**: DeepLearning.AI / Andrew Ng
- **推荐理由**: 从神经网络基础到 CNN/RNN/Transformer 的体系化课程。2025 年新增《Generative AI with LLMs》《AI Python for Beginners》等,与 Agent 开发直接相关。
- **使用方式**: Coursera 或官网免费旁听;重点完成《Machine Learning Specialization》+《Generative AI with LLMs》。
- **优先级**: P1

### 资源 3: [fast.ai — Practical Deep Learning for Coders](https://course.fast.ai/)
- **平台/作者**: fast.ai / Jeremy Howard & Sylvain Gugger
- **推荐理由**: 实战派圣经,"自上而下"教学法:先让你用 5 行代码跑通 SOTA 模型,再逐层拆解原理。2025 年课程持续更新,涵盖 Stable Diffusion、HuggingFace Transformers、Gradio 部署。
- **使用方式**: 配合 [fastbook](https://fastai.github.io/fastbook2e/) 免费在线版,用 Kaggle Notebook 完成每章作业。
- **优先级**: P1

### 资源 4: [Cornell CS4780 — Machine Learning for Intelligent Systems](https://www.cs.cornell.edu/courses/cs4780/2024sp/)
- **平台/作者**: Cornell / Kilian Weinberger 等
- **推荐理由**: "stochastic balanced notes" 替代品中的优选。笔记极度清晰,概率图模型、核方法、Boosting 等面试高频推导都有详细步骤。
- **使用方式**: 阅读 Lecture Notes PDF,重点复习 SVM、Kernel Methods、EM Algorithm。
- **优先级**: P1

---

## 3. 容器化与部署 (Agent Infra 必备) — P1

### 资源 1: [Docker — Get Started 官方教程](https://docs.docker.com/get-started/)
- **平台/作者**: Docker Inc.
- **推荐理由**: 容器化的唯一官方入口。2025 年教程已整合 Docker Desktop、Dockerfile best practices 和 multi-stage build。Agent 服务打包成镜像是一切部署的前提。
- **使用方式**: 完成 12 步 Hands-on 教程;重点理解 `Dockerfile` 分层缓存和 `.dockerignore`。
- **优先级**: P1

### 资源 2: [Docker Compose 官方文档](https://docs.docker.com/compose/)
- **平台/作者**: Docker Inc.
- **推荐理由**: 本地开发 Agent 平台(LLM API + Vector DB + Web App)的标配编排工具。一个 `docker-compose.yml` 就能拉起 Postgres + Redis + FastAPI + Celery 全栈。
- **使用方式**: 阅读 Compose file reference;写一个包含 `app`、`db`、`redis`、`worker` 四个 service 的 compose 文件。
- **优先级**: P1

### 资源 3: [Kubernetes Basics 官方教程](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- **平台/作者**: Kubernetes / CNCF
- **推荐理由**: 生产级 Agent 平台部署的通用标准。理解 Pod、Deployment、Service、ConfigMap 是 K8s 面试和实际运维的最低要求。
- **使用方式**: 用 Minikube 或 Kind 本地跑通官方 Interactive Tutorial;尝试部署一个 FastAPI 服务。
- **优先级**: P1

### 资源 4: [GitHub Actions — CI/CD 官方文档](https://docs.github.com/en/actions)
- **平台/作者**: GitHub
- **推荐理由**: 2025 年最主流的免费 CI/CD 平台。自动化测试 → 构建镜像 → 推送 Registry → 触发部署,是 Agent 项目从代码到上线的标准流水线。
- **使用方式**: 写一个 `.github/workflows/ci.yml`,实现 pytest → Docker build → push to GHCR 的完整流水线。
- **优先级**: P1

---

## 4. 系统设计 (LLM / RAG / Agent 平台) — P1-2

### 资源 1: [Designing Data-Intensive Applications (DDIA)](https://dataintensive.net/)
- **平台/作者**: Martin Kleppmann / O'Reilly
- **推荐理由**: 系统设计面试的"圣经"。2025 年第二版 Early Release 已出,新增流处理、数据契约、事件溯源等现代架构内容。RAG 系统的向量存储、一致性、分区策略全部能在书中找到理论根基。
- **使用方式**: 精读 Part I (数据模型/存储) 和 Part II (分布式数据);配合 [ddia2-references](https://github.com/ept/ddia2-references) 追踪每章延伸阅读。
- **优先级**: P1

### 资源 2: [System Design Primer](https://github.com/donnemartin/system-design-primer)
- **平台/作者**: Donne Martin (355K+ stars)
- **推荐理由**: GitHub 上星数最高的系统设计学习仓库。包含大量面试题(设计 Twitter、URL Shortener、Chat 系统)的逐步拆解,以及 Anki 记忆卡。2026 年 3 月仍在活跃更新。
- **使用方式**: 精读 README 中的 "Index of system design topics";用 Anki 卡片背诵核心概念;尝试手写一个 "Design a RAG-based QA System" 的方案。
- **优先级**: P1

### 资源 3: [Chip Huyen — LLMOps & LLM Patterns](https://huyenchip.com/2023/10/10/llmops.html)
- **平台/作者**: Chip Huyen (Stanford / Claypot AI)
- **推荐理由**: 《Designing Machine Learning Systems》作者,2023-2025 年持续输出 LLM 工程化文章。涵盖 Prompt 管理、模型路由、A/B 测试、Guardrails、成本优化等 Agent 平台设计实战细节。
- **使用方式**: 阅读 "LLM Patterns" 系列博客;关注她的 Newsletter 获取最新工程实践。
- **优先级**: P1

### 资源 4: [LangChain — Build a RAG Application 官方教程](https://python.langchain.com/docs/tutorials/rag/)
- **平台/作者**: LangChain
- **推荐理由**: 2025 年最标准的 RAG 系统实现教程。覆盖 Document Loader → Text Splitter → Embedding → Vector Store → Retriever → Generation 的完整链路,代码可直接嵌入生产项目。
- **使用方式**: 完整跑通 Tutorial;尝试替换不同组件(Chroma → Pinecone / OpenAI → Ollama)理解模块化设计。
- **优先级**: P1

### 资源 5: [LiteLLM (LLM Gateway)](https://github.com/BerriAI/litellm)
- **平台/作者**: BerriAI (10K+ stars)
- **推荐理由**: 开源 LLM Gateway 实现,统一调用 100+ 模型(OpenAI、Anthropic、本地 vLLM 等),内置速率限制、负载均衡、成本追踪、Fallback 机制。是理解"LLM Gateway 设计模式"的最佳生产级参考。
- **使用方式**: 本地部署 LiteLLM Proxy;配置多个模型端点,测试 Fallback 和 Rate Limiting。
- **优先级**: P2(读研后/大型 Agent 平台场景)

### 资源 6: [ByteByteGo — System Design 视频与 newsletter](https://bytebytego.com/)
- **平台/作者**: Alex Xu (《System Design Interview》作者)
- **推荐理由**: 2025 年最活跃的系统设计可视化学习资源。有专门的 "Designing a RAG System"、"LLM Gateway Architecture" 等 AI 基础设施专题。
- **使用方式**: 订阅 Newsletter;观看 YouTube 上的 RAG/Agent 架构视频。
- **优先级**: P2

---

## 5. 测试工程 (pytest) — P1

### 资源 1: [pytest 官方文档](https://docs.pytest.org/)
- **平台/作者**: pytest-dev 社区
- **推荐理由**: Python 测试的事实标准。2025 年文档已覆盖 fixtures、parametrize、plugins、async 测试等全功能。AI 应用工程师写的每一个 LLM 调用封装都必须有测试。
- **使用方式**: 完成 Getting Started 和 "How to write and report assertions in tests";重点掌握 `conftest.py` 和 fixture 作用域。
- **优先级**: P1

### 资源 2: [Coverage.py + pytest-cov](https://coverage.readthedocs.io/)
- **平台/作者**: Ned Batchelder / pytest-dev
- **推荐理由**: 测试覆盖率是代码质量的底线指标。pytest-cov 一键生成 HTML 报告,能精确定位哪些 LLM 分支逻辑没有被测试覆盖。
- **使用方式**: `pip install pytest-cov` → `pytest --cov=src --cov-report=html` → 将覆盖率门槛写入 CI。
- **优先级**: P1

### 资源 3: [Pytest-with-Eric — pytest TDD Example](https://github.com/Pytest-with-Eric/pytest-tdd-example)
- **平台/作者**: Eric (Pytest 实战博主)
- **推荐理由**: 一个完整展示 Red-Green-Refactor 流程的示例仓库,包含 fixtures、mocking、parametrize 的实战用法。比官方文档更贴近真实项目结构。
- **使用方式**: Clone 仓库 → 按 README 步骤执行 TDD 循环 → 将模式迁移到自己的 Agent 项目。
- **优先级**: P1

### 资源 4: [freeCodeCamp — Test-Driven Development 教程](https://www.freecodecamp.org/news/tag/tdd/)
- **平台/作者**: freeCodeCamp 社区
- **推荐理由**: 大量免费的 TDD + pytest 实战文章,覆盖 Flask/FastAPI 项目的测试策略。适合快速查阅具体场景(如 "How to mock OpenAI API calls in pytest")。
- **使用方式**: 搜索 "pytest mock API" 等关键词,按需阅读。
- **优先级**: P1

### 资源 5: [unittest.mock 官方指南](https://docs.python.org/3/library/unittest.mock.html)
- **平台/作者**: Python 官方
- **推荐理由**: AI 应用测试的核心难点是 LLM 调用不可控、慢、贵。Mock 是单元测试隔离外部依赖的唯一手段。必须掌握 `Mock`、`patch`、`side_effect`。
- **使用方式**: 阅读 Python 官方 `unittest.mock` 文档;在测试中 `patch("openai.ChatCompletion.create")` 模拟 LLM 响应。
- **优先级**: P1

---

## 快速行动建议

| 时间窗口 | 行动 |
|---------|------|
| **本周** (P0) | ① 跑通 TRL Quickstart SFT 示例;② 用 LLaMA-Factory WebUI 微调一个 7B 模型;③ 精读 LoRA 论文前 4 节 |
| **1 个月内** (P1) | ① 完成 Docker Get Started + Compose 多服务编排;② 用 pytest + mock 给现有项目补测试;③ 跑通 LangChain RAG Tutorial |
| **3 个月内** (P1) | ① 精读 DDIA Part I & II;② 完成 System Design Primer 中 3 个经典设计题;③ 本地部署 LiteLLM 理解 Gateway 模式 |
| **读研后** (P2) | ① 系统复习 CS229 notes + 西瓜书;② 深入 K8s 生产运维;③ 跟进 Chip Huyen / ByteByteGo 最新架构文章 |

---

> **维护状态确认**: 以上所有 GitHub 仓库和官方文档在 2025-2026 年均有活跃 commit 或持续更新,可直接作为简历项目和面试谈资。
> **搜集日期**: 2026-07-07
