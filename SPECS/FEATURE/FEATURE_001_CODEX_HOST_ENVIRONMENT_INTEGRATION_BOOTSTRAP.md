# Feature 001 — Codex Host Environment Integration Bootstrap

# 1. Feature 概述

## 1.1 Feature 名称

Codex Host Environment Integration Bootstrap

## 1.2 Feature 状态

NOT_IMPLEMENTED

## 1.3 Feature 目标

当 Project Incubator 在 Codex 环境中初始化或接管一个 Managed Project 时，为该项目建立 Codex 项目级 Agent 协作入口。

对于尚未存在项目级 `AGENTS.md` 的 Managed Project：

Project Incubator 应能够生成：

<PROJECT_ROOT>/AGENTS.md

使后续 Codex Task 可以通过项目级 `AGENTS.md`：

- 识别该项目由 Project Incubator 管理；
- 定位 Core Context；
- 以 `PROJECT_STATE.md` 作为当前项目状态唯一 Source of Truth；
- 在涉及项目 Phase、Workflow、Gate、Validation、Iteration 或受控状态变化时使用 `project-incubator` Skill；
- 遵守 Maker / Agent / Runtime Boundary；
- 不绕过 Project Incubator Runtime 执行受控项目状态变化。

该能力只负责宿主环境集成。

不得改变 Project Incubator Core Workflow、Core Context、Gate Model 或 Runtime Authority。


# 2. 问题背景

Project Incubator 当前能够初始化 Managed Project 的 Core Context：

- `PROJECT_PROFILE.md`
- `PROJECT_STATE.md`
- `PROJECT_PLAN.md`
- `PROJECT_DECISIONS.md`

但当 Managed Project 在 Codex 中使用时：

Codex 项目根目录可能不存在项目级 `AGENTS.md`。

因此第一次 Project Incubator Task 完成后，后续新的 Codex Task 无法仅依靠当前项目目录自动获得以下 Project Incubator 协作入口信息：

- 当前项目由 Project Incubator 管理；
- 项目 Context 位于何处；
- 当前 State 应从何处读取；
- 什么情况下应该调用 `project-incubator`；
- 哪些项目行为不得绕过 Runtime；
- 哪些项目决策必须保留给 Maker。

Feature 001 用于补充这一 Host Environment Integration 能力。


# 3. Feature 定位

Feature 001 属于：

Host Environment Integration

首个支持的 Host Adapter 为：

Codex

该 Feature：

- 不是新的 Core Module；
- 不是新的 Workflow Phase；
- 不是新的 Gate Type；
- 不是新的 Context Type；
- 不改变现有 Phase Transition Matrix；
- 不改变 Maker / Agent / Runtime Authority；
- 不改变 `PROJECT_STATE.md` Source of Truth 规则。

项目级 `AGENTS.md` 是：

Host Environment Integration Artifact

不是：

Core Context。


# 4. Skill Package 扩展

Feature 001 在 Skill Package 中增加 Codex Host Integration Template。

新增：

PROJECT_INCUBATOR/templates/integrations/codex/AGENTS.template.md

该 Template 用于生成：

<PROJECT_ROOT>/AGENTS.md

Skill Package 自身已有：

PROJECT_INCUBATOR/AGENTS.md

与 Managed Project 生成的：

<PROJECT_ROOT>/AGENTS.md

职责完全不同。

`PROJECT_INCUBATOR/AGENTS.md`：

约束 Agent 使用 Project Incubator Skill Package 时的行为。

`<PROJECT_ROOT>/AGENTS.md`：

为 Codex 提供 Managed Project 的项目级 Agent 协作入口。


# 5. 触发时机

Feature 001 只在 Project Incubator 已被调用的前提下执行。

主要触发时机：

1. Project Incubator 初始化新的 Managed Project；
2. Project Incubator 第一次在已有 Managed Project 中建立协作上下文；
3. Maker 在已初始化的 Managed Project 中明确请求执行 Host Environment Integration Bootstrap。

该触发不受 Current Phase 限制。

即使 Managed Project 已经完成 Core Context 初始化并进入 P0–P6 中任意 Phase，
仍允许单独执行 Host Environment Integration Bootstrap。

该操作：

- 不重新初始化 Core Context；
- 不重新执行 P0 Bootstrap；
- 不改变 Current Phase；
- 不触发 Workflow Transition；
- 不改变 PROJECT_STATE.md；
- 只处理当前 Host Environment 所需的 Integration Artifact。
正常项目讨论不需要每轮重新生成 `AGENTS.md`。


# 6. Host Environment Resolution

Host Environment 必须先被解析。

允许的 Host Result：

- CODEX
- OTHER
- UNKNOWN

Host Identity 只能来自：

- 宿主执行环境能够明确提供的 Host 信息；
- Project Incubator Skill Invocation 中能够可靠确认的宿主信息；
- 明确提供的 Host Environment Input。

不得通过以下方式猜测当前宿主：

- 项目目录名称；
- 用户名称；
- `.codex` 目录是否存在；
- Git Repository 内容；
- 历史聊天；
- Agent 自行推断。

如果 Host Result：

CODEX

继续执行 Codex Integration Bootstrap。

如果：

OTHER

不生成 Codex `AGENTS.md`。

如果：

UNKNOWN

不生成 Codex `AGENTS.md`，并返回 Host Environment 无法确认。


# 7. Bootstrap 逻辑

Codex Host Integration Bootstrap 固定使用以下流程：

Project Incubator Invocation
↓
Resolve Host Environment
↓
Host = CODEX ?
↓
YES
↓
Resolve Managed Project Root
↓
检查 <PROJECT_ROOT>/AGENTS.md
↓
根据文件状态执行对应处理


# 8. AGENTS.md 状态判断

## 8.1 文件不存在

如果：

<PROJECT_ROOT>/AGENTS.md

不存在：

从：

PROJECT_INCUBATOR/templates/integrations/codex/AGENTS.template.md

生成：

<PROJECT_ROOT>/AGENTS.md

Result：

CREATED


## 8.2 文件已存在并已经包含 Project Incubator Integration

生成的 Project Incubator Codex Template 必须包含稳定 Integration Marker：

<!-- project-incubator:codex-integration -->

如果现有：

<PROJECT_ROOT>/AGENTS.md

包含该 Marker：

不得重复写入。

Result：

ALREADY_INTEGRATED


## 8.3 文件已存在但不包含 Project Incubator Integration

如果：

<PROJECT_ROOT>/AGENTS.md

已经存在，但没有 Project Incubator Integration Marker：

不得：

- 覆盖原文件；
- 删除原内容；
- 自动重写原文件；
- 自动将 Template 强行追加到原文件。

Result：

INTEGRATION_REQUIRED

Agent 应向 Maker说明：

当前项目已经存在 `AGENTS.md`，需要在保留原规则的前提下进行 Project Incubator Integration。

自动合并现有 `AGENTS.md` 不属于 Feature 001。


# 9. AGENTS Template 内容要求

`AGENTS.template.md` 必须保持简洁，只提供项目级入口规则。

必须包含以下内容。


## 9.1 Project Incubator Identity

说明：

当前项目由 Project Incubator 管理。


## 9.2 Core Context Entry

涉及项目目标、当前状态、未来计划、重要决策或项目推进时，应读取：

- `PROJECT_PROFILE.md`
- `PROJECT_STATE.md`
- `PROJECT_PLAN.md`
- `PROJECT_DECISIONS.md`


## 9.3 State Source of Truth

明确：

`PROJECT_STATE.md` 是当前项目状态的唯一 Source of Truth。

不得使用：

- 历史聊天；
- Agent Memory；
- 未执行 Plan；
- 临时推测

覆盖当前 State。


## 9.4 Project Incubator Skill Trigger

涉及以下行为时，应使用 `project-incubator`：

- 判断当前 Phase；
- 判断下一步项目行动；
- Workflow Transition；
- Gate；
- Validation；
- Iteration；
- 受控 Context Mutation；
- 项目状态推进。


## 9.5 Runtime Boundary

不得绕过 Project Incubator Runtime：

- 直接执行受控状态变化；
- 自行推进 Workflow；
- 自行修改受保护 Context。


## 9.6 Maker Boundary

Maker 保留：

- Project Goal；
- Project Scope；
- Project Direction；
- 重要 Decision；
- 需要 Maker Authorization 的变更

的最终决策权。


# 10. Template 内容边界

`AGENTS.template.md` 不得复制：

- 完整 Workflow Definition；
- 完整 Gate Definition；
- Runtime Specification；
- Contract；
- Phase Advisory 全量内容；
- Script Definition。

这些内容继续由 Project Incubator Skill Package 管理。

项目级 `AGENTS.md` 只负责：

Host Entry + Context Entry + Skill Routing + Authority Boundary。


# 11. 动态项限制

生成的 `AGENTS.md` 不保存容易变化的项目事实。

不得复制：

- Current Phase；
- 当前 Task；
- 当前 Validation Result；
- 当前 Gate Result；
- 临时计划；
- 当前 Runtime State。

这些信息必须继续从 Core Context 和 Runtime 获取。

因此：

`AGENTS.md` 是稳定入口文件，

不是项目状态副本。


# 12. Runtime / Script 实现方式

Host Integration Bootstrap 属于确定性 Operation。

实现必须复用现有：

Script Coordinator
+
Script Runner
+
DETERMINISTIC_OPERATION

执行链。

不得创建新的 Runtime Core Module。

新增 Script Capability：

BOOTSTRAP_HOST_INTEGRATION

建议实现文件：

PROJECT_INCUBATOR/scripts/bootstrap_host_integration.py


# 13. Script Responsibility

`bootstrap_host_integration.py` 只负责确定性文件操作。

允许：

- 接收 Host Environment Input；
- 接收 Managed Project Root；
- 检查目标 `AGENTS.md` 是否存在；
- 检查 Integration Marker；
- 读取 Codex AGENTS Template；
- 在允许情况下创建项目级 `AGENTS.md`；
- 返回确定性执行结果。

不得：

- 读取 Core Context 并解释项目状态；
- 判断 Current Phase；
- 作出 Maker Decision；
- 推进 Workflow；
- 修改 Core Context；
- 修改 Runtime State；
- 自动合并已有 `AGENTS.md`。


# 14. Runtime Integration

Host Integration 必须通过现有 Runtime / Script Invocation Path 执行。

正常 Invocation：

Invocation Purpose:

DETERMINISTIC_OPERATION

Validation Requirement:

empty

成功执行：

Execution Status:

COMPLETED

Validation Result:

empty

不得因为 Validation Result 为空：

- 生成 `VALIDATION_NOT_COMPLETED`；
- 将 Runtime 置为 SUSPENDED；
- 自动生成 `REQUIREMENT_SATISFIED`。


# 15. Skill Entry Integration

修改：

PROJECT_INCUBATOR/SKILL.md

增加 Host Environment Bootstrap 使用规则。

Skill 在建立 Managed Project Context 时：

1. 判断是否需要 Host Integration；
2. Resolve Host Environment；
3. 如果 Host = CODEX，执行 Codex Integration Bootstrap；
4. 如果 Host != CODEX，不生成 Codex Integration Artifact。

该逻辑不得影响 Core Workflow Phase 判断。


# 16. 第一次 Codex Task 行为

必须明确：

第一次在空项目中调用 Project Incubator 时：

Codex 当前 Task 启动时不存在项目级 `AGENTS.md`。

Project Incubator 可以在本次 Task 中创建：

<PROJECT_ROOT>/AGENTS.md

但不得假设新创建的文件已经重新进入当前 Task 的启动级 Agent Instruction。

因此 Feature 001 生成的 `AGENTS.md` 主要从后续 Codex Task 开始作为原生项目级 Agent Entry 生效。

当前 Task 继续依据：

- 已加载的 Project Incubator Skill；
- 当前 Maker Input；
- 当前 Runtime Result

完成本次初始化工作。


# 17. 后续 Codex Task 行为

Feature 001 成功执行后：

新的 Codex Task
↓
Codex 加载项目级 AGENTS.md
↓
Agent 获得 Project Incubator Entry Rule
↓
读取必要 Core Context
↓
涉及 Project Incubator 管理行为时调用 project-incubator
↓
继续 Maker / Agent / Runtime 协作流程


# 18. Non-Goal

Feature 001 不负责：

- 为所有 Agent Host 定义统一 Integration Standard；
- 支持 Cursor；
- 支持 Claude Code；
- 支持其他 IDE Agent；
- 自动修改已有第三方 `AGENTS.md`；
- 自动合并冲突规则；
- 创建新的 Core Context；
- 修改 Workflow；
- 修改 Gate；
- 修改 Phase；
- 修改 Maker Authority；
- 将 Project Incubator 全部规则复制到 Managed Project。


# 19. Generated / Modified Files

新增：

PROJECT_INCUBATOR/templates/integrations/codex/AGENTS.template.md

PROJECT_INCUBATOR/scripts/bootstrap_host_integration.py

修改：

PROJECT_INCUBATOR/SKILL.md

现有 Script Capability Registration / Script Coordinator 所需最小实现文件

必要的 Test 文件

如 README 当前承担用户使用说明，则同步更新：

PROJECT_INCUBATOR/README.md

不得为了 Feature 001 重构无关 Runtime Component。


# 20. Implementation Tasks

## F001-TASK-001 — Codex AGENTS Template

### Goal

建立 Managed Project Codex Integration Template。

### Implementation Scope

新增：

PROJECT_INCUBATOR/templates/integrations/codex/AGENTS.template.md

Template 必须满足第 9～11 节要求。

### Validation Criteria

- 包含 Integration Marker；
- 包含 Core Context Entry；
- 包含 State Source of Truth；
- 包含 project-incubator Skill Trigger；
- 包含 Runtime Boundary；
- 包含 Maker Boundary；
- 不包含动态项目状态。


## F001-TASK-002 — Host Integration Deterministic Operation

### Goal

实现 Codex Integration 的确定性 Bootstrap Capability。

### Implementation Scope

新增：

PROJECT_INCUBATOR/scripts/bootstrap_host_integration.py

按照第 6～8、12～14 节实现。

### Validation Criteria

能够区分：

- CREATED
- ALREADY_INTEGRATED
- INTEGRATION_REQUIRED
- NOT_APPLICABLE
- HOST_UNKNOWN

不得覆盖已有非 Project Incubator `AGENTS.md`。


## F001-TASK-003 — Runtime Integration

### Goal

将 Host Integration Capability 接入现有 Runtime Script Invocation Path。

### Implementation Scope

复用：

- Script Coordinator；
- Script Runner；
- DETERMINISTIC_OPERATION。

只进行 Feature 001 所需最小修改。

### Validation Criteria

- 不创建新 Core Module；
- Script 不直接修改 Core Context；
- 不改变 Workflow；
- 不改变 Gate；
- 不改变 Runtime State Model；
- Pure DETERMINISTIC_OPERATION 语义保持不变。


## F001-TASK-004 — Skill Trigger Integration

### Goal

使 Project Incubator 在适当时机触发 Host Integration Bootstrap。

### Implementation Scope

修改：

PROJECT_INCUBATOR/SKILL.md

必要时同步：

PROJECT_INCUBATOR/README.md

### Validation Criteria

- Codex Host 可以进入 Bootstrap；
- 非 Codex Host 不创建 `AGENTS.md`；
- UNKNOWN Host 不猜测；
- Host Bootstrap 不影响 Current Phase；
- Host Bootstrap 不自动触发 Workflow Transition。


## F001-TASK-005 — Feature Verification

### Goal

验证 Feature 001 行为及现有 V1 Regression。

### Required Cases

Case 1：

Host = CODEX
+
AGENTS.md 不存在

Expected：

AGENTS.md 创建成功
Result = CREATED


Case 2：

Host = CODEX
+
AGENTS.md 已包含 Integration Marker

Expected：

文件不重复修改
Result = ALREADY_INTEGRATED


Case 3：

Host = CODEX
+
已有普通 AGENTS.md

Expected：

原文件保持完全不变
Result = INTEGRATION_REQUIRED


Case 4：

Host = OTHER

Expected：

不创建 AGENTS.md
Result = NOT_APPLICABLE


Case 5：

Host = UNKNOWN

Expected：

不创建 AGENTS.md
Result = HOST_UNKNOWN


Case 6：

Bootstrap 成功后检查 Core Context

Expected：

- PROJECT_PROFILE.md 未因 Feature 001 被修改；
- PROJECT_STATE.md 未因 Feature 001 被修改；
- PROJECT_PLAN.md 未因 Feature 001 被修改；
- PROJECT_DECISIONS.md 未因 Feature 001 被修改。


Case 7：

运行现有 Project Incubator Regression Test。

Expected：

现有 Workflow、Context、Gate、Script、Runtime Test 不因 Feature 001 产生 Regression。


# 21. Task Execution Order

固定顺序：

F001-TASK-001
↓
F001-TASK-002
↓
F001-TASK-003
↓
F001-TASK-004
↓
F001-TASK-005

不得跳过 Feature Verification。


# 22. Feature Completion Criteria

只有以下条件全部满足，Feature 001 才可以标记为 COMPLETED：

1. Codex AGENTS Template 已建立；
2. Codex Managed Project 可以自动生成项目级 `AGENTS.md`；
3. 已有 `AGENTS.md` 不会被自动覆盖；
4. Host UNKNOWN 时不会猜测；
5. 非 Codex Host 不产生 Codex Artifact；
6. Bootstrap 使用现有确定性执行链；
7. Core Context Authority 未改变；
8. Workflow / Gate / Phase Model 未改变；
9. Runtime Core Architecture 未新增 Core Module；
10. Feature Test 全部通过；
11. 现有 Project Incubator Regression Test 通过。


# 23. Expected Result

Feature 001 完成后：

Project Incubator 可以继续保持 Host-independent Core Architecture。

当运行于 Codex Host 时：

Project Incubator
↓
初始化 / 恢复 Managed Project
↓
识别 Codex Host
↓
初始化项目级 AGENTS.md
↓
建立 Codex → Project Context → project-incubator Skill 的持续协作入口

从后续 Codex Task 开始：

Codex 可以通过项目级 `AGENTS.md` 自动恢复 Project Incubator 的项目协作入口，而不需要 Maker 每次重新说明如何进入 Project Incubator 协作流程。