# Project Incubator Gate Execution Design

> Phase 4 - Design 的结构化 gate 执行协议设计

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 4 - Design |
| 文档状态 | Active |
| 权威范围 | Project Incubator Skill 1.0 中关键硬性门槛的结构化 gate schema、输入字段、输出枚举、阻断条件、执行顺序、Agent 可继续动作、失败处理、验证方式和后续 Planning / Build 拆解依据 |
| 消费 Phase | Phase 4-9，Phase 5 Planning 与 Phase 6 Build 必读 |
| 更新条件 | Maker 调整关键 gate 集合、gate schema、输出枚举、阻断规则、脚本 / 工具检查器承载、验证方式或后续 Planning / Build 拆解方式 |
| 依赖文档 | `DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`、`DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`、`DOCS/05-planning/ROADMAP.md`、`DOCS/05-planning/MILESTONES.md`、`DOCS/05-planning/VERIFICATION_PLAN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-27 |

## 1. 文档职责

本文档定义 Skill 1.0 的结构化 gate 执行机制。

它修订 Phase 4 原设计中的一个关键缺口：原设计已经确认了高风险动作门禁、硬性门槛矩阵、门槛回应与授权字段，但这些内容主要以自然语言协议存在。自然语言协议可以指导 Agent 行为，却不能保证每个关键门槛都产生非黑即白的命中 / 未命中结果。

本文档把关键门槛从“Agent 应该遵守的协作规则”升级为“Agent 在进入受限动作前先用低成本结构化字段路由，再对命中的 gate 判定并输出结果的执行协议”。

Gate 的目标不是增加上下文消耗，而是提前缩小语义判断范围。gate 应尽量用短字段、枚举、布尔值、路径和状态摘要完成判定；当命中阻断条件时，应立即停止后续动作，避免继续消耗 token 解释、规划或实现越界内容。

本文档不实现脚本、不发布 Skill、不安装 Skill、不创建完整自动化系统。脚本 / 工具检查器如有必要，只在本文档中作为承载设计依据和后续任务拆解输入。

## 2. 修订结论

现有 Phase 4 设计中仍有效的部分：

- Phase 驱动协作、Maker 决策权、文档权威来源、状态入口、Git 验收门、Builder 交接边界仍有效；
- 高风险动作应先暂停、说明风险、提供安全替代动作并等待 Maker 明确授权的交互原则仍有效；
- R1 主运行链路、R2 硬性门槛、R3 Builder 交接闭环作为机制型规划方向仍有效；
- `SKILL/` 当前 Draft 的主流程、入口分流和项目接入方向可作为后续 Build 基线；其中门槛类型、授权字段和验证场景可作为结构化 gate 改造素材来源。

必须修订的部分：

- 不能再把自然语言 Skill reference 视为 Skill 1.0 的最终 gate 承载；
- R2 不能只交付“门槛矩阵”和“回应格式”，必须交付结构化 gate 配置与判定协议；
- Phase 5 不能把“脚本化检查工具”继续放在低优先级或可选事项里一笔带过，必须先判断哪些关键 gate 需要脚本 / 工具检查器承载；
- 后续 Phase 6 Build 不应推翻当前 P6 Skill Draft 的有效主流程，但必须先实现或配置 gate 执行承载，再把自然语言 gate references 改造为结构化 gate 的解释层；
- 验证不能只看文本是否描述了门槛，必须用样例输入断言 gate 输出枚举、阻断状态和允许继续条件。

## 3. 承载类型边界

Skill 1.0 的 gate 机制必须区分以下承载类型，不能把一种承载物的规则套到另一种承载物上。

| 承载类型 | 职责 | 是否可作为 gate 判定权威 |
| --- | --- | --- |
| 自然语言协作协议 | 说明 Maker 与 AI 如何对话、何时解释、何时请求决定 | 否。它只能解释行为，不产生可验证判定结果 |
| Skill runtime reference | 为 Agent 提供运行时步骤、读取策略和行为说明 | 否。它可以调用 gate，但不应独自承担关键 gate 判定 |
| Skill asset / template | 生成项目协议、状态入口或阶段文档的模板资产 | 否。它可包含 gate 字段占位，但不负责判定 |
| 结构化 gate 配置 | 定义 gate id、触发域、输入字段、输出枚举、阻断规则和安全动作 | 是。它是 gate 判定的主要设计承载 |
| 脚本 / 工具检查器 | 读取结构化输入并输出确定枚举、错误或报告 | 是，适用于可由文件、Git、配置或字段完整性验证的 gate |
| 目标项目权威文档 | 保存目标项目事实、状态、范围、设计、Planning 和验证结果 | 是，但只对自身事实有效；不替代 gate schema |
| 目标项目 `AGENTS.md` | 保存该项目本地 Agent 执行协议和 Git / Diff / 写回边界 | 部分。它可要求执行 gate，但不应把所有 gate 配置写成长文 |
| 代码 / 配置 | 实现检查逻辑、配置规则或测试样例 | 是，前提是由 Planning 明确输入输出和验证 |
| Prompt 正文 | 只承载本轮任务 delta、授权、限制或验收要求 | 否。Prompt 不保存项目状态，也不作为 gate 配置 |

结构化 gate 配置是新增的核心承载。脚本 / 工具检查器不是所有 gate 的必选实现，但关键 gate 若存在可机器检查输入，就应优先规划检查器或最小配置验证。

## 3.1 Gate 配置路径可迁移性

未来 Skill gate 配置会随 Skill 一起被带到其他项目中使用，因此配置字段不得指向当前 Project Incubator 仓库内的设计文档路径。

禁止进入 runtime gate 配置的路径类型：

- 当前仓库 Phase 文档路径，例如 `DOCS/04-design/GATE_EXECUTION_DESIGN.md`；
- 当前仓库状态入口路径，例如 `DOCS/PROJECT_STATE.md`；
- 当前仓库架构决策路径，例如 `SPECS/ARCHITECTURE_DECISIONS.md`；
- 当前机器绝对路径；
- 某个目标项目的实例文档路径。

允许进入 runtime gate 配置的引用类型：

- Skill 包内相对路径，例如 `references/gate-response-and-authorization.md`、`gates/gates.yaml`、`tools/check-gates`；
- 稳定 schema 或 spec id，例如 `gate-schema-v1`、`gate-execution-design`；
- gate id、case id、checker id 等不依赖项目路径的稳定标识；
- 由运行时输入提供的目标项目路径字段，例如 `project_root`、`project_state_path`，但这些只能作为每次判定输入，不得固化为某个具体项目路径。

当前 `DOCS/04-design/GATE_EXECUTION_DESIGN.md` 只作为 Project Incubator 自身的 Phase 4 设计依据。Phase 5 可以引用它来规划和生成 Skill 内部配置，但生成后的 gate schema / config 不得保留该文档路径。

## 4. 关键 Gate 集合

Skill 1.0 必须百分之百命中的关键 gate 至少包括：

| Gate ID | 名称 | 必须命中的原因 |
| --- | --- | --- |
| `GATE_PHASE_TRANSITION` | Phase 切换 gate | 防止 AI 未经 Maker 决定改变 Phase、角色、Exit Criteria 或状态入口 |
| `GATE_GIT_WRITE` | Git 写操作 gate | 防止 AI 未授权改变分支、暂存、提交、推送、合并、远端或历史 |
| `GATE_AUTHORITY_SOURCE` | 权威文档 gate | 防止 AI 静默改变权威路径、文档状态、事实归属或索引 |
| `GATE_SCOPE_EXPANSION` | 范围扩大 gate | 防止 AI 把公开、商业化、团队协作、实现深度或新目标混入当前主线 |
| `GATE_BUILDER_HANDOFF` | Builder 交接 gate | 防止任务边界不完整时进入执行 |
| `GATE_UNCLOSED_WORK` | 未闭环工作 gate | 防止未确认基线、未提交 Diff、未推送提交、错误分支或状态冲突污染新任务 |
| `GATE_CONTEXT_INTEGRITY` | 上下文完整性 gate | 防止压缩污染、连续纠偏或状态误判后继续关键写入 |
| `GATE_CARRIER_TYPE` | 承载类型 gate | 防止项目文档、Skill reference、模板、代码、配置和 Prompt 规则互相套用 |
| `GATE_LOCAL_PROTOCOL` | 本地协议 gate | 防止通用 Skill 写法覆盖目标项目 `AGENTS.md`、语言、格式、读写和工具边界 |
| `GATE_CORRECTION_DEPOSITION` | 纠偏沉淀 gate | 防止把单次纠偏、临时偏好或一次错误写成长期规则 |
| `GATE_ARCHITECTURE_DECISION` | 架构决策写回 gate | 防止未经 Maker 批准改写长期架构边界 |

上述集合是 Skill 1.0 的最小关键 gate。Phase 5 可以增加非关键辅助 gate，但不能删除这些 gate，除非 Maker 明确批准降低 Skill 1.0 的验收目标。

## 5. Gate Schema

每个 gate 必须按同一 schema 定义。字段缺失时，gate 本身判定为 `CONFIG_INVALID`，不得继续。

```yaml
gate_id: GATE_GIT_WRITE
gate_name: Git write operation gate
criticality: critical
schema_version: gate-schema-v1
source_reference:
  type: skill_internal_spec
  id: gate-execution-design
runtime_carrier:
  natural_language_reference: references/gate-response-and-authorization.md
  structured_config: gates/gates.yaml
  checker: tools/check-gates
trigger_domains:
  - git
  - branch
  - diff
required_inputs:
  - maker_instruction
  - intended_action
  - target_objects
  - project_state
  - git_state
  - authorization
decision_rules:
  hit_when:
    - intended_action.changes_git_state == true
    - target_objects.includes_branch_or_remote == true
  miss_when:
    - intended_action.read_only == true
    - intended_action.only_reports_manual_commands == true
outputs:
  enum: [HIT_BLOCK, HIT_NEEDS_AUTH, HIT_SAFE_ALTERNATIVE, MISS, INPUT_INCOMPLETE, CONFIG_INVALID]
blocking_outputs: [HIT_BLOCK, HIT_NEEDS_AUTH, INPUT_INCOMPLETE, CONFIG_INVALID]
safe_actions:
  - readonly_git_check
  - report_risk
  - provide_manual_commands
required_authorization_fields:
  - action
  - object
  - scope
  - stop_condition
verification_cases:
  - id: S2_continue_is_not_git_auth
  - id: S3_unclosed_git_blocks_new_write
failure_handling:
  on_input_incomplete: stop_and_request_missing_fields
  on_config_invalid: stop_and_report_config_error
```

Phase 5 可以调整字段名，但不得降低以下最低要求：

- 每个 gate 必须有稳定 `gate_id`；
- 每个 gate 必须使用 Skill 内部可迁移引用，不得写入当前 Project Incubator 仓库的 `DOCS/`、`SPECS/` 或本地绝对路径；
- 每个 gate 必须声明 `required_inputs`；
- 每个 gate 必须有输出枚举；
- 每个 gate 必须声明哪些输出会阻断继续；
- 每个 gate 必须定义安全替代动作；
- 每个 gate 必须映射验证样例；
- 每个 gate 必须说明由自然语言 reference、结构化配置、脚本 / 工具检查器或目标项目权威文档中的哪一种承载。

## 6. 判定输入

Gate 判定输入分为通用输入和 gate 专用输入。

通用输入：

| 输入字段 | 来源 | 用途 |
| --- | --- | --- |
| `maker_instruction` | 本轮 Maker 指令 | 判断 Maker 的新增目标、授权、限制和验收要求 |
| `intended_action` | AI 执行前声明 | 判断下一步是否会改变 Phase、Git、文档、范围或执行状态 |
| `target_objects` | AI 执行前声明 | 说明动作作用于哪些文件、分支、Phase、文档、Ticket 或规则 |
| `project_state` | `DOCS/PROJECT_STATE.md` | 判断当前 Phase、角色、主目标、任务状态、权威文档集合和阻塞项 |
| `local_protocol` | 目标项目 `AGENTS.md` | 判断本地语言、格式、读写、Git 和结束协议 |
| `authority_index` | `PROJECT_STATE.md` 权威文档集合 | 判断目标文档是否是正确权威来源 |
| `authorization` | Maker 明确授权字段 | 判断是否具备动作、对象、范围和必要停止条件 |

专用输入示例：

| Gate | 专用输入 |
| --- | --- |
| `GATE_GIT_WRITE` | `git_state`、当前分支、工作区、暂存区、ahead/behind、未合并分支 |
| `GATE_BUILDER_HANDOFF` | Ticket 字段、验收标准、验证步骤、允许 / 禁止范围 |
| `GATE_CARRIER_TYPE` | 产物承载类型、路径域、适用写法、禁止套用规则 |
| `GATE_ARCHITECTURE_DECISION` | 候选长期规则、现有 Decision 覆盖判断、写入位置 |

如果关键输入无法取得，输出必须是 `INPUT_INCOMPLETE`，而不是由 Agent 猜测。

## 7. 输出枚举

Gate 输出必须使用封闭枚举。

| 输出 | 含义 | 是否阻断 | Agent 可继续动作 |
| --- | --- | --- | --- |
| `MISS` | 当前动作未命中该 gate | 否 | 继续检查下一个 gate |
| `HIT_BLOCK` | 命中 gate，且当前动作禁止继续 | 是 | 只可报告风险、缺口和安全替代动作 |
| `HIT_NEEDS_AUTH` | 命中 gate，缺少 Maker 明确授权 | 是 | 请求动作、对象、范围等授权字段 |
| `HIT_SAFE_ALTERNATIVE` | 命中 gate，但存在不越权安全动作 | 部分 | 只能执行声明的安全替代动作 |
| `INPUT_INCOMPLETE` | 判定输入缺失或不可信 | 是 | 请求补充输入或重新读取权威文档 |
| `CONFIG_INVALID` | gate 配置缺字段、枚举不合法或规则冲突 | 是 | 停止执行并报告配置缺陷 |

禁止使用开放式结果，例如“可能可以继续”“看情况”“建议暂停”。如果确实无法判断，必须输出 `INPUT_INCOMPLETE`。

## 8. Gate 路由与执行顺序

每次受限动作前，Agent 不应全文展开所有 gate。正确流程是先执行低成本 gate router，再只执行命中的候选 gate。

### 8.1 低成本路由

Gate router 只读取或生成最小结构化摘要：

- `intended_action.action_type`：只读、写入、Git、Phase、Builder、Prompt、模板、脚本、架构写回等；
- `target_objects.object_type`：文件、文档、分支、Phase、Ticket、Skill asset、Prompt 正文等；
- `changes`：是否会改变 Git、Phase、权威文档、范围、长期规则、状态入口或 Builder 执行状态；
- `known_state_flags`：是否存在未闭环工作、上下文不可靠、本地协议缺失、授权缺失等；
- `carrier_type`：仅在涉及写入产物时填写；
- `authorization_fields_present`：动作、对象、范围和必要停止条件是否齐全。

Router 输出：

```yaml
applicable_gates:
  - GATE_GIT_WRITE
  - GATE_UNCLOSED_WORK
skipped_gates:
  - gate_id: GATE_PHASE_TRANSITION
    reason: intended_action does not change phase_or_role
```

Router 不应长篇解释，不应读取无关文档，不应把所有 gate 都展开为自然语言推理。无法确定是否适用时，只把相关 gate 标记为 applicable，不扩大到全量 gate。

### 8.2 候选 gate 执行优先级

命中的候选 gate 按以下优先级执行：

1. `GATE_CONTEXT_INTEGRITY`：仅当上下文可靠性存在风险，或本轮将执行关键写入 / Git / Phase / 架构动作时执行；
2. `GATE_LOCAL_PROTOCOL`：仅当本轮涉及目标项目输出、写入、工具使用或格式约束时执行；
3. `GATE_CARRIER_TYPE`：仅当本轮涉及写入产物、生成模板、Skill asset、Prompt、代码或配置时执行；
4. `GATE_UNCLOSED_WORK`：仅当本轮涉及写入、分支创建、任务续作或新任务启动时执行；
5. `GATE_GIT_WRITE`：仅当本轮可能改变 Git 分支、暂存、提交、推送、合并、远端或历史时执行；
6. `GATE_PHASE_TRANSITION`：仅当本轮可能改变 Phase、角色、Exit Criteria、阶段状态或阶段目标时执行；
7. `GATE_AUTHORITY_SOURCE`：仅当本轮可能写入权威文档、改变文档状态、改变权威路径或更新索引时执行；
8. `GATE_SCOPE_EXPANSION`：仅当本轮可能扩大范围、公开、商业化、团队化、目标用户或实现深度时执行；
9. `GATE_BUILDER_HANDOFF`：仅当本轮准备交给 Builder 或启动执行型任务时执行；
10. `GATE_CORRECTION_DEPOSITION`：仅当本轮准备把纠偏、偏好或单次错误沉淀为长期规则时执行；
11. `GATE_ARCHITECTURE_DECISION`：仅当本轮准备写回或修改架构决策时执行。

执行策略：

- Router 只负责选出候选 gate，不得替代候选 gate 的最终判定；
- 一个候选 gate 输出阻断结果，即可停止后续受限动作，也不再执行低优先级候选 gate，除非需要报告同一动作已经明确命中的其他高优先级阻断；
- 多个 gate 同时命中时，报告最高阻断级别和必要的命中 gate，不展开无关 gate；
- `CONFIG_INVALID` 高于 `INPUT_INCOMPLETE`，二者都高于授权不足；
- 只有所有候选 gate 为 `MISS`，或命中项仅允许安全替代动作且本轮只执行该替代动作，Agent 才可继续；
- 被 router 明确跳过的 gate 不需要输出 `MISS`，只需要保留短理由，避免额外 token 消耗。

## 9. Agent 可继续动作

Gate 阻断后，Agent 仍可执行以下动作：

- 只读检查文件、状态或 Git；
- 报告命中的 gate、输入、输出枚举和阻断原因；
- 提供 Maker 手动命令或决策选项；
- 请求缺失授权字段；
- 输出最小恢复入口；
- 修正当前 Draft 中不改变权威边界的局部文本；
- 更新已确认的状态入口事实，前提是该更新本身未被 gate 阻断。

Gate 阻断后，Agent 不得继续：

- 写入未授权文件；
- 切换 Phase；
- 交给 Builder；
- 暂存、提交、推送、合并或清理分支；
- 改变权威路径、文档状态或长期规则；
- 把 Prompt、Skill reference、模板和项目文档规则互相套用。

## 10. 失败处理

| 失败类型 | 处理方式 |
| --- | --- |
| 输入缺失 | 输出 `INPUT_INCOMPLETE`，列出缺失字段，停止受限动作 |
| 配置缺陷 | 输出 `CONFIG_INVALID`，报告 gate id 和缺陷字段，停止所有依赖该 gate 的动作 |
| 授权不足 | 输出 `HIT_NEEDS_AUTH`，请求动作、对象、范围和必要停止条件 |
| 权威冲突 | 输出 `HIT_BLOCK`，报告冲突文件、内容和影响，等待 Maker 决定 |
| 脚本 / 检查器失败 | 视为 `INPUT_INCOMPLETE` 或 `CONFIG_INVALID`，不得用自然语言猜测补过 |
| 验证样例失败 | 回到 Phase 5 对应 Ticket 重拆，不进入 Build |

## 11. 验证方式

Gate 验证必须从“文本描述完整”升级为“输入输出可断言”。

每个关键 gate 至少需要：

- 一个命中样例；
- 一个未命中样例；
- 一个输入缺失样例；
- 一个授权不足样例；
- 一个安全替代动作样例；
- 明确预期输出枚举；
- 明确是否阻断；
- 明确 Agent 下一步允许动作。

Gate router 还必须具备跳过样例：给定一个只涉及 Git 的动作，验证输出只包含 Git / 未闭环相关候选 gate，并为 Phase、Builder、架构决策等无关 gate 给出短跳过理由。通过标准不是“所有 gate 都被执行”，而是“无关 gate 未展开，相关 gate 足以阻断后续 token 消耗”。

最小验证样例格式：

```yaml
case_id: S2_continue_is_not_git_auth
gate_id: GATE_GIT_WRITE
input:
  maker_instruction: "继续"
  intended_action:
    changes_git_state: true
    action: "commit"
  authorization:
    action: null
    object: null
    scope: null
expected:
  applicable_gates:
    - GATE_GIT_WRITE
  output: HIT_NEEDS_AUTH
  blocks: true
  allowed_next_actions:
    - request_authorization_fields
    - provide_manual_git_commands
```

Phase 5 必须基于本文档重写 `VERIFICATION_PLAN.md` 和 R2 / R3 Ticket，使 S1-S8 从自然语言场景升级为可判定样例。

## 12. 脚本 / 工具检查器判断

本任务不实现脚本 / 工具检查器，但设计结论是：Skill 1.0 至少需要为可机器检查的关键 gate 规划检查器或等价结构化验证。

优先适合检查器承载的 gate：

- `GATE_GIT_WRITE`；
- `GATE_UNCLOSED_WORK`；
- `GATE_AUTHORITY_SOURCE`；
- `GATE_BUILDER_HANDOFF`；
- `GATE_CARRIER_TYPE`；
- `GATE_LOCAL_PROTOCOL`；
- `GATE_ARCHITECTURE_DECISION` 的候选字段完整性检查。

主要保留为结构化配置 + 自然语言判断的 gate：

- `GATE_SCOPE_EXPANSION`；
- `GATE_CONTEXT_INTEGRITY`；
- `GATE_CORRECTION_DEPOSITION`。

即使暂不脚本化，也必须有结构化配置和验证样例。没有结构化配置的自然语言 reference 不得作为关键 gate 的最终验收承载。

## 13. Phase 5 拆解输入

Phase 5 必须基于本文档拆解以下内容：

- `ROADMAP.md`：把 R2 从“硬性门槛矩阵”升级为“结构化 gate 执行协议与配置机制”；
- `MILESTONES.md`：新增或重定义 gate config / checker planning 里程碑，不再把脚本推迟为低优先级实现细节；
- `VERIFICATION_PLAN.md`：把 S1-S8 改为 gate case，包含输入字段、输出枚举、阻断结果和允许动作；
- `TICKET-R2-01-hard-gate-matrix.md`：拆解为 gate router / gate schema / gate registry / critical gate set；
- `TICKET-R2-02-gate-response-and-authorization.md`：基于 gate 输出枚举定义回应，不再独立凭自然语言判断；
- `TICKET-R3-01-builder-handoff-checklist.md`：升级为 `GATE_BUILDER_HANDOFF` 的结构化输入和判定；
- `TICKET-R3-02-builder-return-and-review.md`：补充 Builder 返回后是否触发权威文档、Git、状态入口和验收 gate；
- 后续新增 Ticket：设计 gate 配置文件、最小检查器、gate case fixtures 和 P6 Draft gate 缺口验证。

Phase 5 完成上述拆解前，不得进入下一轮 gate Build 验收，也不得把当前 `SKILL/` Draft 中的自然语言 gate references 当成可验收 Skill 1.0 gate 承载；其有效主流程可作为后续 Build 基线复用。

## 14. Maker 待确认事项

Maker 需要确认：

- 本文档列出的关键 gate 是否就是 Skill 1.0 必须百分之百命中的最小集合；
- 输出枚举是否足够非黑即白；
- 阻断规则是否允许 Agent 在安全替代动作内继续；
- 是否接受“结构化 gate 配置 + 部分脚本 / 工具检查器 + 自然语言 reference 解释”的承载组合；
- Phase 5 是否按本文档列出的范围拆解 Planning 与 Ticket。
