---
name: mod-incubator
description: 用于已由 Project Incubator Router 确认为 mod 类型的 Managed Project。围绕玩家可观察的 Product Point，按宿主风险、代表性垂直切片、最终包和真实环境证据推进 Mod 开发；实现中模型失效时进入轻量 MODEL_REVIEW。
---

# Mod Incubator

## 当前 Kernel 权威与恢复

Plugin Router `project-incubator-router` 是唯一现行入口。权威集合为 `.project-incubator/activation.json`、`.project-incubator/state.json` 和 `.project-incubator/latest-receipt.json`；State 是唯一业务状态，Activation 约束身份/路由，Receipt 证明闭合。临时 Runtime Data 和 Markdown Artifact 不替代它们。

恢复与状态查询先调用 `inspect_project`，验证失败时报告稳定错误并停止受影响推进，不从聊天补全。只使用已验证路由的 Child Skill/Host Profile；不得直接编辑权威文件。所有受控变更经现行 Kernel，提交后确认 revision、回读与 Receipt 一致再报告完成。缺少 Plugin/MCP 时停止，不调用旧执行资产。


## 运行边界

- 开始前调用 `inspect_project`，验证 Receipt 后，确认 `project_type_id` 为 `mod`。
- 所有状态变化通过 Kernel MCP 的 `prepare_change` 与 `commit_change`；不得直接编辑 `.project-incubator/`。
- 发现 Pending Request 内容错误、过时或不应获批时，必须请求 Maker 明确拒绝，并使用 `decline_change` 精确匹配 `request_id` 与 `scope_digest`；不得提交后再补救，也不得直接清理状态文件。
- 新增或修改 Decision 时，在拟议状态中写明新的有效声明；真实 `authorization_ref` 与 `confirmed_at` 由 Runtime 在 Commit 时绑定，Agent 不得伪造。
- Product Boundary、架构决定、人工测试预算和支持范围由 Maker 确认。
- API 可用性、局部调用和自动化测试不得表述为完整宿主语义成立。

## 六阶段

1. `M0_BOUNDARY`：确认玩家价值、目标宿主、Mod 类型、成功结果与排除范围。
2. `M1_RISK_MODEL`：按八维评估 Capability 不透明性，区分事实、假设与决定。
3. `M2_VERTICAL_SLICE`：完成一个代表性完整生命周期，使关键边界可观察并允许推翻 Candidate Model。
4. `M3_BUILD_PACKAGE`：实现受支持模型，验证最终包内容、依赖、安装结构和本地回归。
5. `M4_TARGET_VALIDATION`：在真实宿主验证 Capability Claim、失败与副作用。
6. `M5_EXPAND_RELEASE`：只沿一个主要风险维度扩展，或明确当前发布边界。

阶段转换必须调用领域 Workflow 评估，不得跳级。M0 退出和任何 Product Boundary 变化必须获得 Maker Authorization。

## MODEL_REVIEW

在 M2、M3 或 M4 出现反例、重复无效修补或实现与模型冲突时：

1. 标记失效 Runtime Assumption；
2. 暂停同方向补丁；
3. 更新 Candidate Model 与受影响边界；
4. 重放受影响的自动验证；
5. 返回原阶段，或在涉及产品/架构边界时请求 Maker 决定。

`MODEL_REVIEW` 是当前阶段内的纠偏子流程，不是 M5，不得称为“功能完成后的迭代”。

## Evidence 与成本

- Evidence 使用 `E0` 至 `E5`，结论不得超过证据上限。
- 任一不透明维度为 `2`，或至少两个维度为 `1`，建议代表性 Vertical Slice；未知按 `1` 计算并明确显示未知。
- 一次目标宿主完整成功最高支持 `E3`；API Availability 不提升 Semantic Capability。
- 人工验证次数只能由 Maker 设置；未设置时保持 `UNSET`，Agent 只提出可区分假设的测试批次。
- 真实异常应归一化为可重复验证，再返回目标宿主确认产品结果。
