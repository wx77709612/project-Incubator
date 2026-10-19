---
name: web-product-incubator
description: Use when：Project Incubator Router 已确认 Managed Project 类型为 web-product，需要按 P0–P6 孵化、恢复或推进同时具有前后端职责的浏览器产品；不适用于未确认路由、浏览器扩展、静态前端、纯后端或独立 MCP Service。
---

# Web Product Incubator

## 当前 Kernel 权威与恢复

Plugin Router `project-incubator-router` 是唯一现行入口。权威集合为 `.project-incubator/activation.json`、`.project-incubator/state.json` 和 `.project-incubator/latest-receipt.json`；State 是唯一业务状态，Activation 约束身份/路由，Receipt 证明闭合。临时 Runtime Data 和 Markdown Artifact 不替代它们。

恢复与状态查询先调用 `inspect_project`，验证失败时报告稳定错误并停止受影响推进，不从聊天补全。只使用已验证路由的 Child Skill/Host Profile；不得直接编辑权威文件。所有受控变更经现行 Kernel，提交后确认 revision、回读与 Receipt 一致再报告完成。缺少 Plugin/MCP 时停止，不调用旧执行资产。


本 Skill 是随插件分发的自包含领域指导，复用 Registry、Web Profile 与 MCP Kernel 契约；研发规格仅用于源码溯源，不是安装环境的外部依赖。

## 启动与权威边界

仅在 Router 已提议 `web-product`、Maker 已批准完整激活范围且 Runtime 返回有效激活状态后使用。恢复和查询先调用 `inspect_project`，只根据已验证的 Activation、State 和 Receipt 判断当前状态，不从聊天记忆补全。Kernel 负责授权、Context Mutation、Revision、Receipt 和 Workflow 结构；Agent 负责设计、阶段判断和 Evidence 解释，不能替 Maker 决定产品或架构。

适用条件是通用浏览器为主要界面，同时存在前端呈现/交互与后端业务/授权/数据职责，至少一条核心旅程跨越浏览器与后端或数据边界。前后端是逻辑职责，不规定框架、进程、仓库或部署拓扑。浏览器扩展、无后端职责的静态前端、纯后端、独立 MCP Service、CLI、SDK、库、移动、桌面和 Mod 不由本 Skill 接管。

`host_profile_requirement = FORBIDDEN`，`host_profile_id = null`。浏览器、localhost、操作系统、命令和端口是项目配置与 Evidence 条件，不得创建 Host Profile。

## Workflow Entry

- `NEW_PROJECT`：标准入口只能是 P0。
- `ADOPT_EXISTING`：检查已有设计、计划、Artifact、实现、构建、本地运行和验证 Evidence，判断 P0–P6 正常阶段；记录 `assessment_summary` 和至少一个 `evidence_refs`，不得以 Correction 或 Review 子流程作为入口。
- Maker 确认来源、Project Type、Product Boundary、Entry Mode 与完整激活范围；Agent 负责阶段分析，Kernel 只验证结构、合法阶段和授权。
- Entry 激活后不可修改。错误判断必须报告证据并通过受控处置解决，不直接改写 `workflow.entry`。

## 正式阶段

仅使用 P0→P1→P2→P3→P4→P5→P6 与 P6→P2/P3/P4/P5。Web 副说明、Checkpoint、Validation Channel 和 Correction 都不是 Stage，不增加 Runtime 枚举或权威状态文件。

### P0 `Intent Discovery`

目标：确认用户问题、核心结果、可观察成功标准和浏览器载体理由。

输入：Maker Intent、用户故事、现有 Observation 与 Hypothesis；有次级界面时说明消费者和结果。

产物：Intent、核心旅程候选、浏览器适用依据、主要排除项与待决问题。

Completion Conditions：Maker 已确认问题、结果、成功标准和载体；主要结果不是纯后端或独立服务，次级界面未变成未经批准的第二个产品目标。

失败路由：证据不足留在 P0 调查；载体或产品方向冲突提交 Maker Review，不擅自激活或迁移。

### P1 `Project Definition`

目标：建立 Web Product Boundary、支持和排除范围。

输入：已确认 Intent、核心旅程、用户、数据与依赖背景。

产物：前端与后端职责、关键数据与外部依赖、次级界面归属、Build/localhost/真实浏览器验收范围、部署挂起和风险清单。

Completion Conditions：Project Type 和边界受控确认，无 Host；至少一条跨边界旅程可观察；高风险能力明确为待决政策而非默认授权。

失败路由：定义缺失留在 P1 补全；Intent 或主要形态失效提出 Maker Review，不通过后续实现扩大边界。

### P2 `Solution Design`

目标：形成 `Web System Model`，解释核心旅程和失败反馈如何跨越信任边界。

输入：已确认 Product Boundary、风险与现有 Evidence。

产物：浏览器入口、前端状态/输入/错误反馈、后端业务/服务端授权/数据访问/副作用、数据所有权/持久化/缓存/迁移、身份/会话/角色、外部依赖隔离、次级界面、日志/隐私/审计、本地运行模型与 Artifact 关系。

Completion Conditions：关键 Architecture Assumption 有支持 Evidence、备选路径，或 Maker 接受的有界风险与停止条件。高影响未知项可使用阶段内 `FEASIBILITY_PROBE`，记录假设、最小实验、结论上限与停止条件；Probe 不是 Stage。

失败路由：设计不足留在 P2；推翻 Product Boundary 或授权政策时提交 Maker Review，再继续受影响部分。

### P3 `Execution Planning`

目标：将设计转为可执行工作包和验证计划。

输入：Web System Model、风险、现有 Baseline 与 Maker 验证预算。

产物：代表性切片、依赖顺序、两个 P4 Checkpoint、六类 P5 Design Channel、本地命令/readiness/数据/清理、模拟边界、关键失败与恢复测试、Known-Good Baseline、回归集合和部署非目标。

Completion Conditions：工作包、完成条件、Evidence 绑定、停止点与回滚可执行；次级界面包含独立协议、授权、失败和真实 Client 任务。人工批次与预算由 Maker 确认，未设置记为 `UNSET`，不编造上限。

失败路由：计划不足留在 P3；设计缺失报告最早受影响的 P2 层并请求受控处置，不发明逆向 Transition。

### P4 `Creation`

目标：在获批工作包内实现 Artifact，并分别完成 `Usable Web Slice` 和 `Build Readiness`；两个 Checkpoint 都不是 Stage，且不得标为不适用以绕过要求。

输入：设计、执行计划、Baseline 和可重放本地运行配置。

产物：实现、构建 Artifact、两个独立检查点结论与受影响回归 Evidence。

| Checkpoint | 最低观察与独立评估 |
| --- | --- |
| Usable Web Slice | 真实浏览器入口、核心交互、前端/后端/数据边界、可见成功与失败反馈、授权及副作用可归因；分别提供 Evidence Refs、Claim Scope、Known Limitations、Failure Routing 和独立 Gate Evaluation，结果必须为 `REQUIREMENT_SATISFIED`。 |
| Build Readiness | 依赖/版本、成功构建、缺失配置失败、可重复 localhost 启动、readiness、前后端可触达、停止与失败清理；分别提供 Evidence Refs、Claim Scope、Known Limitations、Failure Routing 和独立 Gate Evaluation，结果必须为 `REQUIREMENT_SATISFIED`。 |

Completion Conditions：只有两项均为 `REQUIREMENT_SATISFIED` 时，Checkpoint Contract 才不阻止 P4→P5；仍须走合法受控转换。Script Validation Result 不是 Gate Result，P4 出口不代表 P5 已通过。

失败路由：切片失败沿核心旅程定位边界；构建或启动失败沿配置与运行模型定位。两项分别记录缺口和返回工作包，留在 P4，不用一项成功替代另一项。

P4 `Creation Correction` 复用普通受控 Context Mutation：记录失效 Assumption、暂停同方向补丁、界定影响、修正设计/计划/Artifact、重放验证，Stage 保持 P4，不提交 `workflow_transition`。若涉及 Product Boundary、Architecture Decision、授权政策或 Runtime Invariant，提出 Maker Scope Review Requirement；不把 `MODEL_REVIEW` 变成 Web Stage。

### P5 `Validation`

目标：完成 `Local Product Validation`，让结论受实际 Evidence 限制。

输入：被测 Revision、Artifact、配置、P4 两项结论与验证计划。

产物：区分六类 Design Channel 的 Validation Result；每项附适用性、Evidence Refs、Claim Scope、Known Limitations、观察事实及未形成结论的 Reason。

| Design Channel | Claim 上限 |
| --- | --- |
| LOGIC_AUTOMATION | 仅证明确定性逻辑、解析、授权规则和失败恢复；不能证明真实浏览器或完整集成。 |
| BUILD_VALIDATION | 仅证明受控依赖下的编译、打包、静态检查和 Artifact；不证明运行中的用户旅程。 |
| LOCAL_INTEGRATION_VALIDATION | 仅证明指定 localhost 配置下前后端、数据与适用外部依赖的集成；不能替代真实浏览器。 |
| LOCAL_BROWSER_VALIDATION | 仅证明指定真实浏览器、构建与配置中的呈现、交互、错误和核心结果；不证明未测环境或生产能力。 |
| SECONDARY_INTERFACE_VALIDATION | 仅证明真实适用 Client 的协议、授权、结果、失败和副作用；不能替代浏览器旅程。 |
| HUMAN_VALIDATION | 仅证明明确观察者角色在指定场景和环境中的结果理解与业务接受性；不能替代技术 Evidence。 |

Completion Conditions：以下 Requirement 必须分别评估，不能仅列出 Channel 名称：

- Build Requirement 的 Gate Evaluation 为 `REQUIREMENT_SATISFIED`。
- Local Integration Requirement 的 Gate Evaluation 为 `REQUIREMENT_SATISFIED`。
- Local Browser Requirement 的 Gate Evaluation 为 `REQUIREMENT_SATISFIED`，Evidence 至少覆盖一条真实浏览器核心旅程。
- Product Boundary 包含次级界面时，适用 Secondary Interface Requirement 的 Gate Evaluation 为 `REQUIREMENT_SATISFIED`。
- 适用关键失败路径有 Evidence；条件通道不适用时记录与边界一致的理由，不能写成通过；明确 Deployment 未验证。

Build-only、Logic-only 或进程存活不能满足 P5。Build、Logic、Browser、Secondary Interface 与 Human Evidence 不能互相替代。Script Validation Result、Observation 或 Human Judgment 不能直接替代 Gate Evaluation Result。Design Channel 不增加 Core Runtime 枚举。

失败路由：未满足必要 Requirement 则留在 P5，记录 Failure Routing、缺口、最早受影响层与修复建议；不得伪称通过。完成 Validation Result 后在合法 P5→P6 中受控形成迭代决定，不能直接逆跳。

### P6 `Iteration`

目标：按完整 Validation Result 决定有界迭代。

输入：验证结果、反例、风险、Baseline 和待决事项。

产物：迭代理由、目标阶段、范围、授权要求和回归计划。

Completion Conditions：系统模型变更走 P6→P2，执行/验证计划变更走 P6→P3，Artifact 调整走 P6→P4，同边界补充验证走 P6→P5；受控提交与回读成功后才算转换完成。

失败路由：推翻 P0 Intent 或 P1 Definition 时提出 Maker Review，由 Maker 决定重开边界、迁移或终止；不得发明 P6→P0/P1 Transition。

## 本地运行与 Evidence 绑定

构建最低要求是可恢复的依赖准备、依赖和工具版本、构建命令、成功状态/Artifact、代码 Revision 与配置摘要。localhost 最低要求是可重复启动命令、localhost URL、端口、协议、环境变量名称/来源类别/缺失行为、数据准备/迁移、readiness、停止与失败清理。进程存活不等于 readiness，也不证明前后端可触达。

每份结果绑定前端、后端、数据与适用外部依赖状态，明确真实、模拟、替代或不可用；模拟成功不能外推到真实依赖。敏感值只记录脱敏标识或来源类别。真实浏览器结果还绑定浏览器名称与版本、入口、用户步骤、可见结果、对应后端或数据结果、关键失败反馈与副作用；不能以 HTTP 探测、截图或构建日志代替完整旅程。

## 次级界面

REST、GraphQL、WebSocket、Webhook、MCP 只有同时满足以下条件才属于同一 Web Managed Project：服务同一 Product Boundary 与主要用户结果；复用同一业务模型、数据所有权、身份、授权、审计和外部副作用政策；共享主要版本和变更生命周期；不是主要独立交付物。

每个 Capability 要有独立 Claim、Security Boundary 和 Evidence。次级界面 Evidence 不能替代真实浏览器 Evidence，浏览器 Evidence 也不能证明次级协议。MCP Tool、Resource、Prompt 或等价能力只暴露获批后端 Capability，不复制另一套业务或授权规则。

真实 MCP Client 验证绑定 Client 名称与版本、Transport、Capability、非敏感授权上下文、输入和结果，分别验证允许路径、未授权或越权拒绝、协议失败、业务失败、审计与副作用；证明与同一后端授权政策一致，不因 Client 调用成功跳过拒绝路径。

Transport（含 SSE、Streamable HTTP、stdio）、独立进程、包或部署单元变化不自动改变类型。出现独立产品目标、消费者、版本支持、发布/回滚边界并取代浏览器核心结果时，提出 Maker Project Type Review，不自动迁移或发明独立服务类型。

## 安全与 Maker Authority

浏览器、次级 Client、文件、富文本、Webhook 和外部响应均是不可信输入；服务端必须执行授权，不依赖隐藏前端控件。设计和验证覆盖适用身份/会话、跨站边界、Secrets、日志隐私、外部请求、迁移、资源耗尽与副作用；不适用需说明理由，不等于已验证。

Product Decision、Architecture Decision、类型确认、真实账户、付费服务、外部写入、高成本验证、超预算和接受残余风险由 Maker Authorization 决定。Evidence 可以推翻 Runtime Assumption，不能自动改写 Maker Decision。使用 E0–E5 与绑定范围的 Known-Good Baseline；一次成功不能外推未测试边界。

## Deployment 与 Closure

Deployment 保持 `DEFERRED_CAPABILITY`。域名、DNS、TLS、CDN、生产托管、生产 Secrets、线上迁移、扩缩容、监控和公开可用性不属于本版本验收；既有线上资料只作背景。不得根据构建、localhost、浏览器或 MCP 成功声称 Production Ready 或 Deployment Validated。

不新增 Deployment Stage、Host、Gate Type 或 Runtime Schema 字段；未来启用须另提 Architecture Change。

普通 Context Mutation 和 Phase Transition 均通过现有 Kernel；Gate Result 不直接修改状态。`READY_FOR_TRANSITION` 不等于 Transition 已执行；Project State 持久化、revision 递增、回读与 Receipt 一致后才可声明受控变更完成。
