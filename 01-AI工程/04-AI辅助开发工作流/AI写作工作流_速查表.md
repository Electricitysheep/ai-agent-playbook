# AI 写作工作流 - 速查表

## 🚀 5 分钟快速开始

### 安装（3 分钟）
```bash
# Opencode
npm install -g @opencode/cli

# Quarto
brew install quarto  # macOS
choco install quarto  # Windows

# Zettlr
brew install --cask zettlr  # macOS
choco install zettlr  # Windows
```

### 配置（2 分钟）
```bash
# 创建 config.json
cat > ~/.opencode/config.json << EOF
{
  "providers": {
    "google": {
      "apiKey": "你的 Gemini API Key"
    }
  }
}
EOF

# 获取免费 API Key：https://makersuite.google.com/app/apikey
```

### 测试（1 分钟）
```bash
opencode "写一篇关于 AI 的短文"
```

---

## 📝 常用命令速查

### Opencode 命令
```bash
# 基础使用
opencode "写 [内容类型] 关于 [主题]"

# 指定模型
opencode --model claude-sonnet-4 "写论文"

# 使用 MCP 工具
opencode mcp latex "生成论文模板"

# 文件操作
opencode "总结这个文件" document.md
```

### Quarto 命令
```bash
# 创建项目
quarto create project academic
quarto create project book

# 渲染文档
quarto render document.qmd
quarto render document.qmd --to pdf
quarto render document.qmd --to docx

# 实时预览
quarto preview document.qmd
```

### Zettlr 快捷键
```
Ctrl/Cmd + B     粗体
Ctrl/Cmd + I     斜体
Ctrl/Cmd + K     插入链接
Ctrl/Cmd + E     引用
Ctrl/Cmd + Enter 实时预览
```

---

## 🎯 场景化模板

### 学术论文模板
```bash
# 1. 创建框架
quarto create project paper
cd paper

# 2. AI 生成内容
opencode "写学术论文，主题：[你的主题]，包含摘要、引言、方法、结论" > index.qmd

# 3. 添加引用
# 在 Zettlr 中编辑 references.bib

# 4. 渲染
quarto render index.qmd --to pdf
```

**时间**：30-60 分钟  
**输出**：5000+ 字论文草稿 + PDF

---

### 产品文档模板
```bash
# 1. 创建目录
mkdir -p docs/{overview,features,api}

# 2. 批量生成
opencode "写产品概述" > docs/overview.md
opencode "写功能说明" > docs/features.md
opencode "写 API 文档" > docs/api.md

# 3. 渲染
cd docs
quarto render *.md --to html
```

**时间**：20-40 分钟  
**输出**：完整产品文档 + HTML 网站

---

### 营销文案模板
```bash
# 1. 生成文案
opencode "写营销文案，突出 [卖点 1]、[卖点 2]" > copy.md

# 2. 生成社交媒体版本
opencode "写 10 条推文，每条 280 字" > social.md

# 3. 导出
pandoc copy.md -o copy.docx
pandoc copy.md -o copy.pdf
```

**时间**：15-30 分钟  
**输出**：营销文案 + 社交媒体内容

---

## 🔧 故障排查速查

| 问题 | 快速解决 |
|------|---------|
| Opencode 无响应 | `opencode config show` 检查配置 |
| Quarto 渲染失败 | `quarto install tinytex` |
| 中文乱码 | 保存为 UTF-8 编码 |
| API Key 无效 | 重新获取：https://makersuite.google.com |
| MCP 服务器离线 | `npm install` 重新安装依赖 |

---

## 📊 输出格式对比

| 格式 | 适用场景 | 命令 |
|------|---------|------|
| **PDF** | 学术论文、正式文档 | `--to pdf` |
| **Word** | 企业文档、协作文档 | `--to docx` |
| **HTML** | 网页、博客 | `--to html` |
| **LaTeX** | 学术出版、期刊 | `--to latex` |
| **Markdown** | 技术文档、版本控制 | 原生格式 |

---

## ⚡ 效率技巧

### 快捷键工作流
```
1. Zettlr 编辑 → Ctrl+E 预览
2. 选中内容 → 右键 → Opencode → AI 处理
3. 保存 → Quarto 渲染 → PDF
```

### 批量处理
```bash
# 批量渲染所有文档
for f in *.qmd; do quarto render "$f"; done

# 批量转换为 Word
for f in *.md; do pandoc "$f" -o "${f%.md}.docx"; done
```

### 自动化脚本
```bash
#!/bin/bash
# write.sh - 一键写作工作流

# 1. AI 生成
opencode "$1" > draft.md

# 2. 打开编辑
zettlr draft.md &

# 3. 渲染输出
sleep 5  # 等待编辑完成
quarto render draft.md --to pdf --to docx

echo "完成！输出在 output/ 目录"
```

---

## 📈 质量检查清单

### 写作前
- [ ] 明确写作目标
- [ ] 确定目标读者
- [ ] 准备相关资料
- [ ] 选择合适模板

### 写作中
- [ ] AI 生成初稿
- [ ] 人工审阅修订
- [ ] 添加个人见解
- [ ] 检查逻辑连贯

### 写作后
- [ ] 语法检查（Grammarly）
- [ ] 引用验证（CrossRef）
- [ ] 格式调整（Quarto）
- [ ] 多格式导出

---

## 🔗 资源链接

### 工具官网
- [Opencode](https://github.com/opencode-ai/opencode)
- [Quarto](https://quarto.org)
- [Zettlr](https://zettlr.com)

### API Keys
- [Google Gemini（免费）](https://makersuite.google.com/app/apikey)
- [Anthropic Claude（付费）](https://console.anthropic.com/)
- [OpenAI（付费）](https://platform.openai.com/api-keys)

### 学习资源
- [完整教程](./AI 写作工作流搭建教程_企业版.md)
- [Quarto 文档](https://quarto.org/docs/)
- [MCP 协议](https://modelcontextprotocol.io/)

---

**快速支持**：遇到问题先查故障排查表，再查完整教程  
**版本**：v1.0 | **更新**：2026-03-15
