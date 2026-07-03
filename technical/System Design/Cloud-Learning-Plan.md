# AWS / Azure / GCP 学习计划(配合 System Design 面试准备)

配合 [AI-Engineer-System-Design-Interview.md](./AI-Engineer-System-Design-Interview.md) 和 [AI-Engineer-System-Design-Examples.md](./AI-Engineer-System-Design-Examples.md) 使用。

## 总体策略

不追求三个云都精通,采用"一深两广"策略:

- **选一个主力云深入**:优先看目标公司常用哪个云,没有明确目标时默认选 **AWS**(市场占有率最高,岗位覆盖面最广)
- **另外两个云做对照表**:只需要知道"同样的需求在另外两家叫什么服务",面试时能说出替代方案即可,不必深入配置细节
- **锚定 AI/ML 场景**:所有学习都围绕 system design 例题里出现的组件(向量检索、模型托管、消息队列、缓存、对象存储),不做通用云计算的全面学习

---

## 阶段一:三云 AI 核心服务对照表(1-2 天)

先建立一张对照表,搞清楚每个云在 AI 系统里各组件的对应服务叫什么。

| 组件 | AWS | Azure | GCP |
|---|---|---|---|
| 托管大模型 API | Bedrock | Azure OpenAI Service | Vertex AI (Model Garden) |
| 模型训练/部署平台 | SageMaker | Azure Machine Learning | Vertex AI |
| 向量数据库 | OpenSearch (向量引擎) / Aurora pgvector | Azure AI Search (向量检索) | Vertex AI Vector Search |
| 对象存储(存文档/embedding) | S3 | Blob Storage | Cloud Storage |
| 消息队列/异步任务 | SQS / EventBridge | Service Bus / Event Grid | Pub/Sub |
| 容器/服务编排 | ECS / EKS | AKS | GKE |
| 无服务器函数 | Lambda | Azure Functions | Cloud Functions |
| API 网关 | API Gateway | API Management | Apigee / API Gateway |
| 缓存 | ElastiCache (Redis) | Azure Cache for Redis | Memorystore |
| 日志/可观测性 | CloudWatch | Azure Monitor | Cloud Logging / Monitoring |
| 权限管理 | IAM | Azure AD / RBAC | IAM |

**产出**:把这张表填充完整并保存(可以在这份文档里直接补充),作为长期参考。

---

## 阶段二:AWS 深入(主力云,约 1-2 周)

按 system design 常见组件顺序学习,每个服务只学"是什么、什么时候用、和其他服务怎么配合",不深挖运维细节。

1. **Bedrock**:托管基础模型调用方式,和自己调用 OpenAI/Anthropic API 的区别,适合什么场景(企业内部合规/多模型切换)
2. **SageMaker**:模型训练、部署、endpoint 托管,与 Bedrock 的分工边界(SageMaker 更适合自训练/微调模型)
3. **OpenSearch + 向量引擎**:作为 RAG 场景的向量检索方案,和 Aurora pgvector 的取舍
4. **S3**:文档存储、数据湖,生命周期管理(冷热数据分层,配合成本优化话题)
5. **Lambda + API Gateway**:轻量级 API 服务架构,适合流量不稳定的场景
6. **SQS/EventBridge**:异步任务解耦(比如文档摄入 pipeline 中的清洗/embedding 步骤)
7. **ElastiCache**:语义缓存/会话状态存储
8. **IAM**:多租户权限隔离设计(对应 Agent 系统的权限控制话题)

**产出**:能画出"用 AWS 服务实现 RAG 客服系统"的架构图,标注每个组件对应的 AWS 服务。

---

## 阶段三:Azure / GCP 广度了解(约 2-3 天)

只需要做到:给一个 AWS 架构图,能快速说出 Azure/GCP 对应服务是什么,以及是否有本质差异。

- **Azure 重点**:Azure OpenAI Service(和 OpenAI 原生 API 的关系、企业客户为什么选它)、Azure AI Search 的向量检索能力
- **GCP 重点**:Vertex AI 的一体化程度(训练、部署、向量检索都在一个平台里,是三家里集成度最高的)、Pub/Sub 的使用场景

**产出**:补充阶段一的对照表,标注每家的"独特卖点"(比如 Azure 的企业合规优势、GCP 的一体化平台优势、AWS 的服务丰富度优势)。

---

## 阶段四:整合练习(和 system design 例题结合,持续进行)

把 [AI-Engineer-System-Design-Examples.md](./AI-Engineer-System-Design-Examples.md) 里的 5 道题,each 用具体云服务重新画一遍架构图:

- [ ] 题目一(RAG 客服系统)→ 用 AWS 服务标注架构图
- [ ] 题目二(AI Coding Assistant)→ 用 AWS 服务标注架构图
- [ ] 题目三(多轮对话 Agent)→ 用 AWS 服务标注架构图
- [ ] 题目四(内容审核系统)→ 用 AWS 服务标注架构图
- [ ] 题目五(推荐/搜索排序)→ 用 AWS 服务标注架构图

每道题画完后,口头练习:如果面试官问"如果用 GCP/Azure 你会怎么改",能立刻给出对应服务替换方案。

---

## 时间线建议

| 周次 | 内容 |
|---|---|
| Week 1 | 阶段一(对照表)+ 阶段二前半(Bedrock/SageMaker/OpenSearch) |
| Week 2 | 阶段二后半(S3/Lambda/SQS/ElastiCache/IAM)+ 阶段三(Azure/GCP 广度) |
| Week 3+ | 阶段四,持续把新学的服务和 system design 例题结合练习 |

## 注意事项

- 不要陷入考证式学习(不需要为了学习去考 AWS/Azure/GCP 认证),目标是能在白板上画出可信的架构并说清楚选型理由
- 优先看官方架构参考(AWS Architecture Center / Azure Architecture Center / GCP Architecture Center 里搜 "RAG" "LLM" 相关的参考架构),比啃文档效率高
- 如果目标公司/岗位 JD 里明确提到某个云,直接把"阶段二深入"换成那个云,不用纠结默认选 AWS
