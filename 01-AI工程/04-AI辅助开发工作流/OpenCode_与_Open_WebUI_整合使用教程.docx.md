# OpenCode_与_Open_WebUI_整合使用教程.docx

> **自动转换视窗** (原文件: `OpenCode_与_Open_WebUI_整合使用教程.docx`)


OpenCode 与 Open WebUI 整合使用教程

目录

1. 简介

2. 整合方案概述

3. 前提条件

4. 安装步骤

5. 配置方法

6. 使用示例

7. 常见问题与解决方案

8. 最佳实践

1. 简介

OpenCode 是一个强大的本地 AI 编程工具，支持多种 AI 模型提供商。

Open WebUI 是一个流行的自托管 AI 界面，支持 OpenAI 兼容 API。通过 opencode-llm-proxy 插件，OpenCode 可以将 Open WebUI 作为模型提供程序，实现无缝集成。

主要优势：

- 使用已订阅的模型（如 GitHub Copilot、Claude、Gemini 等）

- 集中管理多个 AI 提供商

- 本地部署，提高隐私和安全性

- 降低 API 成本

2. 整合方案概述

核心组件：

1. OpenCode：主应用程序，作为 AI 模型的管理器

2. opencode-llm-proxy：OpenCode 插件，充当 OpenAI 兼容的代理服务器

3. Open WebUI：前端界面，通过代理服务器访问 OpenCode 模型

工作流程：

- OpenCode 启动并加载 opencode-llm-proxy 插件

- 代理服务器在 localhost:4010 上运行

- Open WebUI 配置为使用代理服务器作为 API 端点

- 所有请求通过代理转发到相应的模型提供商

3. 前提条件

- Node.js 环境（用于安装 opencode-llm-proxy）

- OpenCode CLI 工具已安装

- Open WebUI 实例（本地或远程）

- 对基础 Linux/Unix 命令的熟悉度

4. 安装步骤

4.1 安装 OpenCode

# 通过 npm 安装（推荐）

npm install -g opencode

# 或者使用 curl 安装

curl -fsSL https://opencode.ai/install.sh | sh

4.2 安装 opencode-llm-proxy 插件

npm install opencode-llm-proxy

4.3 安装 Open WebUI（可选）

# 使用 Docker 快速启动

curl -fsSL https://raw.githubusercontent.com/open-webui/open-webui/main/scripts/install.sh | sh

# 或者使用 Docker Compose

wget https://raw.githubusercontent.com/open-webui/open-webui/main/docker-compose.yml

docker compose up -d

5. 配置方法

5.1 配置 OpenCode

创建或编辑 opencode.json 配置文件：

{

"$schema": "https://opencode.ai/config.json",

"provider": {

"openwebui": {

"options": {

"baseURL": "http://localhost:3001"

},

"models": {

"qwen3.5:9b": {

"limit": {

"context": 8192,

"output": 1024

},

"options": {

"num_ctx": 8192,

"num_predict": 512,

"temperature": 0.2,

"top_p": 0.9,

"repeat_penalty": 1.05

}

}

}

}

}

}

5.2 配置 Open WebUI

在 Open WebUI 中添加 OpenCode 模型提供程序：

1. 登录 Open WebUI 管理界面

2. 导航到 Admin Settings → Connections

3. 点击 Add Connection

4. 输入：

- Name: OpenCode-Proxy

- API Base URL: http://localhost:4010/v1

5. 点击 Save

5.3 环境变量配置

export OPENCODE_LLM_PROXY_HOST=127.0.0.1

export OPENCODE_LLM_PROXY_PORT=4010

export OPENCODE_LLM_PROXY_TOKEN=your-secret-token

export OPENCODE_LLM_PROXY_CORS_ORIGIN=https://your-webui.com

5.4 启动服务

# 启动 OpenCode（自动启动代理）

opencode

# 或者设置环境变量后启动

OPENCODE_LLM_PROXY_HOST=0.0.0.0 \

OPENCODE_LLM_PROXY_PORT=4010 \

OPENCODE_LLM_PROXY_TOKEN=my-secret \

opencode

6. 使用示例

6.1 Python SDK 使用

from openai import OpenClient

client = OpenClient(

base_url="http://127.0.0.1:4010/v1",

api_key="unused"

)

response = client.chat.completions.create(

model="qwen3.5:9b",

messages=[{"role": "user", "content": "解释 SOLID 原则"}]

)

print(response.choices[0].message.content)

6.2 命令行使用

# 直接使用 OpenCode CLI

opencode chat "如何优化数据库查询性能？"

# 指定特定模型

opencode --model qwen3.5:9b chat "解释 RESTful API 设计原则"

7. 常见问题与解决方案

7.1 连接问题

症状: Open WebUI 无法加载模型列表

解决方案：

1. 验证代理服务器是否运行：curl http://localhost:4010/v1/models

2. 检查防火墙设置，确保端口 4010 可访问

3. 验证 OpenCode 服务是否正常运行

7.2 认证失败

症状: 401 未授权错误

解决方案：

1. 确认 OPENCODE_LLM_PROXY_TOKEN 环境变量匹配

2. 在 Open WebUI 配置中正确设置 API Key

3. 检查令牌是否过期

7.3 模型不可用

症状: 在 Open WebUI 中选择模型时提示不可用

解决方案：

1. 确认模型已在 OpenCode 中正确配置

2. 检查模型名称格式：provider:model

3. 重启 OpenCode 服务以重新发现模型

8. 最佳实践

8.1 安全配置

- 使用 HTTPS 连接（生产环境）

- 设置强认证令牌

- 限制网络访问权限（仅本地或特定 IP）

- 定期轮换 API 密钥

8.2 模型管理

- 为不同项目使用独立的 opencode.json 配置

- 记录模型使用情况以优化成本

- 定期测试模型质量和响应时间

8.3 故障排除

- 启用调试日志：OPENCODE_LOG_LEVEL=debug opencode

- 检查代理服务器日志

- 使用 OpenAPI 测试工具验证端点

- 保持 OpenCode 和插件版本同步

8.4 性能优化

export OPENCODE_LLM_PROXY_HOST=0.0.0.0

export OPENCODE_LLM_PROXY_PORT=4010

export OPENAI_NUM_THREADS=4

附录 A: 支持的模型提供商

- OpenAI (GPT 系列)

- Anthropic (Claude 系列)

- Google (Gemini 系列)

- Azure OpenAI

- AWS Bedrock

- Ollama (本地模型)

- 自定义 OpenAI 兼容端点

附录 B: 配置验证

1. 检查代理服务器状态：curl http://localhost:4010/v1/health

2. 列出可用模型：curl http://localhost:4010/v1/models

3. 测试简单请求：curl -X POST http://localhost:4010/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "qwen3.5:9b", "messages": [{"role": "user", "content": "Hello"}]}'

附录 C: 版本兼容性

OpenCode 版本

最新稳定版

附录 D: 故障排除命令

# 查看 OpenCode 日志

opencode --log-level debug

# 测试代理连接

curl -v http://localhost:4010/v1/models

# 检查进程状态

ps aux | grep opencode

# 查看端口使用情况

netstat -tlnp | grep 4010

附录 E: 高级配置

E.1 负载均衡

{

"provider": {

"openwebui": {

"options": {

"baseURL": "http://localhost:3001,http://localhost:3002",

"load_balancing": "round_robin"

}

}

}

}

E.2 缓存配置

{

"provider": {

"openwebui": {

"options": {

"cache_enabled": true,

"cache_ttl": 3600

}

}

}

}

E.3 多租户支持

{

"provider": {

"openwebui": {

"options": {

"tenant_mode": true,

"tenant_config": {

"tenant1": {"baseURL": "http://tenant1:3001"},

"tenant2": {"baseURL": "http://tenant2:3001"}

}

}

}

}

}

附录 F: 参考资料

- OpenCode 官方文档 (https://open-code.ai/docs)

- Open WebUI 文档 (https://docs.openwebui.com)

- opencode-llm-proxy GitHub (https://github.com/KochC/opencode-llm-proxy)

- OpenWebUI GitHub (https://github.com/open-webui/open-webui)

---

版本: 1.0

最后更新: 2026年3月

作者: OpenCode 文档团队