# Project Incubator V1 Architecture Decisions


# 1. 文档定位


## 1.1 Purpose


本文档用于记录 Project Incubator V1 在进入 Design 完善阶段前，需要由 Maker 确认的核心架构决策。


本文档的作用：

- 明确尚未冻结的架构选择；
- 记录候选方案；
- 记录最终决策；
- 作为 PROJECT_INCUBATOR_V1_DESIGN.md 更新依据。


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

Architecture Decision Frozen

冻结日期：

YYYY-MM-DD


冻结范围：

- Runtime Architecture
- Context Model
- Phase Model
- Gate Boundary
- Project Type Runtime Architecture


后续修改必须通过 Architecture Change Proposal。

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


- PROJECT_INCUBATOR_V1_DESIGN.md；
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

- PROJECT_INCUBATOR_V1_DESIGN.md；
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


# 4. Decision Record Rules


所有 Architecture Decision 必须记录：


## Decision

最终选择。


## Reason

选择原因。


## Impact

对以下内容的影响：

- PROJECT_INCUBATOR_V1_DESIGN.md
- Skill Architecture
- Implementation Plan


## Status

状态：

- Pending
- Accepted
- Deprecated



---

# 5. Decision Completion Criteria


当以下条件满足时：

PROJECT_INCUBATOR_V1_ARCHITECTURE_DECISIONS.md

进入冻结状态。


条件：

- 所有 P0 Decision 已完成；
- 冲突方案已关闭；
- Design 更新方向明确；
- 不存在影响整体架构的未决问题。

