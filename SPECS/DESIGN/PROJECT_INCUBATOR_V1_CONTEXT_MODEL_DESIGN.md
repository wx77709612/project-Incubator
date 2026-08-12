# Project Incubator V1 Context Model Design


## 1. 文档目的


本文档定义 Project Incubator V1 的 Project Context Layer 详细设计。


Project Context Layer 用于管理项目在长期 AI 协作过程中的核心上下文信息。


主要解决：

- 项目上下文无法长期保存；
- Agent 无法恢复项目状态；
- 项目目标和范围漂移；
- 计划、状态、决策混淆；
- 项目无法跨会话持续推进。


Project Context Layer 为：

- Maker；
- Agent；
- Runtime；

提供统一的项目上下文来源。


---

# 2. Context Model Overview


## 2.1 Context Layer Definition

Project Context Layer 是 Project Incubator 的持久化项目上下文领域模型。

Project Context Layer 负责定义和保存：

- 项目身份；
- 当前项目状态；
- 项目执行计划；
- Maker 已确认的重要决策；
- Project Type 扩展上下文。

Project Context Layer 负责回答：

- Project Context 包含哪些 Context Type；
- 每一种 Context 保存什么信息；
- 不同项目数据分别归属于哪个 Context；
- 哪一个 Context 对特定类型的信息具有 Authority；
- 不同 Context 在项目生命周期中如何建立、持续、变化或退出。

Project Context Layer 不属于 Runtime Engine。

本文件不定义：

- Context Access API；
- Read Permission；
- Write Permission；
- Mutation Authority；
- Agent Access Control；
- Runtime Context Invocation；
- Context Mutation Execution；
- Context Writeback。

Context 的访问与 Mutation 规则由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

Context 的具体 Runtime 执行机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---

## 2.2 Context Layer Architecture


Project Context Layer：


```text
Project Context Layer

├── Core Context
│
│   ├── PROJECT_PROFILE.md
│   ├── PROJECT_STATE.md
│   ├── PROJECT_PLAN.md
│   └── PROJECT_DECISIONS.md
│
└── Optional Context Extension

    └── PROJECT_ARTIFACTS.md
```


---

# 3. Core Context Model


## 3.1 Context Responsibility


Project Incubator V1 默认使用以下 Core Context：


| Context | Responsibility |
| --- | --- |
| PROJECT_PROFILE.md | 项目身份和长期目标 |
| PROJECT_STATE.md | 当前项目实际状态 |
| PROJECT_PLAN.md | 项目未来执行计划 |
| PROJECT_DECISIONS.md | Maker 已确认的重要决策 |


---

## 3.2 Context Separation Principle


不同 Context 文件必须保持职责分离。


```text
PROJECT_PROFILE

定义：

项目是什么。


        ↓


PROJECT_STATE

记录：

项目当前在哪里。


        ↓


PROJECT_PLAN

描述：

项目准备如何推进。


        ↓


PROJECT_DECISIONS

记录：

哪些关键选择已经被确认。
```


禁止：

- PROJECT_STATE 保存未来计划；
- PROJECT_PLAN 保存当前执行状态；
- PROJECT_PROFILE 保存临时任务；
- PROJECT_DECISIONS 保存未确认方案。


---

## 3.3 Context Authority Model

Context Authority 表示某一种 Context 对特定项目信息所具有的领域权威。

Context Authority 不表示访问权限或修改权限。

Core Context Authority 定义如下：

| Context | Authority Scope |
| --- | --- |
| PROJECT_PROFILE.md | 项目身份、项目类型、Intent、用户对象、成功标准和长期约束 |
| PROJECT_STATE.md | 项目当前实际状态 |
| PROJECT_PLAN.md | 项目当前有效的未来执行计划 |
| PROJECT_DECISIONS.md | Maker 已确认的重要项目决策 |
| Optional Context | 对应 Project Type 的扩展上下文 |

Authority 原则：

### PROJECT_PROFILE.md

PROJECT_PROFILE.md 对以下信息具有 Authority：

- 项目是什么；
- 项目服务什么对象；
- 项目长期目标是什么；
- 成功标准是什么；
- 长期约束是什么。

PROJECT_PROFILE.md 不作为：

- 当前执行状态；
- 当前未来计划；
- 临时任务；
- 未确认方案

的 Authority。

### PROJECT_STATE.md

PROJECT_STATE.md 对项目当前实际状态具有唯一 Source of Truth Authority。

包括：

- 当前 Phase；
- 当前 Gate 状态；
- 当前执行状态；
- 已完成事项；
- 当前阻塞事项；
- 最近状态变化。

以下信息不得替代 PROJECT_STATE.md 作为当前状态来源：

- PROJECT_PLAN.md；
- 历史聊天记录；
- Agent 临时记忆；
- 未持久化上下文；
- Project Artifact State；
- Runtime State。

### PROJECT_PLAN.md

PROJECT_PLAN.md 对项目当前有效的未来执行计划具有 Authority。

包括：

- 阶段目标；
- 阶段任务；
- 执行顺序；
- 依赖关系；
- 预期 Artifact；
- 风险；
- 验证方式。

PROJECT_PLAN.md 不作为项目当前实际状态的 Authority。

### PROJECT_DECISIONS.md

PROJECT_DECISIONS.md 对 Maker 已确认的重要项目决策具有 Authority。

以下内容不属于 PROJECT_DECISIONS.md Authority：

- 普通讨论；
- 临时想法；
- Agent 自主判断；
- 未确认方案。

历史 Decision 不被覆盖。

后续发生新的已确认决策时，通过新的 Decision Record 表达。

### Optional Context

Optional Context 只对对应 Project Type 的扩展上下文具有 Authority。

Optional Context 不得：

- 覆盖 PROJECT_PROFILE.md Authority；
- 覆盖 PROJECT_STATE.md Authority；
- 覆盖 PROJECT_PLAN.md Authority；
- 覆盖 PROJECT_DECISIONS.md Authority；
- 重新定义 Core Context Model。

### Authority Conflict Principle

当多个 Context 看似涉及同一信息时：

必须根据该信息的领域性质确定其 Authority。

判断原则：

- 项目身份与长期目标 → PROJECT_PROFILE.md；
- 当前实际状态 → PROJECT_STATE.md；
- 当前有效未来计划 → PROJECT_PLAN.md；
- Maker 已确认的重要决策记录 → PROJECT_DECISIONS.md；
- Project Type 特定扩展信息 → 对应 Optional Context。

Context Authority 只定义领域信息归属。

Context 的 Read Permission、Write Permission、Mutation Authority 与 Access Boundary 由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

---

# 4. PROJECT_PROFILE.md Design


## 4.1 Definition


PROJECT_PROFILE.md 是 Project Identity Context。


用于定义：

项目是什么。


---

## 4.2 Responsibility


PROJECT_PROFILE.md 保存项目长期稳定信息。


包含：

- 项目名称；
- 项目类型；
- Intent；
- 用户对象；
- 成功标准；
- 长期约束；
- Maker 确认的信息。


---

## 4.3 Lifecycle

PROJECT_PROFILE.md 在项目初始化阶段建立。

建立后：

- 作为项目身份与长期目标的稳定 Context；
- 在项目持续期间保持长期有效；
- 不随普通任务、Phase 推进或短期执行状态频繁变化。

当以下领域信息发生已确认的实质变化时，PROJECT_PROFILE.md 可以形成新的当前内容：

- 项目身份；
- 项目类型；
- Intent；
- 用户对象；
- 成功标准；
- 长期约束。

临时任务、当前执行状态和短期计划变化不属于 PROJECT_PROFILE.md Lifecycle Change。

---

# 5. PROJECT_STATE.md Design


## 5.1 Definition


PROJECT_STATE.md 是 Project 当前状态来源。


用于描述：

项目当前实际在哪里。


---

## 5.2 Responsibility


PROJECT_STATE.md 保存：

- 当前 Phase；
- 当前 Gate 状态；
- 当前执行状态；
- 已完成事项；
- 当前阻塞事项；
- 最近状态变化。


---

## 5.3 Source of Truth

Project 当前状态唯一来源：

PROJECT_STATE.md


Runtime State 和 Project Artifact State：

用于 Runtime 执行过程中的辅助信息。


它们不能替代 PROJECT_STATE.md 作为项目当前状态来源。

不依赖：

- 历史聊天记录；
- Agent 临时记忆；
- 未持久化上下文。


---

## 5.4 Lifecycle

PROJECT_STATE.md 在项目当前状态首次建立时进入有效生命周期。

建立后：

- 在项目持续期间保持有效；
- 随项目实际状态变化持续演进；
- 始终表达项目当前实际状态；
- 当前有效内容取代已经不再代表现实状态的旧状态内容。

PROJECT_STATE.md 的 Lifecycle Change 可以由以下领域变化产生：

- Current Phase 变化；
- Gate 状态变化；
- 当前执行状态变化；
- 已完成事项变化；
- 当前阻塞事项变化；
- 其他影响项目当前实际状态的事实变化。

PROJECT_STATE.md 不因以下内容单独发生状态生命周期变化：

- 尚未执行的未来计划；
- 未确认方案；
- 设计讨论过程。

在任何时点：

PROJECT_STATE.md

始终是项目当前实际状态的唯一 Source of Truth。

---

## 5.5 Boundary


PROJECT_STATE.md 只记录：

当前事实状态。


不记录：

- 未来计划；
- 未执行方案；
- 设计讨论过程。


---

# 6. PROJECT_PLAN.md Design


## 6.1 Definition


PROJECT_PLAN.md 是项目执行计划。


用于描述：

项目未来准备如何推进。


---

## 6.2 Responsibility


PROJECT_PLAN.md 包含：

- 阶段目标；
- 阶段任务；
- 执行顺序；
- 依赖关系；
- 预期 Artifact；
- 风险；
- 验证方式。


---

## 6.3 PROJECT_PLAN 与 PROJECT_STATE Boundary


PROJECT_PLAN 与 PROJECT_STATE 必须严格分离。


PROJECT_PLAN：

描述：

```text
计划发生什么。
```


PROJECT_STATE：

描述：

```text
实际发生什么。
```


---

## 6.4 Lifecycle

PROJECT_PLAN.md 在项目形成当前有效执行计划时建立。

建立后：

- 表达项目当前有效的未来执行计划；
- 可以随项目目标、任务、执行顺序、依赖关系或预期 Artifact 的变化而调整；
- 新的当前有效计划可以取代已经不再适用的旧计划内容。

PROJECT_PLAN.md 的 Lifecycle Change 可以由以下领域变化产生：

- 阶段目标调整；
- 阶段任务调整；
- 执行顺序调整；
- 依赖关系调整；
- 预期 Artifact 调整；
- 风险变化；
- 验证方式变化。

PROJECT_PLAN.md 只描述未来准备如何推进。

已经实际发生的项目状态变化属于：

PROJECT_STATE.md

而不是 PROJECT_PLAN.md。

---

# 7. PROJECT_DECISIONS.md Design


## 7.1 Definition


PROJECT_DECISIONS.md 是项目关键决策记录。


用于保存：

已经由 Maker 确认的重要项目决策。


---

## 7.2 Responsibility


包含：

- Decision ID；
- Decision Context；
- Selected Option；
- Decision Owner；
- Decision Timestamp；
- Impact。


---

## 7.3 Lifecycle


生命周期：

长期保存。


原则：

历史 Decision 不覆盖。


新的决定：

创建新的 Decision Record。


---

## 7.4 Boundary


PROJECT_DECISIONS.md 不记录：

- 普通讨论；
- 临时想法；
- Agent 自主判断；
- 未确认方案。


---

# 8. Optional Context Extension


## 8.1 Definition


Optional Context Extension 用于支持不同 Project Type 的额外上下文需求。


Optional Context：

不属于所有项目默认上下文。


建立条件：

- 当前 Project Type 存在 Core Context 无法表达的额外上下文需求；
- 该扩展 Context 具有明确的数据职责和 Authority Scope。


---

## 8.2 PROJECT_ARTIFACTS.md


PROJECT_ARTIFACTS.md 定位：

Artifact Lifecycle Registry。


用于管理：

- Artifact 身份；
- Artifact 类型；
- 所属 Phase；
- 当前状态；
- 创建来源；
- 依赖关系；
- 验证状态。


---

## 8.3 Extension Boundary


Optional Context 不得改变 Core Context Model。


必须保持：

- PROJECT_PROFILE Boundary；
- PROJECT_STATE Boundary；
- PROJECT_PLAN Boundary；
- PROJECT_DECISIONS Boundary。


---

## 8.4 Lifecycle

Optional Context Extension 默认不属于所有项目的有效 Context。

当特定 Project Type 存在额外 Context Requirement 时，可以建立对应 Optional Context。

Optional Context 建立后：

- 只在对应 Project Type 的上下文范围内有效；
- 只保存 Core Context 无法表达的 Project Type 特定上下文；
- 不改变 Core Context 的生命周期；
- 不改变 Core Context Authority。

当对应 Project Type Context Requirement 不再适用时：

- Optional Context 可以停止作为当前有效扩展上下文参与项目 Context Model；
- 其退出不得改变 PROJECT_PROFILE.md、PROJECT_STATE.md、PROJECT_PLAN.md 或 PROJECT_DECISIONS.md 的领域职责。

Optional Context 的建立、持续和退出只描述领域生命周期。

具体访问、创建、修改或持久化机制不属于当前文档。

---

# 9. Context 与 Workflow Relationship

Workflow 与 Context 是两个职责独立但存在领域依赖关系的 Domain Model。

Workflow 定义：

- Phase；
- Phase Goal；
- Phase Input；
- Phase Output；
- Required Artifact；
- Artifact Flow；
- State Change Requirement；
- Phase Transition Relationship。

Context 定义：

- 项目身份信息；
- 当前项目状态；
- 当前有效执行计划；
- Maker 已确认的重要决策；
- Project Type 扩展上下文。

Workflow 可以将 Context 作为：

- Phase Input；
- Phase Output；
- Workflow 推进所依赖的项目事实；
- State Change Requirement 所涉及的领域对象。

Workflow 不重新定义：

- Context Type；
- Context 文件职责；
- Context Lifecycle；
- Context Authority。

Context 不重新定义：

- Phase；
- Phase Goal；
- Phase Transition；
- Artifact Flow；
- Workflow Requirement。

Workflow 与 Context 之间的具体访问、Mutation 和 Runtime 交互机制不属于当前 Context Domain Model。

相关规则由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

以及：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---

# 10. Context 与 Runtime Relationship

Runtime Layer 是 Context Domain Model 的下游使用者。

Context Domain Model 向 Runtime 提供：

- Context Type；
- Context 文件职责；
- Context 数据归属；
- Context Lifecycle；
- Context Authority；
- Source of Truth 定义。

Runtime 不得重新定义：

- Core Context Type；
- Core Context Responsibility；
- Context Lifecycle；
- Context Authority；
- Context Source of Truth。

本文件不定义 Runtime 如何：

- Load Context；
- Read Context；
- Write Context；
- Validate Context Mutation；
- Execute Context Mutation；
- Persist Context；
- Write Back Context。

Runtime 与 Context 的访问规则由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

Runtime 的具体 Context Interaction 机制由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

---

# 11. Summary

Project Incubator V1 Context Model 采用：

Project Context Layer

├── PROJECT_PROFILE.md
├── PROJECT_STATE.md
├── PROJECT_PLAN.md
├── PROJECT_DECISIONS.md
└── Optional Context Extension

核心原则：

1. Context Layer 保存项目长期可持续使用的项目上下文。

2. PROJECT_PROFILE.md 对项目身份、长期目标和长期约束具有 Authority。

3. PROJECT_STATE.md 是项目当前实际状态的唯一 Source of Truth。

4. PROJECT_PLAN.md 对项目当前有效的未来执行计划具有 Authority。

5. PROJECT_PLAN.md 与 PROJECT_STATE.md 必须严格分离：

   - PROJECT_PLAN.md 描述未来准备如何推进；
   - PROJECT_STATE.md 描述当前实际发生什么。

6. PROJECT_DECISIONS.md 对 Maker 已确认的重要项目决策具有 Authority。

7. 历史 Decision 不覆盖；新的已确认决策形成新的 Decision Record。

8. Optional Context Extension 只用于 Project Type 特定上下文，不得覆盖 Core Context Authority。

9. Context Lifecycle 由各 Context Type 的领域职责决定。

10. Context Layer 不保存项目 Artifact 本体。

以下内容属于项目 Artifact：

- Design Document；
- Source Code；
- Generated Content；
- Validation Result。

Context Layer 保存：

- 项目身份；
- 当前状态；
- 当前有效执行计划；
- Maker 已确认的重要决策；
- 必要的 Project Type 扩展上下文。

本 Context Design 不定义：

- Read Permission；
- Write Permission；
- Mutation Authority；
- Agent Access Control；
- Context Access API；
- Runtime Context Invocation；
- Context Mutation Execution。

Context Access Contract 由：

SPECS/CONTRACTS/PROJECT_INCUBATOR_V1_CONTEXT_ACCESS_CONTRACT.md

定义。

Runtime Context Interaction 由：

SPECS/RUNTIME/PROJECT_INCUBATOR_V1_SKILL_RUNTIME_SPEC.md

定义。

