# Project Incubator Architecture Decisions


# 1. 文档定位


## 1.1 Purpose


本文档记录 Project Incubator 当前有效的核心架构决策及其版本关系。


本文档的作用：

- 保留 V1.0 已发布架构决策；
- 登记后续版本新增、部分替代、替代或撤销的决策；
- 明确决策的 Authority、Scope、Impact 与 Status；
- 作为 `PROJECT_INCUBATOR_DESIGN.md` 及下游规格的架构依据。


---

## 1.2 Scope


本文档只处理：

- 架构边界；
- 核心模型；
- 系统职责；
- 长期设计方向。


本文档不处理：

- 具体代码实现；
- Task 执行顺序；
- Codex 操作指令；
- Template 字段设计细节。


---

# 2. Decision Status


当前状态：

V1.0 Architecture Baseline Frozen / V1.1 Core Evolution Active / V1.2 Plugin Web Product Extension Active

V1.0 冻结范围：

- Runtime Architecture；
- Context Model；
- Phase Model；
- Gate Boundary；
- Project Type Runtime Architecture。

V1.1 增量来源：

`SPECS/ARCHITECTURE/ARCHITECTURE_CHANGE_PROPOSAL.md`

提案状态：`APPROVED`（2026-09-23）。

V1.2 Plugin Web Product 增量来源：

`SPECS/ARCHITECTURE/WEB_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md`

提案状态：`APPROVED`（2026-10-13）。

V1.0 Decision 001–006 保留其历史语义。V1.1 通过新增 Decision 扩展或明确边界，不隐式改写历史决策。

---

# 3. Architecture Decision List


# Decision 001: V1 Design 与 Runtime 的关系


## Decision Question


Project Incubator V1 是否包含 Runtime 概念？


需要确认：

- V1 是否只是一个 Skill；
- 是否需要 Runtime Interface；
- Runtime 能力属于 V1 还是未来版本。


---

## Decision


Project Incubator V1 采用 Full Runtime Engine 架构。


Project Incubator V1 不仅包含 Skill Layer，还包含完整 Runtime 执行能力。


Runtime Engine 作为 Project Incubator 的核心执行层存在。


---

## Runtime Responsibilities


Runtime Engine 负责：

- 提供统一执行框架；
- 协调 Runtime Component；
- 管理 Runtime 生命周期；
- 控制 Component 调用关系。


具体领域能力由对应 Runtime Component 负责。


---

## Runtime Components


V1 Runtime 包含：


### Runtime Core

负责：

- Runtime 生命周期；
- 执行上下文；
- Component 协调。


Runtime Core 负责协调 Runtime Component 执行流程。

Runtime Core 不直接管理具体领域状态。


### State Engine

负责：

- PROJECT_STATE 状态管理；
- 状态迁移；
- 状态查询；
- 状态持久化。


State Engine 不负责：

- PROJECT_PROFILE 修改；
- PROJECT_PLAN 内容生成。

### Phase Engine

负责：

- 当前 Phase 判断；
- Phase Transition；
- 生命周期管理。


### Gate Engine

负责：

- Gate Evaluation；
- Permission Check；
- Risk Control；
- Action Constraint。


### Execution Engine

负责：

- Task 调度；
- Execution Context；
- Task Validation。


### Artifact Engine

负责：

- Artifact 创建；
- Artifact 更新；
- Artifact 验证。


### Validation Engine

负责：

- 自动检查；
- 规则验证；
- 完成条件判断。


---

## Runtime Component Interaction Model


Project Incubator Runtime 采用 Runtime Core Orchestration Model。


Runtime Core 是所有 Runtime Component 的唯一协调入口。


Runtime Component 之间不直接调用。


所有：

- 状态变化；
- Phase 转换；
- Gate 判断；
- Task 执行；
- Artifact 更新；
- Validation 流程；

必须经过 Runtime Core 协调。



Runtime Component 结构：


Runtime Core

↓

- State Engine
- Phase Engine
- Execution Engine
- Gate Engine
- Artifact Engine
- Validation Engine



---

## Runtime Interaction Rule


Runtime Component 不允许：

- 绕过 Runtime Core 直接修改其他 Component 状态；
- 自主触发跨领域流程；
- 自主执行状态迁移。


所有跨 Component 操作必须经过 Runtime Core。

---

## Decision Impact


该决策影响：


- PROJECT_INCUBATOR_DESIGN.md；
- Skill Architecture；
- Runtime Architecture；
- State Model；
- Phase Model；
- Gate Model；
- Execution Model；
- Validation System。


---

## Status

Accepted

# Decision 002: Context Model 边界


## Decision


Project Incubator V1 采用 Project Context Layer 作为项目上下文模型。


Project Context Layer 不属于 Runtime Engine。


Runtime Engine 负责读取、验证、更新 Project Context Layer。


Project Context Layer 负责保存项目运行过程中需要持久化的信息。



---

## Project Context Layer Structure


Project Context Layer 分为：

- Core Context
- Optional Context Extension


---

## Core Context


以下文件属于所有 Project Incubator 生成项目的核心上下文模型。


### PROJECT_PROFILE.md


定位：

Project Identity Context


职责：

记录项目基础定义。


包括：

- 项目目标；
- 项目范围；
- 项目类型；
- 成功标准；
- 长期约束；
- Maker 确认的核心信息。


生命周期：

- 项目初始化阶段创建；
- 目标确认阶段后形成稳定版本；
- 后续允许修改；
- 修改需要明确确认。


修改频率：

低。


修改权限：

Maker 主导。


---

### PROJECT_STATE.md


定位：

Current Project State


职责：

记录项目当前实际状态。


包括：

- 当前 Phase；
- 当前 Gate 状态；
- 当前执行状态；
- 已完成事项；
- 当前阻塞事项；
- 最近状态变化。


生命周期：

持续更新。


修改频率：

高。


修改权限：

State Engine 根据确认后的 State Change Proposal 更新。


流程：

Execution Result

↓

State Change Proposal

↓

Agent Review

↓

State Engine Update

↓

PROJECT_STATE.md Write Back


约束：

PROJECT_STATE.md 只记录当前事实状态。

不记录：

- 未来计划；
- 下一阶段任务安排；
- 未执行方案。


---

### PROJECT_PLAN.md


定位：

Execution Plan


职责：

记录项目未来执行计划。


包括：

- 当前 Phase 目标；
- 当前阶段任务；
- 执行顺序；
- 依赖关系；
- 预期产出。


生命周期：

随着 Phase 推进更新。


修改频率：

中高。


修改权限：

PROJECT_PLAN 采用：

Agent Draft + Runtime Tracking Model。


Agent 负责：

- 生成计划；
- 调整计划。


Runtime 负责：

- 跟踪执行状态；
- 记录计划变化。


约束：

PROJECT_PLAN.md 描述：

“计划发生什么”。

PROJECT_STATE.md 描述：

“实际发生了什么”。

两者必须保持分离。


---

### PROJECT_DECISIONS.md


定位：

Confirmed Maker Decision Record


职责：

记录已经由 Maker 确认的重要决策。


包括：

- 架构选择；
- 技术方向选择；
- 项目范围限制；
- 长期约束；
- 关键取舍。


生命周期：

长期保存。


修改频率：

低。


触发规则：

仅在以下情况生成：

- 存在多个合理方案；
- 方案选择会影响未来方向；
- Maker 明确完成选择。


记录内容：

包括：

- Decision；
- Selected Option；
- Reason；
- Impact。


禁止记录：

- 普通讨论；
- 临时想法；
- Agent 自主判断；
- 未确认方案。


PROJECT_DECISIONS.md 不作为 Memory 使用。


---

## Optional Context Extension


以下文件根据项目类型和 Runtime 能力决定是否启用。


---

### PROJECT_ARTIFACTS.md


定位：

Artifact Lifecycle Registry


职责：

管理项目 Artifact 生命周期。


包括：

- Artifact 身份；
- Artifact 类型；
- 所属 Phase；
- 当前状态；
- 创建来源；
- 依赖关系；
- 验证状态。


PROJECT_ARTIFACTS.md 不属于所有项目的默认 Context。


是否启用：

由 Runtime Capability 和 Project Type 决定。


---

## PROJECT_PROFILE Modification Authority


PROJECT_PROFILE.md 属于长期项目身份信息。


任何 PROJECT_PROFILE.md 修改必须经过 Maker Authorization。


流程：

Change Proposal

↓

Agent Review

↓

Maker Approval

↓

Write Back



Agent 可以：

- 提出修改建议；
- 分析影响。


Agent 不可以：

- 自主修改；
- 自动写回。



Runtime 不直接修改 PROJECT_PROFILE.md。

---

## PROJECT_PLAN Generation Authority


PROJECT_PLAN.md 属于项目执行规划信息。


PROJECT_PLAN 的生成和修改采用：

Agent Draft + Runtime Tracking Model。


流程：


Phase Change

↓

Agent Generate Plan Proposal

↓

必要时 Maker Approval

↓

Runtime Track Execution



Runtime 负责：

- 跟踪计划执行状态；
- 记录计划变化。


Agent 负责：

- 生成计划；
- 调整计划内容。


重大阶段计划调整需要 Maker 确认。

---
## PROJECT_PLAN 与 PROJECT_TASKS Relationship


PROJECT_PLAN.md 与 PROJECT_TASKS.md 属于不同粒度的信息。


PROJECT_PLAN.md：

负责：

- 阶段目标；
- 执行方向；
- 阶段产出；
- 流程规划。


PROJECT_TASKS.md：

负责：

- 具体执行任务；
- Task 状态；
- Task 依赖；
- Task 完成情况。


关系：

PROJECT_PLAN

↓

Task Breakdown

↓

PROJECT_TASKS


PROJECT_TASKS 是 PROJECT_PLAN 的执行细化。

---

## Execution Layer Boundary


TASKS 不属于 Project Context Layer。


TASKS 属于 Execution Layer。


职责：

管理：

- 当前执行任务；
- Task 生命周期；
- Task 依赖；
- Task Validation。


TASK Schema 不在当前 Decision 中冻结。


不同 Project Type 可以拥有不同 Task 模型。


---

## Task Ownership


TASK 属于 Execution Layer。


Task 信息需要暴露给用户。


Project Incubator V1 采用：

PROJECT_TASKS.md Model。



PROJECT_TASKS.md 属于项目级执行信息。


职责：

记录：

- Task 列表；
- Task 状态；
- Task 依赖；
- Task 负责人；
- Task Validation Result。



PROJECT_TASKS.md 不属于 Core Context。


它属于：

Project Execution Layer。



---

## Task Update Authority


Task 状态由 Runtime 管理。


流程：


Execution Result

↓

Task Update Proposal

↓

Agent Review

↓

PROJECT_TASKS.md Update



用户可以查看：

- 当前任务数量；
- 已完成任务；
- 未完成任务；
- 当前阻塞任务。

---

## Rejected Context Component


### PROJECT_MEMORY.md


不创建 PROJECT_MEMORY.md。


原因：

PROJECT_MEMORY.md 与以下内容职责重叠：

- PROJECT_DECISIONS.md；
- Agent Memory。


Project Incubator V1 不建立不可控长期 Memory。


---

## Decision Impact


该决策影响：

- PROJECT_INCUBATOR_DESIGN.md；
- Context Model；
- Runtime Architecture；
- State Engine；
- Execution Engine；
- Template System。


---

## Status


Accepted

# Decision 003: Reference 与 Script 权限边界


## Decision


Project Incubator V1 采用分层职责模型处理 Reference、Structured Gate、Script、Agent 和 Maker 之间的权限边界。


Gate System 的架构边界由 Runtime Architecture 定义。

具体 Gate Rule 根据 Runtime、Project Type 和 Workflow Requirement 分层定义。

本 Decision 不重新定义 Gate。


本 Decision 只定义：

- Reference 的职责；
- Structured Gate 的职责；
- Script 的职责；
- Agent 的职责；
- Maker 的最终决策权限。



---

## Reference Boundary


### Reference 定位


Reference 属于 Explanation Layer。


Reference 负责：

- 解释规则；
- 提供判断依据；
- 描述使用场景；
- 提供轻量流程判断。


---

### Reference 允许内容


Reference 可以包含：

- 非确定性的流程说明；
- 需要 Agent 理解的判断依据；
- 无法通过 Script 自动确认的语义规则。


例如：

- 什么情况下一个变化可能属于范围扩大；
- 什么情况下一个修改可能影响长期架构；
- 什么情况下需要请求 Maker 判断。


---

### Reference 禁止内容


Reference 不负责：

- 执行 Gate 判定；
- 作为关键 Gate 的唯一判断来源；
- 定义确定性的状态迁移规则；
- 自动触发写回动作。


确定性规则必须由 Structured Gate 或 Script 承载。


---

## Structured Gate Boundary


### Structured Gate 定位


Structured Gate 是 Gate System 的权威定义层。


负责定义：

- Gate ID；
- 触发条件；
- 输入字段；
- 输出枚举；
- 阻断规则；
- 安全替代动作；
- 验证场景。


Structured Gate 不属于 Reference。


---

## Script Boundary


### Script 定位


Script 属于 Deterministic Execution Layer。


Script 负责执行可以被确定性验证的检查。


包括：

- 文件检查；
- 字段检查；
- 格式检查；
- Git 状态检查；
- 状态一致性检查；
- Artifact 状态检查。



---

### Script 输出规则


Script 输出：

- Validation Result；
- State Change Proposal；
- Artifact Change Proposal。


Script 不直接决定语义结果。



---

### Script 状态修改权限


Script 不直接修改核心项目上下文。


Script 可以生成状态变更建议。


最终写回必须经过 Agent 确认。


---

### Script 可影响范围


Script 可以参与：

- PROJECT_STATE.md 更新建议；
- PROJECT_PLAN.md 更新建议；
- PROJECT_ARTIFACTS.md 更新建议。


---

### Script 不可直接修改范围


Script 不可直接修改：

- PROJECT_PROFILE.md；
- PROJECT_DECISIONS.md。


原因：

这些文件包含 Maker 确认的长期方向、范围和决策。


---

## Agent Boundary


### Agent 定位


Agent 属于 Semantic Evaluation Layer。


Agent 负责：

- 理解上下文；
- 判断非确定性问题；
- 评估 Script 输出；
- 判断是否接受状态变更建议；
- 触发必要写回流程。


---

### Agent 不拥有最终架构决策权


Agent 不可以：

- 自主改变项目方向；
- 自主修改长期规则；
- 自主写入 Architecture Decision；
- 将临时纠偏沉淀为长期规则。


---

## Maker Boundary


### Maker 定位


Maker 是最终决策权拥有者。


Maker 负责确认：

- 架构方向；
- 项目范围；
- 长期约束；
- 高风险写回；
- 重大状态变化。


---

## Gate Execution Model


Gate 判断采用混合模式。


流程：

Reference

↓

Structured Gate Definition

↓

Script Deterministic Check

↓

Agent Semantic Evaluation

↓

Maker Authorization（必要时）

↓

Write Back



---

## Writeback Authority


Project Incubator V1 采用 Runtime Writeback Engine Model。


任何文件写回必须经过 Writeback Engine。


流程：


Change Proposal

↓

Gate Evaluation

↓

Agent Review

↓

Runtime Writeback Engine

↓

File Update



Agent 不直接修改核心项目文件。


Script 不直接修改核心项目文件。



---

## Writeback Permission


Writeback Engine 根据：

- Authorization Result；
- File Authority；
- Gate Result；

决定是否执行写回。

---

## Gate Responsibility Rule


Gate 不由单一角色完成。


职责划分：


Script：

负责确定性验证。


Agent：

负责语义判断。


Maker：

负责最终方向和高风险授权。



---

## Gate Registry Model


Project Incubator V1 采用分层 Gate Registry。


结构：


gates/

- common/

- project_incubator/

- project_type/



---

## Common Gates


Common Gates 属于 Runtime 通用能力。


例如：

- Writeback Gate；
- Authority Gate；
- Context Integrity Gate。



---

## Project Incubator Gates


Project Incubator Gates 用于当前 Skill 特定约束。


例如：

- Skill Structure Gate；
- Skill Validation Gate。



---

## Project Type Gates


Project Type Gates 属于具体项目类型扩展。


例如：

- APP Build Gate；
- Content Compliance Gate。



Gate 不应全部存放于 Reference。

---

## Decision Impact


该决策影响：

- Runtime Architecture；
- Gate Execution Model；
- Script System；
- Reference Structure；
- Writeback System；
- Validation System。


---

## Status


Accepted

# Decision 004: Phase Model


## Decision


Project Incubator V1 采用 Simplified Phase Model。


Phase Model 用于描述项目生命周期阶段。


Phase 不绑定具体项目类型。


同一套 Phase Model 应适用于：

- Skill 开发；
- APP 开发；
- 内容创作；
- 其他类型项目孵化。


Phase 只负责描述：

- 当前项目生命周期位置；
- 当前阶段目标；
- 阶段产物方向。


Phase 不负责：

- Gate 判断；
- 权限控制；
- 自动批准；
- 风险判断。



---

## Phase Definition


### Intent Discovery


目标：

理解 Maker Intent，探索项目机会，并确认初始项目方向。


职责：

- 识别需求；
- 探索可能方案；
- 判断项目价值。


主要产出：

初步项目方向。


---

### Project Definition


目标：

明确项目定义。


职责：

- 明确项目目标；
- 明确项目范围；
- 明确项目约束；
- 明确成功标准。


主要产出：

PROJECT_PROFILE.md。


---

### Solution Design


目标：

形成项目解决方案设计。


职责：

- 架构设计；
- 内容设计；
- 技术方案设计；
- 执行方案设计。


主要产出：

设计文档和设计决策。


---

### Solution Design 与 Execution Planning Relationship


Solution Design Phase 负责：

- 定义解决方案；
- 确认系统边界；
- 形成设计决策；
- 明确实现方向。


Execution Planning Phase 基于 Solution Design 输出：

- 制定执行路线；
- 拆分执行任务；
- 定义阶段里程碑；
- 规划 Artifact 生成。


Execution Planning 不负责重新定义项目架构。

---

### Execution Planning


目标：

根据 Solution Design 输出制定项目执行路线。


职责：

- 拆分执行任务；
- 定义执行顺序；
- 定义里程碑；
- 规划 Artifact。


主要产出：

PROJECT_PLAN.md。


Execution Planning 不负责：

- 修改项目架构；
- 修改解决方案设计。

---

### Creation


目标：

生成项目产物。


职责：

- 实现；
- 编写；
- 创建；
- 构建。


主要产出：

项目 Artifact。


---

### Validation


目标：

验证项目质量。


职责：

- 正确性验证；
- 完整性验证；
- 规范验证；
- 风险检查。


主要产出：

Validation Result。


---

### Iteration


目标：

根据反馈持续优化。


职责：

- 分析问题；
- 调整方案；
- 优化产物。


主要产出：

下一轮改进方向。



---

## Phase Transition Model


Project Incubator V1 不采用固定线性 Phase 流程。


Phase 支持：

- 前进；
- 回退；
- 循环。


典型流程：


Intent Discovery

↓

Project Definition

↓

Solution Design

↓

Execution Planning

↓

Creation

↓

Validation

↓

Iteration


Iteration 后可以根据实际情况返回：

- Design；
- Creation；
- Validation。



---

## Phase Transition Rules


Phase Transition 由 Runtime 根据以下信息决定：

- PROJECT_STATE.md；
- Validation Result；
- Runtime Evaluation；
- Agent Semantic Evaluation。

Phase 不允许：

- 根据固定顺序自动推进；
- 根据时间自动推进；
- 绕过必要判断自动切换。



---

## Legacy Phase Mapping


Project Incubator V1 不保留 Legacy Phase Mapping。


不引入：

- Legacy Phase；
- Phase 0-9；
- 旧 Runtime Phase 映射。


原因：

V1 基于重新设计的架构生成，不继承旧流程模型。



---

## Phase 与 Gate Relationship


Phase 与 Gate 解耦。


Phase 负责：

- 生命周期位置；
- 阶段目标；
- 阶段产物。


Gate 负责：

- 权限控制；
- 风险控制；
- 状态变化验证；
- 写回约束。


Gate 不绑定固定 Phase。


Gate 的触发来源包括：

- Maker Request；
- Agent Action Proposal；
- Artifact Change Proposal；
- State Change Proposal；
- Architecture Change Proposal。


Runtime 根据：

- 当前 Phase；
- 当前 State；
- Change Type；
- Risk Level；

决定是否执行对应 Gate。


同一个 Gate 可以被多个 Phase 使用。


Phase 提供上下文。

Gate 提供约束。

## Phase and Task Relationship


Phase 负责：

- 生命周期管理；
- 阶段目标；
- 阶段产物方向。


Task 负责：

- 具体执行动作；
- 执行顺序；
- 执行状态。



Phase 不直接定义所有 Task。


Task 由 Project Type Runtime 根据 Phase 生成。



关系：


Phase

↓

Project Type Runtime

↓

Task Definition

↓

Task Execution



不同 Project Type 可以在相同 Phase 下拥有不同 Task。

---

## Decision Impact


该决策影响：


- Runtime Phase Engine；
- PROJECT_STATE.md；
- PROJECT_PLAN.md；
- Gate Trigger System；
- Task Execution Model；
- Validation System。



---

## Status


Accepted

# Decision 005: Architecture Change Control

## Decision


已 Accepted 的 Architecture Decision 不允许被下游设计文档隐式修改。


涉及以下内容的变化：

- Phase Model；
- Runtime Boundary；
- Context Ownership；
- Component Responsibility；
- Gate Model；

必须先创建 Architecture Change Proposal。


流程：

Change Proposal

↓

Impact Analysis

↓

Architecture Decision Update

↓

Downstream Document Update


Architecture Change Control 不禁止架构演进。

它保证架构变化具有明确来源和影响范围。

# Decision 006: Project Type Adaptive Depth


## Decision


Project Incubator V1 采用 Project Type Adaptive Depth Architecture。


Project Incubator Runtime 支持不同 Project Type Runtime。


不同 Project Type 可以拥有不同的：

- Artifact；
- Template；
- Validation；
- Capability。


Project Type Runtime 不修改 Core Runtime。


Core Runtime 保持统一。


---

## Core Runtime Boundary


所有 Project Type 共享以下 Core Runtime 能力：

- Phase Engine；
- Context Model；
- Gate System；
- Execution Model；
- Validation Framework。


Core Runtime 不包含具体项目类型逻辑。


---

## Project Type Runtime Architecture


Project Type Runtime 采用配置驱动架构。


Runtime 根据 Project Type 加载对应的 Project Type Profile。


结构：

Project Incubator Runtime

↓

Project Type Runtime Layer

↓

Project Type Profile



Project Type Profile 负责定义：

- 项目类型特征；
- Artifact 定义；
- Template 定义；
- Validation 定义；
- Capability 配置。


---

## V1 Project Type Implementation Scope


Project Incubator V1 完整实现：

Skill Project Runtime。


原因：

Project Incubator 当前自身属于 Skill 项目。


Skill Project Runtime 必须支持完整孵化流程。


包括：

- Skill Architecture Design；
- Skill Structure Generation；
- Reference Management；
- Template Management；
- Script Integration；
- Runtime Validation。



---



## Skill Project Runtime Scope

Project Incubator V1 完整实现 Skill Project Runtime。

Skill Project Runtime 支持完整 Skill 生命周期。

包括：

- Skill Architecture Design；
- Skill Structure Generation；
- SKILL.md Generation；
- Reference Management；
- Template Management；
- Script Integration；
- Validation System；
- Testing；
- Packaging。

Skill Project Runtime 是 V1 唯一完整实现的 Project Type Runtime。

---

## Future Project Type Support


以下 Project Type 在 V1 架构中保留扩展能力：

- Agent Workflow Project；
- APP Project；
- Video Content Project。


这些 Project Type 在 V1 中仅保留扩展入口。


它们通过未来真实项目孵化过程逐步沉淀。

---


## Future Project Type Skeleton


未来 Project Type 采用扩展机制。


未完整实现的 Project Type 仅保留 Skeleton。


Skeleton 包含：


- Project Type ID；
- Profile Interface；
- Extension Location。



Skeleton 不包含：

- 完整 Runtime Logic；
- Artifact Schema；
- Validation Rule；
- Capability Implementation。



未来通过真实项目孵化过程逐步沉淀。

---

## Generic Project Runtime


对于当前未定义的 Project Type，Runtime 提供 Generic Project Runtime。


Generic Project Runtime 用于：

- 支持未知项目类型启动；
- 提供通用孵化流程；
- 收集未来 Project Type Runtime 需求。


Generic Project Runtime 使用：

- Common Phase Model；
- Common Context Model；
- Common Gate System；
- Basic Validation。

Generic Project Runtime 用于未定义 Project Type 的运行支持。

Future Project Type Skeleton 用于未来正式 Project Type Runtime 的扩展入口。

二者职责不同。

---

## Project Type Extension Model


未来新增 Project Type Runtime 时，不修改 Core Runtime。


新增内容包括：

- Project Type Profile；
- Artifact Definition；
- Template Definition；
- Validation Definition；
- Capability Definition。


新增 Project Type 通过真实项目使用过程沉淀。


---

## Project Type Evolution Model


Project Type Runtime 采用反馈驱动演进。


流程：

Real Project Usage

↓

Problem Discovery

↓

Capability Extraction

↓

Project Type Runtime Update



真实项目中的新需求，需要经过沉淀后进入 Project Incubator。


---

## User Defined Project Type


Project Incubator 支持用户自定义 Project Type。


用户自定义 Project Type 默认使用 Generic Project Runtime。


当某类项目经过多次实践并形成稳定需求后，可以沉淀为正式 Project Type Runtime。


---

## Decision Boundary


Project Incubator V1 不定义：

- 所有未来 Project Type；
- 所有项目类型完整 Runtime；
- 所有项目类型 Task 流程。


Project Incubator V1 只定义：

- Project Type Runtime 架构；
- Skill Project Runtime 完整实现；
- Generic Project Runtime 兜底能力；
- Future Extension Mechanism。



---

## Decision Impact


该决策影响：

- Runtime Architecture；
- Project Type Loading System；
- Template System；
- Validation System；
- Capability Extension System。


---

## Status


Accepted

---


# Decision 007: Capability Claim 与 Evidence Maturity

## Decision

Project Incubator Core 必须以 Capability Claim 表达当前实际支持边界，并采用 E0–E5 Evidence Maturity 约束结论强度。

Evidence Level 绑定具体 Capability Claim 与适用 Scope，不作为整个项目的单一全局等级。

Artifact 完成、API 存在或局部自动化成功，不自动证明完整目标环境能力成立。Confidence 必须允许随反证降低。

## Reason

V1.0 主要验证 Artifact 和流程状态，无法阻止文档证据、局部调用或一次成功被表述为稳定产品能力。Capability Claim 与 Evidence Maturity 为能力声明建立统一边界，同时不强制所有项目使用不透明能力扩展。

## Boundary

Core 定义：

- Capability Claim 的最低语义；
- E0–E5 的通用等级；
- Evidence Level 与结论强度的约束；
- Confidence 可升可降；
- 未覆盖范围必须进入 Excluded Boundary 或 Known Limitations。

Core 不定义所有领域的证据格式、目标环境步骤或代表性场景枚举。

## Impact

- Evidence Model Design；
- Context Model Design；
- Gate Design；
- Context Access Contract；
- Gate Contract；
- Runtime Specification；
- Implementation Plan Template。

## Status

ACTIVE — V1.1

---

# Decision 008: Decision、Assumption 与历史治理分离

## Decision

Project Incubator 必须区分 Product Decision、Architecture Decision、Runtime Assumption、Implementation Detail、Observation 与 Hypothesis。

Runtime Assumption 可以被 Evidence 支持、降级或判定失效。Assumption 失效不等于未经授权修改 Product Decision，但由此产生的产品或架构变化仍须取得对应 Authority 的确认。

Decision 历史采用：

- Active Decision View；
- Bounded Changelog；
- Archived Decision History；
- Stable Decision ID。

不采用无限增长的单文件 append-only 策略。

Decision Status 支持：

- `ACTIVE`；
- `PARTIALLY_SUPERSEDED`；
- `SUPERSEDED`；
- `REVOKED`。

## Reason

把可推翻技术假设写成 Maker Decision 会阻止模型纠偏；无限追加历史又会持续增加 Context 读取成本。活动视图与有界历史可以同时保留当前权威状态和必要追踪证据。

## Boundary

Active Decision View 只保存当前有效决策及必要关系。当前迭代窗口内的变化进入 Bounded Changelog；发布或达到下游 Design 定义的体积阈值后，详细历史进入 Archive。

Archive 不参与默认上下文恢复，但必须能够通过 Stable Decision ID 追踪。

## Impact

- Context Model Design；
- Context Access Contract；
- Decision Record Template；
- Runtime Context Mutation；
- Migration Rules。

## Status

ACTIVE — V1.1

---

# Decision 009: P4 Creation Correction Loop

## Decision

P4 Creation 支持可选的内部 Correction Loop，用于 Evidence 推翻 Candidate Model、重复失败、Known-Good 回归或实质 Drift 时的局部模型纠偏和执行重规划。

Correction Loop：

- 不新增 Core Phase；
- 不进入 P6 Iteration；
- 不新增 P4→P2/P3 常规 Transition；
- 不改变 `current_phase = P4`；
- 不绕过 Maker 的 Product / Architecture Authority。

触发采用混合判定：Runtime 处理确定性计数和结构检查；Agent 提交语义判断与 Evidence；Maker 确认涉及产品或架构权威的变化。

相同 Failure Signature 连续 2 次失败触发 `MODEL_REVIEW_ADVISORY`，连续 3 次失败要求暂停同方向修补并输出 `P4_CORRECTION_REQUIRED`。Project Type Profile 只能收紧阈值，不能放宽。

Runtime Result 仅包括：

- `NO_CORRECTION`；
- `MODEL_REVIEW_ADVISORY`；
- `P4_CORRECTION_REQUIRED`；
- `MAKER_SCOPE_REVIEW_REQUIRED`。

这些结果不直接产生 Phase Transition 或 Context Mutation。

## Reason

P4 中发现模型错误并不表示已有完整功能进入迭代，也不适合加载完整 P2/P3 阶段职责。内部 Correction Loop 保持 Phase 语义稳定，同时允许以最小必要范围修正设计和计划。

## Escalation Boundary

下游 Workflow Design 必须使用已批准提案中的结构化 Impact Assessment。涉及 Product Goal、Success Criteria、Maker-approved Scope、Core Phase Model、Context Authority、Runtime Invariant，越过当前 Work Package，或无法识别有限影响范围与回归集合时，必须输出 `MAKER_SCOPE_REVIEW_REQUIRED`。

该结果仍不自动跳转 P2/P3，由 Maker 决定扩大局部纠偏、暂停 Capability 或正式重开设计。

## Impact

- Workflow Design；
- Gate Design；
- Advisory Design；
- Workflow Contract；
- Gate Contract；
- Runtime Specification；
- Project State 与 Plan Mutation Rules。

## Status

ACTIVE — V1.1

---

# Decision 010: Capability 级 Opaque Extension

## Decision

Opaque Capability Extension 按 Capability 激活，不把整个 Project 或 Project Type 永久标记为不透明。

Core 负责治理“何时不能继续把未知表述为已知”；Extension 负责指导“如何在未知条件下获得下一层可靠 Evidence”。

Extension 可以提供：

- 能力级不透明度评估；
- 产品点螺旋验证；
- 发现轮与验证轮；
- 假设区分设计；
- 可观察性计划；
- 证据到可重复验证闭环；
- 单圈闭合检查；
- 目标环境已知可用基线；
- 人工验证预算；
- 兼容性扩展轮。

每项 Extension 能力必须使用中文主名称，并可附稳定 Identifier。Design 必须定义其目的、启用条件、输入输出、责任主体、持久化位置、自动化边界与非职责。

## Relationship to Project Type

本 Decision 不 supersede Decision 006。

Project Type Profile 可以提供领域默认值、代表性路径和更严格阈值；Extension 是否启用仍由具体 Capability 的 Opacity Assessment 决定。同一项目内可以同时存在透明与不透明 Capability。

## Optional Context Boundary

高风险 Capability 可以创建 Capability Spiral Record。它属于 Optional Context / Extension Artifact：

- 不替代 Core Context；
- 不成为第二份 Current Project State；
- 不强制透明、低风险 Capability 创建；
- 不重复保存已有 Core Authority 数据，只保存 Extension 特有证据和引用。

## Impact

- Document Architecture；
- Opaque Capability Extension Design；
- Evidence Model Design；
- Context Model Design；
- Project Type Profile；
- Optional Context Template。

## Status

ACTIVE — V1.1

---

# Decision 011: Known-Good Baseline、Drift 与验证成本

## Decision

Core 必须定义高风险改变前识别 Known-Good Baseline、评估回归影响和更新 Confidence 的规则。

Baseline 的职责采用分层模型：

- Core 定义触发时机、最低字段与回归义务；
- Optional Context 保存项目级 Baseline Record；
- Opaque Capability Extension 定义目标环境证据、观察和兼容性细节。

Planning 必须区分 Agent 可自动完成的验证和依赖 Maker、设备、账号或外部宿主的验证，并记录人工验证预算、批次、次数上限、证据要求与停止条件。

Agent 必须检测 Capability Claim、Active Design、Active Decision、Implementation、Repeatable Verification、Target-Environment Evidence 与 Known-Good Baseline 之间的 Drift。

Script 只能报告结构化、确定性的 Drift；语义 Drift 由 Agent 基于 Evidence 提出。Advisory 不直接控制 Workflow 或 Runtime。

## Reason

没有 Baseline 和验证成本边界时，修改可能破坏 Maker 已确认工作的真实路径，并让 Maker 重复执行低信息量人工测试。结构 Drift 与语义 Drift 分离可以保留自动化价值，同时避免 Script 越权裁决语义。

## Impact

- Evidence Model Design；
- Context Model Design；
- Gate Design；
- Advisory Design；
- Implementation Plan Template；
- Optional Context Template；
- Runtime Specification。

## Status

ACTIVE — V1.1

---

# Decision 012: Multi-Context Mutation Orchestration

## Decision

当同一业务事件需要修改两个或以上 Context、涉及 Maker Authorization、存在跨 Context 后置条件，或 Event Recipe 明确要求 Closure Check 时，必须使用 `Context Mutation Set`。

Mutation Set 是有界 Runtime 执行对象，不是新的 Core Context。它必须声明触发事件、Authority Requirement、全部目标 Context、提交顺序、Closure Assertions 和回滚策略。

涉及 `PROJECT_STATE.md` 时，该文件必须最后提交。只有全部目标 Read-back、Context Closure、Authorization Finalization 和 Final Closure 通过后，事件才能报告完成。

Maker Authorization 必须绑定既有 Pending Authorization Request、Maker 输入引用、明确授权陈述、有效 Scope 和允许的 Context Targets。`source = MAKER` 与 `confirmed = true` 不能单独证明授权。

Opaque Capability Extension 使用以下 Core 治理状态：

- `PROPOSED`；
- `PENDING_MAKER_AUTHORIZATION`；
- `ACTIVE`；
- `DECLINED`；
- `SUSPENDED`。

`ACTIVE` 只能由匹配 Pending Request 的有效 Maker Authorization 触发，不改变 Current Phase。

## Reason

V1.1 RC 人工验收 Round 2 证明，单个 Context Mutation 合法不等于跨 Context 业务状态闭合。Agent 曾把要求评估的语境误判为已授权，并在 State、Plan 与 Spiral Record 中同步保存错误状态；现有 Runtime 既不能验证授权来源与 Pending Request 的关系，也不能在多文件部分失败时整体回滚。

## Boundary

- Runtime 验证结构、引用、Scope、顺序和确定性闭合，不创作语义内容；
- Agent 仍负责提出业务语义和从 Maker 原始输入中提取明确授权；
- Maker 保留 Product、Architecture 和 Extension Activation 的最终 Authority；
- 不新增 Core Phase、Transition、Gate Type 或 Runtime Execution State；
- 单文件、无受保护 Authority 且无跨 Context 后置条件的 Mutation 保持原路径。

## Impact

- Context Mutation Orchestration Design；
- Context Mutation Orchestration Contract；
- Context Mutation Orchestration Runtime Specification；
- Context Model Definition 与 Runtime Types；
- Context Coordinator、Runtime Coordinator 与 File Store；
- Skill Guidance、Templates、Unit / Integration / Acceptance Tests；
- RC 人工验收重放。

## Status

ACTIVE — V1.1 RC Remediation，Maker 于 2026-09-24 批准

---

# Decision 013: Desktop Product Project Type 与 Core Phase 语义复用

## Decision

Project Incubator Plugin 新增按产品形态划分的 `desktop-product` Project Type，并由 `desktop-product-incubator` Child Skill 提供桌面产品的阶段指导、交付约束、验证边界与风险控制。

`desktop-product` 不编码具体业务领域、产品品牌、跨产品组合或“伴侣”关系。浏览器扩展属于后续独立 Project Type 设计范围，不由当前 Child Skill 管理，也不因与某个桌面产品协作而自动成为同一 Managed Project。

Desktop Product Workflow 原样复用适用的 Core Phase ID 与 Phase Name：

- `P0 Intent Discovery`；
- `P1 Project Definition`；
- `P2 Solution Design`；
- `P3 Execution Planning`；
- `P4 Creation`；
- `P5 Validation`；
- `P6 Iteration`。

Desktop System Model、Usable Slice、Delivery Hardening、Target Environment Validation、`FEASIBILITY_PROBE` 与 Creation Correction 是 Child Skill 对相应 Core Phase 的 description、活动、检查点或 Gate Evidence，不是新的顶层 Phase，不写入 `workflow.stage`，也不产生额外 Transition。

Windows 通过独立的 `windows-desktop` Host Profile 具体化安装、权限、签名、进程、文件系统、升级与真实环境验证要求。`desktop-product` 不把 Windows 规则写入通用 Project Type，也不据此排除未来 macOS 或 Linux Host Profile。

Host 不设置默认值。每个 Project Type 必须在 Registry 中显式声明 `host_profile_requirement = REQUIRED | OPTIONAL | FORBIDDEN`。`desktop-product` 为 `REQUIRED`；Router 根据 Maker 输入提议具体 Host，Maker 明确确认后才能激活。`windows-desktop` 只是当前首个候选，不得在 Host 未确认或不匹配时自动填入。

激活采用通用 Workflow Entry：

- `NEW_PROJECT` 使用 Child Workflow 声明的标准初始阶段；
- `ADOPT_EXISTING` 由 Maker 提供项目来源和背景，Agent 基于可复核 Evidence 判断当前阶段；
- Kernel 验证 Entry 完整性、阶段集合、Workflow Shape、Host Requirement 与授权，不判断 Evidence 的业务语义；
- 临时 Correction / Review 子流程不能成为已有项目接管入口。

新激活状态必须保存通用 `workflow.entry`，至少包含 Entry Mode、Initial Stage、Assessment Summary、Evidence Refs 与 Assessed At。旧激活状态允许没有该字段，以保持兼容。

Shared Kernel 的 Maker Authorization、MCP-only Mutation、Pending Request、Receipt、Hook、Evidence 与状态摘要继续复用。为保证激活完整性，本 Decision 只批准通用 Workflow Entry 校验、`workflow.entry` 和 Registry Host Requirement；不得仅为桌面副命名增加其他 Kernel 或 Schema 语义。

## Reason

Project Type 的主要复用单位是产品形态及其研发风险，而不是业务领域。桌面产品在安装、升级、权限、本地状态、进程生命周期、恢复与真实 Host 验证方面具有稳定共性，足以形成独立 Child Incubator。

P0–P6 对桌面产品仍具有完整语义。保留既有 Phase 名称可以降低 Maker 与 Agent 的理解成本，保持跨项目状态、Gate 与 Evidence 的可比较性；桌面差异由 Child Skill 的 Phase Profile 表达即可，无需制造第二套生命周期词汇。

## Authority Boundary

- Maker 决定 Product Boundary、Architecture Decision、Host 支持范围、高风险自动化政策、真实环境验证预算与残余风险接受；
- Child Skill 提供桌面产品的指导、检查点、证据要求和风险提示，不决定其他产品形态如何组合；
- Host Profile 只能具体化特定操作系统环境，不得改变 Project Type 或 Core Workflow；
- Runtime 只执行结构、授权、Revision、Mutation、Receipt 与 Workflow 合法性校验，不替 Maker 作出产品或架构决策。
- Agent 对 `ADOPT_EXISTING` 的阶段归属负责；Maker 确认项目来源、路由和完整激活请求，但不被要求替 Agent 完成阶段分析。

## Compatibility and Migration

- 现有 `mod`、`mod-incubator` 与 `sims-4` Host Profile 不修改、不迁移、不重新解释；
- 已激活 Managed Project 不自动迁移 Project Type；
- 旧激活状态允许缺少 `workflow.entry`；所有新激活状态必须提供；
- 现有 `mod` 的 Host Requirement 登记为 `OPTIONAL`，不改变其既有路由行为；
- 首版不提供激活后的 Host 迁移；
- 浏览器扩展设计不得反向把浏览器规则写入 `desktop-product`；
- 不新增权威 Markdown 状态文件；
- 下游 Design 若发现必须增加 Kernel 或 Schema 语义，必须登记 `DESIGN_GAP` 并返回 Architecture 层审批。

## Impact

- Desktop Product Project Type Profile；
- Desktop Product Workflow 与 Gate Design；
- `desktop-product-incubator` Child Skill；
- Windows Desktop Host Profile；
- Registry 与 Router 候选类型；
- Workflow Entry、Registry Host Requirement 与 Kernel 激活校验；
- Contract、Runtime Specification、Implementation Plan 与 Acceptance Test Plan；
- Plugin、Legacy 与现有 `mod` 回归矩阵。

## Source

`SPECS/ARCHITECTURE/DESKTOP_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md`

## Status

ACTIVE — Plugin 后续迭代，Maker 于 2026-10-04 批准；Workflow Entry 与 Host Requirement 修订于 2026-10-05 批准

---

# Decision 014: Web Product Project Type、Local Browser Validation 与次级集成界面归属

## Decision

Project Incubator Plugin 新增按主要产品形态划分的 `web-product` Project Type，并由 `web-product-incubator` Child Skill 提供通用浏览器端产品的阶段指导、构建与本地运行边界、验证要求和安全约束。

`web-product` 的成立条件是：主要用户界面由通用浏览器访问，产品同时具有前端与后端逻辑职责，并且至少一条核心用户旅程穿过浏览器界面与后端或数据边界。前端与后端是逻辑职责，不要求前后端分离，也不因 SPA、SSR、MPA、静态生成、全栈框架、单体或多仓库结构产生不同 Project Type。

浏览器扩展、纯后端 API、独立 MCP Service、只有前端静态内容且没有后端逻辑职责的站点、桌面端、移动端、CLI、SDK 与库不属于 `web-product`。Router 只能提议类型；Maker 明确确认后才能激活或迁移。

Web Product Workflow 原样复用 Core P0–P6：

- `P0 Intent Discovery`；
- `P1 Project Definition`；
- `P2 Solution Design`；
- `P3 Execution Planning`；
- `P4 Creation`；
- `P5 Validation`；
- `P6 Iteration`。

Web Product Model、Usable Web Slice、Build Readiness、Local Browser Validation、Secondary Interface Validation 与 Creation Correction 是 Child Skill 对 Core Phase 的领域解释、活动、检查点或 Evidence 条件，不是新的顶层 Phase，不写入 `workflow.stage`，也不产生额外 Transition。

`web-product` 显式声明：

```text
host_profile_requirement = "FORBIDDEN"
deployment_capability = "DEFERRED_CAPABILITY"
```

通用浏览器、localhost、端口、启动命令、构建命令、环境变量与本地依赖属于 Managed Project 的运行配置和 Evidence 条件，不形成 Host Profile。公开部署、生产托管、域名、TLS、CDN、扩缩容、生产密钥和线上迁移不进入 V1.2 完成条件；build、localhost 与本地浏览器成功不得产生部署或生产就绪声明。

P4 至少形成两个可区分检查点：

- `Usable Web Slice`：一条核心浏览器旅程穿过适用的前端、后端与数据边界，结果、失败和副作用可观察；
- `Build Readiness`：依赖、配置、构建、localhost 启动和 readiness 路径可重复，且失败不会被手工修补掩盖。

P5 必须区分 Logic、Build、Local Service Integration、Local Browser、Secondary Interface 与 Human Evidence 的结论上限。Build-only Evidence 不能满足 P5；真实浏览器核心旅程是 V1.2 Web Product 验证的必要条件。

Project Type 约束主要产品形态，不枚举或禁止后端内部组件与次级协议界面。Web Product 可以在同一业务模型上提供 REST、GraphQL、WebSocket、Webhook、MCP 或等价接口。当 MCP Server 只是封装既有后端 Capability 时，它仍属于同一 `web-product` Managed Project，无论使用 SSE、Streamable HTTP、stdio，或位于独立进程、包或部署单元。它必须拥有独立 Claim、Security Boundary 与真实 Client Evidence，但其 Evidence 不能替代浏览器旅程 Evidence。

只有当 MCP Server 成为具有独立产品目标、消费者、版本支持、发布与回滚边界的主要交付物，且不再以浏览器核心旅程作为当前 Managed Project 的主要结果时，才不属于 `web-product`。当前版本不定义该独立 Project Type。

Shared Kernel 的 Maker Authorization、MCP-only Mutation、Pending Request、Receipt、Hook、Evidence、Workflow Entry 与状态摘要继续复用。Web 规则通过 Project Type Profile、Child Skill、独立 Workflow evaluator、Registry 和既有状态分区表达；不新增 Web 或 MCP 专用权威状态文件，不因阶段副命名增加 Runtime Schema。

## Reason

浏览器端产品在前后端责任边界、本地服务启动、浏览器旅程、网络与数据输入、服务端授权、Secrets、外部依赖和验证结论上限方面具有稳定共性，足以形成独立 Child Incubator；这些共性与具体框架、渲染方式或仓库拓扑无关。

复用 P0–P6 能保持跨 Project Type 的状态、Gate、Evidence 和授权语义一致。把 localhost 或浏览器建成 Host Profile 会把普通运行配置错误提升为路由复杂度；把部署设为必经 Gate 则会超出当前产品目标和验证预算。

MCP、REST 或 Webhook 描述的是能力暴露界面，不天然决定产品的主要形态。将绑定于同一业务模型的次级界面留在 Web Product 边界内，可以避免重复项目状态、重复业务规则与授权分叉，同时仍要求界面级 Evidence。

## Authority Boundary

- Maker 决定 Intent、Product Boundary、Project Type 激活或迁移、Architecture Decision、外部副作用政策、真实账户与付费服务使用、人工验证预算及残余风险接受；
- Agent 对 `ADOPT_EXISTING` 的阶段判断、Web System Model、工作包、实现细节和 Evidence 解释负责，但不得扩大已批准边界；
- Child Skill 提供 Web 产品领域指导、检查点、验证要求和风险提示，不选择技术栈，不自动授权部署或次级接口；
- Runtime 只执行结构、授权、Revision、Mutation、Receipt、Host Requirement 与 Workflow 合法性校验，不替 Maker 或 Agent 完成创造性判断。

## Compatibility and Migration

- 现有 `mod`、`desktop-product`、`sims-4` 与 `windows-desktop` 语义不修改、不迁移、不重新解释；
- 已激活 Managed Project 不自动迁移到 `web-product`；
- `NEW_PROJECT` 使用 P0，`ADOPT_EXISTING` 由 Agent 基于可复核 Evidence 判断 P0–P6 正常阶段；
- `web-product` 激活时必须拒绝非空 Host Profile；
- 旧状态不要求回填 Web 专用字段，因为本 Decision 不新增 State Schema；
- V1.2 发布前必须重新确认 V1.1 的实际发布基线、Plugin Package Version 与迁移记录；
- 未来启用 Deployment Capability 或独立 MCP Service Project Type 时，必须提出新的 Architecture Change Proposal；
- 下游 Design 若发现现有 Registry、Workflow evaluator、状态分区或 Evidence 机制无法无歧义表达所需语义，必须登记 `DESIGN_GAP` 并返回 Architecture 层。

## Impact

- Web Product Project Type Profile；
- `web-product-incubator` Child Skill；
- Web P0–P6 Workflow evaluator；
- Registry、Router 候选类型与 `FORBIDDEN` Host Requirement；
- Web Build、localhost、真实浏览器与次级界面 Evidence；
- Contract、Runtime Specification、Implementation Plan 与 Acceptance Test Plan；
- Plugin、Legacy、`mod` 与 Desktop 完整回归矩阵；
- 首个已有 Web 项目的 `ADOPT_EXISTING` Field Validation。

## Source

`SPECS/ARCHITECTURE/WEB_PRODUCT_INCUBATOR_CHANGE_PROPOSAL.md`

## Status

ACTIVE — Plugin V1.2 Web Product Extension，Maker 于 2026-10-13 批准

---

# 4. Decision Record Rules


所有 Architecture Decision 必须记录：


## Decision

最终选择。


## Reason

选择原因。


## Impact

对以下内容的影响：

- PROJECT_INCUBATOR_DESIGN.md
- Skill Architecture
- Implementation Plan


## Status

状态：

- `PENDING`；
- `ACTIVE`；
- `PARTIALLY_SUPERSEDED`；
- `SUPERSEDED`；
- `REVOKED`。

V1.0 文档中的 `Accepted` 等同于 V1.1 的 `ACTIVE`，无需为历史决策批量重写状态。

Decision Record 还必须在适用时记录：

- `Supersedes`；
- `Affected Decisions`；
- `New Evidence`；
- `Effective Scope`；
- `Migration Impact`。

当前有效决策进入 Active Decision View。变更摘要进入 Bounded Changelog；详细历史按发布版本或体积阈值归档，不在默认上下文恢复时加载。



---

# 5. Decision Completion Criteria


某一目标版本的 Architecture Decision 在以下条件全部满足后进入冻结状态：

- 该版本 Architecture Change Proposal 已获 Maker 批准；
- 所有该版本 Architecture Decision 已成为 `ACTIVE` 或已明确关闭；
- 冲突方案已关闭；
- Design 更新方向明确；
- 不存在阻塞下游 Design 的架构未决问题；
- `SPECS/README.md` 已记录对应状态。

一个版本的冻结不禁止后续版本演进。后续变化必须创建新的 Architecture Change Proposal，并通过新增、部分替代、替代或撤销 Decision 表达，不得由下游文档隐式覆盖。
