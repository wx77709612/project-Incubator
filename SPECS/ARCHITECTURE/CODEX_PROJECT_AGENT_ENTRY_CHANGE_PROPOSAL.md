# Codex Managed Project 协作入口初始化变更提案

状态：APPROVED；Maker 于 2026-10-23 明确批准本书面提案。批准架构方向，不授权修改 Plugin 代码、安装包或真实 Managed Project；实施仍须通过下游规格与计划 Gate。

## 1. 问题与目标

Plugin 0.3.x 已将 `.project-incubator/activation.json`、`state.json`、`latest-receipt.json` 确立为唯一权威集合，`project-incubator-router` 是唯一现行入口。这些决定继续有效。当前 `initialize_project` 只创建三个 JSON；项目根目录缺少 Codex 原生 `AGENTS.md`，后续任务不会自动获得项目协作入口及默认中文规则。

旧版曾分别提供 Skill Package 内的 `PROJECT_INCUBATOR/AGENTS.md` 和面向 Managed Project 的 `AGENTS.template.md` / `BOOTSTRAP_HOST_INTEGRATION`。两者职责不同。Kernel 对齐正确淘汰了依赖旧 Python Runtime、四份 Markdown Core Context 和旧 Skill 的执行路径，却没有把“旧实现退役”和“宿主入口能力是否保留”拆开决策，也没有把“新项目获得项目级 Codex 入口”迁移到初始化契约。旧 Feature 001 在活动层仍标为 `NOT_IMPLEMENTED` 且限定为 Legacy 语义，不得直接作为 Plugin 0.3.x 实现依据。具体审查失误见[影响分析](CODEX_PROJECT_AGENT_ENTRY_IMPACT_ANALYSIS.md#11-为什么设计审查会漏掉它)。

目标：使用当前 Codex Plugin 成功初始化一个根目录尚无 `AGENTS.md` 的 Managed Project 时，项目根目录必须存在经过回读验证的 `AGENTS.md`。它仅指导后续 Agent 使用 Router/Kernel，不成为第四份权威状态文件。既有 `AGENTS.md` 不覆盖、不自动追加。

## 2. 已考虑方案

| 方案 | 优点 | 不足 | 结论 |
| --- | --- | --- | --- |
| 仅在 Router Skill 中要求 Agent 事后写文件 | 代码变化小 | `initialize_project` 返回成功后仍可能没有文件；Agent 遗漏、写入失败及后续恢复无法由初始化契约保证 | 不采用 |
| 将入口创建纳入 Plugin 初始化的闭合条件 | 成功返回即可验证文件存在；与授权初始化同一时机；可覆盖所有项目类型 | 需要扩展初始化副作用、失败恢复及返回契约 | 推荐 |
| 增加独立 Host Bootstrap Tool，由 Router 在初始化后调用 | 可单独重试 | 两次调用之间存在已激活但缺入口的状态；不能单独满足本次“初始化即具备”的目标 | 不作为主路径；后续存量修复另行设计 |

## 3. 拟议架构决定

### 3.1 适用范围与权威

本提案只约束以 `.codex-plugin` 形式分发的现行 Codex Plugin 初始化路径；不宣称通用 MCP 客户端也必须生成 Codex 文件。Codex 宿主身份来自本分发边界，不从 `host_profile_id` 推断。`web-product` 的 `host_profile_id = null` 不妨碍 Codex 项目级入口；Project Type Host Profile 和 Agent Host Environment 是不同维度。

插件包应自包含一份当前语义的简体中文 `AGENTS.md` 模板。该模板只包含稳定规则：Plugin Router 入口、`inspect_project` 恢复、三个 JSON 的职责、Maker/Agent/Kernel 边界、受控变更和 Receipt 验证、人类可读文本默认简体中文；不得复制 Current Phase、Task、Gate、Decision 或其他动态项目状态，也不得引用旧 Python Runtime、旧 Skill、四份 Markdown 状态模型或研发仓库中的包外文件。

生成的 `AGENTS.md` 是普通宿主集成 Artifact，不加入权威集合，不参与项目 revision、Receipt 哈希或阶段判定。它不能代替 `inspect_project`，不能授权状态 Mutation。现有 Decision 015 关于唯一入口和三个权威文件的决定保持不变；下游 Architecture Decision 应记录本补充边界。

### 3.2 初始化结果

- 目标不存在 `AGENTS.md`：初始化流程以排他创建方式写入模板并回读验证；只有入口和三个 JSON 权威文件均闭合后，`initialize_project` 才能返回成功。
- 目标已存在普通文件 `AGENTS.md`：绝不覆盖、追加或自动合并；权威初始化可完成，但结果必须明确报告 `EXISTING_REVIEW_REQUIRED`，提示 Maker 人工核对现有规则与当前 Router/Kernel 是否兼容，不得声称已完成项目级指导集成。
- 目标路径是目录、链接或不可读文件：初始化失败关闭，返回稳定的 `AGENT_ENTRY_PATH_UNSAFE`；不消费 Pending Activation，不覆盖目标，也不报告成功 Receipt。
- 排他创建时遭遇并发 `EEXIST`：初始化失败关闭并报告 `AGENT_ENTRY_CONFLICT`，不得假定新出现的文件符合模板，也不得删除竞争者的文件。
- 对于原本不存在的入口，创建或回读失败时初始化失败关闭：不返回成功 Receipt，不消费 Pending Activation，并恢复本次已写入的权威文件及本次创建且仍与创建时内容一致的入口；如果入口已被外部修改或恢复不完整，则保留冲突内容、报告具体残留和人工恢复要求，不得宣称项目未初始化或已完整初始化。

`initialize_project` 的返回应同时给出权威 Receipt 与独立的 Agent Entry 结果。Agent Entry 结果不是 Gate Result，也不更改 State Schema。具体字段、错误码和恢复顺序由下游 Contract/Runtime 定义。

### 3.3 既有项目与版本边界

不自动修改任何已经激活的 Managed Project；其现有阶段、Pending Request 与 Receipt 保持不变。存量项目补齐入口应走单独、显式的修复流程，经 Maker 决定后再设计，不能通过重新运行 `initialize_project` 或直接改三个权威 JSON 实现。本提案不更改 Project Type、阶段、Gate、授权协议、请求摘要算法或旧 V1.x / RC 历史基线。

## 4. 验收上限

下游计划至少覆盖：无入口新项目的真实 `prepare_activation` → Maker 授权 → `initialize_project` → 文件与 Receipt 回读；已有文件不变；入口写入失败与权威写入失败的恢复；三种 Project Type；候选包包含模板且在仓库外安装后可用；生成文本不包含旧权威指令且明确简体中文；当前任务与后续新任务的加载时机区别。

只用单元测试或只看到模板在源码中，均不能证明“安装后的 Plugin 初始化实际生成文件”。不得把生成文件当成修复既有英文计划的追溯性保证。

## 5. 审批与实施 Gate

Maker 批准本提案后，按顺序更新影响分析、Architecture Decision、Design、Contract、Runtime Specification、Implementation Plan 与 Acceptance Test Plan；其中任何新的权威边界或失败语义必须回到本层确认。只有书面规格和两份计划获批后，才能修改 Plugin、Router、模板、测试及安装候选。Implementation Repository 的规格审批不使用 Managed Project 的 `request_id` / `scope_digest`。
