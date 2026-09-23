# Project Incubator V1 Design Document Architecture

# 1. Purpose

本文档定义 Project Incubator V1 的设计文档架构。

目标：

明确：

- Project Incubator V1 所需设计文档类型；
- 每个设计文档的职责边界；
- 每个设计文档的依赖关系；
- 每个设计文档对 Codex 实现提供的信息。


本文档不定义 Project Incubator V1 的功能、流程或实现。


本文档作为：

Project Incubator V1 设计文档体系的架构契约。


后续所有设计文档必须遵守：

- 文档职责边界；
- Source of Truth 规则；
- 层级依赖关系。


禁止：

- 一个文档承担多个层级职责；
- 将 Runtime 实现内容写入 Architecture 文档；
- 将 Contract 内容写入 Domain Design 文档。


---

# 2. Design Document Architecture


Project Incubator V1 设计文档分为以下层级：

Architecture Layer

↓

Design Layer

↓

Contract Layer

↓

Runtime Layer

↓

Implementation Layer


每一层负责不同的问题：

Architecture Layer:

定义系统整体结构。


Design Layer:

定义领域模型。


Contract Layer:

定义模块交互规则。


Runtime Layer:

定义系统执行机制。


Implementation Layer:

定义 Codex 实现计划。

---

# 3. Architecture Layer


## Purpose


定义 Project Incubator V1 整体系统架构。


回答：

- Project Incubator V1 是什么？
- 系统包含哪些核心模块？
- 模块之间如何划分职责？


Architecture Layer 只负责：

- 系统定位；
- 核心模块；
- 架构边界；
- 角色职责。


不负责：

- 数据字段；
- API；
- Runtime 调用流程；
- Script 实现。


---

## Documents


### PROJECT_INCUBATOR_V1_DESIGN.md


文件路径：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_DESIGN.md


职责：

定义 Project Incubator V1 总体架构。


负责：

- Project Incubator 定位；
- Maker / Agent 角色；
- Runtime Architecture；
- Core Module Boundary；
- Skill Package Architecture。


不负责：

- API Contract；
- Runtime Implementation；
- Script Implementation；
- 具体数据 Schema。

---

# 4. Design Layer


## Purpose


定义 Project Incubator V1 各领域模型。


回答：

- 每个模块是什么？
- 每个模块包含哪些核心概念？
- 模块生命周期是什么？


Design Layer 不负责：

- Runtime 调用方式；
- 模块接口协议；
- Script 执行。


---

## Documents


### PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md


文件路径：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_WORKFLOW_DESIGN.md


职责：

定义 Workflow Domain Model。


负责：

- Phase Workflow；
- Phase 生命周期；
- Phase 输入输出；
- Artifact Flow。


不负责：

- Runtime Workflow Loader；
- Phase API。


---

### PROJECT_INCUBATOR_V1_GATE_DESIGN.md

文件路径：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_GATE_DESIGN.md


职责：

定义 Gate Domain Model。


负责：

- Gate Model；
- Gate Type；
- Gate Lifecycle；
- Gate Definition。


不负责：

- Gate Runtime Engine；
- Script 执行。


---

### PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md


文件路径：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_CONTEXT_MODEL_DESIGN.md


职责：

定义 Context Domain Model。


负责：

- Context 类型；
- Context 文件结构；
- Context 生命周期；
- Context Authority。


不负责：

- Context Access API；
- Runtime Context Invocation。


---

### PROJECT_INCUBATOR_V1_PHASE_ADVISORY_DESIGN.md


文件路径：

SPECS/DESIGN/PROJECT_INCUBATOR_V1_PHASE_ADVISORY_DESIGN.md


职责：

定义 Agent Advisory 能力。


负责：

- Advisory Trigger；
- Advisory Content；
- Advisory Response。

---

# 5. Contract Layer


## Purpose


定义模块之间交互契约。


回答：

- 模块如何通信？
- 谁可以读取什么？
- 谁可以修改什么？
- Runtime 如何调用模块？


Contract Layer 是 Codex 实现的重要依据。


---

## Documents


### PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md


文件路径：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md


职责：

定义 Runtime 与 Context 的访问规则。


负责：

- Read Permission；
- Write Permission；
- Mutation Authority；
- Access Boundary。


---

### PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md


文件路径：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_WORKFLOW_CONTRACT.md


职责：

定义 Workflow Runtime Interface。


负责：

- Workflow Schema；
- Phase Interface；
- Transition Contract。


---

### PROJECT_INCUBATOR_V1_GATE_CONTRACT.md


文件路径：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_GATE_CONTRACT.md


职责：

定义 Gate Invocation Contract。


负责：

- Gate Input；
- Gate Output；
- Evaluation Result。


---

### PROJECT_INCUBATOR_V1_SCRIPT_CONTRACT.md


文件路径：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_SCRIPT_CONTRACT.md


职责：

定义 Runtime 与 Script 交互规则。


负责：

- Script Input；
- Script Output；
- Error Handling；
- Validation Result。

---

# 6. Runtime Layer


## Purpose


定义 Project Incubator V1 如何执行。


## Document


### PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md


文件路径：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md


职责：

定义 Runtime 执行机制。


负责：

- Runtime Lifecycle；
- Component Loading；
- Execution Flow；
- Context Interaction；
- Gate Invocation；
- Script Invocation。


Runtime 必须依赖：

- Design Layer；
- Contract Layer。


Runtime 不重新定义：

- Workflow Model；
- Gate Model；
- Context Model。

---

# 7. Implementation Layer


## Purpose


指导 Codex 实现 Project Incubator V1。


## Document


### PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md


文件路径：

SPECS/IMPLEMENTATION/PROJECT_INCUBATOR_V1_IMPLEMENTATION_PLAN.md


职责：

定义实现计划。


负责：

- Implementation Order；
- Task Breakdown；
- Generated Files；
- Validation Criteria。

---

# 8. Dependency Relationship


Architecture

provides direction


↓

Design

provides domain definition


↓

Contract

provides integration boundary


↓

Runtime

provides execution mechanism


↓

Implementation

provides coding plan


---

# 9. Source of Truth Rule


当多个文档涉及同一概念时：

Architecture:

负责整体职责。

Design:

负责领域模型。

Contract:

负责交互规则。

Runtime:

负责执行机制。

Implementation:

负责实现步骤。


低层文档不得重新定义高层概念。

高层文档不得包含低层实现细节。