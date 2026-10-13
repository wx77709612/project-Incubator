# Web Product Project Type Design

## 1. 文档状态

| 字段 | 值 |
| --- | --- |
| Specification Version | V1.2 |
| Layer | Project Type Design |
| Status | APPROVED |
| Project Type ID | `web-product` |
| Child Skill ID | `web-product-incubator` |
| Architecture Source | `SPECS/ARCHITECTURE/WEB_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md` |
| Architecture Decision | Decision 014 |
| Development Base | Desktop Product Incubator accepted commit `3482f3b6fce98452d5f9f64e7d5c8142a4079c31` |
| Host Profile Requirement | `FORBIDDEN` |
| Deployment Capability | `DEFERRED_CAPABILITY` |
| Implementation Authorization | NOT GRANTED |
| Maker Approval | 2026-10-13 |

本文档把已批准的 Web Product Architecture Decision 具体化为 Project Type Domain Model、P0–P6 Phase Profile、P4 检查点、Evidence 结论上限、安全边界和现有权威状态映射。

本文档不定义字段级 Contract、Runtime Algorithm、文件实现位置或具体产品功能。Maker 于 2026-10-13 明确批准本 Design；该批准只授权继续编写 Web Product Contract 与 Runtime Specification，不授权 Implementation Plan、Acceptance Test Plan、产品代码、Runtime、Template、JSON、Registry、Router、Skill、Manifest 或测试变更。

## 2. 设计目标

`web-product-incubator` 用于孵化以通用浏览器界面为主要用户交付表面、同时具有前端与后端逻辑职责的 Managed Project。它提供跨业务领域、技术栈和工程拓扑可复用的 Web 产品指导，重点处理：

- 浏览器用户、核心结果与 Product Boundary；
- 前端、后端、数据、身份和外部依赖之间的责任与信任边界；
- 代表性核心旅程及其跨边界可观察结果；
- 依赖、配置、构建、localhost 启动和 readiness 的可重复性；
- 逻辑、构建、本地集成、真实浏览器、次级界面和人工 Evidence 的结论上限；
- 不可信输入、服务端授权、Secrets、日志和外部副作用；
- 已有项目接管、Creation Correction 与受控 Iteration；
- 公开部署保持挂起，不被本地成功隐式声明为完成。

业务对象、品牌、商业模式、目标用户细分、具体框架、渲染方式、数据库、仓库布局和部署平台属于具体 Managed Project 的 Product、Architecture 或 Implementation 范围，不属于 Project Type Definition。

## 3. 设计原则

1. 原样复用 P0–P6 Core Phase ID、名称与合法 Transition。
2. Web 专门术语只作为 Phase description、活动、检查点、Gate 或 Evidence 条件。
3. `web-product` 按主要产品形态定义，不按 SPA、SSR、MPA、前后端分离、单体、微服务或技术栈拆分。
4. 前端与后端是逻辑职责，可以位于同一代码库、进程或框架，也可以分别实现和运行。
5. Shared Kernel 继续负责授权、Mutation、Receipt、Hook、Evidence、Workflow Entry 和状态完整性，不进入 Web 领域判断。
6. `host_profile_requirement = FORBIDDEN`；浏览器、localhost、端口、命令和本地依赖是项目配置与 Evidence 条件，不是 Host Profile。
7. `deployment_capability = DEFERRED_CAPABILITY`；部署不进入 V1.2 完成条件，本地结果不得产生生产就绪声明。
8. P4 的 Usable Web Slice 与 Build Readiness 分别给出结论；Build-only 不能满足 P5。
9. P5 必须在真实浏览器中验证至少一条核心用户旅程，并绑定被测构建、配置、URL、步骤和结果。
10. REST、GraphQL、WebSocket、Webhook、MCP 等次级界面不自动改变 Project Type，但必须拥有与其风险相称的独立 Claim 和 Evidence。
11. 浏览器 Evidence 与次级界面 Evidence 不互相替代；所有界面复用同一后端业务、授权、数据和副作用边界。
12. 新项目与已有项目使用不同 Workflow Entry；已有项目阶段由 Agent 基于 Evidence 判断。
13. 使用现有状态分区和稳定引用；不创建 Web 专用 Current Project State 或 MCP 专用 Runtime Schema。
14. 首个真实已有项目用于 Field Validation，不反向成为通用业务规则或目录结构模板。

## 4. Domain Model

### 4.1 `WebProductProfile`

表示 `web-product` 的稳定设计规则，包括：

- Core Phase Profile；
- Web System Model 最低维度；
- Workflow Entry；
- Local Run Configuration；
- Usable Web Slice；
- Build Readiness；
- Validation Channel；
- Secondary Interface Boundary；
- Deployment Deferral；
- Web Risk Assessment；
- Maker Authority 边界。

它不保存具体 Managed Project 的技术选型或业务答案。

### 4.2 `WebPhaseProfile`

对一个 Core Phase 增加 Web 产品解释，至少包含：

- `core_phase_id`；
- Web 阶段目标；
- 关键问题；
- 可观察出口；
- 所需 Evidence；
- Maker Authority Trigger；
- 失败后的最早受影响层级。

`WebPhaseProfile` 不创建新 Phase ID，不修改 Core Transition。

### 4.3 `WebSystemModel`

P2 至少描述以下维度：

- 浏览器用户、入口和核心交互；
- 前端呈现、输入、状态与错误反馈职责；
- 后端业务规则、授权、数据访问和外部副作用职责；
- 数据所有权、持久化、缓存、一致性与迁移；
- 身份、会话、角色、授权检查点和匿名边界；
- 浏览器、前端、后端、数据存储、外部服务之间的信任边界；
- 本地运行单元、启动依赖、端口、环境变量和 readiness；
- 外部 API、身份服务、内容服务、队列或其他依赖的失败隔离与降级；
- REST、GraphQL、WebSocket、Webhook、MCP 等适用的次级集成界面；
- 日志、诊断、隐私、审计与可观察性；
- 构建 Artifact 与本地运行结果之间的关系。

这些维度描述责任与交互，不规定组件数量、仓库拓扑或框架。

### 4.4 `LocalRunConfiguration`

表示能够重放 Web Product 本地运行条件的项目级配置，至少可恢复：

- 依赖准备方式与适用版本；
- 前端和后端职责所需的构建命令；
- localhost 启动命令或命令集合；
- 预期端口、URL、协议和 readiness 信号；
- 必需环境变量的名称、来源类别和缺失行为；
- 本地数据、种子数据、迁移和清理条件；
- 外部依赖是否真实、模拟、替代或不可用；
- 启动、停止和失败清理路径；
- 被测 Artifact、配置和代码 Revision。

敏感值不得写入普通 Evidence 或日志。`LocalRunConfiguration` 是 Design 概念，不要求新增 Runtime Schema；具体值通过现有计划、Artifact 和 Evidence 引用管理。

### 4.5 `UsableWebSlice`

P4 中代表性、端到端且可观察的 Web 产品切片。它至少满足：

- 从真实浏览器可到达明确入口；
- 用户能够提交或触发与核心结果有关的交互；
- 旅程穿过适用的前端、后端与数据边界；
- 成功结果在浏览器和适用的后端或数据结果中可观察；
- 关键失败能够反馈给用户，且不会被静默吞掉；
- 外部副作用与授权边界可归因；
- 结果不依赖无法复现的手工补丁或隐式状态。

Usable Web Slice 不等于完整产品，也不证明部署、兼容矩阵、容量或生产安全。

### 4.6 `BuildReadiness`

P4 中证明项目能够从受控前置条件进入可验证本地运行状态的检查点。它至少覆盖：

- 依赖准备和版本前置条件明确；
- 构建命令成功，输出 Artifact 或成功状态可识别；
- 必需配置与缺失配置失败语义明确；
- localhost 启动命令可重复；
- readiness 信号不等同于进程仅存活；
- 前端和后端逻辑职责均可被本地旅程触达；
- 停止与失败清理不会遗留不可解释状态；
- 构建和本地启动绑定代码 Revision、环境与配置摘要。

Build Readiness 可以与 Usable Web Slice 交错推进，但 P4 退出时必须分别给出结论。

### 4.7 `ValidationChannel`

Web Product 区分以下 Evidence 通道：

1. `LOGIC_AUTOMATION`：纯逻辑、状态转换、解析、授权规则和确定性失败恢复；
2. `BUILD_VALIDATION`：依赖准备、编译、打包、静态检查与构建 Artifact；
3. `LOCAL_INTEGRATION_VALIDATION`：localhost 服务、前后端职责、数据和外部依赖之间的集成；
4. `LOCAL_BROWSER_VALIDATION`：真实浏览器中的核心用户旅程、呈现、交互、错误反馈和可观察结果；
5. `SECONDARY_INTERFACE_VALIDATION`：通过真实适用 Client 验证 REST、Webhook、MCP 等次级界面的协议、授权、结果、失败和副作用；
6. `HUMAN_VALIDATION`：Maker 或目标用户对结果、可理解性和业务可接受性的人工观察。

这些是 Design 层的通道标识，不要求全部成为 Runtime 枚举。某通道不适用时必须记录与 Product Boundary 一致的理由，不能标记为已通过。

### 4.8 `SecondaryInterfaceBoundary`

表示 Web Product 在浏览器主要界面之外暴露既有后端 Capability 的接口边界。

一个次级界面继续属于同一 `web-product`，当且仅当：

- 它服务同一 Product Boundary 与主要用户结果；
- 它复用同一业务模型、数据所有权和授权政策；
- 它与 Web Product 共享主要版本和变更生命周期；
- 它不是当前 Managed Project 的主要独立交付物。

每个适用次级界面至少明确：

- 消费者与调用意图；
- 暴露的 Capability Boundary；
- 输入、输出和协议失败；
- 身份、授权、审计与速率或资源约束；
- 数据读取、写入和外部副作用；
- Transport 与 Client 前置条件；
- 独立 Claim、Evidence 和结论上限；
- 与浏览器旅程的一致性检查。

对于 MCP，Tool、Resource、Prompt 或等价能力只暴露 Maker 已批准的 Capability；MCP 输入视为不可信；真实 MCP Client Evidence 不能替代真实浏览器 Evidence。SSE、Streamable HTTP、stdio 或独立进程、包、部署单元不会单独触发 Project Type 迁移。

若次级界面形成独立产品目标、消费者、版本支持、发布和回滚边界，并取代浏览器核心旅程成为主要结果，Agent 必须提出 Maker Project Type Review；当前 Child Skill 不自动迁移，也不为独立服务发明类型。

### 4.9 `WorkflowEntry`

Managed Project 激活入口分为：

- `NEW_PROJECT`：使用 Child Workflow 声明的标准初始阶段 P0；
- `ADOPT_EXISTING`：Maker 提供项目来源和已知背景，Agent 检查已有设计、计划、Artifact、实现、构建、本地运行和验证 Evidence 后判断 P0–P6 当前阶段。

新激活状态继续使用通用 `workflow.entry`，至少保存：

- `mode`；
- `initial_stage`；
- `assessment_summary`；
- `evidence_refs`；
- `assessed_at`。

`ADOPT_EXISTING` 必须有可复核 Evidence，只能进入 Child Workflow 声明的正常阶段，不能直接进入临时 Correction 或 Review 子流程。Maker 确认项目来源、Project Type、Product Boundary 与完整激活请求；Agent 对阶段归属判断负责；Kernel 只验证结构、合法阶段和授权。

### 4.10 `HostProfileRequirement`

`web-product` 使用：

```text
host_profile_requirement = "FORBIDDEN"
```

Router 不为 Web Product 提议 Host Profile；Kernel 必须拒绝绑定非空 `host_profile_id` 的激活请求。目标浏览器、localhost、操作系统、端口、命令和依赖仍需在项目设计、计划和 Evidence 中可恢复，但不获得 Host Authority。

### 4.11 `DeploymentDeferral`

V1.2 使用：

```text
deployment_capability = "DEFERRED_CAPABILITY"
```

它表达：

- 域名、DNS、TLS、CDN、生产托管、扩缩容、生产监控、生产 Secrets、线上迁移和公开可用性不是 V1.2 必经范围；
- localhost、真实浏览器或已有线上环境的观察不能自动产生生产就绪 Claim；
- 已有项目的部署资料可以作为背景 Evidence 保留，但本版本不验证或承诺其生产语义；
- 未来启用部署必须经过独立变更控制，并定义新的 Design、Contract、Runtime 与验收边界。

该标记不要求新增 Runtime Schema 字段；通过 Profile、Plan、Gate、Risk 与 Evidence 语义保持。

### 4.12 `WebRiskAssessment`

适用能力出现时，P2–P5 对相关风险域形成以下一种结论：

- 适用，进入 Design、Plan、Creation 与 Validation；
- 不适用，记录与 Product Boundary 一致的理由；
- 暂缓，由 Maker 明确接受残余风险、停止条件和后续触发点。

风险域包括：身份与会话、服务端授权、数据迁移、文件与富文本输入、外部请求、Secrets、日志隐私、跨站边界、外部副作用、第三方账号、付费服务、次级接口和资源耗尽。Child Skill 不得把“不适用”误写成“已验证”。

## 5. 组件职责

| 组件 | 负责 | 不负责 |
| --- | --- | --- |
| Router | 根据主要产品形态提议 `web-product`，解释适用与排除依据 | 自动确认类型、绑定 Host 或把 HTTP/MCP Transport 当成产品类型 |
| Shared Kernel | 授权、Revision、MCP-only Mutation、Receipt、Hook、状态、Entry、Host Requirement 与 Workflow 结构校验 | 判断 Web 架构优劣、选择技术栈或解释浏览器 Evidence |
| `web-product-incubator` | P0–P6 Web 指导、检查点、风险、Evidence 与下一步建议 | 管理浏览器扩展、独立后端服务或承诺部署 |
| Managed Project Agent | 在批准边界内完成阶段判断、设计、计划、实现与 Evidence 解释 | 伪造 Maker Authorization、扩大 Product Boundary 或把构建成功升级成 P5 通过 |
| Maker | Product、Architecture、类型激活、外部副作用、预算与残余风险决策 | 被 Runtime 自动替代 |
| Browser / Protocol Client | 产生绑定环境和步骤的观察 Evidence | 直接修改权威状态或决定 Gate Result |

## 6. P0–P6 Web Product Phase Profile

### 6.1 P0 `Intent Discovery`

Web 解释：确认用户问题、核心结果、成功标准，以及为什么通用浏览器界面适合作为主要产品载体。

若计划通过 MCP 或其他次级界面暴露能力，同时确认该界面的消费者、用户结果和它与浏览器主要产品的关系。

最小出口：

- 用户与核心问题清晰；
- 成功标准可观察；
- 浏览器载体理由已由 Maker 确认；
- 主要结果不是浏览器扩展、纯后端或独立 MCP Service；
- 次级界面未被误写为第二个未经批准的产品目标。

Maker 边界：Intent、核心结果、载体方向和主要排除项必须由 Maker 确认。

### 6.2 P1 `Project Definition`

Web 解释：建立 Product Boundary、浏览器用户、前端与后端职责、支持与排除范围、关键数据和外部依赖、次级界面归属、localhost 验收边界与部署挂起状态。

最小出口：

- `project_type_id = web-product` 已受控确认；
- 激活请求没有 Host Profile；
- 前端与后端逻辑职责均存在且边界可说明；
- 至少一条核心旅程需要穿过浏览器和后端或数据边界；
- 适用的 MCP 等次级界面明确属于同一 Product Boundary 或触发 Maker Review；
- Build、localhost 和真实浏览器是 V1.2 完成边界；
- Deployment 明确保持 `DEFERRED_CAPABILITY`；
- 高风险能力标记为待决政策而不是默认授权。

Maker 边界：Product Boundary、Project Type、次级界面产品归属、外部副作用和明确排除范围需要 Maker Authorization。

### 6.3 P2 `Solution Design`

Web 副说明：`Web System Model`。

最低设计维度使用第 4.3 节。设计必须说明代表性浏览器旅程如何穿过前端、后端与数据或外部依赖边界，以及每个关键失败如何被发现和反馈。

关键可行性未知项通过既有 `FEASIBILITY_PROBE` 方法调查。进入 P3 前，不要求所有实现细节均已证明；但可能推翻 Product Boundary、核心旅程、服务端授权、数据所有权或本地运行模型的高影响未知项，必须具有支持 Evidence、可行备选路径，或由 Maker 接受有界风险与停止条件。

若存在 MCP 等次级界面，设计必须把它映射到已有后端 Capability，并分别说明协议、授权、审计、失败、副作用和一致性边界。不得复制第二套未经记录的业务规则。

Maker 边界：Architecture Decision、身份与授权政策、敏感数据、真实账户、付费服务、外部写入和高影响残余风险需要 Maker 确认。

### 6.4 P3 `Execution Planning`

Web 解释：将 Web System Model 转换为代表性切片、工作包、构建与本地运行计划和验证计划。

Implementation Plan 至少区分：

- 核心浏览器用户旅程；
- Usable Web Slice 完成条件；
- Build Readiness 完成条件；
- `LOGIC_AUTOMATION`、`BUILD_VALIDATION`、`LOCAL_INTEGRATION_VALIDATION`、`LOCAL_BROWSER_VALIDATION`、`SECONDARY_INTERFACE_VALIDATION` 与 `HUMAN_VALIDATION`；
- 本地运行命令、端口、readiness、数据和清理；
- 外部依赖、模拟边界与不可控条件；
- Known-Good Baseline 和回归集合；
- 安全关键路径、失败反馈和恢复测试；
- Deployment Deferred 的明确非目标；
- 人工验证预算、批次与停止条件。

若包含 MCP 等次级界面，工作包可以与 Web 后端共同实现，但必须具有独立协议、授权、失败和真实 Client 验证任务。

Maker 边界：高成本人工验证、真实账户、付费依赖、外部写入和超出既有范围的工作包需要 Maker 确认。

### 6.5 P4 `Creation`

Web 解释：在批准的工作包内实现 Project Artifact，并完成 Usable Web Slice 与 Build Readiness 两个内部检查点。

`Usable Web Slice` 观察项使用第 4.5 节；`Build Readiness` 观察项使用第 4.6 节。

适用的次级界面还必须观察：

- 只暴露已批准 Capability；
- 复用后端业务与授权规则；
- 输入被当作不可信；
- 结果、失败、审计与副作用可观察；
- 未形成绕过浏览器产品政策的替代写入路径。

若 Evidence 推翻 Web System Model、授权边界或关键 Assumption，使用 P4 Creation Correction；不得把 `MODEL_REVIEW` 写成新 Phase，也不得通过局部修补暗中改变 Product Boundary。

P4 出口不代表 P5 已通过。构建成功、服务启动或局部客户端成功都不能代替完整验证结果。

### 6.6 P5 `Validation`

Web 副说明：`Local Product Validation`。

Validation Result 必须绑定：

- 代码 Revision 与构建 Artifact；
- 依赖和关键工具版本；
- 目标浏览器名称与版本；
- localhost URL、端口、协议和运行配置摘要；
- 前端、后端、数据和外部依赖状态；
- 场景、步骤、结果、失败反馈和副作用；
- Evidence 引用、Claim Scope、已知限制与结论上限。

V1.2 P5 的最低组合为：

1. Build Validation 成功；
2. `LOCAL_INTEGRATION_VALIDATION` 能证明前端与后端职责在受控配置中协作；
3. Local Browser Validation 在真实浏览器中完成至少一条核心用户旅程；
4. 对适用的关键失败路径观察用户反馈和无未授权副作用；
5. 若存在 MCP 等次级界面，使用真实 Client 单独验证协议、授权、结果、失败和副作用；
6. 明确记录 Deployment 未验证，结论不包含生产就绪。

一次本地成功最高证明绑定构建和环境中的被测场景 Observed Working，不自动形成跨浏览器、跨环境、容量、安全或长期兼容声明。

### 6.7 P6 `Iteration`

Web 解释：根据完整 Validation Result 决定下一轮调整位置。

- Web System Model、信任边界、授权模型或 Architecture Assumption 需要调整：P6 → P2；
- 工作包、切片、构建、本地运行或验证计划需要调整：P6 → P3；
- Project Artifact、配置或实现需要调整：P6 → P4；
- 只需补充同一边界内验证：P6 → P5。

若结果推翻 P0 Intent、P1 Product Boundary、Project Type、次级界面归属或 Deployment 边界，P6 不发明到 P0/P1 的 Transition，而是提出 Maker Review，由 Maker 决定重开边界、迁移、暂停或终止。

## 7. 可行性调研设计

`FEASIBILITY_PROBE` 用于降低错误投入，不是生产 Artifact，也不能替代 P5。

| 问题类型 | 主要位置 | 处理规则 |
| --- | --- | --- |
| 用户问题与浏览器载体是否成立 | P0 | 影响 Intent，由 Maker 确认 |
| Product Boundary、前后端职责与次级界面归属 | P1 | 影响项目定义，由 Maker 确认 |
| 身份、授权、数据、信任边界与本地运行模型 | P2 | 用最小判别实验验证 Architecture Assumption |
| 可能推翻核心旅程或外部副作用政策的第三方依赖 | P2 | 不得拖到 P4 才首次调查 |
| 不改变系统边界的框架或构建未知项 | P3 安排、P4 执行 | 必须有预算、停止条件和受影响工作包 |
| 浏览器或真实 Client 中的实际行为 | P5 | Probe 不能替代绑定构建的真实验证 |

## 8. P4 Creation Correction

P4 中出现以下情况时进入 Correction Review：

- Evidence 推翻 Web System Model 或 Runtime Assumption；
- 相同 Failure Signature 达到 Core 阈值；
- Known-Good 浏览器旅程或后端结果发生回归；
- 浏览器与次级界面出现业务、授权或副作用分叉；
- 实现被迫形成未记录的数据、身份或外部依赖模型；
- 当前修补无法识别有限影响范围或回归集合。

有界纠正继续使用 Core 流程：记录 Trigger 与失效 Assumption，暂停受影响工作，评估 Artifact、Gate、Plan、Baseline 和回归范围，在当前工作包与批准边界内修正，更新现有状态分区并重放验证。

若影响 Product Goal、Success Criteria、Maker-approved Scope、Architecture Decision、Project Type、次级界面产品归属、Deployment 边界、Core Phase、Context Authority 或 Runtime Invariant，必须提出 Maker Scope Review Requirement。该结果不自动修改状态或迁移 Project Type。

## 9. Evidence 与结论上限

| Evidence 来源 | 可以证明 | 不能单独证明 |
| --- | --- | --- |
| Logic Automation | 确定性规则、解析、授权判定、状态和失败恢复 | 构建可用、服务集成或真实浏览器行为 |
| Build Validation | 指定环境与 Revision 的构建成功和 Artifact 产生 | localhost 可用、核心旅程或生产可用 |
| `LOCAL_INTEGRATION_VALIDATION` | 指定本地配置中的服务、数据和依赖协作 | 浏览器呈现、用户交互或跨环境兼容 |
| Local Browser Validation | 指定构建、浏览器和 localhost 配置中的真实用户旅程 | 未测浏览器、部署、容量、生产安全或长期稳定性 |
| Secondary Interface Validation | 指定 Transport、Client 和 Capability 的协议、授权、结果与副作用 | 浏览器核心旅程或该接口的独立产品成立性 |
| Human Validation | 被测结果的可理解性与业务接受观察 | 未绑定环境的普遍正确性或 Runtime Gate 自动通过 |
| 部署或线上历史资料 | 已发生的背景 Observation | V1.2 已验证部署或生产就绪 |

Evidence 通道不能通过改名提高等级。更宽 Claim 必须增加对应环境、场景、时间和回归 Evidence。

## 10. 安全与外部副作用边界

适用能力出现时，Design、Plan、Creation 与 Validation 必须覆盖：

- 浏览器输入、URL、查询参数、Cookie、Header、上传、富文本、文件名、外部响应和 MCP 参数均视为不可信；
- 权限检查发生在可信后端边界，不能只依赖前端可见性或客户端声明；
- 身份、会话、角色、租户和对象级授权具有明确失败语义；
- 数据读取、写入、删除、导出和迁移具有最小权限、归属与恢复边界；
- Secrets 不进入前端 Bundle、普通日志、Evidence 或仓库；
- 日志和审计记录避免泄露令牌、Cookie、个人数据和敏感内容；
- 外部请求、Webhook、邮件、付费 API、真实账户和生产数据写入需要明确授权与副作用预算；
- 文件和富文本处理限制路径、类型、大小、数量与资源消耗；
- 浏览器安全边界、跨站请求、内容注入和服务端请求代理按适用性评估；
- MCP 等次级界面不得绕过同一后端业务、授权、审计和副作用政策；
- 失败时不得以吞错、假成功或残留部分写入掩盖状态；
- localhost 只代表本地验收边界，不自动代表安全隔离或生产保护。

Child Skill 不默认开启外部写入、第三方登录、真实邮件、付费服务、生产数据或公开部署。

## 11. 现有权威状态映射

本设计不新增权威状态文件或第二份 Current Project State：

| Web 设计信息 | 现有状态落点 |
| --- | --- |
| 用户目标、Product Boundary、前后端职责与排除范围 | `boundary` |
| 新建/接管模式、初始阶段与评估 Evidence | `workflow.entry` |
| P0–P6 Current Phase | `workflow` |
| 浏览器旅程、后端结果与次级接口 Capability | `capabilities` |
| Product / Architecture Decision | `decisions` |
| Web System Model 主张、可行性与失效模型 | `assumptions` |
| 当前 Probe、Slice、Build、Correction 或验证行动 | `plan` |
| Phase、构建、服务、浏览器、安全与授权阻断条件 | `gates` |
| 外部依赖、Deployment Deferred 与残余风险 | `risks` |
| Known-Good 构建、配置、浏览器与场景 | `baselines` |
| Maker 人工验证预算 | `human_validation` |
| 设计、构建日志、浏览器记录与 Client Evidence | 稳定引用，不复制进 `state.json` |

次级界面使用同一映射，通过 `capabilities`、`assumptions`、`plan`、`gates`、`risks` 和 Evidence 区分其 Claim，不新增 `primary_surface`、`integration_surface` 或 MCP 专用状态字段。

下游 Contract 若发现这些分区无法无歧义表达必须由 Runtime 强制的语义，应登记 `DESIGN_GAP` 并返回 Architecture 层，不得通过自由文本或代码分支暗中扩展 Schema。

## 12. Maker Authority

以下事项必须由 Maker 决定或确认：

- Intent、Product Boundary、核心成功标准和明确排除范围；
- Project Type 激活、迁移、暂停或终止；
- Entry Mode、项目来源和完整激活范围；
- Architecture Decision；
- 次级界面是否仍属于 Web Product 或成为独立产品；
- 身份、授权、敏感数据、真实账户、付费服务和外部写入政策；
- 高成本真实浏览器、真实 Client 与人工验证预算；
- 是否在未来迭代启用 Deployment Capability；
- P4 Correction 超出当前工作包或批准边界后的处理；
- 发布支持范围和残余风险接受。

Agent 可以在批准边界内决定 Implementation Detail、Probe 设计、测试组织、内部组件命名和局部实现策略。Runtime 只验证结构与授权，不替 Maker 或 Agent 完成创造性判断。

## 13. 适用边界

### 13.1 适用

- 通用浏览器是主要用户界面；
- 同时存在前端与后端逻辑职责；
- 至少一条核心旅程穿过浏览器和后端或数据边界；
- 可以构建并通过 localhost 启动受控服务；
- 结果可在真实浏览器中观察；
- 可选包含绑定于同一 Product Boundary 的 MCP 等次级界面。

### 13.2 排除

- 浏览器扩展；
- 纯后端 API、后台任务或基础设施；
- 以 MCP Server 为主要独立交付物且没有浏览器核心旅程的服务；
- 只有前端静态内容且没有后端逻辑职责的站点；
- 桌面、移动、CLI、SDK、库或游戏 Mod；
- 只有设计稿、文档或不可运行原型的项目。

外部 API、数据库、身份或内容服务可以是依赖，不自动改变 Project Type。主要产品形态变化必须触发 Maker Review。

## 14. 非目标

本设计不：

- 选择技术栈、框架、渲染模式、数据库或仓库布局；
- 要求前后端分离或合并；
- 定义具体业务功能、品牌或商业模式；
- 设计浏览器扩展、独立 MCP Service 或纯后端 Project Type；
- 设计或验证公开部署、生产安全、容量、高可用或规模化；
- 为浏览器或 localhost 新增 Host Profile；
- 新增 Web、Deployment 或 MCP 顶层 Phase；
- 新增 P6→P0/P1 Transition；
- 修改 Shared Kernel Authorization、Mutation、Receipt、Hook 或 Evidence 语义；
- 新增 Web 专用权威状态文件或未经 Architecture 批准的 Schema；
- 修改 `mod`、`desktop-product`、`sims-4` 或 `windows-desktop` 既有语义；
- 授权实现。

## 15. 下游 Contract 与 Runtime 约束

下游规格必须保持：

- Router 只提议，Maker 确认后才激活；
- Registry 将 `web-product` 路由到独立 Child Skill 与 Workflow evaluator；
- `host_profile_requirement = FORBIDDEN`，非空 Host 激活失败关闭；
- `NEW_PROJECT` 使用 P0；`ADOPT_EXISTING` 使用 Agent 基于 Evidence 判断的 P0–P6 正常阶段；
- Workflow evaluator 使用正式 P0–P6 和既有合法 Transition；
- Web 副命名、检查点和 Validation Channel 不进入 `workflow.stage`；
- P4 Correction 不伪装成 P6 或新 Phase；
- Build-only 不能满足 P5；真实浏览器核心旅程是必要 Evidence；
- 浏览器与次级界面使用独立 Claim 和 Evidence，不能互相替代；
- Deployment Deferred 不产生部署 Gate 通过或生产 Claim；
- 普通状态更新与 Phase Transition 继续由 Kernel 区分；
- 无有效 Pending Request、Maker Authorization 和 Receipt 时，受保护变化失败关闭；
- 现有 Schema 足够时不得增加字段；不足时先登记 `DESIGN_GAP`。

## 16. Design 验收标准

本文档只有在 Maker 确认以下条件后才能标记为 `APPROVED`：

1. `web-product` 按主要产品形态定义，不依赖业务领域、技术栈或工程拓扑；
2. 前端与后端作为逻辑职责表达；
3. 适用与排除边界清晰，尤其区分浏览器扩展、纯后端与独立 MCP Service；
4. P0–P6 ID、名称和 Transition 未被 Web 副命名改写；
5. Web System Model 的最低维度足以支持通用浏览器端项目；
6. Usable Web Slice 与 Build Readiness 可区分并分别给出结论；
7. Build、localhost 集成、真实浏览器和次级界面 Evidence 的结论上限清晰；
8. Build-only 不能通过 P5；P5 要求真实浏览器核心旅程；
9. `host_profile_requirement = FORBIDDEN`，但目标浏览器与本地运行配置仍可恢复；
10. Deployment 保持挂起，且本地成功不产生生产就绪 Claim；
11. MCP 等次级界面继续属于同一 Web Product 的条件及独立服务触发条件清晰；
12. 次级界面复用后端业务、授权、数据、审计和副作用边界；
13. 浏览器 Evidence 与次级界面 Evidence 不互相替代；
14. 不可信输入、服务端授权、Secrets、日志、真实账户和外部副作用边界清晰；
15. `NEW_PROJECT` 与 `ADOPT_EXISTING` 可恢复且符合既有 Entry 语义；
16. P4 Creation Correction 与 P6 Iteration 的失败路由清晰；
17. 现有状态分区原则上足够，没有创建第二份权威状态；
18. Shared Kernel、现有 Project Type 和历史基线未被 Web 领域规则重定义。

## 17. Maker 审批记录

Maker 于 2026-10-13 明确确认：

1. Web Product Domain Model 与最低 Web System Model 维度；
2. P0–P6 Web Phase Profile 的职责和出口；
3. Usable Web Slice、Build Readiness 与 Local Product Validation 的层级；
4. `FORBIDDEN` Host Requirement 与 Local Run Configuration 的边界；
5. `DEFERRED_CAPABILITY` 的部署挂起语义；
6. Validation Channel 与 Claim 上限；
7. MCP 等次级界面的归属、独立 Evidence 和 Project Type Review 触发条件；
8. 安全、外部副作用与 Maker Authority；
9. 现有状态映射和不新增 Web/MCP 专用 Schema 的原则；
10. 本批准只授权继续 Contract 与 Runtime Specification，不授权 Implementation Plan、Acceptance Test Plan 或实现。
