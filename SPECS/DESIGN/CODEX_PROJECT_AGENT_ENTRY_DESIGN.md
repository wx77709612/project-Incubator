# Codex 协作入口与权威恢复设计

状态：DRAFT / MAKER REVIEW REQUIRED；上游：[Decision 016](../ARCHITECTURE/ARCHITECTURE_DECISIONS.md#decision-016codex-协作入口与-managed-project-权威恢复)。

## 1. 两类对象

- **权威集合**：`.project-incubator/activation.json`、`state.json`、`latest-receipt.json`。Kernel 负责校验和写入。
- **协作入口**：项目根目录 `AGENTS.md`。它为 Codex 提供稳定指导，但不保存项目阶段、Decision、Gate 或 Receipt。

二者在同一次项目工作中都可能被发现缺失，但不得混成同一种状态或同一套 revision。

## 2. 任务首次进入

“任务首次进入”是 Router 在同一 Codex 任务／聊天中第一次接管当前项目。Router 只在此时请求一次 Agent Entry 检查；后续轮次和后续 Plugin 调用复用当前任务已经得到的结果。切换 `project_root` 后，对新项目重新执行一次。

Agent Entry 检查只返回：

- `CURRENT`：已有普通文件与包内模板相同；
- `EXISTING_REVIEW_REQUIRED`：已有普通文件但内容不同，不修改；
- `MISSING`：文件不存在，可向 Maker 提出补建；
- 不安全路径或读取失败：返回稳定错误并停止入口处理。

这项检查不调用 `inspect_project`，不读取三个 JSON，也不写持久“已检查”标记。重复调用是安全的，但 Router 指导不得要求重复调用。

## 3. AGENTS 创建

首次接入的激活授权包含“缺失时创建入口”，无需第二次批准。已接入项目缺失入口时，Router 展示补建请求；Maker 明确确认后才创建。

包内模板使用简体中文，只描述 Router、按需 `inspect_project`、三个 JSON 职责、Maker／Agent／Kernel 边界、受控写入、Receipt 和默认中文规则。它不包含动态项目状态，不引用 Legacy Python Runtime、旧 Markdown Core Context 或包外规格。

创建使用排他写入并回读。已有文件永不自动覆盖、追加或合并。当前任务中途创建后，Agent 显式读取一次；下一个新任务由 Codex 正常加载。

## 4. 权威 JSON 的按需验证

不为三个 JSON 增加任务入口预检。现有操作在实际需要状态时读取：

- 状态或恢复查询使用 `inspect_project`；
- 普通变更使用现有 `prepare_change`、`commit_change`、`decline_change`；
- 每次写入继续回读并验证 revision、state hash 和 Receipt。

完整权威集合验证通过时，行为不变。缺失、残缺、Schema 错误、项目 ID 不一致或 Receipt 不可验证时，当前操作失败关闭，并允许 Router 提出权威恢复。

## 5. 权威恢复请求

权威恢复使用 Runtime Data 保存短期请求，因为损坏的 `state.json` 不能承载 Pending Request。

准备恢复时，Kernel：

1. 分别读取三个路径，记录 `MISSING`、`VALID` 或具体错误，并计算所有现存原始字节的 SHA-256；
2. 接收 Agent 根据 Artifact、Evidence、可用旧资料和 Maker 已表达事实形成的完整 Activation 与 State 候选；
3. 校验候选 Schema、路由和阶段，清空旧 `pending_requests`；
4. 将当前文件指纹、候选状态和操作 `RECOVER_PROJECT_AUTHORITY` 纳入 `scope_digest`，返回短期 `request_id`。

Maker 下一轮明确批准请求编号与范围后，Kernel 重新核对文件指纹。任何文件新增、删除或字节变化都返回 `RECOVERY_SOURCE_CHANGED`，不写入。

## 6. 恢复提交

- 现存 `state.json` 可按现行 Schema 解析时，候选 revision 必须是现存 revision + 1，Receipt 的 previous state 指向该 State。
- State 缺失或不可解析时，候选 revision 必须为 0，Receipt 的 previous state 为 null；这是新的恢复基线，不代表历史从未存在。
- Kernel 写入完整 Activation、State 和最新 Receipt，逐项回读并验证。State 的 `last_change.operation` 固定为 `RECOVER_PROJECT_AUTHORITY`。
- 写入中发生可捕获错误时恢复操作前原始字节；若不能闭合，报告残留路径，不宣称恢复成功。
- 恢复成功后，任何旧 Pending Request 都必须按现行流程重新提出。

没有足够证据形成完整候选状态时，Agent 只报告缺口并等待 Maker，不调用准备或提交恢复。

## 7. 非目标

不扫描其他项目；不新增项目阶段、Gate 或恢复阶段；不自动更新已有 `AGENTS.md`；不让 `inspect_project` 产生写入；不将聊天、计划或旧 Markdown 直接升级为权威；不改变正常项目的 Router、Workflow 或状态变更语义。
