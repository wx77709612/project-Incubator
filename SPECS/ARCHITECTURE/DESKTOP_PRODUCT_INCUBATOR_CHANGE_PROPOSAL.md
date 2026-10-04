# Project Incubator Plugin Desktop Product Incubator Architecture Change Proposal

## 1. 文档状态

| 字段 | 值 |
| --- | --- |
| Specification Track | Project Incubator Plugin 下一迭代 |
| Status | DRAFT |
| Plugin Baseline | `0.1.0+codex.20261002144305` |
| Verified Commit | `6f4daf05acad92f3c097b4729c81d36fab3906b2` |
| Change Type | Project Type Extension |
| Implementation Authorization | NOT GRANTED |
| Maker Discussion Baseline | 2026-10-04 |

本文档是新增第二种项目孵化能力前的 Architecture Change Proposal。它只定义 `desktop-product` 项目类型、`desktop-product-incubator` 的职责边界、与 Shared Kernel 的关系以及下游设计约束。

本文档处于 `DRAFT`，不是当前实现依据，不授权修改 Plugin Runtime、Schema、Registry、Skill、Host Profile 或测试。

## 2. 变更动机

当前 Project Incubator Plugin 已形成 Router + Shared Kernel + Child Incubator + Host Profile 架构，但正式项目类型只有 `mod`，无法为桌面产品提供可复用的产品形态指导。

本次变化的目标不是孵化某个特定业务领域，也不是为某个具体产品建立组合式专用类型，而是新增可跨领域复用的桌面产品孵化能力。该能力应沉淀桌面产品共同面对的生命周期、交付、安全、目标环境验证和发布问题，使后续不同领域的桌面产品可以使用同一 Child Incubator。

具体 Managed Project 可以搜索、采集、管理或处理不同类型的在线机会或其他业务对象；这些内容属于项目自身的 Product Boundary，不进入 `desktop-product` 的类型定义。

## 3. 已确认的架构原则

### 3.1 Project Type 按产品形态划分

`Project Type` 表示可复用的产品形态及其研发风险，不表示业务领域、商业产品组合或多个交付物之间的组织关系。

本提案采用：

```text
project_type_id = "desktop-product"
child_skill_id = "desktop-product-incubator"
```

不采用 `desktop-companion`、`mod-hunter`、`opportunity-hunter` 等组合关系或领域名称作为 Project Type。

### 3.2 Child Incubator 只负责单一产品形态

`desktop-product-incubator` 只负责桌面产品的孵化指导、阶段规则、验证边界和风险控制。它不负责决定其他产品形态如何与桌面产品组合。

未来的浏览器扩展能力将作为独立任务设计为独立 Project Type 与 Child Incubator。本提案既不实现该能力，也不否定其后续新增。

### 3.3 Project Incubator 不拥有产品组合决策

Project Incubator 是孵化工具，不是产品组合、项目群或系统集成的最终控制器。Maker、Agent、具体产品架构和其他工具可以在 Project Incubator 之外决定不同产品、项目、仓库或交付物如何协作。

当前 Runtime 的单一 `project_type_id` 与单一 `child_skill_id` 只表示一次受控孵化路由由哪个 Child Workflow 负责，不构成“一个商业产品只能有一种产品形态”的架构规则。

### 3.4 Shared Kernel 继续保持领域中立

Maker Authorization、MCP-only Mutation、Pending Request、Receipt、Hook、Evidence、状态摘要和三份机器可读权威状态继续由 Shared Kernel 提供。桌面产品规则不得进入 Kernel。

## 4. `desktop-product` 适用边界

### 4.1 适用条件

满足以下主要条件的 Managed Project 可以路由到 `desktop-product`：

- 主要交付物是安装或运行在桌面操作系统中的用户产品；
- 产品具有本地进程、桌面 UI、系统托盘、后台任务或等价桌面生命周期中的至少一种；
- 产品需要处理本地数据、权限、安装、升级、卸载、恢复或桌面环境兼容性中的至少一种；
- 最终能力需要在目标桌面环境中形成用户可观察结果。

### 4.2 排除条件

以下项目不因与桌面产品协作而自动路由到 `desktop-product`：

- 游戏 Mod 本身；
- 浏览器扩展本身；
- 纯 Web、SaaS 或服务端产品；
- 移动应用；
- 操作系统驱动或内核级组件；
- 仅作为库、SDK 或协议定义交付的项目。

若项目的主要交付形态发生变化，Router 只能提议迁移；Maker 确认后才能改变已激活的 Project Type。

## 5. Child Incubator 职责

`desktop-product-incubator` 应负责：

1. 明确桌面产品的用户结果、支持边界和排除边界；
2. 识别桌面进程、本地数据、UI、后台任务和外部集成的最小架构边界；
3. 识别安装、升级、卸载、数据迁移、权限和恢复风险；
4. 推进一个用户可观察的桌面产品完整切片；
5. 区分本地自动化、桌面 UI 自动化和真实目标环境 Evidence；
6. 管理打包、签名、发布、升级和回滚的准备度；
7. 依据 Capability 风险选择必要验证，不强迫所有桌面产品执行相同检查；
8. 使用 Shared Kernel 完成状态读取、授权、Mutation 与 Receipt 闭合。

`desktop-product-incubator` 不负责：

- 规定项目具体搜索、采集或管理什么业务对象；
- 替 Maker 决定产品功能、商业模式或支持范围；
- 定义浏览器扩展、Web、移动端或游戏 Mod 的领域流程；
- 决定多个产品形态是否属于同一商业产品、仓库或发布计划；
- 直接修改权威状态或绕过 Kernel；
- 用一次本地成功替代目标桌面环境证据。

## 6. Host Profile 边界

`desktop-product` 与桌面操作系统之间保持 Project Type 与 Host Profile 分离：

```text
desktop-product
    -> windows-desktop Host Profile
    -> future macOS Host Profile
    -> future Linux Host Profile
```

首个实际产品以 Windows 桌面环境为起点，因此下游设计可以提议 `windows-desktop` Host Profile。该 Profile 只具体化 Windows 安装、权限、签名、进程、文件系统、升级和真实环境验证规则，不得把 Windows 规则写入通用 `desktop-product` Workflow。

新增首个 Windows Host Profile 不等于作出“所有未来桌面产品只支持 Windows”的 Product Decision。

## 7. 阶段模型复用评估

P0–P6 是本次设计的重要输入，但不是必须原样继承的 Runtime Phase Set。Desktop Product Workflow 必须同时满足两项要求：复用已有治理经验，且让阶段边界对应桌面产品真正不同的风险与证据。

### 7.1 可直接复用的经验

下列经验与产品形态无关，应继续保留：

- Intent、Project Definition、Solution Design 与 Execution Planning 必须在 Creation 前闭合；
- Required Artifact、Phase Artifact 与 Context Mutation 必须分开表达；
- State Change Requirement 不等于 Context 已修改；
- Gate Result 不直接执行 Transition；
- `READY_FOR_TRANSITION` 不等于 Transition 已完成；
- Maker 保留 Product 与 Architecture Decision 权威；
- Validation 必须回看 Intent、边界、Artifact 与约束；
- Validation 失败应返回最早受影响的设计、计划、创建或验证范围；
- Evidence、Known-Good Baseline、Correction 与 Confidence 规则继续适用。

### 7.2 不宜原样复用的部分

P0–P6 的阶段目标具有通用价值，但原始阶段切分不完全贴合桌面产品：

- Plugin Activation 已建立项目身份与机器权威状态，P0 Intent Discovery 与 P1 Project Definition 在运行态可以合并，避免重复 Gate；
- P4 Creation 对桌面产品过宽，无法区分“核心用户路径可用”和“安装、升级、卸载、数据迁移、权限、签名、恢复已经闭合”；
- P5 Validation 需要显式区分逻辑自动化、桌面 UI 自动化与真实 Host Evidence；
- P6 Iteration 更适合作为基于 Validation Result 返回受影响阶段的转换机制，而不是所有项目必须经过的固定尾部阶段；
- Legacy Core Context 的物理文件和 Artifact 结构不应恢复，Plugin 继续使用现有机器可读权威状态。

### 7.3 推荐的选择性复用方案

本提案推荐吸收 P0–P6 的职责与治理规则，同时根据桌面产品风险重新设置阶段边界：

| Desktop Phase | 主要复用来源 | 桌面产品目标 | 最小可观察出口 |
| --- | --- | --- | --- |
| `PRODUCT_BOUNDARY` | P0 + P1 | 明确用户、核心结果、桌面载体理由、首个 Host、支持与排除边界 | Maker 已确认 Product Boundary；项目身份、Host 与不支持范围可恢复 |
| `DESKTOP_SYSTEM_MODEL` | P2 | 定义进程、UI、本地数据、权限、外部集成、信任边界和失败恢复模型，并通过低成本探针处理可能推翻整体方案的关键可行性未知项 | Architecture Decision、Assumption、风险与验证路径可追踪；进入 Creation 所需的关键可行性主张已有证据、备选路径或经 Maker 接受的有界风险 |
| `EXECUTION_PLAN` | P3 | 将系统模型转换为切片、工作包、依赖、交付和验证计划 | 实施顺序、完成条件、自动/人工验证与预算边界明确 |
| `USABLE_SLICE` | P4 的核心创建职责 | 完成一个代表性、用户可操作、可观察的桌面产品完整路径 | 用户旅程在受控桌面环境可执行；失败位置、产物和副作用可归因 |
| `DELIVERY_HARDENING` | P4 的交付职责 + 桌面专门化 | 闭合打包、安装、升级、卸载、数据迁移、权限、签名、恢复和回归风险 | 交付物内容可验证；失败可恢复；Known-Good Baseline 与关键回归存在 |
| `TARGET_VALIDATION` | P5 + P6 返回语义 | 在真实 Host 验证支持边界、发布准备度、升级/回滚和已知限制 | 形成受约束的 Validation Result；满足发布边界或明确返回受影响阶段 |

`TARGET_VALIDATION` 不是单向终点。Validation Result 必须指出结论、Evidence 上限和最早受影响阶段：

- 产品边界错误返回 `PRODUCT_BOUNDARY`；
- 系统模型或 Architecture Assumption 错误返回 `DESKTOP_SYSTEM_MODEL`；
- 执行路线或验证计划不足返回 `EXECUTION_PLAN`；
- 核心用户路径实现问题返回 `USABLE_SLICE`；
- 安装、升级、迁移、权限、恢复或发布问题返回 `DELIVERY_HARDENING`；
- 仅需补充同边界验证时保持在 `TARGET_VALIDATION`。

### 7.4 可行性调研的位置

可行性调研不是独立的常驻 Phase，而是服务于阶段决策的 `FEASIBILITY_PROBE` 活动。它的主要归属是 `DESKTOP_SYSTEM_MODEL`：在冻结执行路线前，用最小成本验证可能推翻核心用户路径、系统边界或关键 Architecture Assumption 的未知项。

不同问题应在最早能影响决策的位置处理：

- “是否存在值得孵化的用户问题、桌面载体是否必要”属于 `PRODUCT_BOUNDARY`；
- 框架能力、进程模型、本地数据、权限、系统集成、外部接口和失败恢复是否成立，主要属于 `DESKTOP_SYSTEM_MODEL`；
- 已知需要实验但不会改变系统边界的实现未知项，由 `EXECUTION_PLAN` 安排有预算和停止条件的探针；
- 打包、安装、升级、签名或安全软件交互若可能推翻架构，必须在进入 Creation 前提前探查；若只影响交付实现，则可在 `DELIVERY_HARDENING` 中验证。

每个可行性探针至少记录：待验证主张、关键未知项、最小判别实验、成功与失败信号、预算或停止条件、Evidence 引用、受影响 Assumption 以及结论。探针产物默认不是生产实现，也不能以孤立实验宣称完整 Host 语义成立。

进入 `USABLE_SLICE` 前，不要求所有实现细节均已证明；但任何可能推翻整体系统模型或核心用户路径的高影响未知项，必须满足以下之一：

- 已取得足以支持当前 Architecture Decision 的证据；
- 已定义可行的备选路径和切换条件；
- Maker 明确接受有界风险、验证预算与失败停止条件。

上述记录继续使用现有 `assumptions`、`plan`、`gates`、`risks`、`evidence` 与 `human_validation` 分区，不新增可行性 Markdown 状态文件，也不要求扩展 Shared Kernel 或权威状态 Schema。

### 7.5 Creation 中发现设计问题

Creation 中出现反例不是自动失败、固定进入 P6，也不是继续用局部补丁掩盖模型问题。`USABLE_SLICE`、`DELIVERY_HARDENING` 和 `TARGET_VALIDATION` 均可进入轻量 `MODEL_REVIEW` 子流程，复用既有 Correction、Evidence、Assumption 与 `return_stage` 机制：

1. 标记被反例推翻或显著削弱的 Assumption，并保存可复核 Evidence；
2. 暂停依赖该 Assumption 的受影响工作，不冻结无关工作；
3. 定位最早失效层级，评估受影响 Artifact、Gate、Plan、Baseline 与验证范围；
4. 形成纠正提案；涉及 Product Boundary、Architecture Decision、Host 支持范围或发布边界时请求 Maker 授权；
5. 完成获授权的 Context Mutation，更新受影响计划和验证条件；
6. 重放受影响验证，证据成立后通过 `return_stage` 恢复原工作流。

返回位置由问题性质决定：

- 仅为局部 Implementation Detail 时留在当前 Creation Phase；
- 执行顺序、切片或验证计划失效时返回 `EXECUTION_PLAN`；
- 系统边界、信任边界、交互模型或 Architecture Assumption 失效时返回 `DESKTOP_SYSTEM_MODEL`；
- 用户问题、核心结果、桌面载体理由或明确排除范围失效时，先请求 Maker 决策，再返回 `PRODUCT_BOUNDARY`；
- 仅缺少同一边界内的验证证据时留在 `TARGET_VALIDATION`。

`MODEL_REVIEW` 是纠正子流程，不是新的必经主阶段。下游 Design 必须定义触发条件、暂停范围、恢复条件和 Evidence 要求，但原则上可由现有 Workflow evaluator、`model_invalidated`、`model_updated` 与 `return_stage` 承载，不构成本轮 Kernel 或 Schema 扩展理由。

## 8. Maker Authority 边界

以下事项继续由 Maker 决定：

- 激活、停用或迁移 `desktop-product` Project Type；
- Product Boundary、核心用户结果与明确排除范围；
- 首个或新增 Host 支持范围；
- Architecture Decision；
- 自动更新、管理员权限、敏感凭据、外部代码执行等高风险产品政策；
- 高成本真实桌面环境验证和人工验证预算；
- 发布支持矩阵与残余风险接受。

Agent 可以在获批边界内决定 Implementation Detail、测试组织、内部命名和局部实现策略。Runtime 只验证结构、授权、Revision、Workflow 合法性与 Receipt，不替 Maker 或 Agent 完成创造性判断。

## 9. Shared Kernel、Registry 与状态影响

### 9.1 原样复用

本次提案原则上原样复用：

- Activation 与 Router 两步确认；
- Maker Prompt provenance；
- `prepare_change`、`commit_change` 与 `decline_change`；
- Registry 驱动的 Workflow evaluator；
- revisioned `state.json`；
- Receipt、哈希、回读和失败关闭；
- Hook 作用域与权威文件保护；
- Capability、Evidence、Assumption、Gate、Risk、Baseline 与人工验证预算；
- `inspect_project` 固定状态摘要。

### 9.2 本次不扩展

本次不新增：

- 多 `project_type_id`；
- 多 `child_skill_id`；
- Delivery Surface 权威数组；
- 跨项目关系 Schema；
- 项目组合或父子项目 Runtime；
- 新的权威状态文件；
- 浏览器扩展专用字段；
- 业务领域专用字段。

现有 `boundary`、`workflow`、`capabilities`、`decisions`、`assumptions`、`plan`、`gates`、`risks`、`baselines` 与 `human_validation` 分区足以承载首个桌面产品孵化流程。若下游设计发现必须新增机器强制语义，应登记 `DESIGN_GAP` 并返回本提案修订，不得在 Schema 或 Runtime 中隐式增加。

### 9.3 预计扩展点

在本提案获批且下游计划获批后，产品实现预计通过以下扩展点完成：

- Registry 中新增 Child Skill 与 Project Type；
- 新增 `desktop-product` Project Type Profile；
- 新增独立桌面 Workflow evaluator；
- 新增 `desktop-product-incubator` Skill；
- 经批准后新增首个 `windows-desktop` Host Profile；
- 增加对应 Workflow、Registry、Router、Kernel 集成和端到端验收。

具体文件范围由 Implementation Plan 冻结，本提案不直接授权修改这些文件。

## 10. Evidence 与验证边界

### 10.1 自动化测试

自动化测试可以证明：

- Registry 路由和 Workflow 合法转换；
- Kernel Authorization、Mutation 与 Receipt 保持有效；
- 领域规则未渗入 Shared Kernel；
- 纯逻辑、状态迁移、配置解析、路径限制和失败恢复规则；
- 打包内容、安装清单和可重复回归机制。

自动化测试不能单独证明桌面产品在真实操作系统、权限、升级、杀毒软件或用户会话中的完整语义成立。

### 10.2 桌面自动化与真实环境验证

桌面 UI 自动化可以证明被测窗口、控件和流程在指定环境中可重复执行，但不能替代真实安装、权限、签名、系统升级和外部依赖行为。

真实环境验证至少绑定：

- 操作系统版本与架构；
- 产品构建与安装包版本；
- 安装模式与权限边界；
- 关键外部依赖版本；
- 场景、结果、副作用和 Evidence 引用。

一次真实环境成功最高证明该场景在该环境 Observed Working，不自动形成跨版本或跨机器支持声明。

## 11. 桌面产品安全边界

下游 Design 至少必须处理：

- 外部输入、网络响应、本地导入内容和文件名均视为不可信；
- 文件系统写入必须限制目标根目录并防止路径穿越、链接绕过和意外覆盖；
- 安装、升级、卸载和数据迁移必须有明确前后状态、失败语义与恢复路径；
- 管理员权限、开机启动、后台服务、防火墙规则和系统范围写入必须最小化并由明确产品政策支持；
- 自动更新必须验证来源、完整性、版本关系并支持失败回退；
- 凭据、令牌、本地隐私数据和日志必须按最小权限与最小保留处理；
- 下载、解包或导入内容不得因来源属于业务流程而自动获得执行权限；
- 安全扫描或签名存在不等于内容行为安全；
- 外部服务和未来其他产品形态只能通过明确接口进入当前桌面产品边界。

具体算法、技术选型和平台 API 属于 Design 或 Implementation Detail，不在本提案中冻结。

## 12. 影响分析

| Layer | 预计影响 | 本提案后的动作 |
| --- | --- | --- |
| Architecture | 新增按产品形态划分的 `desktop-product`；明确 Project Incubator 不拥有产品组合决策 | Maker 批准后更新 Architecture Decisions 与 Document Architecture |
| Design | 需要定义 P0–P6 经验到六个 Desktop Phase 的映射、Domain Model、Gate、Evidence、`FEASIBILITY_PROBE`、`MODEL_REVIEW` 与 Host Profile 接口 | 新增或更新活动 Design 文档 |
| Contract | 需要定义桌面 Workflow evaluator 输入输出、阶段转换和 Host Profile 收紧规则 | 下游 Contract 更新 |
| Runtime Specification | 原则上复用 Registry evaluator、授权、Receipt 与状态；需说明无 Kernel 新语义 | 下游 Runtime Spec 记录加载与失败语义 |
| Implementation Plan | 需要冻结 Registry、Profile、Skill、Workflow、测试与候选打包范围 | 在 Architecture、Design、Contract、Runtime 均批准后编写 |
| Implementation Code | 当前禁止修改 | 仅在 Implementation 与 Acceptance Plan 获批后开始 |
| Existing `mod` Type | 不修改、不迁移、不重新解释 | 必须保持 `mod-incubator` 与 `sims-4` Profile 行为和测试通过 |
| Future Browser Extension Type | 明确保留为下一独立设计任务 | 当前不新增其 Skill、Profile、Schema 或 Workflow |

## 13. 兼容与迁移策略

- 现有 `mod` 项目与已激活项目不自动迁移；
- `mod-incubator`、`sims-4` Host Profile 及其历史验收不得删除、改写或并入桌面流程；
- Shared Kernel 的授权、状态、Receipt、Hook、Evidence 与摘要行为保持兼容；
- Router 增加候选类型后仍只能提议，不能自动为新项目确认类型；
- 已激活项目改变 Project Type 仍需 Maker Authorization；
- Candidate Package 必须继续通过现有 Plugin 与 Legacy 回归矩阵；
- 浏览器扩展的后续设计不得反向把浏览器规则写入 `desktop-product`。

## 14. 备选方案与取舍

### 14.1 `desktop-product`：推荐

按产品形态沉淀桌面生命周期、交付和验证规则，跨业务领域复用；Host 差异由 Host Profile 具体化。

### 14.2 `desktop-companion`：拒绝

该名称编码了桌面产品与其他产品形态之间的组合关系，复用范围较窄，并诱使 Child Incubator 越界管理浏览器扩展或跨产品协作。

### 14.3 `software-product`：拒绝

该类型覆盖桌面、Web、移动、服务端和扩展等不同生命周期，无法提供足够具体的阶段、风险和验证指导，会重新形成大而全流程。

### 14.4 当前扩展多 Project Type Kernel：拒绝

本次目标只需要新增独立桌面产品孵化能力。多类型组合、跨项目关系和项目群治理不属于当前问题，没有证据支持修改 Kernel。

## 15. 非目标

本提案不：

- 决定首个 Managed Project 的正式名称或业务品牌；
- 把某类在线机会、Mod 或其他业务对象固化为桌面产品类型；
- 设计浏览器扩展 Project Type；
- 决定桌面产品与浏览器扩展如何串联；
- 设计覆盖所有软件产品的通用大流程；
- 增加大量 Markdown 运行态文件；
- 修改 Shared Kernel 权限、状态或 Receipt 语义；
- 授权任何产品实现。

## 16. 下游规格验收标准

本提案获批后的下游规格必须能够证明：

- `desktop-product` 的规则不依赖具体业务领域；
- 桌面产品与 Windows Host Profile 的职责没有混淆；
- 浏览器扩展规则未进入本轮 Child Skill、Workflow 或 Schema；
- P0–P6 的通用治理经验具有明确复用映射，Desktop Phase 的合并、拆分和返回路径均由桌面风险与证据边界解释；
- 可行性调研作为阶段内探针服务于决策，进入 Creation 的证据门槛、备选路径和 Maker 风险接受边界清晰；
- Creation 或 Validation 中的模型反例可以暂停受影响工作、返回最早失效阶段、完成纠正并重放验证；
- Maker Authority、Agent 创造性职责与 Runtime 机械校验边界清晰；
- 自动化、桌面自动化和真实环境 Evidence 的结论上限清晰；
- 安装、升级、卸载、数据迁移、权限和回滚风险具有对应 Gate；
- 新类型可通过 Registry 与独立 Workflow 扩展，Shared Kernel 不出现桌面领域分支；
- 现有 `mod`、`sims-4` 与完整回归矩阵保持不变。

## 17. 待 Maker 审批

Maker 需要确认：

1. `desktop-product` 是按产品形态复用的第二个 Project Type；
2. `desktop-product-incubator` 只负责桌面产品孵化，不负责产品组合关系；
3. 本轮采用“选择性复用”阶段模型：保留 P0–P6 的通用职责与治理经验，按桌面产品风险采用六个 Desktop Phase，并由 `TARGET_VALIDATION` 返回最早受影响阶段；
4. 可行性调研采用阶段内 `FEASIBILITY_PROBE`，主要归属 `DESKTOP_SYSTEM_MODEL`；Creation 中的模型反例进入轻量 `MODEL_REVIEW`，返回最早失效阶段后再恢复；
5. Windows 作为首个 Host Profile 方向，但不构成所有未来桌面产品的唯一 Host；
6. 本次原则上不扩展 Shared Kernel 或权威状态 Schema；
7. 浏览器扩展保留为下一独立 Project Type 设计任务，本轮不实现；
8. 批准后只授权继续更新 Architecture Decisions 与 Design Layer，不授权产品实现。
