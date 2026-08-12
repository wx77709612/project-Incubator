# Project Incubator V1 Phase Advisory Design

# 1. Advisory Model

Agent Advisory 是 Project Incubator 中用于辅助 Agent 理解当前项目情境、识别问题并形成下一步建议的指导能力。

Advisory 的核心作用是：

- 帮助 Agent 理解当前 Phase 的关注重点；
- 提醒当前缺失的信息；
- 提示潜在风险和约束；
- 识别需要 Maker 澄清或确认的问题；
- 提供与当前项目状态相关的建议；
- 为 Agent 准备下一步行动提供领域指导。

Advisory 属于建议性能力。

Advisory 可以影响：

- Agent 的分析重点；
- Agent 向 Maker 提出的问题；
- Agent 给出的建议；
- Agent 对下一步工作的准备。

Advisory 不具有项目控制权。

Advisory 不允许：

- 修改 Workflow 状态；
- 执行 Phase Transition；
- 决定 Gate 是否通过；
- 替代 Maker Authorization；
- 修改 Context；
- 直接控制 Runtime；
- 将建议直接转化为执行结果。

Advisory Response 始终表示：

指导结果。

不表示：

- Workflow Decision；
- Gate Decision；
- Maker Authorization；
- Runtime Command。

---

# 2. Advisory Responsibility Boundary

Advisory 与 Workflow、Gate、Context、Runtime 保持明确职责分离。

## 2.1 Workflow Boundary

Workflow 是以下领域概念的 Source of Truth：

- Phase；
- Phase Goal；
- Phase Input；
- Phase Output；
- Required Artifact；
- Phase Transition Relationship；
- Artifact Flow。

Advisory 可以根据 Current Phase 提供阶段相关指导。

Advisory 不允许：

- 新增 Phase；
- 修改 Phase；
- 修改 Phase Goal；
- 改变 Allowed Next Phase；
- 执行 Phase Transition；
- 修改 Workflow State。

Advisory 发现 Workflow 相关问题时：

只能形成 Advisory Content 或 Recommended Action。

是否发生实际 Workflow Change，不由 Advisory 决定。

---

## 2.2 Gate Boundary

Gate 是以下领域概念的 Source of Truth：

- Gate Model；
- Gate Type；
- Gate Lifecycle；
- Gate Definition；
- Gate Evaluation Requirement；
- Maker Authorization Requirement。

Advisory 可以：

- 提醒存在风险；
- 提醒某个行为可能涉及 Gate；
- 提醒需要进一步确认。

Advisory 不允许：

- 判断 Gate 已通过；
- 判断 Gate 已解除；
- 替代 Gate Evaluation；
- 替代 Maker Authorization；
- 绕过 Gate Requirement。

Advisory 中的 Risk Notice：

不等于 Gate Decision。

---

## 2.3 Context Boundary

Context Domain Model 是项目上下文数据归属和 Source of Truth 的设计依据。

Advisory 可以依赖 Context 中已经存在的项目事实形成指导。

Advisory 不重新定义：

- Context Type；
- Context Responsibility；
- Context Lifecycle；
- Context Authority；
- Context Source of Truth。

Advisory 不修改 Context。

Context 的访问与修改机制不属于当前文档。

---

## 2.4 Runtime Boundary

Runtime 负责具体系统执行。

Advisory 不定义：

- Runtime Invocation；
- Runtime Execution Flow；
- Runtime Component；
- Runtime Command；
- Runtime State Change。

Advisory Response 不直接触发 Runtime Execution。

如果 Agent 根据 Advisory 决定准备某项行动：

实际执行仍必须遵循对应 Workflow、Gate、Contract 与 Runtime 规则。

---

# 3. Advisory Trigger Model

Advisory Trigger 表示：

当前项目情境出现了值得 Agent 获取额外指导的信息需求。

Advisory Trigger 只触发指导需求。

不表示：

- Phase Transition；
- Gate Trigger；
- Gate Decision；
- Runtime Execution。

Project Incubator V1 定义以下 Core Advisory Trigger Type。

## 3.1 Phase Entry

当项目进入新的 Current Phase 时，可以触发 Advisory。

目的：

帮助 Agent 理解：

- 当前 Phase Goal；
- 当前阶段应关注的信息；
- 当前阶段可能缺失的关键内容；
- 当前阶段常见风险。

---

## 3.2 Maker Guidance Request

当 Maker 主动询问：

- 下一步做什么；
- 当前应该关注什么；
- 当前方案是否合理；
- 是否存在风险；
- 当前阶段还缺什么；

可以触发 Advisory。

---

## 3.3 Missing Information

当 Agent 发现当前项目缺少继续分析所需的重要领域信息时，可以触发 Advisory。

Advisory 应说明：

- 缺失什么；
- 为什么该信息重要；
- 缺失信息会影响什么判断。

Advisory 本身不得虚构缺失信息。

---

## 3.4 Risk Detected

当 Agent 发现可能影响当前项目目标、范围、质量、架构或后续执行的风险时，可以触发 Advisory。

Risk Detected 只产生风险指导。

如果风险同时满足某个 Gate Trigger Condition：

Gate 是否被触发仍由 Gate Domain Model 与后续执行机制决定。

---

## 3.5 Decision Required

当当前工作存在无法由 Agent 单方面确定的重要选择时，可以触发 Advisory。

Advisory 可以：

- 描述需要决定的问题；
- 说明主要影响；
- 给出可理解的建议。

Advisory 不替 Maker 做最终决定。

---

## 3.6 Validation Feedback

当存在 Validation Result，且其中包含：

- 问题；
- 差距；
- 风险；
- 未满足条件；
- 后续调整方向；

可以触发 Advisory。

Advisory 用于帮助 Agent理解 Validation Feedback 对下一步工作的意义。

---

## 3.7 Iteration Re-entry

当项目因 Iteration 返回：

- Solution Design；
- Execution Planning；
- Creation；
- Validation；

可以触发新的 Advisory。

Advisory 应基于：

- Validation Result；
- 当前返回目标；
- 已知问题；

提示本轮重新进入该 Phase 时需要重点处理什么。

---

## 3.8 Project Type Specific Trigger

特定 Project Type 可以定义额外 Advisory Trigger。

Project Type Specific Trigger 必须：

- 与该 Project Type 的领域特点直接相关；
- 不重新定义 Core Workflow；
- 不重新定义 Gate；
- 不修改 Runtime 行为。

---

# 4. Advisory Context Model

Advisory Context 表示：

形成 Advisory 时可以参考的领域信息。

Advisory Context 不是 Input Contract。

本章节不定义：

- Input Schema；
- Interface；
- Required Field Protocol；
- Runtime 如何加载这些信息。

Core Advisory Context 包括：

- PROJECT_PROFILE.md；
- PROJECT_STATE.md；
- Current Phase；
- Project Type。

根据当前 Advisory Trigger，还可以参考：

- PROJECT_PLAN.md；
- PROJECT_DECISIONS.md；
- 当前相关 Artifact；
- Validation Result；
- 当前 Blocker；
- 当前已识别 Risk。

Advisory 必须尊重现有 Source of Truth。

Advisory 不允许：

- 用历史聊天记录覆盖当前 Context Source of Truth；
- 用 Agent 临时判断覆盖已确认项目事实；
- 将缺失信息当作已确认事实；
- 重新解释其他 Domain Model 的权威职责。

如果 Advisory 所需信息不足：

应产生 Missing Information 或 Required Clarification 类型的 Advisory Content。

不得自行补全关键项目事实。

---

# 5. Advisory Content Model

Advisory Content 表示：

Advisory 可以向 Agent 提供的领域指导内容。

Project Incubator V1 定义以下 Core Advisory Content Type。

## 5.1 Goal Clarification

用于说明：

- 当前工作的目标；
- 当前 Phase 应解决什么问题；
- 当前工作与 Project Intent 的关系。

---

## 5.2 Missing Information

用于指出：

- 当前缺失的关键信息；
- 缺失信息影响的判断；
- 需要进一步澄清的事项。

---

## 5.3 Risk Notice

用于指出：

- 已识别风险；
- 风险影响对象；
- 风险可能影响的后续工作。

Risk Notice 不等于 Gate Decision。

---

## 5.4 Constraint Reminder

用于提醒：

- 项目范围；
- 长期约束；
- 已冻结边界；
- 已确认 Decision；
- 当前 Project Type Constraint。

---

## 5.5 Decision Needed

用于表达：

当前存在需要 Maker 参与的重要决定。

可以包含：

- Decision Topic；
- 主要影响；
- 需要 Maker 确认的事项。

不得把 Advisory Recommendation 当作 Maker Decision。

---

## 5.6 Recommended Action

用于给出：

Agent 建议采取的下一步行动。

Recommended Action 可以是：

- 继续分析；
- 补充信息；
- 向 Maker 提问；
- 检查某个风险；
- 准备下一阶段所需内容；
- 根据 Validation Feedback 调整当前工作。

Recommended Action 只是建议。

不直接改变项目状态。

---

## 5.7 Validation Concern

用于指出：

当前工作中与 Validation 相关的潜在问题。

可以涉及：

- 完整性；
- Intent 一致性；
- 项目约束；
- 当前计划；
- Artifact 质量风险。

Advisory 不执行 Validation。

---

## 5.8 Project Type Guidance

用于提供特定 Project Type 的领域指导。

Project Type Guidance 只能增加：

该 Project Type 特有的关注点。

不得重新定义 Core Advisory Model。

---

# 6. Advisory Response Model

Advisory Response 是一次 Advisory 形成的指导结果。

Advisory Response 可以包含以下内容：

- Advisory Summary；
- Identified Issue；
- Relevant Context；
- Missing Information；
- Risk Notice；
- Constraint Reminder；
- Decision Needed；
- Recommended Action；
- Required Clarification；
- Suggested Next Step；
- Project Type Guidance。

并非每一次 Advisory Response 都必须包含所有内容。

具体内容由：

- Advisory Trigger；
- Current Phase；
- Project Context；
- 当前问题；

决定。

Advisory Response 必须保持建议性质。

Advisory Response 不允许：

- 修改 Workflow State；
- 完成 Phase Transition；
- 输出 Gate PASS / BLOCK 等 Gate Decision；
- 声称已经获得 Maker Authorization；
- 直接产生 Runtime Command；
- 直接执行项目修改。

当 Advisory 发现需要 Maker 输入时：

Response 可以明确产生：

Required Clarification

或：

Decision Needed。

当 Advisory 发现下一步较明确时：

Response 可以产生：

Recommended Action

或：

Suggested Next Step。

当 Advisory 发现当前信息不足以可靠建议时：

Response 应明确表达信息不足。

不得通过推测补齐关键事实。

---

# 7. Agent Advisory Use Model

Agent 使用 Advisory 的目的：

是改善分析和建议质量，而不是获得新的系统权限。

Agent 可以根据 Advisory：

- 调整当前分析重点；
- 检查缺失信息；
- 识别风险；
- 向 Maker 提出澄清问题；
- 向 Maker 提出需要确认的决定；
- 准备 Recommended Action；
- 准备 Suggested Next Step；
- 调整当前工作内容。

Agent 不可以因为 Advisory：

- 自动改变 Phase；
- 自动更新 Workflow State；
- 自动修改 Context；
- 自动解除 Gate；
- 自动视为 Maker 已授权；
- 自动执行 Runtime Action。

如果 Advisory 建议的下一步涉及：

Workflow Transition：

必须继续遵循 Workflow Domain Model。

如果涉及：

Gate Requirement：

必须继续遵循 Gate Domain Model。

如果涉及：

Context Access 或 Mutation：

必须继续遵循 Context Access Contract。

如果涉及：

具体执行：

必须继续遵循 Runtime Specification。

Advisory 只提供：

Agent 下一步判断所需的领域指导。

---

# 8. Project Type Extension

不同 Project Type 可以在 Core Advisory Model 基础上增加 Project Type Specific Advisory。

Project Type Extension 可以增加：

- Project Type Specific Trigger；
- Project Type Specific Content；
- Project Type Specific Risk；
- Project Type Specific Constraint；
- Project Type Specific Guidance。

例如：

## Video Project

可以增加：

- 内容结构关注点；
- 法律风险；
- 平台规则；
- 发布形式约束。

## Skill Project

可以增加：

- Runtime Boundary；
- Reference Design；
- Skill Structure Concern；
- Agent Behavior Boundary。

Project Type Extension 不允许：

- 修改 Core Advisory Trigger 语义；
- 删除 Core Advisory Content Type；
- 重新定义 Workflow；
- 重新定义 Gate；
- 重新定义 Context；
- 定义 Runtime Execution；
- 定义 Prompt Template Implementation。

Project Type Extension 只增加：

特定 Project Type 所需的额外指导信息。

---

# 9. Summary

Project Incubator V1 Agent Advisory Domain Model 定义：

- Advisory Model；
- Advisory Responsibility Boundary；
- Advisory Trigger Model；
- Advisory Context Model；
- Advisory Content Model；
- Advisory Response Model；
- Agent Advisory Use Model；
- Project Type Extension。

核心原则：

1. Advisory 是建议性能力，不是控制能力。

2. Advisory 可以帮助 Agent：

   - 理解当前 Phase；
   - 识别缺失信息；
   - 发现风险；
   - 识别约束；
   - 识别需要 Maker 决定的问题；
   - 准备下一步建议。

3. Advisory 不修改 Workflow State。

4. Advisory 不执行 Phase Transition。

5. Advisory 不替代 Gate Evaluation。

6. Advisory 不产生 Maker Authorization。

7. Advisory 不修改 Context。

8. Advisory 不直接控制 Runtime。

9. Advisory Response 只表示指导结果。

10. Advisory 不定义 Prompt Template Implementation。

11. Workflow、Gate、Context 与 Runtime 继续分别保持自己的 Source of Truth。

12. Project Type 可以扩展 Advisory，但不得改变 Core Advisory Domain Model。