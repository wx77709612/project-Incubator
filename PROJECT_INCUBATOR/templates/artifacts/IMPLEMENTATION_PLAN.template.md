> Legacy / 非现行：仅供旧 RC 兼容回归或 Artifact 参考，Plugin 不加载、不默认分发；正文的旧 Context 语义不适用于 MCP Kernel。

# Implementation Plan

## Artifact Boundary / Artifact 边界

Implementation Plan 是 Phase Artifact。

本 Artifact 用于将 Solution Design 转换为可执行实施方案。

本 Artifact 不属于 Core Context，不替代 `PROJECT_PLAN.md`。

`PROJECT_PLAN.md` 记录项目生命周期规划；Implementation Plan 记录当前 Project Type 对应的实施方案。

本模板是通用结构。不同 Project Type 可以使用不同 Implementation Plan 模板，例如 Software、Skill、Video 等。

## Source / 来源

- Solution Design Artifact：待填写
- PROJECT_PROFILE.md：待填写
- PROJECT_PLAN.md Lifecycle Context：待填写

## Implementation Scope / 实施范围

<!--
填写本轮实施需要覆盖的范围。

一个范围一个 Markdown 无序列表项。
-->

- 待填写

## Task Breakdown / 任务拆解

<!--
填写 Project Type 对应的具体实施任务。

一个任务一个 Markdown 有序列表项。
-->

1. 待填写

## Execution Order / 执行顺序

<!--
填写任务之间的执行顺序。
-->

1. 待填写

## Dependency / 依赖关系

<!--
填写实施任务所依赖的输入、资源、Artifact 或决策。

无依赖时填写：

- 无
-->

- 待填写

## Expected Artifact / 预期 Artifact

<!--
填写本实施方案预计生成或更新的 Project Artifact。
-->

- 待填写

## Validation Method / 验证方式

<!--
填写用于确认 Implementation Plan 执行结果的验证方式。
-->

- 待填写

## Capability Risk / 能力风险

<!-- 对每项关键 Capability 说明透明度、当前 Evidence Level、目标 Evidence Level 和主要失败风险。透明 Capability 可以保持简要。 -->

- Capability ID：待填写
- Opacity：待填写
- Current Evidence：待填写
- Target Evidence：待填写

## Representative Vertical Slice / 代表性垂直切片

仅对高不透明 Capability 强制设计代表性端到端切片；透明、低风险 Capability 可填写“不适用”。切片应从用户可识别条件开始，穿过主要风险边界并到达可观察结果。

- 触发条件：待填写
- 风险边界：待填写
- 可观察结果：待填写
- Delivery Artifact：待填写
- Repeatable Verification：待填写
- Target-Environment Evidence：待填写

## Evidence Target / 证据目标

- Capability Claim：待填写
- Required Evidence Level：待填写
- Evaluated Scope：待填写
- 不允许宣称的范围：待填写

## Human Validation Budget / 人工验证预算

- 是否依赖 Maker、设备或目标环境：待填写
- 可用验证次数或时间：待填写
- 每次验证必须区分的 Hypothesis：待填写
- 预算耗尽后的处理：待填写

## Failure Stop Condition / 失败停止条件

<!-- 定义何时停止同方向补丁并触发 Model Review 或 P4 Correction。默认同 Signature 连续 2 次产生 Advisory，连续 3 次要求 Correction；Profile 只能更早触发。 -->

- Failure Signature：待填写
- Advisory Threshold：2
- Correction Threshold：3
- Baseline Regression Action：待填写
- Maker Scope Review Trigger：待填写
