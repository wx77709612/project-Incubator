# Desktop Product Project Type Design

## 1. 文档状态

| 字段 | 值 |
| --- | --- |
| Layer | Project Type Design |
| Status | APPROVED |
| Project Type ID | `desktop-product` |
| Child Skill ID | `desktop-product-incubator` |
| Architecture Source | `SPECS/ARCHITECTURE/DESKTOP_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md` |
| Architecture Decision | Decision 013 |
| Plugin Baseline | `0.1.0+codex.20261002144305` |
| Implementation Authorization | NOT GRANTED |
| Maker Approval | 2026-10-05 |
| Approved Amendment | Workflow Entry 与 Host Requirement，2026-10-05 |

本文档定义 `desktop-product` 的领域模型、P0–P6 Phase Profile、桌面交付检查点、Evidence 边界、安全边界以及 Host Profile 接口。它不定义 Contract、Runtime Payload、文件实现位置或具体产品功能。

Maker 已批准本文档的 Design 决策。该批准授权继续编写下游 Contract 与 Runtime Specification；在 Implementation Plan 与 Acceptance Test Plan 获得批准前，仍不授权实现。

## 2. 设计目标

`desktop-product-incubator` 用于孵化以桌面软件为交付主体的 Managed Project。它提供可跨业务领域复用的桌面产品指导，重点处理：

- 桌面载体必要性；
- 进程与 UI 生命周期；
- 本地状态与数据迁移；
- 权限、信任与系统集成；
- 打包、安装、升级、卸载与恢复；
- 自动化、桌面自动化和真实 Host Evidence；
- 发布支持边界与残余风险。

业务对象、品牌、目标网站、目标游戏、搜索策略、商业模式和跨产品组合属于具体 Managed Project 的 Product Boundary，不属于 Project Type Definition。

## 3. 设计原则

1. 语义适用的 Core Phase 原样复用 P0–P6 ID 与名称。
2. 桌面专门术语只作为 Phase description、活动、检查点、Gate 或 Evidence 要求。
3. Child Skill 不替 Maker 决定 Product Boundary、Architecture Decision、Host 支持或高风险自动化政策。
4. Host Profile 只具体化目标操作系统环境，不吸收业务领域规则。
5. Shared Kernel 继续负责授权、Mutation、Receipt、Hook、Evidence 与状态完整性，不进入桌面领域判断。
6. 现有机器可读状态优先；不创建第二份 Current Project State，也不默认增加 Markdown 运行态文件。
7. 首个实现服务于实际桌面产品，但不提前抽象成覆盖所有软件形态的大而全流程。
8. 新项目与已有项目使用不同 Workflow Entry；已有项目的阶段由 Agent 基于 Evidence 判断，不由 Kernel 或 Maker 代替。
9. Host 必须按 Project Type Requirement 显式处理；`desktop-product` 激活前必须由 Maker 确认 Host，不使用默认值。

## 4. Domain Model

### 4.1 `DesktopProductProfile`

表示 `desktop-product` Project Type 的稳定设计规则，包括：

- Core Phase Profile；
- Desktop System Model 最低维度；
- Creation Checkpoint；
- Validation Channel；
- Delivery Lifecycle Risk；
- Host Profile 接口；
- Maker Authority 边界。

它不保存具体 Managed Project 的业务答案。

### 4.2 `DesktopPhaseProfile`

对一个 Core Phase 增加桌面产品解释，至少包含：

- `core_phase_id`；
- 桌面阶段目标；
- 关键问题；
- 可观察出口；
- 需要的 Gate Evidence；
- Maker Authority Trigger；
- 允许 Host Profile 收紧的部分。

`DesktopPhaseProfile` 不创建新 Phase ID，不修改 Core Transition。

### 4.3 `FeasibilityProbe`

为一个可能影响方案成立性的未知项提供有界调查：

- 待验证主张；
- 关键未知项与受影响 Assumption；
- 最小判别实验；
- 成功与失败信号；
- Evidence 引用与结论上限；
- 预算、停止条件与备选路径；
- 结论对 Design、Plan 或 Product Boundary 的影响。

它是阶段活动，不是生产 Artifact，也不是 Workflow Phase。

### 4.4 `CreationCheckpoint`

P4 `Creation` 使用两个桌面专门检查点：

- `Usable Slice`：代表性用户路径在受控桌面环境中可操作、可观察和可归因；
- `Delivery Hardening`：安装、升级、卸载、迁移、权限、签名、恢复与关键回归达到进入 P5 的条件。

检查点用于组织 P4 内部工作与 Gate Evidence，不写入 `workflow.stage`。两者可以在实施中交错，但 P4 退出时必须分别给出结论。

### 4.5 `ValidationChannel`

桌面产品区分三种验证通道：

1. `LOGIC_AUTOMATION`：纯逻辑、状态转换、解析、路径约束和确定性失败恢复；
2. `DESKTOP_AUTOMATION`：指定桌面会话中的窗口、控件、进程和用户路径自动化；
3. `TARGET_HOST_VALIDATION`：绑定真实操作系统、权限、安装模式、构建版本与外部依赖的目标环境验证。

验证通道决定 Evidence 的结论上限，不代表三个固定 Runtime 枚举必须进入 Schema。

### 4.6 `DesktopHostProfile`

Host Profile 具体化桌面产品运行环境，至少能够表达：

- 操作系统、版本和架构；
- 安装范围与权限边界；
- 文件系统、进程、系统集成与安全软件约束；
- 打包、签名、安装、升级、卸载和恢复检查；
- 真实环境 Evidence 所需的环境绑定；
- Host 特有的高风险操作和 Maker 验证要求。

首个候选为 `windows-desktop`。该选择不改变 `desktop-product` 的跨 Host 定义。

### 4.7 `DeliveryRiskAssessment`

桌面交付风险按具体项目判断适用性，不要求所有项目都实现安装器、签名、后台服务或自动更新。P2–P4 对每个相关风险域必须形成以下一种结论：

- 适用，并进入 Design、Plan 与验证；
- 不适用，并记录与 Product Boundary 一致的理由；
- 暂缓，由 Maker 明确接受残余风险、停止条件和后续触发点。

Child Skill 不得把“不适用”误写成“已验证”，也不得因为某项能力常见就默认扩大 Product Boundary。

### 4.8 `WorkflowEntry`

Managed Project 激活入口分为：

- `NEW_PROJECT`：使用 Child Workflow 声明的标准初始阶段；Desktop Product 为 P0；
- `ADOPT_EXISTING`：Maker 说明项目来源和已知背景，Agent 检查现有设计、计划、Artifact、实现与 Evidence 后判断当前阶段。

新激活状态的 `workflow.entry` 至少保存：

- `mode`；
- `initial_stage`；
- `assessment_summary`；
- `evidence_refs`；
- `assessed_at`。

`ADOPT_EXISTING` 必须具有 Evidence 引用，只能进入 Child Workflow 声明的正常阶段，不能直接进入 `MODEL_REVIEW` 或其他临时子流程。Maker 确认项目来源、Project Type、Host 和完整激活请求；Agent 对阶段归属的语义判断负责；Kernel 只验证结构与合法范围。

### 4.9 `HostProfileRequirement`

每个 Project Type 必须通过 Registry 字段 `host_profile_requirement` 显式声明：

- `REQUIRED`：没有 Maker 确认的匹配 Host 时不得激活；
- `OPTIONAL`：允许无 Host 激活；
- `FORBIDDEN`：不得绑定 Host。

`desktop-product` 为 `REQUIRED`。`windows-desktop` 是当前可提议 Profile，不是默认值。若 Maker 的目标环境没有匹配 Profile，Router 必须报告不支持并停止激活。

## 5. 组件职责

| 组件 | 负责 | 不负责 |
| --- | --- | --- |
| Router | 提议 `desktop-product` 与可用 Host Profile，解释路由依据 | 自动确认类型或把业务领域当作类型 |
| Shared Kernel | 授权、Revision、MCP-only Mutation、Receipt、Hook、状态与 Workflow 结构校验 | 判断桌面架构优劣或创造产品方案 |
| `desktop-product-incubator` | P0–P6 桌面指导、检查点、风险、Evidence 和下一步建议 | 管理浏览器扩展或决定跨产品组合 |
| `windows-desktop` Host Profile | Windows 安装、权限、进程、文件系统、签名、升级与真实环境要求 | 定义桌面产品的业务能力或改写 Core Phase |
| Managed Project Agent | 在获批边界内完成创造性设计、计划、实现与证据解释 | 伪造 Maker Authorization 或扩大 Product Boundary |
| Maker | Product、Architecture、Host、预算、高风险政策与残余风险决策 | 被 Runtime 自动替代 |

## 6. P0–P6 Desktop Phase Profile

### 6.1 P0 `Intent Discovery`

桌面解释：确认用户问题、核心结果、成功标准，以及为什么桌面载体比网页、浏览器扩展、脚本或服务更适合承担主要产品职责。

最小出口：

- 用户与核心问题清晰；
- 成功标准可观察；
- 桌面载体理由已由 Maker 确认；
- 未把某个业务领域误写为 Project Type。

Maker 边界：Intent、核心结果和载体方向必须由 Maker 确认。

### 6.2 P1 `Project Definition`

桌面解释：建立 Product Boundary、首个 Host、支持与排除范围、交付对象、关键外部依赖和初始风险约束。

最小出口：

- `project_type_id = desktop-product` 已受控确认；
- 首个运行 Host 已在激活前由 Maker 明确确认，并绑定非空 `host_profile_id`；Router 与 Kernel 不提供默认 Host；
- 支持与排除边界可恢复；
- 外部依赖不被错误登记为 Host；
- 高风险能力仍标记为待决政策而不是默认授权。

Maker 边界：改变 Product Boundary、Host 支持或明确排除范围需要 Maker Authorization。

### 6.3 P2 `Solution Design`

桌面副说明：`Desktop System Model`。

最低设计维度：

- 用户交互与窗口生命周期；
- 进程、后台任务和退出语义；
- 本地数据、缓存、配置、迁移与清理；
- 文件系统写入根、权限与提权边界；
- 外部输入、网络来源和信任边界；
- 外部依赖、失败隔离和降级；
- 安装、更新与恢复对系统模型的影响；
- 日志、诊断、隐私与可观察性。

关键可行性未知项通过 `FEASIBILITY_PROBE` 调查。进入 P3 前，不要求所有实现细节均已证明；但可能推翻整体系统模型或核心用户路径的高影响未知项，必须已有支持证据、可行备选路径，或由 Maker 接受有界风险与停止条件。

Maker 边界：Architecture Decision、高风险自动化政策、管理员权限、后台服务、自动更新和敏感凭据政策需要 Maker 确认。

### 6.4 P3 `Execution Planning`

桌面解释：将 Desktop System Model 转换为代表性切片、工作包、交付计划和验证计划。

Implementation Plan 至少区分：

- 核心用户路径；
- `Usable Slice` 完成条件；
- `Delivery Hardening` 完成条件；
- 自动验证、桌面自动化和目标 Host 验证；
- 外部依赖与不可控条件；
- 人工验证预算、批次与停止条件；
- Known-Good Baseline 和回归集合；
- 安全关键路径与恢复测试。

Maker 边界：高成本真实环境验证、人工预算和超出既有范围的工作包需要 Maker 确认。

### 6.5 P4 `Creation`

桌面解释：实现 Project Artifact，并完成两个内部检查点。

`Usable Slice` 观察项：

- 一条代表性用户旅程端到端可执行；
- 输入、结果、副作用和失败位置可观察；
- 本地状态和外部依赖影响可归因；
- 结果不依赖无法解释的手工修补。

`Delivery Hardening` 观察项：

- 构建与交付物内容可验证；
- 安装、升级、卸载和数据迁移等适用项具有明确前后状态；
- 权限请求、签名、后台服务和系统范围修改等适用项符合已批准政策；
- 每个适用的交付风险存在恢复、回滚或安全停止路径；
- 不适用项具有与 Product Boundary 一致的明确理由，未被伪装成已验证；
- 关键 Known-Good 场景有回归证据。

若 Evidence 推翻模型，使用 P4 Creation Correction；不得把 `MODEL_REVIEW` 写成新的 Phase。

### 6.6 P5 `Validation`

桌面副说明：`Target Environment Validation`。

Validation Result 必须区分三个 Validation Channel，绑定：

- 产品构建与交付物版本；
- 操作系统版本与架构；
- 安装模式、权限和用户会话；
- 关键外部依赖版本或状态；
- 场景、结果、副作用、失败与 Evidence 引用；
- Claim Scope、已知限制和结论上限。

一次真实环境成功最高证明该场景在该环境 Observed Working，不自动形成跨版本、跨机器或长期兼容声明。

### 6.7 P6 `Iteration`

桌面解释：根据完整 Validation Result 决定下一轮调整位置。

- 系统模型或 Architecture Assumption 需要调整：P6 → P2；
- 执行路线、切片或验证计划需要调整：P6 → P3；
- Project Artifact 或交付实现需要调整：P6 → P4；
- 只需补充同一边界内验证：P6 → P5。

若结果推翻 P0 Intent 或 P1 Project Definition，P6 不发明到 P0/P1 的新 Transition，而是提出 Maker Review，由 Maker 决定正式重开边界、迁移或终止。

## 7. 可行性调研设计

`FEASIBILITY_PROBE` 的首要目标是降低错误投入，而不是提前制造生产实现。

| 问题类型 | 主要位置 | 处理规则 |
| --- | --- | --- |
| 用户问题与桌面载体是否成立 | P0 | 影响 Intent，由 Maker 确认 |
| Product Boundary、首个 Host 与支持范围 | P1 | 影响项目定义，由 Maker 确认 |
| 框架、进程、权限、本地数据、外部接口和恢复模型 | P2 | 用最小判别实验验证 Architecture Assumption |
| 不改变系统边界的实现未知项 | P3 安排、P4 执行 | 必须有预算、停止条件和受影响工作包 |
| 可能推翻架构的安装、升级、签名或安全软件交互 | P2 | 不得拖到 Delivery Hardening 才首次发现 |
| 只影响交付实现的 Host 细节 | P4 | 作为 Delivery Hardening Evidence |

孤立 Probe 通常只能证明局部机制或候选路径，不能替代 P5 的目标 Host 语义证据。

## 8. P4 Creation Correction

P4 中出现以下情况时进入 Correction Review：

- Evidence 推翻 Candidate Model 或 Runtime Assumption；
- 相同 Failure Signature 重复出现并达到 Core 阈值；
- Known-Good 场景发生回归；
- 实现被迫形成未记录的领域模型；
- 当前修补无法识别有限影响范围或回归集合。

有界纠正流程：

1. 保存 Trigger、Evidence Ref 与失效 Assumption；
2. 暂停受影响工作，不冻结无关工作；
3. 评估 Artifact、Gate、Plan、Baseline 和回归范围；
4. 在当前工作包与已批准边界内修正 Candidate Model 和执行计划；
5. 更新现有状态分区并重放受影响验证；
6. Evidence 成立后恢复 P4 工作。

若影响 Product Goal、Success Criteria、Maker-approved Scope、Architecture Decision、Host 支持、Core Phase、Context Authority、Runtime Invariant，或无法形成有界修正，必须输出 Maker Scope Review Requirement。该结果不自动跳转 Phase，也不自动修改 Product Boundary。

状态映射继续使用现有字段：失效模型进入 `assumptions`，当前纠正行动进入 `plan`，阻止继续的条件进入 `gates`，残余影响进入 `risks`，证明材料通过 Evidence 引用和 `baselines` 关联。不得创建第二份纠正状态文件。

## 9. Host、交付表面与外部依赖

### 9.1 分类规则

| 对象 | 本设计中的分类 | 理由 |
| --- | --- | --- |
| Windows | Host，由 `windows-desktop` Host Profile 表达 | 它承载桌面产品的运行、安装、权限和真实环境语义 |
| 桌面 UI、后台进程、托盘程序、安装器 | 同一 Desktop Managed Project 内的组件或 Delivery Surface | 它们共同构成桌面产品交付，不是独立 Host |
| 浏览器扩展 | 后续独立 Project Type 设计范围 | 当前 Child Skill 不拥有浏览器生命周期，也不决定跨产品关系 |
| Mod 网站、内容网站、远端 API | External Dependency | 它们提供数据或能力，但不承载桌面产品 Runtime |
| 游戏安装目录、游戏客户端、目标内容生态 | 具体 Managed Project 的 External Dependency 与 Domain Constraint | 它们影响 Capability 与验证，不应伪装成桌面操作系统 Host |

### 9.2 Domain Profile 边界

当前不新增 Domain Profile、Integration Profile 或 Capability Profile 注册表实体。具体项目的领域约束先由 `boundary`、`capabilities`、`assumptions`、`risks`、`gates` 与 Evidence 引用表达。

只有当多个 Desktop Managed Project 反复出现稳定、可复用且无法由 Host Profile 表达的领域规则时，才另行提出 Profile 类型的 Architecture Change Proposal。

### 9.3 单一 `host_profile_id`

当前单一 `host_profile_id` 足以表达首个桌面运行 Host。它不承担 Delivery Surface、External Dependency 或跨项目关系。若未来一个 Desktop Managed Project 必须同时声明多个并列运行 Host，属于新的架构证据，需要单独评估 Schema，而不是在本设计中提前扩展。

## 10. Evidence 与结论上限

| Evidence 来源 | 可以证明 | 不能单独证明 |
| --- | --- | --- |
| 逻辑自动化 | 确定性规则、状态转换、解析、路径约束和受控恢复 | 真实桌面会话、安装器、权限与安全软件行为 |
| 桌面自动化 | 指定环境中的窗口、控件、进程和用户旅程可重复执行 | 跨机器兼容、系统升级、签名信誉或长期稳定性 |
| 目标 Host 验证 | 被测构建在绑定环境中的观察结果与副作用 | 未测试版本、未测试权限模式或所有用户环境 |
| 多边界与长期证据 | 更宽支持声明与回归信心 | 无限制兼容承诺 |

Host Profile 可以提高最低 Evidence 要求，但不能把低等级 Evidence 重命名为更高等级，也不能放宽 Shared Kernel 的 E0–E5 规则。

## 11. 安全边界

适用能力出现时，Design、Plan、Creation 与 Validation 必须覆盖：

- 网络响应、网页元数据、本地导入、压缩包、文件名和清单均视为不可信；
- 下载必须记录来源、目标、完整性结论和失败后的临时文件处理；
- 文件写入必须限制根目录，防止路径穿越、链接绕过和意外覆盖；
- 解包必须限制条目路径、大小、数量和递归深度，防止 Zip Slip 与资源耗尽；
- 下载、解包或导入内容不得自动获得执行权限；
- 安装与更新必须具备明确前后状态、冲突策略、回滚或安全停止路径；
- 自动更新必须验证来源、完整性、版本关系和降级政策；
- 管理员权限、后台服务、开机启动、防火墙规则和系统范围写入必须最小化；
- 登录令牌、Cookie、凭据、隐私数据与日志必须按最小权限和最小保留处理；
- 安全扫描、签名或来源信誉只能形成有限 Evidence，不等于内容行为安全。

是否允许自动下载、自动安装、第三方登录、解析压缩包、执行其中内容或系统级修改，是具体 Managed Project 的 Product / Architecture Decision，不由 Child Skill 默认开启。

## 12. 现有权威状态映射

本设计新增一个通用、内嵌于 `workflow` 的 Entry 记录，不新增权威文件或第二份 Current Project State：

| Desktop 设计信息 | 现有状态落点 |
| --- | --- |
| 用户目标、支持与排除范围 | `boundary` |
| 新建/接管模式、初始阶段与评估证据 | `workflow.entry` |
| P0–P6 Current Phase | `workflow` |
| 可观察能力与支持边界 | `capabilities` |
| Product / Architecture Decision | `decisions` |
| 可行性主张与失效模型 | `assumptions` |
| 当前探针、Creation 或 Correction 行动 | `plan` |
| Phase、可行性、安全与交付阻断条件 | `gates` |
| 未解决风险与残余风险 | `risks` |
| Known-Good 环境与 Artifact | `baselines` |
| Maker 人工验证预算 | `human_validation` |
| 大型设计、测试日志与外部证据 | 稳定引用，不复制进 `state.json` |

下游 Design 或 Contract 若发现这些分区无法无歧义表达必须由 Runtime 强制的语义，应登记 `DESIGN_GAP`，不得通过自由文本约定暗中扩展 Schema。

## 13. Maker Authority

以下事项必须由 Maker 决定或确认：

- Intent、Product Boundary、核心成功标准与明确排除范围；
- Project Type 激活或迁移；
- Project Type、Entry Mode 与首个 Host 的激活确认；
- 新增 Host 支持；
- Architecture Decision；
- 自动下载、自动安装、自动更新、管理员权限、后台服务和外部代码执行政策；
- 第三方账号、敏感凭据与隐私数据政策；
- 高成本真实环境验证和人工验证预算；
- 发布支持矩阵与残余风险接受；
- P4 Correction 超出当前工作包或已批准边界后的处理。

Agent 可以在获批边界内决定 Implementation Detail、探针设计、测试组织、内部组件命名和局部实现策略。Runtime 只验证结构与授权，不替 Maker 或 Agent完成创造性判断。

## 14. 产品问题的归属

下列问题不再影响 `desktop-product` Project Type 是否成立，但会影响具体 Managed Project 的 P0–P3 Product Boundary 与 Solution Design：

- 核心能力包括发现、搜索、订阅、更新检测、下载、安装或冲突检查中的哪些；
- 首个支持的游戏、网站、来源或其他领域对象；
- 是否允许自动下载、自动安装或后台更新；
- 是否登录第三方网站；
- 是否解析压缩包或执行其中内容；
- 是否仅支持 Windows；
- 桌面产品与未来浏览器扩展如何协作、发布和版本化。

这些答案由具体 Managed Project 在相应 Phase 中形成，不能被本 Child Skill 预设。

## 15. 非目标

本设计不：

- 定义某个具体产品的名称、业务功能或技术栈；
- 设计浏览器扩展 Project Type；
- 管理多个 Managed Project 的组合、版本或发布关系；
- 将 Windows、网站或游戏生态固化为 `desktop-product` 的业务定义；
- 新增多个 `project_type_id`、`child_skill_id` 或 `host_profile_id`；
- 修改 Shared Kernel Authorization、Mutation、Receipt、Hook 或 Evidence 语义；
- 修改现有 `mod-incubator`、`sims-4` 或其状态；
- 提供激活后的 Host 迁移；
- 授权实现。

## 16. 下游 Contract 与 Runtime 约束

下游规格必须保持：

- Router 只提议，Maker 确认后才激活；
- Router 不提供默认 Host；Registry 对每个 Project Type 显式声明 Host Requirement；
- `desktop-product` 的 Host Requirement 为 `REQUIRED`，Host 为空时激活失败关闭；
- 新激活必须提供 `workflow.entry`；旧状态允许缺省；
- `NEW_PROJECT` 使用标准初始阶段；`ADOPT_EXISTING` 使用 Agent 基于 Evidence 评估且由 Child Workflow 允许的正常阶段；
- Registry 将 `desktop-product` 路由到独立 Child Skill 与 Workflow evaluator；
- Workflow evaluator 使用 P0–P6 正式标识与既有合法 Transition；
- Desktop 副命名不进入 `workflow.stage`；
- P4 Correction 不伪装成 P6 或新的 Phase；
- Host Profile 只能收紧阶段出口和 Evidence Requirement；
- 普通状态更新与 Phase Transition 继续由 Kernel 区分；
- 无有效 Pending Request、Maker Authorization 和 Receipt 时，受保护变化必须失败关闭；
- 现有 Schema 足够时不得增加字段；不足时先登记 `DESIGN_GAP`。

## 17. Design 验收标准

本设计只有在以下条件均被下游规格保持时才可进入实施计划：

1. `desktop-product` 不依赖具体业务领域；
2. P0–P6 Phase ID、名称和 Transition 语义未被桌面副命名改写；
3. P2 Feasibility、P4 Creation Checkpoint、P4 Correction、P5 Evidence 与 P6 Iteration 的职责可区分；
4. Windows Host、桌面 Delivery Surface、External Dependency 与领域约束没有混淆；
5. 自动化、桌面自动化和目标 Host Evidence 的结论上限清晰；
6. 下载、解包、安装、更新、权限、凭据和执行边界具有 Maker Authority 与失败语义；
7. `workflow.entry` 能够恢复新建/接管模式、初始阶段和 Evidence；旧激活状态保持兼容；
8. Shared Kernel 不出现桌面领域分支；
9. `mod-incubator` 与 `sims-4` 不修改；
10. 浏览器扩展保持在下一独立设计任务。

## 18. Maker 审批记录

Maker 于 2026-10-05 确认：

1. P0–P6 Desktop Phase Profile 的职责与出口；
2. Desktop System Model、Usable Slice、Delivery Hardening 和 Target Environment Validation 的副命名层级；
3. `FEASIBILITY_PROBE` 与 P4 Creation Correction 的位置；
4. Windows、Delivery Surface、External Dependency 和领域约束的分类；
5. 当前不新增 Domain / Integration / Capability Profile 注册表实体；
6. 当前状态 Schema 原则上足够，不为桌面副命名增加字段；
7. 下载、安装、更新、权限和外部内容的安全边界；
8. 批准后才进入 Contract 与 Runtime Specification，不授权实现。

Maker 于 2026-10-05 补充确认：

9. 新项目从标准初始阶段开始；已有项目由 Agent 基于 Evidence 判断当前阶段，Maker 确认项目来源和完整激活请求；
10. `desktop-product` 激活前必须显式确认非空 Host，`windows-desktop` 不作为默认值；
11. 批准通用 `workflow.entry`、Workflow Entry 校验与 Registry Host Requirement；首版不增加激活后 Host 迁移。
