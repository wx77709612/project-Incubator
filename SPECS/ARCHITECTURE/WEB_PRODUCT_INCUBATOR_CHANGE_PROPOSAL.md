# Project Incubator Plugin Web Product Incubator Architecture Change Proposal

## 1. 文档状态

| 字段 | 值 |
| --- | --- |
| Specification Version | V1.2 |
| Specification Track | Project Incubator Plugin Web Product Incubator |
| Status | DRAFT |
| Development Base | Desktop Product Incubator accepted commit `3482f3b6fce98452d5f9f64e7d5c8142a4079c31` |
| Released Baseline | `SPECS/_V1.0/` |
| Plugin Candidate Baseline | `0.2.0+codex.20261009161423` |
| Change Type | Project Type Extension |
| Implementation Authorization | NOT GRANTED |
| Maker Discussion Baseline | 2026-10-13 |
| Written Proposal Approval | PENDING |

本文档把 Maker 已确认的 Web 产品方向固化为 V1.2 Architecture Change Proposal。它定义 `web-product` 项目类型、`web-product-incubator` 的职责边界、P0–P6 解释、验证结论上限、部署挂起语义以及对现有 Plugin 的预计影响。

本提案不直接授权修改 Plugin Runtime、Registry、Router、Skill、Profile、Manifest 或测试。Maker 审阅并批准本文档后，只允许继续更新 Architecture Decisions 与 Design Layer；Contract、Runtime Specification、Implementation Plan 与 Acceptance Test Plan 仍须按 Change Control 顺序完成和审批。

## 2. 变更动机

Project Incubator Plugin 已通过 `mod` 与 `desktop-product` 证明 Router、Shared Kernel、Child Incubator、Project Type Profile 和可选 Host Profile 的扩展结构。当前仍缺少面向通用浏览器端产品的可复用孵化能力。

本次变化的目标不是规定 SPA、SSR、前后端分离、全栈框架或具体语言，而是为具有前端与后端职责的浏览器端产品提供统一的生命周期、边界、验证和安全指导。它必须适用于单体或分离式仓库、服务端渲染或客户端渲染以及不同技术栈，同时保持足够具体的 Web Product Model 与 localhost 验收标准。

V1.2 的首个真实验证对象是一个已有 Web 项目。该项目用于验证 `ADOPT_EXISTING`、阶段识别、构建、localhost 启动和真实浏览器核心旅程，但其业务领域、技术栈和仓库结构不得反向成为通用 Project Type 规则。

## 3. 版本与分支边界

### 3.1 V1.1 与 V1.2 分离

- V1.1 继续完成桌面端与既有 Core 的人工验收、发布审阅和归档；
- V1.2 在独立分支中设计和实现 `web-product`；
- V1.2 不改写 V1.1 的历史规格、人工验收记录或发布结论；
- V1.2 以桌面端验收闭合提交 `3482f3b` 为开发基线，以复用已验证的 Plugin 扩展骨架；
- V1.1 尚未发布不授权 V1.2 将其描述为 Released Baseline；V1.2 发布前必须重新确认实际发布基线与迁移关系。

### 3.2 当前提案的授权上限

当前只允许：

1. 编写和审阅本 Architecture Change Proposal；
2. 进行只读影响分析和现有基线调查；
3. 在本提案获批后更新 Architecture Decisions 与 Design Layer。

当前不允许编写或修改产品实现。任何实现前工作必须先完成 Contract、Runtime Specification、Implementation Plan 与 Acceptance Test Plan，并取得对应批准。

## 4. 已确认的架构原则

### 4.1 Project Type 按产品形态划分

本提案采用：

```text
project_type_id = "web-product"
child_skill_id = "web-product-incubator"
```

`web-product` 表示通过通用浏览器界面向用户提供完整产品结果、且具有前端与后端逻辑职责的产品形态。它不表示业务领域、技术栈、渲染模式、仓库布局或部署拓扑。

### 4.2 前端与后端是逻辑职责，不是工程拓扑

Web 产品至少具有：

- 前端职责：向浏览器用户呈现信息、接收交互并反馈结果；
- 后端职责：处理受信任业务规则、授权、数据访问或等价服务端责任。

上述职责可以位于同一代码库、同一进程或同一框架，也可以前后端分离。Child Incubator 不以 SPA、SSR、MPA、静态生成、BFF、Serverless 或其他实现方式作为项目类型分支。

### 4.3 Project Type 与次级集成界面分离

Project Type 约束 Managed Project 的主要产品形态和项目级孵化流程，不枚举或禁止工程内部组件、进程或次级协议界面。一个 `web-product` 可以在同一后端业务模型上同时提供 REST、GraphQL、WebSocket、Webhook、MCP 或等价接口。

当 MCP Server 只是把 Web Product 已有的后端业务能力封装为 MCP Tools、Resources 或其他 MCP 能力时，它属于：

- Web Product 的后端组件；
- 次级集成界面；
- 需要独立 Claim、Security Boundary 和 Evidence 的 Capability；
- 同一 `web-product` Managed Project 的 P0–P6 范围。

MCP Server 使用 SSE、Streamable HTTP、stdio 或其他 Transport，不改变上述归属。MCP Server 位于独立进程、包或部署单元，也不自动改变 Project Type；只要它仍共享同一 Product Boundary、业务模型、数据、授权政策和主要生命周期，就继续由 `web-product-incubator` 受控推进。

只有当 MCP Server 本身成为主要独立交付物，拥有独立产品目标、消费者、版本支持、发布与回滚边界，且不再以通用浏览器核心产品旅程作为当前 Managed Project 的主要结果时，才不属于 `web-product`。该独立服务需要未来相应 Project Type；当前 Router 不得将其强制归入 Web Product。

该分类先使用现有 `boundary`、`capabilities`、`assumptions`、`plan`、`gates`、`risks` 与 Evidence 表达，不新增 `primary_surface`、`integration_surface` 或 MCP 专用 Runtime Schema 字段。若下游 Design 证明现有状态无法恢复必要语义，必须登记 `DESIGN_GAP`。

### 4.4 Shared Kernel 保持领域中立

Maker Authorization、MCP-only Mutation、Pending Request、Receipt、Hook、Evidence、状态摘要和权威状态继续由 Shared Kernel 提供。Web 项目的浏览器、HTTP、认证、数据和本地运行规则不得进入 Kernel。

V1.2 原则上不修改 Shared Kernel Schema 或通用授权语义。若下游设计发现 Web Project Type 无法通过现有 Registry、Workflow evaluator、状态分区和 Evidence 机制表达，必须登记 `DESIGN_GAP` 并返回 Architecture 层，不得在实现中隐式扩展 Kernel。

### 4.5 Host Profile 对 `web-product` 禁止

本提案采用：

```text
host_profile_requirement = "FORBIDDEN"
```

通用浏览器与本地开发环境由 Managed Project 的目标浏览器、端口、启动命令、构建命令、环境变量和本地依赖配置表达，不新增 `browser-host`、`localhost-host` 或具体浏览器 Host Profile。

Host Profile 禁止只表示路由和权威状态中不得绑定 Host，不表示项目可以忽略目标浏览器或本地运行环境。相关信息仍是 P1–P5 的项目配置与 Evidence 条件。

### 4.6 部署能力挂起

V1.2 将公开部署定义为：

```text
deployment_capability = "DEFERRED_CAPABILITY"
```

该标记是 Architecture 与 Planning 语义，不要求新增 Runtime Schema 字段。部署不进入 V1.2 完成条件，也不得被 localhost 成功隐式声明为已完成。

V1.2 不要求域名、DNS、TLS、CDN、生产托管、扩缩容、生产监控、生产密钥管理、线上迁移或公开可用性验证。未来启用部署能力时必须通过新的受控迭代补充 Design、Contract、Runtime 与验收边界。

## 5. `web-product` 适用边界

### 5.1 适用条件

满足以下条件的 Managed Project 可以路由到 `web-product`：

- 主要用户界面由通用浏览器访问；
- 产品同时具有前端与后端逻辑职责；
- 至少一个核心用户旅程需要穿过浏览器界面与后端或数据边界；
- 项目可以在本地构建，并能够通过 localhost 启动受控服务；
- 最终结果能够在真实浏览器中由用户观察。

### 5.2 排除条件

以下项目不得路由到 `web-product`：

- 浏览器扩展；
- 只有服务端 API、后台任务或基础设施而没有浏览器用户界面的项目；
- 以 MCP Server 本身作为主要独立交付物、且没有通用浏览器核心产品旅程的项目；
- 只有前端静态内容且没有后端逻辑职责的站点；
- 桌面应用、移动应用、CLI、SDK 或库；
- 游戏 Mod 或依赖特定游戏宿主的内容；
- 仅有设计稿、文档或原型而不形成可运行 Web 产品的项目。

外部 API、第三方身份服务、数据库和内容服务可以是 Web 产品依赖，但不会因此改变 Project Type。Web Product 后端新增用于封装既有业务能力的 MCP Server，也不会使项目退出 `web-product`。若主要交付形态发生变化，Router 只能提议迁移；Maker 确认后才能改变已激活 Project Type。

## 6. Child Incubator 职责

`web-product-incubator` 应负责：

1. 明确浏览器用户、核心结果、产品边界与排除边界；
2. 建立与技术栈无关的 Web Product Model；
3. 识别浏览器、前端职责、后端职责、数据、身份、外部依赖和信任边界；
4. 形成一个穿过主要前后端边界的 Usable Web Slice；
5. 确认构建与 localhost 启动路径可重复；
6. 区分构建、逻辑自动化、服务集成和真实浏览器 Evidence；
7. 管理不可信输入、服务端授权、Secrets、日志和外部副作用风险；
8. 对 REST、GraphQL、WebSocket、MCP 等适用的次级集成界面维护与后端业务模型一致的授权、失败和 Evidence 边界；
9. 在 P4 使用 Creation Correction，在 P6 使用合法返回点；
10. 使用 Shared Kernel 完成状态读取、授权、Mutation 与 Receipt 闭合。

`web-product-incubator` 不负责：

- 选择或偏好具体前端、后端、数据库或构建技术栈；
- 要求前后端分离或合并；
- 把 SPA、SSR、MPA 或全栈框架建成不同 Workflow；
- 因后端增加 MCP Server 或其他次级接口而自动迁移 Project Type；
- 负责浏览器扩展、纯后端服务、桌面端或移动端的领域流程；
- 承诺公开部署、生产可用、生产安全或规模化能力；
- 替 Maker 决定产品功能、业务领域、外部写入或付费服务使用；
- 直接修改权威状态或绕过 Shared Kernel。

## 7. P0–P6 Web Product Phase Profile

正式 Phase ID 与 Phase Name 原样复用 P0–P6。Web 专门术语只作为阶段说明、活动、检查点或 Evidence 条件，不形成新的顶层 Phase。

### 7.1 P0 `Intent Discovery`

明确用户问题、核心结果、成功标准，以及为什么浏览器产品是合适载体。若计划通过 MCP 或其他次级界面向 Agent、自动化客户端或外部系统暴露能力，同时明确该能力服务的用户结果及其与浏览器产品 Intent 的关系。区分已观察事实、可推翻假设和 Maker Product Decision。

可观察出口：Maker 已确认 Intent、核心结果、主要排除项和浏览器载体理由。

### 7.2 P1 `Project Definition`

明确目标用户、核心旅程、前端与后端职责、数据边界、身份与授权要求、外部依赖、本地运行标准和部署挂起范围。若存在 MCP 等次级集成界面，同时明确消费者、暴露能力、禁止能力、外部副作用、版本边界和它是否属于同一 Product Boundary。

项目级配置至少应能定位目标浏览器、构建命令、启动命令、localhost 端口或 URL、必要环境变量以及本地依赖。具体存储位置由下游 Design 决定，当前不新增权威配置文件。

可观察出口：Product Boundary、支持与排除范围、成功标准、本地运行条件以及高风险 Product Decision 已明确。

### 7.3 P2 `Solution Design`

形成 `Web Product Model`，至少解释：

- 浏览器用户与前端交互边界；
- 前端与后端逻辑职责；
- 请求、响应、状态和数据流；
- 身份、认证、服务端授权和会话边界；
- 数据持久化与外部依赖；
- 次级集成界面的 Adapter 边界、协议契约、业务层复用和失败语义；
- 浏览器、普通后端接口与 MCP 等次级界面之间的授权一致性；
- Secrets、日志和不可信输入边界；
- 构建、启动、失败恢复和最小可观察性；
- 部署能力的明确挂起范围。

高不确定或高代价路径可以使用阶段内 `FEASIBILITY_PROBE`。Probe 不是生产实现，不新增 Phase，也不能以局部接口成功证明完整浏览器旅程成立。

可观察出口：关键 Architecture Assumption、主要信任边界、失败模式、构建与本地运行路线可解释，并具有验证或降级路径。

### 7.4 P3 `Execution Planning`

将 Web Product Model 转换为工作包、依赖顺序、验证通道和两个 P4 检查点：

- `Usable Web Slice`：至少一个核心用户旅程从浏览器交互穿过后端或数据边界，到达用户可观察结果；
- `Build Readiness`：依赖安装、构建命令、必要配置、localhost 启动和失败诊断达到可重复验证条件。

计划必须识别自动化验证、真实浏览器验证、适用的次级集成界面契约与客户端验证、需要 Maker 参与的验证、外部副作用授权、停止条件和回滚或恢复路径。

可观察出口：任务、依赖、完成条件、验证层级、风险和停止点可执行。

### 7.5 P4 `Creation`

按获批计划创建 Project Artifact，并持续校验 Web Product Model 一致性。`Usable Web Slice` 与 `Build Readiness` 可以交错实现，但退出 P4 前必须分别形成结论。

`Usable Web Slice` 至少证明：

- 浏览器用户能够触发核心行为；
- 请求进入真实后端职责，而不是仅由前端假数据模拟；
- 后端、数据或等价业务结果可观察；
- 成功与关键失败反馈能够回到浏览器用户；
- 旅程没有依赖未授权的外部副作用。

`Build Readiness` 至少证明：

- 依赖与必要配置已明确；
- 构建命令可重复执行；
- localhost 服务可按记录方式启动和停止；
- 启动失败、缺少配置和依赖不可用具有可诊断结果；
- 构建产物和运行证据不会被表述为公开部署完成。

若当前 Product Boundary 包含 MCP Server 或其他次级集成界面，P4 还必须保持以下模型一致性：

- Adapter 复用后端业务能力，不形成未记录的第二套业务规则；
- Tool、Resource 或等价接口只暴露 Maker 已批准的 Capability Boundary；
- 次级界面不能绕过服务端授权、审计、数据和外部副作用控制；
- Transport、进程或包边界不会被误写成新的 Project Type 或顶层 Phase。

若 Evidence 推翻局部模型，进入 P4 内部 `Creation Correction`：记录失效 Assumption，暂停同方向修补，界定影响，修正设计、计划和实现，并重放受影响验证。Stage 保持 P4，不创建新的 Workflow Phase。若影响 Product Boundary、Architecture Decision、部署边界或 Runtime Invariant，提出 Maker Scope Review Requirement。

### 7.6 P5 `Validation`

P5 按结论层级执行：

1. `BUILD_VALIDATION`：证明项目在声明环境中完成构建；
2. `LOGIC_AUTOMATION`：证明确定性规则、解析、状态变化与失败恢复；
3. `LOCAL_INTEGRATION_VALIDATION`：证明前端、后端、数据和本地依赖在 localhost 环境中的集成；
4. `LOCAL_BROWSER_VALIDATION`：使用真实浏览器执行核心用户旅程并观察后端或数据结果；
5. `SECONDARY_INTERFACE_VALIDATION`：当 Product Boundary 包含 MCP 等次级界面时，证明协议契约、真实 Client 调用、授权、失败、副作用以及与后端业务语义的一致性；
6. `HUMAN_VALIDATION`：当产品语义或用户结果不能由自动化充分判断时，由 Maker 提供受控观察。

这些名称是 Design 语义，不要求新增 Runtime 枚举。构建成功只能支持 Build Claim；逻辑自动化不能单独证明浏览器旅程；接口探测不能替代用户可观察结果；localhost 成功不能证明公开部署或生产可用。浏览器旅程成功不能自动证明 MCP Capability 成立，MCP Client 调用成功也不能替代 Web Product 的真实浏览器核心旅程。

进入 P6 前的最低验证集合为：

- 构建成功；
- localhost 服务可访问；
- 至少一个真实浏览器核心旅程完成；
- 对应后端、数据或业务结果可观察；
- Product Boundary 包含次级集成界面时，对应 Capability 已取得协议契约和真实 Client 调用 Evidence；
- 已知限制、失败和残余风险被记录。

### 7.7 P6 `Iteration`

依据完整 Validation Result 选择合法返回点：

- Web Product Model 或 Architecture Assumption 调整：P2；
- 工作包、依赖顺序或验证计划调整：P3；
- Artifact、Usable Web Slice 或 Build Readiness 调整：P4；
- 同一边界内补充验证：P5。

若结果推翻 P0 Intent 或 P1 Project Definition，不得发明 P6→P0/P1 Transition。Child Skill 必须提出 Maker Review，由 Maker 决定是否重开项目边界、迁移 Project Type、暂停或终止。

## 8. Workflow Entry

- `NEW_PROJECT`：正式入口为 P0；
- `ADOPT_EXISTING`：Maker 提供项目来源和背景，Agent 检查设计、计划、Artifact、实现、构建记录和可用 Evidence，判断 P0–P6 中的正常阶段；
- `ADOPT_EXISTING` 至少提供一个 `evidence_refs` 和有界 `assessment_summary`；
- Maker 确认 Entry Mode、Project Type、Product Boundary 与完整激活范围；
- Agent 对阶段归属的语义判断负责，Kernel 只校验结构、阶段集合与 Evidence 引用；
- Entry 激活后不可修改；发现判断错误时必须报告证据并进入受控处置。

首个真实 Web 项目必须使用 `ADOPT_EXISTING` 路径，不得为了简化验收伪装成 `NEW_PROJECT`。

## 9. Evidence 与 Claim 边界

| Evidence 来源 | 可以证明 | 不能单独证明 |
| --- | --- | --- |
| 静态检查与构建 | 语法、类型、依赖解析和构建流程在声明环境中成功 | 服务可启动、前后端集成、用户旅程、生产可用 |
| 逻辑自动化 | 确定性业务规则、解析、状态转换和受控失败恢复 | 浏览器、网络、真实后端或数据边界成立 |
| 本地集成验证 | localhost 环境中的组件连接、接口和本地依赖行为 | 浏览器用户结果、公开部署或生产环境行为 |
| 真实浏览器验证 | 指定浏览器、构建、配置和 localhost 环境中的用户旅程 Observed Working | 未测试浏览器、生产部署、规模、安全或长期稳定性 |
| 次级集成界面验证 | 指定版本、Transport、Client、授权和 Capability Boundary 下的 MCP 或等价接口行为 | 浏览器产品旅程、未测试 Client、独立服务产品成立或生产稳定性 |
| Maker 人工观察 | 指定场景中的产品语义与用户可感知结果 | 自动外推到未测试范围或替代技术根因分析 |

所有 Evidence 继续使用 E0–E5 语义并绑定具体 Claim、Scope、Artifact 和环境。任何结论不得超过其证据层级；一次 localhost 成功不能升级为“生产就绪”。

## 10. 安全与外部副作用边界

下游 Design 至少必须处理：

- 浏览器输入、URL、查询参数、表单、上传、Cookie、Header、网络响应和第三方内容均视为不可信；
- MCP Tool 参数、Resource 请求、Client 元数据和其他次级接口输入同样视为不可信；
- 身份认证结果不等于资源授权，关键授权必须由后端职责执行；
- 浏览器、普通 API 与 MCP 等界面必须共享或明确映射同一后端授权和副作用政策，次级界面不得成为绕过路径；
- Secrets、服务端凭据和高权限令牌不得进入客户端构建产物、浏览器存储或可公开日志；
- 日志、错误响应和诊断证据不得泄露敏感数据、令牌或内部实现细节；
- 输入验证、输出编码、文件访问和重定向必须受明确边界约束；
- 外部账户、付费 API、真实消息发送、生产数据写入和其他外部副作用必须取得 Maker 明确授权；
- 未获授权时，测试默认使用本地、隔离、只读、模拟或可回滚依赖；
- 本地数据库、Fixture 和上传目录必须具备可识别的清理、恢复或隔离策略；
- localhost 验收不得静默暴露为公共网络服务；
- 安全扫描、类型检查或构建成功只能形成有限 Evidence，不等于产品安全成立。

## 11. Maker Authority

以下事项必须由 Maker 明确确认：

- 激活、停用或迁移 `web-product` Project Type；
- Product Boundary、核心用户旅程和排除范围；
- Architecture Decision；
- 身份、账户、敏感数据与外部写入政策；
- 真实账户、付费 API 和不可逆外部副作用；
- 人工验证预算与残余风险接受；
- 将 `DEFERRED_CAPABILITY` 的部署能力正式纳入后续版本。

Agent 可以在获批规格和计划内决定 Implementation Detail、测试组织、内部命名和技术栈适配。Runtime 只验证结构、授权、Revision、Workflow 合法性与 Receipt，不替 Maker 或 Agent 完成创造性判断。

## 12. Plugin 扩展点与禁止变化

### 12.1 预计新增或修改

在本提案及下游计划获批后，预计影响：

- 新增 `profiles/project-types/web-product.json`；
- 新增 `skills/web-product-incubator/SKILL.md`；
- 新增独立 Web Workflow evaluator；
- Registry 注册 `web-product`、Child Skill 和 `FORBIDDEN` Host Requirement；
- Router 增加 Web 适用与排除边界；
- Plugin Manifest 与候选包元数据增加 Web Product Incubation 能力；
- 增加 Unit、Contract、Integration、E2E、Package 与真实项目验收。

具体文件、接口和测试名称由 Implementation Plan 冻结，本节不授权实现。

### 12.2 原样复用

- Router 的提议与两步激活；
- `workflow.entry` 与 `ADOPT_EXISTING` Evidence；
- Registry 驱动的 Workflow evaluator；
- Shared Kernel Authorization、Mutation、Receipt、Hook 与状态完整性；
- `inspect_project` 状态摘要；
- P4 Creation Correction；
- E0–E5 Evidence 与现有 Core Context 分区。

### 12.3 明确禁止或不新增

- 不新增 Web Host Profile；
- 不修改 Shared Kernel 的授权、Receipt 或状态权威边界；
- 不新增第二套项目状态或 Web 专用权威文件；
- 不新增 SPA、SSR、前后端分离等 Project Type；
- 不因 Web Product 包含 MCP Server 或其他次级集成界面而新增 Project Type、Host Profile 或顶层 Phase；
- 不新增 MCP 专用 Runtime Schema 字段；
- 不新增 Deployment Phase；
- 不增加 P6→P0/P1 Transition；
- 不把首个真实项目的业务字段写入 Registry、Schema 或 Child Skill；
- 不修改 `mod`、`desktop-product`、`sims-4` 或 `windows-desktop` 的既有语义。

## 13. 影响分析

| Layer | 预计影响 | 本提案后的动作 |
| --- | --- | --- |
| Architecture | 新增 `web-product`，明确无 Host Profile 与部署挂起边界 | Maker 批准后更新 Architecture Decisions 与 Document Architecture |
| Design | 定义 Web Product Model、P0–P6 Profile、两个 P4 Checkpoint、次级集成界面、验证层级、安全和 Failure Routing | 新增 `WEB_PRODUCT_PROFILE.md` 或等价活动 Design 文档 |
| Contract | 定义 Web Entry、Workflow evaluator、阶段转换、Host Forbidden、验证输入输出与错误码 | Design 获批后编写 |
| Runtime Specification | 定义 Registry 加载、Entry/Transition 校验、失败关闭和安装后运行语义 | Contract 获批后编写 |
| Implementation Plan | 冻结 Profile、Skill、Workflow、Registry、Router、Manifest 和测试范围 | 上游规格获批后编写 |
| Acceptance Test Plan | 覆盖自动化、候选包、安装后行为和真实已有项目验收 | 与 Implementation Plan 同阶段审批 |
| Implementation Code | 当前禁止修改 | 两份 Plan 获批后开始 |
| Existing Types | `mod` 与 `desktop-product` 不修改、不迁移、不重新解释 | 完整回归必须继续通过 |

## 14. 失败路由

验证失败或反例必须按最早受影响层级路由：

- 实现偏差、局部缺陷或构建问题：保持或返回 P4；
- Web Product Model、信任边界或 Architecture Assumption 失效：P2；
- 工作包、顺序、验证方法或依赖计划失效：P3；
- 仅需补充同一边界内的验证：P5；
- Intent、Product Boundary、Project Type 或部署边界发生变化：提出 Maker Review，不自动迁移或改写状态。

P4 中的有界模型反例使用 Creation Correction；P5 形成完整 Validation Result 后通过 P6 选择 P2–P5。两者不得混淆。

## 15. 验收策略

### 15.1 自动化验收

下游 Acceptance Test Plan 至少覆盖：

- Registry 能发现 `web-product` 且 Host Requirement 为 `FORBIDDEN`；
- Router 能区分 Web 产品、浏览器扩展、纯后端 API 与桌面产品；
- 含 MCP Server 的 Web Product 仍路由为 `web-product`，独立 MCP Service 不因使用 HTTP 或附带辅助页面而被误路由；
- `NEW_PROJECT` 只能从 P0 开始；
- `ADOPT_EXISTING` 可基于 Evidence 进入 P0–P6 的正常阶段；
- P0–P6 顺序、P6→P2–P5 与 Maker Authority 保持不变；
- P4 Creation Correction 不产生新 Phase；
- Build-only Evidence 不能满足 P5；
- 浏览器 Evidence 与 MCP 等次级界面 Evidence 不互相替代；
- 次级 MCP Capability 复用后端业务和授权边界，并能通过真实 MCP Client 验证；
- 不要求部署且不能产生生产就绪声明；
- Web Skill 不按 SPA、SSR、分离或技术栈分裂流程；
- `mod`、Desktop、Host、Kernel、Hook、Receipt 和安装候选完整回归通过；
- 新 Skill 必须先建立无 Skill 的失败行为基线，再按测试驱动方式编写并验证。

### 15.2 真实已有项目验收

首个已有 Web 项目作为 V1.2 的 `ADOPT_EXISTING` Field Validation：

1. 基于真实设计、实现、构建记录和 Evidence 判断初始阶段；
2. Maker 确认完整激活范围；
3. 执行并记录构建命令；
4. 在受控 localhost 环境启动前端与后端职责；
5. 使用真实浏览器完成至少一个核心用户旅程；
6. 观察并记录对应后端、数据或业务结果；
7. 验证关键失败反馈和无未授权外部副作用；
8. 若现有项目包含 MCP Server 或其他次级集成界面，使用真实 Client 验证其协议契约、授权、结果、失败和副作用，并确认其未绕过后端业务边界；
9. 形成绑定构建、浏览器、配置、URL、步骤和结果的 Evidence；适用时另绑定次级界面的 Transport、Client、Capability 与结果；
10. 明确声明未执行公开部署，结论不包含生产就绪。

该真实项目只提供 Field Evidence，不替代 Plugin Unit、Contract、Integration、E2E 和安装候选回归。

## 16. 兼容与迁移策略

- 现有 Managed Project 不自动迁移到 `web-product`；
- 现有 `mod` 与 `desktop-product` Registry 条目、Skill、Profile 和 Workflow 保持兼容；
- 旧项目状态不要求回填 Web 字段，因为本提案原则上不新增 State Schema 字段；
- `web-product` 不允许绑定 Host Profile，Router 与 Kernel 必须拒绝非空 Host；
- Candidate Package 必须继续通过 Plugin 与 Legacy 回归矩阵；
- V1.2 发布前重新确认 V1.1 的发布归档、Plugin Package Version 和迁移记录；
- Deployment Capability 后续启用时必须通过独立变更控制，不得回溯改写 V1.2 验收结论。

## 17. 备选方案与取舍

### 17.1 在同一 Plugin 中新增 `web-product`：推荐

复用已验证的 Router、Registry、Shared Kernel、Workflow Entry 和候选打包结构，只增加 Web 领域 Profile、Child Skill 和 evaluator。能够最小化重复授权逻辑和状态分叉。

### 17.2 单独创建 Web Incubator Plugin：拒绝

会复制 Router、Kernel、授权、Receipt、Hook 和安装路径，产生两个状态控制面；当前没有隔离收益足以抵消一致性与维护成本。

### 17.3 使用通用 `software-product`：拒绝

会混合桌面、Web、移动、服务端和扩展的不同验证与风险边界，使 Child Skill 重新成为大而全流程。

### 17.4 为浏览器或 localhost 创建 Host Profile：拒绝

目标浏览器和本地服务配置属于项目级运行与 Evidence 条件，不需要 Host Profile 才能表达。新增 Host 会把普通项目配置错误提升为路由和激活复杂度。

### 17.5 将部署纳入 V1.2 必经 Gate：拒绝

当前 Maker 只要求 build 成功、localhost 可访问和真实浏览器核心旅程。强制部署会扩大外部权限、成本、安全与环境范围，并延迟首个真实项目验证。

## 18. 非目标

本提案不：

- 设计或实现公开部署；
- 宣称生产可用、生产安全、规模化或高可用；
- 决定具体 Web 技术栈、框架、数据库或仓库布局；
- 把 SPA、SSR、MPA、前后端分离或全栈框架定义为不同类型；
- 将独立 MCP Service、浏览器扩展、纯后端 API、静态前端站点、桌面端或移动端强制归入 `web-product`；
- 为独立 MCP Service 定义新的 Project Type 或孵化流程；
- 修改 Shared Kernel Invariant；
- 新增 Web 专用权威状态文件；
- 把首个真实项目的业务领域或实现细节固化为通用规则；
- 授权真实账户、付费 API、生产数据写入或其他外部副作用；
- 授权任何实现代码变更。

## 19. 下游规格验收标准

本提案获批后的下游规格必须能够证明：

1. `web-product` 按产品形态定义，不依赖业务领域或技术栈；
2. 前端与后端作为逻辑职责表达，不要求特定工程拓扑；
3. 浏览器扩展、纯后端、独立 MCP Service、静态前端、桌面、移动、CLI、SDK 与库被明确排除；
4. `host_profile_requirement = FORBIDDEN`，且目标浏览器与 localhost 配置仍可追踪；
5. P0–P6 原样复用，Web 副命名不形成新 Phase；
6. P4 的 Usable Web Slice 与 Build Readiness 具有独立完成条件；
7. Build、Logic、Local Integration、Local Browser、Secondary Interface 与 Human Evidence 的结论上限清晰；
8. Build-only 不能通过 P5，localhost 成功不能产生部署或生产就绪结论；
9. Deployment 保持 `DEFERRED_CAPABILITY`，不进入 V1.2 完成 Gate；
10. 不可信输入、服务端授权、Secrets、日志和外部副作用边界清晰；
11. P4 Creation Correction 与 P6 Iteration 的路由边界清晰；
12. `NEW_PROJECT` 与 `ADOPT_EXISTING` 都可恢复且符合现有 Entry Contract；
13. 首个已有项目能够作为真实 `ADOPT_EXISTING` Field Validation，但不成为通用规则来源；
14. 新类型通过 Registry 与独立 evaluator 扩展，Shared Kernel 不出现 Web 领域分支；
15. Web Product 可以在同一 P0–P6 中设计和验证 MCP Server 等次级界面，不因 Transport、进程、包或部署单元自动改变 Project Type；
16. 浏览器旅程 Evidence 与 MCP Capability Evidence 分别建立且不能互相替代；
17. 次级集成界面复用后端业务、授权、审计、数据和外部副作用边界，不形成未记录的第二套业务规则；
18. `mod`、Desktop、Host、Kernel 与 Legacy 回归保持通过。

## 20. 待 Maker 书面审阅

Maker 已在 2026-10-13 的讨论中确认以下方向，可作为本提案的讨论基线：

1. 面向通用浏览器端产品，不按静态站点、SPA、SSR、前后端分离或技术栈拆分；
2. Web 产品同时具有前端与后端逻辑职责；
3. V1.2 只要求 build 成功、localhost 可访问和真实浏览器核心旅程；
4. 公开部署作为 `DEFERRED_CAPABILITY` 挂起；
5. 使用 P0–P6、Usable Web Slice、Build Readiness、分层 Evidence、安全边界和受控 Failure Routing；
6. 新增 Project Type Profile、Child Skill、Workflow evaluator、Registry、Router 与元数据，不新增 Host Profile；
7. 真实已有 Web 项目作为首个 `ADOPT_EXISTING` Field Validation；
8. V1.1 与 V1.2 分支和版本工作分离；
9. Project Type 约束主要产品形态而不限制内部组件或次级协议界面；Web Product 后端为既有业务能力增加 MCP Server 时，仍由同一 `web-product-incubator` 的 P0–P6 设计、实现和验证；
10. MCP Server 只有在成为具有独立产品目标和生命周期的主要交付物时才不属于 `web-product`，本提案不定义该独立类型。

上述讨论批准不等于对本文档逐条书面批准。Maker 需要审阅本文档并明确确认后，Status 才能改为 `APPROVED`；批准只授权继续 Architecture Decisions 与 Design Layer，不授权实现。
