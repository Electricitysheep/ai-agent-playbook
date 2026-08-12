# Docker 个人上手清单：从零到能独立部署多服务应用

> 目标：用 **2-3 天碎片时间** 建立 Docker 核心心智模型，能看懂 `docker-compose.yml`、写出项目 `Dockerfile`、排查常见问题。
> 适用：Windows / macOS / Linux 通用，以 **Docker Desktop** 为主。

---

## 🎯 学习路线图（按阶段打卡）

| 阶段 | 耗时 | 核心产出 | 验收标准 |
|---|---|---|---|
| **Day 0** | 30 min | 环境就绪 | `docker run hello-world` 成功、能进容器 `sh` |
| **Day 1** | 2-3 h | 概念 + 基础命令 | 能解释 Image/Container/Volume 区别；熟练用 15 条核心命令 |
| **Day 2** | 3-4 h | Dockerfile 实战 | 给自己的一个项目（Python/Node/Go）写出可跑的 `Dockerfile`、构建推送 |
| **Day 3** | 2-3 h | Compose 多服务编排 | 能把 `redis + postgres + 你的服务` 用 `docker-compose.yml` 一键起停 |
| **持续** | 随项目 | 进阶技巧 | 多阶段构建、健康检查、日志/备份策略、CI/CD 集成 |

---

## 📦 Day 0：环境安装与验证

### 0.1 安装 Docker Desktop（推荐）
- **Windows/macOS**：<https://www.docker.com/products/docker-desktop/> 下载安装包 → 双击安装 → 重启电脑
- **Linux**：`curl -fsSL https://get.docker.com | sh` → `sudo usermod -aG docker $USER` → 重新登录
- **WSL2 集成（Win 必开）**：Settings → Resources → WSL Integration → 勾选你的发行版

### 0.2 验证清单
```bash
# 1. 版本
docker --version          # 例：Docker version 27.0.0
docker compose version    # 例：Docker Compose version v2.27.0

# 2. 跑通官方测试镜像
docker run --rm hello-world
# 看到 "Hello from Docker!" 即成功

# 3. 体验一次完整生命周期
docker run -d -p 8080:80 --name my-nginx nginx
curl http://localhost:8080          # 看到 "Welcome to nginx!"
docker logs my-nginx                # 看访问日志
docker exec -it my-nginx sh         # 进容器内部
docker stop my-nginx && docker rm my-nginx
```

> ✅ **Day 0 打卡**：截图保存 `hello-world` 输出 + `nginx` 访问成功页面。

---

## 🧠 Day 1：核心概念 + 15 条必会命令

### 1.1 三大核心对象（必须能白板画出关系图）

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Host                          │
│  ┌──────────────┐    build/pull     ┌──────────────────┐   │
│  │  Dockerfile  │ ────────────────▶ │     Image        │   │
│  │  (配方)      │                   │  (只读分层模板)   │   │
│  └──────────────┘                   └────────┬─────────┘   │
│                                               │ run         │
│                                               ▼             │
│  ┌──────────────┐    -v 挂载      ┌──────────────────┐   │
│  │   Volume     │ ◀────────────── │   Container      │   │
│  │ (持久化数据)  │                 │ (可读写运行实例)   │   │
│  └──────────────┘                 └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

| 概念 | 本质 | 生命周期 | 类比 |
|---|---|---|---|
| **Image** | 只读分层文件系统 + 启动配置 | 永久（除非 `rmi`） | 安装包 / 保鲜盒 |
| **Container** | Image + 可读写层 + 隔离命名空间 | 临时（停止可再启动，`rm` 即删） | 运行中的程序进程 |
| **Volume** | Host 目录或 Docker 管理的存储 | 独立于容器，容器删了数据在 | 移动硬盘 |

### 1.2 15 条核心命令（分类记忆，每天练 3 条）

#### 镜像管理
```bash
docker pull <image>[:tag]        # 下载（不跑也可先 pull）
docker images                    # 列出本地镜像
docker rmi <image>               # 删除镜像
docker image prune -a            # 清理无用镜像（慎用）
```

#### 容器生命周期
```bash
docker run -d -p 80:80 --name web nginx   # 后台跑、映射端口、命名
docker ps                                 # 只看运行中
docker ps -a                              # 全部（含停止）
docker stop <name>                        # 优雅停止 (SIGTERM → 10s → SIGKILL)
docker start <name>                       # 重新启动已停止容器
docker restart <name>                     # 重启
docker rm <name>                          # 删除容器（需先 stop）
docker rm -f <name>                       # 强制删（含运行中）
```

#### 进容器调试
```bash
docker logs -f <name>          # 实时看日志（Ctrl+C 退出不停容器）
docker exec -it <name> sh      # 进容器交互式 shell（最常用）
docker exec -it <name> bash    # 如果镜像有 bash
docker top <name>              # 看容器内进程
docker stats <name>            # 实时资源占用（CPU/内存/网络/IO）
```

#### 数据卷（重点！）
```bash
docker volume create mydata               # 创建命名卷
docker volume ls                          # 列出
docker volume inspect mydata              # 看挂载点（/var/lib/docker/volumes/...）
docker run -v mydata:/app/data ...        # 挂载：容器删了数据还在
docker run -v $(pwd)/config:/etc/app ...  # 绑定挂载：本地目录直连（开发首选）
docker volume rm mydata                   # 删卷（数据永久丢失，慎用）
```

> ✅ **Day 1 打卡**：不看文档，凭记忆在终端完成：起一个 `redis` 容器、挂载本地 `./redis.conf`、进容器 `redis-cli ping`、停容器删容器、卷还在。

---

## 🏗️ Day 2：写 Dockerfile（把你的项目容器化）

### 2.1 标准模板（Node / Python / Go 通用套路）

#### Node.js (Next.js / Express / NestJS)
```dockerfile
# ---- Build Stage ----
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev                 # 只装生产依赖，利用缓存层
COPY . .
RUN npm run build                     # 产出 dist/ 或 .next/

# ---- Runtime Stage ----
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# 非 root 用户（安全最佳实践）
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./
USER nextjs
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

#### Python (FastAPI / Django / Flask)
```dockerfile
# ---- Build Stage ----
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir poetry==1.8.3
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---- Runtime Stage ----
FROM python:3.12-slim
WORKDIR /app
RUN adduser --disabled-password --gecos "" appuser
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Go (原生静态链接，极简)
```dockerfile
# ---- Build Stage ----
FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server .

# ---- Runtime Stage (scratch: 空镜像，仅 2-5MB) ----
FROM scratch
COPY --from=builder /app/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

### 2.2 Dockerfile 核心指令速查

| 指令 | 作用 | 避坑提示 |
|---|---|---|
| `FROM` | 基础镜像 | 优先选 `alpine`/`slim`/`scratch` 减体积；指定 digest `@sha256:...` 锁版本 |
| `WORKDIR` | 设定工作目录 | 只用绝对路径，别用相对 `../` |
| `COPY` | 复制文件进镜像 | **利用缓存层**：先 `COPY package*.json` 再 `RUN npm ci`，代码变不重装依赖 |
| `RUN` | 构建时执行命令 | 合并同层：`RUN apt-get update && apt-get install -y xx && rm -rf /var/lib/apt/lists/*` |
| `ENV` | 环境变量 | 运行时也可 `-e` 覆盖 |
| `EXPOSE` | 文档化端口 | 不实际开放，需 `docker run -p` |
| `USER` | 切换非 root 用户 | **生产必加**，配合 `adduser` |
| `CMD` / `ENTRYPOINT` | 启动命令 | `ENTRYPOINT` 固定主命令，`CMD` 提供默认参数，`docker run` 追加参数会覆盖 `CMD` |
| `HEALTHCHECK` | 健康检查 | `HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8080/health \|\| exit 1` |

### 2.3 .dockerignore（必须有，否则上下文巨大）
```gitignore
# .dockerignore
node_modules
dist
.build
.git
.gitignore
README.md
*.log
*.md
.env
.env.*
.vscode
.idea
coverage
.turbo
```

### 2.4 构建与测试
```bash
# 构建（加 tag 方便管理）
docker build -t myapp:1.0.0 .

# 看分层大小
docker history myapp:1.0.0

# 跑起来测试
docker run --rm -p 3000:3000 -e NODE_ENV=production myapp:1.0.0

# 推送到仓库（可选）
docker tag myapp:1.0.0 yourname/myapp:1.0.0
docker push yourname/myapp:1.0.0
```

> ✅ **Day 2 打卡**：给自己 GitHub 上一个小项目写 `Dockerfile`，构建成功、本地跑通、镜像体积 < 200MB（Node/Python），推送到 Docker Hub 或 GHCR。

---

## 🎼 Day 3：docker-compose 多服务编排（实战核心）

### 3.1 为什么要 Compose
- 单命令起停多容器：`docker compose up -d`
- 声明式配置：版本控制、可复现、团队共享
- 网络自动互通：服务名即域名（`redis://redis:6379`）

### 3.2 标准项目结构
```
my-project/
├── docker-compose.yml          # 主编排（生产）
├── docker-compose.override.yml # 本地开发覆盖（gitignore）
├── .env.example                # 环境变量模板
├── .env                        # 实际值（gitignore）
├── Dockerfile                  # 你的服务镜像
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
└── scripts/
    ├── init-db.sql
    └── backup.sh
```

### 3.3 实战模板（Web + Redis + Postgres + Nginx 反代）

#### docker-compose.yml（生产/通用）
```yaml
version: "3.9"

services:
  # 你的应用服务
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: myapp:${TAG:-latest}
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M

  # PostgreSQL
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASS}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 128mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Nginx 反代（可选：SSL/静态文件/限流）
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on: [app]

volumes:
  pgdata:
  redisdata:

networks:
  default:
    name: myapp-net
```

#### docker-compose.override.yml（本地开发，不提交）
```yaml
version: "3.9"
services:
  app:
    build:
      target: builder          # 用构建阶段镜像（含 devDependencies）
    command: npm run dev       # 热重载
    volumes:
      - .:/app:cached          # 源码挂载（cached 加速 macOS/WSL2）
      - /app/node_modules      # 匿名卷保护容器内 node_modules
    ports:
      - "3000:3000"            # 直接暴露
    environment:
      - NODE_ENV=development
  db:
    ports:
      - "5432:5432"            # 本地直连方便 GUI 工具
  redis:
    ports:
      - "6379:6379"
```

#### .env.example（提交）
```bash
# 应用
TAG=latest

# 数据库
DB_USER=myapp
DB_PASS=changeme_strong_password
DB_NAME=myapp

# Redis 无需密码时留空
# REDIS_PASS=
```

### 3.4 常用 Compose 命令
```bash
# 起所有（后台）
docker compose up -d

# 只起指定服务
docker compose up -d app redis

# 看日志（聚合所有服务）
docker compose logs -f
docker compose logs -f app    # 只看 app

# 进容器
docker compose exec app sh

# 重新构建并起
docker compose up -d --build

# 拉取最新基础镜像再建
docker compose pull && docker compose up -d --build

# 停止并删除容器（保留卷）
docker compose down

# 连卷一起删（慎用！数据全无）
docker compose down -v

# 查看配置合并结果
docker compose config
```

> ✅ **Day 3 打卡**：把模板改成你的项目配置，跑通 `docker compose up -d`，能用 `curl localhost/health` 访问到应用，`docker compose down -v` 后再 `up` 数据库数据还在。

---

## 🚀 进阶：生产级必加项（按需学）

| 主题 | 关键点 | 学习触发时机 |
|---|---|---|
| **多阶段构建** | Build/Runtime 分离、缓存层复用、`scratch` 极简镜像 | 镜像 > 500MB 或构建慢时 |
| **健康检查** | `HEALTHCHECK` / compose `healthcheck`、`depends_on.condition` | 服务启动顺序依赖、自动重启 |
| **资源限制** | `deploy.resources.limits`、OOM Kill 避免 | 多容器共宿主机、内存溢出时 |
| **日志驱动** | `logging.driver: json-file` + `max-size/max-file`、或 `loki`/`fluentd` | 磁盘被日志撑爆时 |
| **数据备份** | `pg_dump` 定时任务、Volume 备份脚本、S3 上传 | 上线前必须有 |
| **密钥管理** | `.env` 不提交、Docker Secrets、1Password CLI 注入、SOPS 加密 | 有真实密钥时 |
| **多架构构建** | `docker buildx build --platform linux/amd64,linux/arm64` | 树莓派/ARM 服务器部署 |
| **CI/CD 集成** | GitHub Actions: `docker/build-push-action`、缓存 `cache-from/to` | 自动化发布需求 |

---

## 🛠️ 常见坑 & 排查清单

| 现象 | 可能原因 | 排查命令 |
|---|---|---|
| 容器秒退 | 启动命令错、缺环境变量、端口冲突 | `docker logs <name>`、`docker inspect <name>` |
| 宿主机访问不到端口 | `-p` 映射错、防火墙、服务没绑 `0.0.0.0` | `docker port <name>`、`ss -tlnp`、容器内 `curl localhost:port` |
| 代码改了不生效 | 没挂载源码、缓存层未失效、热重载未开 | `docker compose exec app ls -la`、检查 `volumes` |
| 数据库连不上 | 服务名解析错、健康检查未通过、`depends_on` 只有启动顺序 | `docker compose exec app ping db`、`docker compose ps` |
| 镜像巨大 | 多阶段没用、装了 devDependencies、没清包管理缓存 | `docker history --no-trunc <image>`、`dive <image>` |
| 权限报错 | 容器 root 写宿主机卷、UID/GID 不匹配 | `docker run --user $(id -u):$(id -g)`、Volume `chown` |
| WSL2 磁盘满 | `ext4.vhdx` 膨胀 | `wsl --shutdown` → `diskpart` compact 或 `wsl --manage` |

---

## 📚 优质学习资源（按推荐度）

| 类型 | 推荐 | 适合阶段 |
|---|---|---|
| **官方文档** | <https://docs.docker.com/>（Get Started → Build images → Compose） | 全程 |
| **实战教程** | 《Docker 实战》（第 2 版，Jeff Nickoloff） | Day 1-3 |
| **最佳实践** | <https://github.com/docker/labs> 官方练习场 | Day 2-3 |
| **镜像瘦身** | <https://github.com/wagoodman/dive> 可视化分层分析 | 进阶 |
| **Compose 规范** | <https://github.com/compose-spec/compose-spec> | 查语法 |
| **安全基线** | <https://docs.docker.com/engine/security/>、CIS Benchmark | 生产上线前 |

---

## ✅ 打卡表（复制到 Obsidian/Notion 勾选）

```
### Day 0 环境
- [ ] Docker Desktop 安装、WSL2 集成开启
- [ ] hello-world 跑通
- [ ] nginx 起停、进容器、看日志、删容器

### Day 1 概念+命令
- [ ] 能画出 Image/Container/Volume 关系图
- [ ] 15 条核心命令不看文档能敲对
- [ ] 完成：起 redis → 挂载配置 → 进容器 ping → 停删 → 卷还在

### Day 2 Dockerfile
- [ ] 给自己项目写出多阶段 Dockerfile
- [ ] 构建成功、本地跑通、镜像 < 200MB
- [ ] 推送到 Docker Hub/GHCR

### Day 3 Compose
- [ ] 写出 app+db+redis+nginx 完整 compose
- [ ] override.yml 区分开发/生产
- [ ] up/down -v 循环数据不丢
- [ ] 能排查：端口不通、服务不健康、挂载不生效

### 进阶（持续）
- [ ] 配置健康检查 + 资源限制
- [ ] 日志轮转 + 备份脚本跑通
- [ ] CI/CD 自动构建推送
- [ ] 多架构构建 + 安全扫描
```

---

## 🎁 附赠：一张纸速查卡（打印贴显示器边）

```
┌─────────────────────────────────────────────────────────────────┐
│  DOCKER 核心命令速查                                           │
├──────────────┬──────────────┬──────────────┬──────────────────┤
│ 镜像         │ 容器         │ 数据卷        │ Compose          │
├──────────────┼──────────────┼──────────────┼──────────────────┤
│ pull         │ run -d -p    │ create       │ up -d            │
│ build -t     │ ps / ps -a   │ ls           │ down / down -v   │
│ images       │ logs -f      │ inspect      │ logs -f          │
│ rmi          │ stop/start   │ rm           │ exec app sh      │
│ tag/push     │ exec -it sh  │ prune        │ config           │
│ history      │ rm -f        │              │ pull + up --build│
└──────────────┴──────────────┴──────────────┴──────────────────┘

Dockerfile 分层缓存铁律：
  1. 依赖文件先 COPY → RUN 安装
  2. 源码最后 COPY
  3. 合并 RUN、清理缓存
  4. 非 root USER
  5. 多阶段：builder → runner

Compose 服务名 = 域名：
  postgres://db:5432/xxx   ✅
  postgres://localhost...  ❌ (容器内不通)

卷的三种形式：
  -v mydata:/data          # 命名卷（推荐生产）
  -v /host/path:/data      # 绑定挂载（推荐开发）
  -v /data                 # 匿名卷（临时）
```

---

> **记住**：Docker 不是目的，**可复现的环境、隔离的依赖、一键部署** 才是目的。先跑通 `hello-world`，再把自己的一个小项目容器化，这条路走下来就入门了。祝你容器化愉快！ 🐳