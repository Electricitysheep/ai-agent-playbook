# Kubernetes 入门清单：从 Docker Compose 到能独立部署微服务

> 目标：用 **3-4 天碎片时间** 建立 K8s 核心心智模型，能看懂 YAML、把 Compose 转成 K8s 部署、排查 Pod 不 Ready、应付面试核心考点。
> 前置：**已会 Docker / Docker Compose**（镜像、容器、卷、网络、Compose 编排）。
> 环境：本地用 **kind** 或 **Docker Desktop 内置 K8s**（单节点），不搭集群、不学 Helm/Operator/CRD。

---

## 🎯 学习路线图（按阶段打卡）

| 阶段 | 耗时 | 核心产出 | 验收标准 |
|---|---|---|---|
| **Day 0** | 30 min | 本地集群跑通 | `kind create cluster` 成功、`kubectl get nodes` Ready |
| **Day 1** | 2-3 h | 核心对象 + kubectl | 能画出 Pod/Service/Deployment/ConfigMap/PVC 关系图；熟练用 20 条核心命令 |
| **Day 2** | 3-4 h | YAML 实战 + Compose 转换 | 给自己的项目写出 Deployment+Service+ConfigMap+Secret+PVC 完整套件，能 `apply` 跑通 |
| **Day 3** | 2-3 h | 排查 + 进阶模式 | 能排查 CrashLoopBackOff/ImagePullBackOff/Pending/OOMKilled；掌握滚动更新、回滚、HPA、Ingress 基础 |
| **持续** | 随项目 | 生产级补齐 | Helm 入门、Kustomize 多环境、监控/日志/链路、安全基线、GitOps |

---

## 📦 Day 0：本地集群安装与验证

### 0.1 选一个轻量本地集群（二选一）

| 方案 | 适合场景 | 安装命令 |
|---|---|---|
| **kind** (Kubernetes in Docker) | **推荐**：启动快、多集群隔离、CI 友好、跨平台 | `go install sigs.k8s.io/kind@latest` → `kind create cluster --name dev` |
| **Docker Desktop 内置 K8s** | Win/macOS 已装 Docker Desktop，懒得装额外工具 | Settings → Kubernetes → Enable Kubernetes → Apply & Restart |

> **推荐 kind**：`kind create cluster --name dev --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80   # Ingress HTTP
    hostPort: 80
  - containerPort: 443  # Ingress HTTPS
    hostPort: 443
EOF`

### 0.2 验证清单
```bash
# 1. 版本与节点
kubectl version --short
kubectl get nodes -o wide

# 2. 核心组件健康
kubectl get pods -n kube-system

# 3. 跑通第一个 Pod
kubectl run nginx --image=nginx --port=80
kubectl wait --for=condition=Ready pod/nginx --timeout=60s
kubectl port-forward pod/nginx 8080:80 &
curl http://localhost:8080
kubectl delete pod nginx
```

> ✅ **Day 0 打卡**：截图保存 `kubectl get nodes` Ready + `curl` 成功。

---

## 🧠 Day 1：核心对象模型 + 20 条必会 kubectl

### 1.1 核心对象关系图（必须能白板画出）

```
┌─────────────────────────────────────────────────────────────────────┐
│                              Cluster                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      Namespace (default)                     │  │
│  │  ┌─────────────┐    selects    ┌─────────────────────────┐  │  │
│  │  │ Deployment  │ ────────────▶ │          Pods           │  │  │
│  │  │ (期望状态)   │  label selector│ (实际运行、可横向扩缩)   │  │  │
│  │  └──────┬──────┘                └───────────┬─────────────┘  │  │
│  │         │ manages ReplicaSet                │                │  │
│  │         ▼                                   ▼                │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │                    Service (ClusterIP)                   │ │  │
│  │  │  selector=app:myapp  →  负载均衡到匹配 label 的 Pods      │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  │         │                                            ▲        │  │
│  │         │ mounts                                     │        │  │
│  │         ▼                                            │        │  │
│  │  ┌─────────────┐    binds    ┌─────────────────────┐  │  │
│  │  │    PVC      │ ──────────▶ │        PV           │  │  │
│  │  │ (存储声明)   │  StorageClass│ (实际存储卷)        │  │  │
│  │  └─────────────┘             └─────────────────────┘  │  │
│  │         │                                                    │  │
│  │         ▼                                                    │  │
│  │  ┌─────────────┐         ┌─────────────┐                   │  │
│  │  │ ConfigMap   │         │   Secret    │                   │  │
│  │  │ (非敏感配置) │         │ (敏感配置)   │                   │  │
│  │  └─────────────┘         └─────────────┘                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                    │                               │
│                                    ▼                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     Ingress (HTTP/HTTPS 入口)                  │  │
│  │  Host/Path 路由 → Service → Pod                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

| 对象 | 核心职责 | 关键字段 |
|---|---|---|
| **Pod** | 最小调度单元，一组共享网络/存储的容器 | `spec.containers`、`spec.volumes`、`spec.restartPolicy` |
| **Deployment** | 管理 Pod 副本、滚动更新、回滚 | `spec.replicas`、`spec.selector`、`spec.template`、`strategy` |
| **Service** | 服务发现 + 负载均衡（ClusterIP/NodePort/LoadBalancer） | `spec.selector`、`spec.ports`、`spec.type` |
| **ConfigMap** | 非敏感配置（环境变量、配置文件） | `data`、`binaryData` |
| **Secret** | 敏感配置（Base64 编码、可加密） | `data`、`stringData`、`type` |
| **PVC/PV** | 存储声明/持久卷，解耦存储实现 | `spec.accessModes`、`spec.resources.requests.storage`、`storageClassName` |
| **Ingress** | 七层入口，Host/Path 路由、TLS 终结 | `spec.rules`、`spec.tls`、`ingressClassName` |
| **Namespace** | 逻辑隔离，资源配额、RBAC 作用域 | `metadata.name` |

### 1.2 20 条核心 kubectl（分类记忆，每天练 5 条）

#### 集群/节点概览
```bash
kubectl cluster-info                    # 控制平面地址
kubectl get nodes -o wide               # 节点状态、IP、版本、角色
kubectl top nodes                       # 节点资源占用（需 metrics-server）
kubectl describe node <name>            # 详细事件、污点、容量
```

#### 命名空间与上下文
```bash
kubectl get ns                          # 列出命名空间
kubectl config get-contexts             # 当前上下文
kubectl config use-context <name>       # 切换集群/用户
kubectl config set-context --current --namespace=my-ns  # 设默认 ns
```

#### 资源通用操作（适用于所有对象）
```bash
kubectl get <resource> -n <ns> -o wide          # 列表
kubectl get <resource> -n <ns> -o yaml          # 看完整清单
kubectl describe <resource> <name> -n <ns>      # 事件+详情（排查首选）
kubectl delete <resource> <name> -n <ns>        # 删除
kubectl explain <resource>                      # 字段文档（离线查语法）
kubectl explain deployment.spec.template.spec.containers
```

#### Pod 专用（调试最常用）
```bash
kubectl logs -f <pod> -n <ns> -c <container>    # 看日志（-f 跟踪、-c 多容器选一个）
kubectl exec -it <pod> -n <ns> -c <container> -- sh   # 进容器
kubectl port-forward <pod> 8080:80 -n <ns>      # 本地转发访问 Pod
kubectl cp <ns>/<pod>:/path ./local             # 拷文件
kubectl debug <pod> -it --image=busybox --target=<container>  # 临时挂载调试容器（不重启业务）
```

#### 部署与滚动更新
```bash
kubectl apply -f deployment.yaml                # 声明式创建/更新
kubectl rollout status deploy/myapp -n <ns>     # 等待滚动完成
kubectl rollout history deploy/myapp -n <ns>    # 看版本历史
kubectl rollout undo deploy/myapp -n <ns>       # 回滚上一版
kubectl rollout undo deploy/myapp --to-revision=3 -n <ns>  # 回滚指定版本
kubectl scale deploy/myapp --replicas=5 -n <ns> # 手动扩缩
```

> ✅ **Day 1 打卡**：不看文档，凭记忆完成：起一个 Deployment（3 副本）→ 改镜像版本触发滚动更新 → 看历史 → 回滚 → 进 Pod 看日志 → 删 Deployment 验证 Pod 自动清理。

---

## 🏗️ Day 2：写 YAML 套件 + Compose 转换实战

### 2.1 标准微服务 YAML 套件（5 个文件，一个应用）

#### 目录结构
```
k8s/
├── base/
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml
│   ├── 02-secret.yaml
│   ├── 03-pvc.yaml
│   ├── 04-deployment.yaml
│   ├── 05-service.yaml
│   └── 06-ingress.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── replica-patch.yaml
    └── prod/
        ├── kustomization.yaml
        ├── replica-patch.yaml
        └── resources-patch.yaml
```

#### 00-namespace.yaml
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
  labels:
    name: myapp
    env: production
```

#### 01-configmap.yaml（非敏感配置）
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: myapp
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  NGINX_CONF: |
    server {
      listen 80;
      location /health { return 200 "ok"; }
    }
```

#### 02-secret.yaml（敏感配置，**值必须 Base64** 或用 `stringData` 明文让 K8s 自动编码）
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secret
  namespace: myapp
type: Opaque
stringData:  # 明文写，K8s 自动 Base64
  DATABASE_URL: "postgresql://user:pass@db:5432/myapp"
  REDIS_URL: "redis://redis:6379"
  JWT_SECRET: "super-secret-key-change-in-prod"
```

#### 03-pvc.yaml（持久化存储）
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: myapp-data
  namespace: myapp
spec:
  accessModes:
    - ReadWriteOnce   # 单节点读写；多节点需 ReadWriteMany (NFS/Ceph)
  storageClassName: standard  # kind 默认；云上用 gp3/ssd
  resources:
    requests:
      storage: 2Gi
```

#### 04-deployment.yaml（核心负载）
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  revisionHistoryLimit: 10          # 保留 10 个版本供回滚
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%                 # 扩容上限
      maxUnavailable: 25%           # 不可用上限
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      serviceAccountName: default
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: app
          image: myapp:1.2.3        # 生产必须固定 tag，禁用 latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
              name: http
          envFrom:
            - configMapRef:
                name: myapp-config
            - secretRef:
                name: myapp-secret
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_IP
              valueFrom:
                fieldRef:
                  fieldPath: status.podIP
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 3
          volumeMounts:
            - name: data
              mountPath: /app/data
            - name: nginx-conf
              mountPath: /etc/nginx/nginx.conf
              subPath: nginx.conf
              readOnly: true
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: myapp-data
        - name: nginx-conf
          configMap:
            name: myapp-config
            items:
              - key: NGINX_CONF
                path: nginx.conf
```

#### 05-service.yaml（内部负载均衡）
```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: myapp
  labels:
    app: myapp
spec:
  type: ClusterIP
  selector:
    app: myapp
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
```

#### 06-ingress.yaml（外部入口，需安装 Ingress Controller）
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  namespace: myapp
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - myapp.example.com
      secretName: myapp-tls
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp
                port:
                  number: 80
```

### 2.2 Compose → K8s 字段映射速查（改配置时对照）

| Docker Compose | Kubernetes | 备注 |
|---|---|---|
| `services.app.image` | `Deployment.spec.template.spec.containers[0].image` | |
| `services.app.build` | **无直接对应** | 需先 `docker build` 推镜像，K8s 只拉镜像 |
| `services.app.command` | `containers[0].command` | |
| `services.app.entrypoint` | `containers[0].args` | 注意：K8s `command` = 入口点，`args` = 参数 |
| `services.app.environment` | `env` + `envFrom` (ConfigMap/Secret) | 敏感值**必须**用 Secret |
| `services.app.ports` | `Service.spec.ports` + `containerPort` | Compose `host:container` → K8s `Service.port:targetPort` |
| `services.app.volumes` | `volumes` + `volumeMounts` + `PVC` | 绑定挂载 → `hostPath`（不推荐生产）；命名卷 → PVC |
| `services.app.deploy.resources` | `resources.requests/limits` | 单位换算：`cpus: 0.5` → `cpu: "500m"` |
| `services.app.deploy.replicas` | `Deployment.spec.replicas` | |
| `services.app.healthcheck` | `livenessProbe` + `readinessProbe` | 必加，否则 K8s 不知道应用挂了 |
| `services.app.depends_on` | **无直接对应** | 用 `initContainers` 或外部工具等待依赖 Ready |
| `services.app.networks` | **无直接对应** | 同一 Namespace 互通；跨 NS 需 Service/NetworkPolicy |
| `services.app.restart` | `restartPolicy` (Pod 级) | Deployment 管理 ReplicaSet 自动重建 |

### 2.3 部署与验证
```bash
# 1. 依次应用（或用 kustomize 一次性）
kubectl apply -f k8s/base/

# 2. 等待滚动完成
kubectl rollout status deploy/myapp -n myapp

# 3. 验证
kubectl get all -n myapp
kubectl get ingress -n myapp
kubectl describe deploy myapp -n myapp

# 4. 测试访问（本地 kind 需配 /etc/hosts 或 port-forward）
kubectl port-forward -n myapp svc/myapp 8080:80
curl http://localhost:8080/health

# 5. 模拟滚动更新
kubectl set image deploy/myapp app=myapp:1.2.4 -n myapp
kubectl rollout status deploy/myapp -n myapp
kubectl rollout history deploy/myapp -n myapp

# 6. 回滚
kubectl rollout undo deploy/myapp -n myapp
```

> ✅ **Day 2 打卡**：把模板改成你的项目配置，`apply` 跑通、`port-forward` 访问成功、触发一次滚动更新并回滚、删 Deployment 验证 Pod 自动清理、PVC 数据还在。

---

## 🎯 Day 3：排查实战 + 进阶模式

### 3.1 常见异常排查决策树（背下来）

```
Pod 不 Ready
    │
    ├─▶ kubectl get pods -n ns -o wide
    │       │
    │       ├─ STATUS: Pending
    │       │   └─▶ kubectl describe pod <name> -n ns
    │       │         ├─ Events: "0/1 nodes are available: 1 Insufficient cpu/memory"
    │       │         │   └─▶ 资源不够：加节点 / 调小 requests / 调度到别的节点
    │       │         ├─ Events: "PersistentVolumeClaim is not bound"
    │       │         │   └─▶ PVC 绑定失败：检查 StorageClass、PV 可用性
    │       │         └─ Events: "node(s) didn't match node selector/affinity"
    │       │             └─▶ 节点亲和性/污点不匹配：调整 tolerations/affinity
    │       │
    │       ├─ STATUS: ImagePullBackOff / ErrImagePull
    │       │   └─▶ 原因：镜像名错 / 私有仓库无 Secret / 网络不通 / 架构不匹配(arm64 vs amd64)
    │       │         └─▶ kubectl describe pod → Events 看具体报错
    │       │
    │       ├─ STATUS: CrashLoopBackOff
    │       │   └─▶ kubectl logs <pod> -n ns --previous
    │       │         ├─ 应用报错：代码 bug、配置错、依赖服务未就绪
    │       │         ├─ OOMKilled：内存超限 → 调大 limits.memory 或优化代码
    │       │         └─ 启动即退：CMD/ENTRYPOINT 错、缺必要环境变量
    │       │
    │       └─ STATUS: Running 但 Readiness 失败
    │           └─▶ kubectl describe pod → Readiness probe 失败
    │                 └─▶ /ready 接口 404/超时/返回非 200 → 修探针路径/延迟/阈值
    │
    └─▶ 进容器调试
            kubectl exec -it <pod> -n ns -- sh
            # 看进程、网络、磁盘、配置文件
            kubectl debug <pod> -it --image=busybox --target=app
            # 不重启业务，挂载调试容器（共享网络/存储/进程命名空间）
```

### 3.2 进阶模式（按需掌握，面试必考）

| 模式 | 核心 YAML 片段 | 适用场景 |
|---|---|---|
| **滚动更新策略** | `strategy: RollingUpdate / maxSurge: 25% / maxUnavailable: 0` | 零停机发布 |
| **蓝绿/金丝雀** | `argocd` / `flagger` / 两个 Deployment + Service 权重 | 低风险发布 |
| **HPA 自动扩缩** | `apiVersion: autoscaling/v2 / kind: HorizontalPodAutoscaler / metrics: cpu/memory/custom` | 流量波动自动扩缩 |
| **PodDisruptionBudget** | `minAvailable: 50% / maxUnavailable: 1` | 保证可用性（节点维护/驱逐时） |
| **ResourceQuota** | `requests.cpu: "10" / requests.memory: 20Gi / limits.cpu: "20"` | Namespace 级资源配额 |
| **NetworkPolicy** | `podSelector / policyTypes: Ingress/Egress / ingress: from: podSelector` | 微服务间访问控制（零信任） |
| **InitContainers** | `initContainers: - name: wait-db / image: busybox / command: ['sh','-c','until nc -z db:5432; do sleep 1; done']` | 启动前等依赖/跑迁移/下配置 |
| **Sidecar** | `containers: - name: app / - name: log-sidecar / volumeMounts 共享 emptyDir` | 日志采集、服务网格代理、配置热更 |
| **ConfigMap/Secret 热更** | `volumeMounts.subPath` + `kubectl rollout restart` / `reloader` 控制器 | 不重建镜像更新配置 |

### 3.3 Ingress Controller 安装（kind 必装）
```bash
# 安装 NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/kind/deploy.yaml

# 等待 Ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

> ✅ **Day 3 打卡**：制造一次 `CrashLoopBackOff`（改错镜像/配置）、一次 `OOMKilled`（限内存 10Mi 跑大数组）、一次 `Pending`（PVC 绑不上），全程用 `describe` + `logs --previous` + `debug` 排查复原。

---

## 🚀 进阶：生产级补齐清单（有项目需求再学）

| 主题 | 关键点 | 学习触发时机 |
|---|---|---|
| **Helm** | Chart 结构、values.yaml、模板函数、依赖管理、Release 版本、回滚 | 重复部署同类应用、需要模板化 |
| **Kustomize** | `kustomization.yaml`、bases/overlays、patches、images、replicas、configMapGenerator | 多环境配置差异管理（dev/staging/prod） |
| **监控三件套** | Prometheus (指标) + Grafana (仪表盘) + Alertmanager (告警) | 上线前必须有可观测性 |
| **日志聚合** | Loki + Promtail / ELK / Fluent Bit → 统一收集、查询、告警 | 故障定位需要集中日志 |
| **链路追踪** | Jaeger / Tempo + OpenTelemetry SDK 埋点 | 微服务调用链耗时分析 |
| **GitOps** | ArgoCD / FluxCD：Git 为单一事实源、自动同步、漂移检测 | 团队协作、审计、回滚 |
| **安全基线** | PSP/PodSecurityAdmission、NetworkPolicy、RBAC 最小权限、镜像签名、运行时安全 | 合规、生产上线前 |
| **多集群/多区域** | Cluster API、Karmada、服务网格 | 业务扩展到多云/多地域 |
| **成本优化** | VPA 垂直扩缩、Spot 实例、资源回收、镜像瘦身 | 账单太高时 |

---

## 🛠️ 常用调试工具箱（装在本地，不装集群里）

| 工具 | 安装 | 典型用法 |
|---|---|---|
| **kubectl** | 官方 | 核心 CLI |
| **k9s** | `brew install k9s` / `scoop install k9s` | **TUI 神器**，可视化看资源、日志、Shell、端口转发、YAML 编辑 |
| **stern** | `brew install stern` | 多 Pod 尾部日志聚合：`stern myapp -n myapp` |
| **kubectx/kubens** | `brew install kubectx` | 快速切换集群/命名空间 |
| **kustomize** | 内置 `kubectl kustomize` / 单独装 | 多环境配置管理 |
| **helm** | `brew install helm` | Chart 管理 |
| **trivy** | `brew install trivy` | 镜像/集群漏洞扫描 |
| **popeye** | `brew install popeye` | 集群资源配置审计（未用的 PVC、缺探针、资源未限制等） |
| **kube-score** | `brew install kube-score` | YAML 静态评分（最佳实践检查） |

---

## 📚 优质学习资源（按推荐度）

| 类型 | 推荐 | 适合阶段 |
|---|---|---|
| **官方文档** | <https://kubernetes.io/docs/home/>（Concepts → Tasks → Tutorials） | 全程 |
| **CKA/CKAD 备考** | Killer.sh 模拟考环境、Kim Wüstkamp 课程 | 系统巩固、面试刷题 |
| **实战书籍** | 《Kubernetes 实战指南》（第 3 版，Marc Boorshtein） | Day 1-3 |
| **最佳实践** | <https://github.com/kubernetes/website/tree/main/content/en/examples> 官方示例 | 查语法 |
| **架构进阶** | 《Kubernetes 最佳实践》（Brendan Burns 等） | 进阶 |
| **排查案例** | <https://github.com/kubernetes/kubernetes/issues>、<https://learnk8s.io/troubleshooting-deployments> | Day 3+ |

---

## ✅ 打卡表（复制到 Obsidian/Notion 勾选）

```
### Day 0 环境
- [ ] kind / Docker Desktop K8s 安装、创建集群
- [ ] kubectl get nodes Ready
- [ ] 起 nginx Pod、port-forward 访问、删 Pod

### Day 1 对象+命令
- [ ] 能画出核心对象关系图
- [ ] 20 条 kubectl 不看文档能敲对
- [ ] 完成：起 Deployment(3副本) → 滚动更新 → 看历史 → 回滚 → 进 Pod 看日志 → 删 Deployment 验证自清理

### Day 2 YAML套件+Compose转换
- [ ] 写出 Namespace/ConfigMap/Secret/PVC/Deployment/Service/Ingress 完整套件
- [ ] apply 跑通、port-forward 访问成功
- [ ] 触发滚动更新、回滚、验证 PVC 数据持久化
- [ ] 能把自己一个 Compose 项目手工转成 K8s YAML

### Day 3 排查+进阶
- [ ] 能独立排查：Pending / ImagePullBackOff / CrashLoopBackOff / OOMKilled / Readiness失败
- [ ] 掌握：滚动更新策略、HPA、PDB、InitContainer、Sidecar、ConfigMap热更
- [ ] 安装 Ingress Controller、配置 Ingress 域名访问

### 进阶（持续）
- [ ] 学会 Helm 基础、Kustomize 多环境
- [ ] 接入 Prometheus+Grafana+Loki+Tempo
- [ ] 搭建 ArgoCD GitOps 流水线
- [ ] 通过 popeye/kube-score 审计集群
```

---

## 🎁 附赠：一张纸速查卡（打印贴显示器边）

```
┌────────────────────────────────────────────────────────────────────┐
│  K8S 核心对象速查                                                 │
├──────────────┬────────────────────────────────────────────────────┤
│ Pod          │ 原子调度单元，共享网络/存储，不可自愈                │
│ Deployment   │ 期望副本数、滚动更新、回滚、管理 ReplicaSet          │
│ Service      │ ClusterIP(内部) / NodePort(节点) / LB(云)            │
│ ConfigMap    │ 非敏感键值对、配置文件 → env/volume                  │
│ Secret       │ 敏感 Base64 → env/volume，可加密                     │
│ PVC/PV       │ 声明/绑定持久化存储，StorageClass 动态供给            │
│ Ingress      │ HTTP/HTTPS 七层路由、TLS 终结、需 Controller          │
│ Namespace    │ 逻辑隔离、配额、RBAC 作用域                          │
└──────────────┴────────────────────────────────────────────────────┘

核心排查三板斧：
  1. kubectl get pods -o wide          # 看 STATUS、NODE、IP
  2. kubectl describe pod <name> -n ns # 看 Events、配置、探针
  3. kubectl logs <pod> -n ns --previous # 看崩溃前日志

Compose → K8s 关键映射：
  image          → containers.image
  environment    → env + envFrom(ConfigMap/Secret)
  ports          → Service.ports + containerPort
  volumes        → PVC + volumeMounts
  deploy.replicas→ Deployment.replicas
  healthcheck    → livenessProbe + readinessProbe
  depends_on     → initContainers / 外部等待

滚动更新零停机铁律：
  ✅ readinessProbe 必加、路径正确
  ✅ maxUnavailable=0 或 25%（视可用性要求）
  ✅ preStop hook 优雅关闭（sleep 10 + drain connections）
  ✅ PodDisruptionBudget 保护最小可用

资源配额铁律：
  ✅ requests ≤ limits（QoS: Guaranteed/Burstable/BestEffort）
  ✅ limits 设上限防噬邻
  ✅ Namespace ResourceQuota 防单团队占满集群
```

---

> **记住**：K8s 的本质是**声明式期望状态协调系统**——你写 YAML 描述“我想要什么”，Control Loop 不断把实际状态推向期望状态。  
> 先把 **Pod/Deployment/Service/ConfigMap/Secret/PVC/Ingress** 这 7 个核心对象的 YAML 写熟，再学 Helm/Kustomize/Operator，这条路走下来就入门了。祝你 K8s 愉快！ ☸️