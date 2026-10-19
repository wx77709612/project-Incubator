---
name: sims-4-host-profile
description: 在已选择 mod-incubator 且目标宿主为 The Sims 4 时使用。把通用 Mod 验证具体化为游戏版本、补丁版本、Script/Package 包、Mods 安装结构、加载诊断和与 Capability 相关的游戏内观察。
---

# Sims 4 Host Profile

## 当前 Kernel 权威与恢复

Plugin Router `project-incubator-router` 是唯一现行入口。权威集合为 `.project-incubator/activation.json`、`.project-incubator/state.json` 和 `.project-incubator/latest-receipt.json`；State 是唯一业务状态，Activation 约束身份/路由，Receipt 证明闭合。临时 Runtime Data 和 Markdown Artifact 不替代它们。

恢复与状态查询先调用 `inspect_project`，验证失败时报告稳定错误并停止受影响推进，不从聊天补全。只使用已验证路由的 Child Skill/Host Profile；不得直接编辑权威文件。所有受控变更经现行 Kernel，提交后确认 revision、回读与 Receipt 一致再报告完成。缺少 Plugin/MCP 时停止，不调用旧执行资产。


## 适用边界

本 Profile 只细化 `mod-incubator`，不得改变 Kernel Authorization、Receipt、Evidence 或 Gate 权限。调用前确认激活状态中的 `project_type_id=mod` 且 `host_profile_id=sims-4`。

## 固定上下文

每项目标环境 Evidence 必须记录：

- 游戏版本与补丁版本；
- Mod 类型：`SCRIPT`、`PACKAGE` 或两者；
- 最终构建包内容；
- Mods 目录安装结构；
- 加载日志与异常入口。

## 按 Capability 选择检查

- 涉及 UI 时检查 UI 可见结果；
- 涉及玩家交互时检查触发、结果和副作用；
- 涉及持久化时检查存档、重载与后续状态污染；
- 声明跨版本支持时才建立兼容矩阵。

不相关 Capability 不得被强制要求 UI、存档或跨版本测试。Script 或 Package 可被加载只证明 Availability，不自动提升 Semantic Capability。

## Maker 观察

Agent 提供狭窄场景和可区分假设的观察格式，Maker 只需回报：场景、游戏/补丁版本、观察结果、失败或副作用、证据引用。Agent 负责结构化记录、判断 Evidence 上限和决定是否需要 `MODEL_REVIEW`，不得把根因推导转嫁给 Maker。
