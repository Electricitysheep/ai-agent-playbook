# OpenCode + oh-my-opencode 接入 DeepSeek V3 完整教程

> 本教程目标：让 oh-my-opencode 的 Subagent 使用 DeepSeek V3（deepseek-chat 模型），实现高性价比的 AI 编程工作流。

---

## 一、背景与架构概览

```
用户指令
   │
   ▼
OpenCode（主入口，CLI 编程助手）
   │
   ├── oh-my-opencode（工作流插件层）
   │       │
   │       ├── Orchestrator Agent（协调器，推荐用 Claude/GPT-4o）
   │       │
   │       └── Subagents（子代理，可单独配置模型）
   │               ├── coder        ← ✅ 推荐接入 DeepSeek V3
   │               ├── reviewer     ← ✅ 推荐接入 DeepSeek V3
   │               ├── planner      ← ✅ 推荐接入 DeepSeek V3
   │               ├── searcher     ← ⚠️  可选
   │               └── summarizer   ← ✅ 推荐接入 DeepSeek V3
   │
   └── DeepSeek API（通过 OpenAI 兼容接口调用）
```

**核心逻辑**：oh-my-opencode 支持为每个 Subagent 单独指定模型，DeepSeek 提供 OpenAI 兼容的 API，因此可以无缝替换。

---

## 二、前置准备

### 2.1 获取 DeepSeek API Key

1. 访问 [https://platform.deepseek.com](https://platform.deepseek.com)
2. 注册并登录账号
3. 进入「API Keys」页面，创建新的 API Key
4. 记录 Key（格式：`sk-xxxxxxxxxxxx`）

> 💡 DeepSeek V3 目前对应模型名为 `deepseek-chat`，DeepSeek R1 为 `deepseek-reasoner`

### 2.2 安装 OpenCode

```bash
# 方式一：npm 全局安装
npm install -g opencode-ai

# 方式二：使用 Homebrew（macOS）
brew install opencode

# 验证安装
opencode --version
```

### 2.3 安装 oh-my-opencode

```bash
# 克隆仓库
git clone https://github.com/sst/opencode ~/.config/opencode/plugins/oh-my-opencode

# 或通过 opencode 插件管理器安装（如支持）
opencode plugin install oh-my-opencode
```

---

## 三、配置 DeepSeek 作为 Provider

### 3.1 配置 OpenCode 的 Provider

编辑 `~/.config/opencode/config.json`（或 `opencode.json`）：

```json
{
  "providers": {
    "deepseek": {
      "name": "DeepSeek",
      "baseURL": "https://api.deepseek.com/v1",
      "apiKey": "sk-你的DeepSeek API Key",
      "models": [
        {
          "id": "deepseek-chat",
          "name": "DeepSeek V3",
          "contextLength": 65536,
          "cost": {
            "input": 0.27,
            "output": 1.10
          }
        },
        {
          "id": "deepseek-reasoner",
          "name": "DeepSeek R1",
          "contextLength": 65536,
          "cost": {
            "input": 0.55,
            "output": 2.19
          }
        }
      ]
    }
  }
}
```

> 💡 DeepSeek API 完全兼容 OpenAI 格式，`baseURL` 换成 `https://api.deepseek.com/v1` 即可。

### 3.2 通过环境变量配置（推荐，更安全）

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export DEEPSEEK_API_KEY="sk-你的DeepSeek API Key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
```

---

## 四、配置 oh-my-opencode Subagent 使用 DeepSeek

### 4.1 oh-my-opencode 配置文件位置

```bash
# 通常在项目根目录或用户配置目录
~/.config/opencode/oh-my-opencode.json
# 或项目级
.opencode/oh-my-opencode.json
```

### 4.2 Subagent 模型配置

```json
{
  "agents": {
    "orchestrator": {
      "model": "anthropic/claude-sonnet-4-5",
      "description": "主协调器，负责任务拆解与分发，建议使用强推理模型"
    },
    "coder": {
      "model": "deepseek/deepseek-chat",
      "provider": "deepseek",
      "description": "代码生成与实现",
      "systemPrompt": "你是一位专业的软件工程师，专注于编写高质量、可维护的代码。"
    },
    "reviewer": {
      "model": "deepseek/deepseek-chat",
      "provider": "deepseek",
      "description": "代码审查与优化建议"
    },
    "planner": {
      "model": "deepseek/deepseek-chat",
      "provider": "deepseek",
      "description": "任务规划与方案设计"
    },
    "summarizer": {
      "model": "deepseek/deepseek-chat",
      "provider": "deepseek",
      "description": "结果总结与文档生成"
    },
    "searcher": {
      "model": "anthropic/claude-haiku-4-5",
      "description": "网络搜索（DeepSeek 暂不支持原生搜索工具，建议保留其他模型）"
    }
  }
}
```

### 4.3 如果使用 YAML 格式配置

```yaml
# oh-my-opencode.yaml
agents:
  orchestrator:
    model: anthropic/claude-sonnet-4-5
    
  coder:
    model: deepseek-chat
    provider: deepseek
    temperature: 0.1        # 代码生成建议低温度
    maxTokens: 8192
    
  reviewer:
    model: deepseek-chat
    provider: deepseek
    temperature: 0.3
    
  planner:
    model: deepseek-chat
    provider: deepseek
    temperature: 0.5        # 规划任务可适当提高创造性
    
  summarizer:
    model: deepseek-chat
    provider: deepseek
    temperature: 0.3
    maxTokens: 4096
```

---

## 五、推荐 Subagent 使用方案

### ✅ 强烈推荐接入 DeepSeek V3 的 Subagent

| Subagent | 推荐理由 | 配置建议 |
|----------|----------|----------|
| **coder**（代码生成） | DeepSeek V3 在代码生成上媲美 GPT-4o，成本极低 | temperature: 0.0~0.1 |
| **reviewer**（代码审查） | 逻辑分析能力强，能发现潜在 Bug 和性能问题 | temperature: 0.2 |
| **planner**（任务规划） | 中文理解能力极强，适合拆解复杂需求 | temperature: 0.3~0.5 |
| **summarizer**（总结器） | 长文档总结效果好，Token 价格便宜 | temperature: 0.3 |
| **refactorer**（重构器） | 代码重构理解深度够用 | temperature: 0.1 |

### ⚠️ 谨慎使用 DeepSeek 的 Subagent

| Subagent | 建议 | 原因 |
|----------|------|------|
| **searcher**（搜索） | ❌ 不推荐 | DeepSeek 不支持原生网络搜索工具调用 |
| **orchestrator**（协调器） | ⚠️ 可选 | 复杂任务协调建议用 Claude/GPT-4o，逻辑更严谨 |
| **vision**（图像理解） | ❌ 不推荐 | DeepSeek V3 视觉能力弱于 GPT-4o Vision |

### 💡 推荐的混合配置方案（最优性价比）

```
Orchestrator  → Claude Sonnet（强规划，确保任务不跑偏）
Coder         → DeepSeek V3（日常代码生成，省钱省力）
Reviewer      → DeepSeek V3（代码审查，逻辑严密）
Planner       → DeepSeek V3（方案设计，中文友好）
Summarizer    → DeepSeek V3（总结文档）
Searcher      → Claude Haiku（联网搜索）
```

---

## 六、验证配置是否生效

```bash
# 在项目目录中启动 opencode
cd your-project
opencode

# 在 opencode 对话中，询问当前使用的模型
> /model

# 或直接触发 subagent 测试
> 帮我写一个 Python 快速排序函数（此请求会触发 coder subagent）
```

查看日志确认 DeepSeek 被调用：

```bash
# 开启详细日志
opencode --debug

# 应能看到类似输出：
# [coder] Using model: deepseek-chat via DeepSeek API
# [coder] Request to: https://api.deepseek.com/v1/chat/completions
```

---

## 七、费用对比参考

| 模型 | 输入价格（/1M tokens） | 输出价格（/1M tokens） |
|------|----------------------|----------------------|
| DeepSeek V3 (`deepseek-chat`) | ¥2（~$0.27） | ¥8（~$1.10） |
| DeepSeek R1 (`deepseek-reasoner`) | ¥4（~$0.55） | ¥16（~$2.19） |
| Claude Sonnet 4.5 | ~$3 | ~$15 |
| GPT-4o | ~$2.5 | ~$10 |

> 💡 **结论**：用 DeepSeek V3 替代 Claude/GPT-4o 做代码生成类任务，可节省 **80%~90%** 的 API 费用，且代码质量差距极小。

---

## 八、常见问题排查

### Q1：调用 DeepSeek 报 401 错误
```bash
# 检查 API Key 是否正确设置
echo $DEEPSEEK_API_KEY

# 手动测试 API 连通性
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

### Q2：Subagent 仍在使用旧模型
- 检查配置文件路径是否正确（项目级 vs 全局）
- 重启 opencode 让配置生效
- 确认 `provider` 字段拼写正确

### Q3：DeepSeek 响应很慢
- 属正常现象，高峰期延迟较高
- 可在 `config.json` 中设置 `timeout: 120000`（120秒）
- 或使用 DeepSeek 的硅基流动镜像节点加速：`https://api.siliconflow.cn/v1`

### Q4：中文输出乱码或质量差
- DeepSeek V3 中文能力极强，如遇问题检查 systemPrompt 是否含中文引导词
- 添加：`"systemPrompt": "请用中文回复，保持专业简洁。"`

---

## 九、进阶：使用国内中转节点（网络不稳定时）

如果直连 DeepSeek API 不稳定，可使用以下兼容节点：

```json
{
  "providers": {
    "deepseek-via-siliconflow": {
      "baseURL": "https://api.siliconflow.cn/v1",
      "apiKey": "你的硅基流动API Key",
      "models": [
        { "id": "deepseek-ai/DeepSeek-V3", "name": "DeepSeek V3 (硅基流动)" }
      ]
    }
  }
}
```

---

*教程版本：2025年3月 | 基于 DeepSeek V3（deepseek-chat）| OpenCode + oh-my-opencode*
