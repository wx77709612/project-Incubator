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

## 7. 推荐阶段模型

`desktop-product` 不复刻 Legacy P0–P6，也不照搬 Mod M0–M5。下游 Workflow Design 应基于以下五个语义阶段细化合法转换、Gate 与失败语义：

| 阶段 | 目的 | 最小可观察出口 |
| --- | --- | --- |
| `PRODUCT_DEFINITION` | 明确桌面产品的用户、核心结果、支持边界、排除边界与首个 Host | Maker 已确认 Product Boundary；当前 Host 与不支持范围明确 |
| `DESKTOP_ARCHITECTURE` | 建立进程、UI、本地数据、权限、外部集成和失败恢复的最小架构模型 | 关键组件与信任边界可追踪；高风险 Assumption 和验证路径已记录 |
| `USABLE_SLICE` | 完成一个代表性、用户可操作、可观察的桌面产品完整路径 | 选定用户旅程在受控桌面环境中可执行；失败位置和证据可归因 |
| `DELIVERY_HARDENING` | 闭合安装、升级、卸载、迁移、权限、恢复、打包和回归风险 | 交付物内容可验证；失败可恢复；关键本地副作用有边界和回归证据 |
| `RELEASE_READINESS` | 在目标桌面环境确认支持矩阵、发布边界和已知限制 | 目标环境证据、发布产物、升级/回滚路径、限制与残余风险可审阅 |

本提案不预先规定阶段编号，也不要求阶段名称带数字。详细 Completion Condition、允许转换、Correction 行为和 Gate 由 Design Layer 定义。

Evidence 推翻 Runtime Assumption 时，默认在当前阶段内收敛影响、更新模型并重放受影响验证。只有 Product Boundary、Architecture Decision、Host 支持范围或发布边界发生变化时，才必须形成新的 Maker 授权请求。

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
| Design | 需要定义桌面产品 Domain Model、五阶段 Workflow、Gate、Evidence 与 Host Profile 接口 | 新增或更新活动 Design 文档 |
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
- 五阶段模型具有可观察出口和合法转换；
- Maker Authority、Agent 创造性职责与 Runtime 机械校验边界清晰；
- 自动化、桌面自动化和真实环境 Evidence 的结论上限清晰；
- 安装、升级、卸载、数据迁移、权限和回滚风险具有对应 Gate；
- 新类型可通过 Registry 与独立 Workflow 扩展，Shared Kernel 不出现桌面领域分支；
- 现有 `mod`、`sims-4` 与完整回归矩阵保持不变。

## 17. 待 Maker 审批

Maker 需要确认：

1. `desktop-product` 是按产品形态复用的第二个 Project Type；
2. `desktop-product-incubator` 只负责桌面产品孵化，不负责产品组合关系；
3. 本轮采用五个语义阶段作为下游 Workflow Design 基线；
4. Windows 作为首个 Host Profile 方向，但不构成所有未来桌面产品的唯一 Host；
5. 本次原则上不扩展 Shared Kernel 或权威状态 Schema；
6. 浏览器扩展保留为下一独立 Project Type 设计任务，本轮不实现；
7. 批准后只授权继续更新 Architecture Decisions 与 Design Layer，不授权产品实现。
