# Project Incubator Technical Design

> Phase 4 — Design 的技术方案设计

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 4 — Design |
| 文档状态 | Active |
| 权威范围 | Project Incubator Skill 1.0 的技术方向、系统边界、资产分工、运行时读取与写入策略、工具权限和进入 Phase 5 的技术拆解输入 |
| 消费 Phase | Phase 4–9，按需读取 |
| 更新条件 | Maker 调整 Skill 技术方向、系统边界、资产分工、工具权限、Git 边界或技术拆解输入 |
| 依赖文档 | `DOCS/04-design/SCOPE.md`、`DOCS/04-design/DESIGN.md`、`DOCS/04-design/SKILL_DESIGN.md`、`FRAMEWORK/Codex-Skill-Specification.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-23 |

## 1. 文档职责

本文档定义 Project Incubator Skill 1.0 的技术方案设计。

本文档不写具体代码，不生成最终 `SKILL.md`，不决定安装发布命令，也不拆分具体 Build Tickets。它负责说明技术方向、边界、资产分工和 Phase 5 可拆解的技术任务类型。

## 2. 技术设计目标

Skill 1.0 的技术设计目标是把当前手动可运行的 Project Incubator 流程，转化为未来可固化为 Codex Skill 的结构。

技术设计应满足：

- 不依赖聊天记忆恢复项目；
- 能根据项目状态加载最小必要上下文；
- 能按 Phase 调整 AI 角色和协作规则；
- 能复用 Framework、模板和脚本资产；
- 能在写入前执行安全检查；
- 能保留 Maker 的 Diff 审阅和 Git 决策权；
- 能在高风险动作前执行门禁检查；
- 能支持不同项目类型选择不同 Design 文档组合。

## 3. 系统边界

Project Incubator Skill 1.0 由以下边界组成：

- Skill 指令层：未来的 `SKILL.md`，负责触发规则、读取顺序、协作协议和阶段行为；
- Framework 规则层：当前 `FRAMEWORK/` 中的 Phase、Role、Document、Skill 规则；
- 模板资产层：当前 `TEMPLATES/` 中的文档和任务 Prompt 模板；
- 项目状态层：每个项目自己的 `DOCS/PROJECT_STATE.md`；
- 项目文档层：每个项目自己的 `DOCS/<phase>/` 阶段交付物；
- 执行协议层：项目根目录 `AGENTS.md`；
- 可选脚本层：未来用于校验、生成、同步或检查文档的脚本；
- Git 边界层：分支、Diff、提交、推送和合并规则。

Skill 不应把所有能力都做成脚本。对话规则、文档模板和状态入口仍是核心资产；脚本只在能降低重复劳动或减少错误时引入。

## 4. 资产分工

Skill 1.0 的资产分工如下：

| 资产 | 职责 |
| --- | --- |
| `SKILL.md` | 定义 Skill 触发场景、读取顺序、Phase 行为和执行约束 |
| `FRAMEWORK/Phase-System.md` | 定义十个 Phase 的 Objective、角色、交付物和 Exit Criteria |
| `FRAMEWORK/Role-System.md` | 定义 Maker、AI Collaborator、AI Builder 与角色切换 |
| `FRAMEWORK/Document-System.md` | 定义文档生命周期、权威来源和读写规则 |
| `TEMPLATES/` | 提供阶段文档、任务 Prompt 或元数据模板 |
| `AGENTS.md` | 提供具体项目内 Agent 启动、Git 和收尾协议 |
| `DOCS/PROJECT_STATE.md` | 提供具体项目状态恢复入口 |
| 写回规则资产 | 定义状态写回、文档写回、写后检查和高权威文档候选写回规则；未来应进入 Framework 文档规则或 Skill references |
| 高风险动作门禁资产 | 定义 Git、Phase、权威文档、范围扩大和破坏性操作的执行前检查；未来应进入 Agent 协议、Skill references 或脚本化检查 |
| 可选脚本 | 执行结构检查、模板生成、状态一致性检查或 Git 只读检查 |

Phase 5 需要判断哪些资产直接复用，哪些需要重写为 Skill 资产，哪些只保留为项目内治理规则。

## 5. 运行时读取策略

Skill 运行时应按最小必要上下文读取，并区分不同文档的读取目的。

### 5.1 启动入口

每轮启动必须先读取：

1. 项目根目录 `AGENTS.md`；
2. `DOCS/PROJECT_STATE.md`。

这两者用于确认当前项目、Phase、AI 角色、主目标、权威文档集合、Git 规则和下一步。若状态入口缺失、冲突或指向不存在的文档，应停止阶段性推进并请求 Maker 决定。

### 5.2 架构决策读取

`SPECS/ARCHITECTURE_DECISIONS.md` 不应作为普通上下文事实库全文长期塞入对话。它的主要作用是 **不可静默改变的架构边界守卫**。

Skill 1.0 可以采用两级读取：

- 启动时读取文档职责和 Decision 标题，确认是否存在与本轮任务相关的硬边界；
- 当本轮任务涉及 Framework、目录结构、角色边界、文档规则、Git 治理、项目类型或 Skill 化方向时，再读取相关 Decision 正文。

在当前仓库规则尚未更新前，`AGENTS.md` 仍要求启动时读取该文档；本文档描述的是 Skill 1.0 期望达到的更精细读取策略。

### 5.3 Framework 规则读取

Framework 文档应优先定向读取与当前阶段有关的章节：

- `FRAMEWORK/Phase-System.md`：读取当前 Phase 的 Objective、Maker Role、AI Role、Conversation Contract、Deliverables 和 Exit Criteria；
- `FRAMEWORK/Role-System.md`：读取当前 AI 角色、Maker 规则、AI Collaborator / Builder 边界和角色切换规则；
- `FRAMEWORK/Document-System.md`：读取文档读取、创建、更新、权威来源和当前任务涉及的文档类型规则。

Skill 不应默认把所有 Phase 和所有角色规则全文当作同等上下文。只有当章节定位失败、文档结构冲突、需要修改 Framework，或需要做跨 Phase 设计时，才全文读取相关文件。

### 5.4 项目权威文档读取

`PROJECT_STATE.md` 指向的当前权威文档集合应按“本轮读取要求”加载：

- 标记为当前 Phase 必读的文档，应读取；
- 标记为按需读取的文档，只在本轮任务涉及对应事实时读取；
- 本轮任务直接相关的设计、范围、Ticket、验证或交接文档，应读取；
- 不应通过递归扫描目录来猜测当前上下文。

### 5.5 Maker 本轮指令

Maker 本轮新增指令是当前任务的增量输入。它不能覆盖已确认架构、Phase 规则、角色边界或项目状态；若存在冲突，Skill 应指出冲突并请求 Maker 决定。

### 5.6 定向读取保障

Skill 1.0 不能只依赖 Prompt 要求 Agent “自觉”定向读取。Phase 5 应拆解出文档索引与读取校验相关任务，使定向读取具备结构和验证支撑。

候选保障包括：

- 为 Framework 文档提供稳定标题、章节编号和可定位锚点；
- 在 `PROJECT_STATE.md` 中维护权威文档集合和本轮读取要求；
- 在 Skill 启动协议中要求说明本轮实际读取了哪些文档或章节；
- 对全文读取要求说明理由，例如章节定位失败、文档结构冲突、跨 Phase 设计或 Framework 变更；
- 设计脚本或清单检查必读文档是否存在、索引是否有效、按需文档是否被无故提升为必读；
- 在任务收尾时报告本轮是否存在超范围读取或上下文膨胀风险。

Phase 5 至少应拆解一个定向读取保障任务，用于定义文档索引格式、章节定位规则、全文读取例外条件和验证方式。

## 6. 写入策略

Skill 写入文件前必须判断：

- 本轮任务是否需要写入；
- 写入是否属于当前 Phase 和当前目标；
- 目标文档是否是正确的权威来源；
- 是否需要创建工作分支；
- 是否存在未闭环 Diff、未推送提交或无关任务分支；
- 是否需要 Maker 先做方向性决定。

写入后应保留未提交 Diff，标记任务为 Ready for Maker Review，等待 Maker 审阅。

写入后的文档卫生检查由写回规则资产定义。Phase 5 应判断其长期承载位置，优先考虑 Framework 文档规则或 Skill references，并将检查项拆解为清单或脚本辅助能力。

### 6.1 高风险动作门禁实现

Skill 1.0 不应只依赖 Agent 自觉遵守高风险边界。Phase 5 应拆解门禁检查任务，使高风险动作在执行前至少经过清单校验，必要时由脚本辅助。

门禁检查应覆盖：

- 动作是否会改变 Git 暂存区、提交历史、分支或远端；
- 动作是否会改变 Phase、角色、任务状态或 Exit Criteria；
- 动作是否会改变权威文档状态、模板规则或架构边界；
- 动作是否会扩大范围、项目类型、实现深度或发布边界；
- Maker 是否明确授权 AI 执行具体动作；
- 当前是否位于允许执行该动作的分支和任务范围；
- 当前是否存在未闭环任务、无关 Diff、未推送提交、错误分支或状态入口冲突；
- 授权是否只是结果确认、方向确认或继续推进，而非 AI 执行具体动作的授权；
- 是否存在更安全的默认处理方式，例如只读检查、提供命令清单或请求 Maker 手动操作。

Git Guard 是 Phase 5 的候选任务。它可以先以检查清单形式实现，后续再评估是否脚本化。脚本化时不得绕过 Maker 授权，只能在执行前阻止或提示风险。

高风险动作门禁在 Phase 5 至少应形成可验证任务：给定若干 Maker 指令和当前项目状态样例，检查结果应能判断是否触发门禁、默认安全处理方式是什么、是否允许 AI 执行、执行前应停止在哪个风险点。

## 7. 工具与脚本策略

Skill 1.0 可以逐步引入脚本，但脚本不是第一原则。

适合脚本化的能力包括：

- 检查必读文档是否存在；
- 检查 `PROJECT_STATE.md` 权威文档索引是否指向真实文件；
- 生成带元数据的阶段文档草案；
- 检查 Draft / Active / Superseded / Archived 状态一致性；
- 执行只读 Git 健康检查；
- 汇总 Diff 范围供 Maker 审阅。

不应优先脚本化的能力包括：

- Maker 的方向选择；
- Phase 切换决定；
- 成功标准判断；
- 是否商业化或公开发布；
- 复杂设计取舍。

## 8. Git 技术边界

Skill 可以执行只读 Git 检查，并在获得授权后进行符合项目规则的文件写入。

默认不执行：

- 暂存；
- 提交；
- 推送；
- 合并；
- 删除分支；
- 重置历史；
- force push；
- 自动解决方向性冲突。

这些操作由 Maker 手动完成，除非 Maker 对具体操作另行明确授权。

## 9. Phase 5 技术拆解输入

Phase 5 可以基于本文档拆解以下技术任务类别：

- Skill 资产结构设计与创建；
- Framework 文档向 Skill 指令的迁移；
- 模板资产整理；
- 状态恢复流程实现；
- Phase 规则读取与校验；
- 新任务 Prompt 生成流程；
- 分叉分类辅助流程；
- Git 只读检查辅助；
- 高风险动作门禁检查；
- 文档状态一致性检查；
- 模拟项目验证。

每个技术任务都必须有明确输入、输出、允许修改范围、验收标准和验证步骤。

## 10. 当前暂不决定的技术事项

以下事项保留到 Phase 5 或 Phase 6：

- Skill 最终目录结构；
- `SKILL.md` 的完整正文；
- 是否需要附带脚本；
- 脚本语言与依赖；
- 安装、发布和版本分发方式；
- 多项目工作区创建机制；
- 自动测试框架；
- 与 Codex 插件或外部工具的集成。
