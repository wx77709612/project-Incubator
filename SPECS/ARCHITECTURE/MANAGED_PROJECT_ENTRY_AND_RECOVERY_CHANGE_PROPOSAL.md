# Managed Project 权威恢复与 AGENTS 补齐提案

状态：APPROVED；Maker 于 2026-10-23 确认本文所述检查节奏与处理边界。批准架构方向，不直接授权产品代码或真实 Managed Project 写入。

## 1. 要解决的问题

Plugin 0.3.x 的“恢复项目”只表示：三个权威 JSON 完整且可验证时，通过 `inspect_project` 重新取得当前项目状态。它没有定义权威 JSON 缺失、残缺或验证失败后的恢复操作。同时，首次接入和已接入项目都可能缺少根目录 `AGENTS.md`。

本次只补两项能力：

1. **权威状态恢复**：实际使用三个 JSON 时发现异常，先报告，再由 Agent 根据项目证据提出恢复状态，Maker 确认后由 Kernel 受控建立完整权威集合。
2. **协作入口补齐**：当前 Codex 任务第一次进入项目并使用 Project Incubator 时检查一次 `AGENTS.md`；缺失时提出补建，Maker 确认后从插件中文模板创建。

不新增项目阶段、Gate 或日常 Workflow，不批量扫描其他项目，也不要求每次 Plugin 调用重复检查。

## 2. 已选择的检查节奏

| 方案 | 结果 |
| --- | --- |
| 每次 Plugin 调用都检查四个文件 | 拒绝：重复 MCP 调用和摘要会增加延迟与上下文消耗 |
| 每个任务第一次进入时检查四个文件并缓存 | 拒绝：三个 JSON 尚未使用时做预检没有必要 |
| `AGENTS.md` 每任务首次进入检查一次；三个 JSON 在实际使用时验证 | 采用：符合 Codex 加载方式，也复用 Kernel 现有按需校验 |

“当前任务”指同一个 Codex 任务／聊天上下文。项目根目录变化时，视为进入另一个项目。`AGENTS.md` 的检查结果只保留在当前任务上下文，不写入权威 JSON，也不建立新的持久状态。

## 3. 首次接入

全新项目使用 `NEW_PROJECT`，已有产品首次采用 Project Incubator 使用 `ADOPT_EXISTING`；两者对 Plugin 都属于首次建立权威状态，继续使用现行 `prepare_activation`、Maker 授权和 `initialize_project`。

首次接入时：

- Kernel 创建三个权威 JSON；
- 根目录没有 `AGENTS.md` 时，从插件包内稳定的简体中文模板创建并回读；
- 已有 `AGENTS.md` 时不覆盖，报告与当前模板是否不同，由 Maker 决定后续改动方向；
- 只有权威写入、Receipt 和入口处理均闭合后，首次接入才报告完整成功。

## 4. 已接入项目的后续任务

当前任务第一次使用 Project Incubator 时，只检查一次 `AGENTS.md`：

- 存在时不在后续 Plugin 调用中重复读取；
- 缺失或激活后被删除时，提出补建，Maker 确认后排他创建并回读；
- 已有文件与模板不同，不自动覆盖或合并；
- 当前任务中途才创建的文件由当前 Agent 显式读取一次，后续新任务由 Codex 原生加载。

三个权威 JSON 不做额外入口预检。`inspect_project`、状态查询或状态变更在真正读取它们时照常验证；若发现缺失、残缺、Schema 错误或 Receipt 不一致，停止受影响工作并进入权威恢复提案。

## 5. 权威状态恢复

恢复遵循一个简单的两步授权：

1. Kernel 逐文件报告当前事实；Agent 根据可用 JSON、项目 Artifact、Evidence 和旧版资料提出完整的 Activation 与当前 State，明确哪些内容是证据支持、哪些需要 Maker 重新确认。
2. Maker 确认请求编号和范围后，Kernel 重新核对文件未被外部改变，受控写入三个 JSON、回读并生成一张新的 `RECOVER_PROJECT_AUTHORITY` Receipt。

若现存 `state.json` 仍可验证其结构，恢复作为下一次 revision；若 State 已缺失或不可解析，则建立 revision 0 的恢复基线。旧 Pending Request 不自动继承，必须在恢复后重新提出。新 Receipt 只证明本次恢复，不伪造丢失的历史。

资料冲突或不足时只报告问题和候选状态，不写入。恢复接口不能用于普通状态变更，也不能绕过首次接入；三个 JSON 仍只由 Kernel 写入。

## 6. 不变边界

- `activation.json`、`state.json`、`latest-receipt.json` 仍是唯一权威集合；`AGENTS.md` 不是第四份权威。
- `inspect_project` 保持只读；正常 `prepare_change`、`commit_change`、`decline_change`、Gate、Transition 和各项目类型阶段语义不变。
- 不从聊天记录直接补写权威状态，不自动修改已有 `AGENTS.md`，不修改 `_V*`。
- 检查和恢复只针对当前任务正在处理的项目，不扫描全部已管理项目。

下游 Design、Contract、Runtime、Implementation Plan 与 Acceptance Test Plan 必须保持上述最小范围，并证明正常项目没有新增重复检查。
