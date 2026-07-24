# Project Incubator Milestones

> Phase 5 - Planning 的机制型里程碑交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | Project Incubator Skill 1.0 的机制型核心里程碑、核心链路、硬性门槛、Builder 交接闭环、验证支撑和首批 Ticket 边界 |
| 消费 Phase | Phase 5-9，按需读取 |
| 更新条件 | Maker 调整核心机制、硬性门槛、Builder 交接、验证方式或首批 Ticket 边界 |
| 依赖文档 | `DOCS/05-planning/ROADMAP.md`、`DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-24 |

## 1. 文档职责

本文档定义 Phase 5 中 Project Incubator Skill 1.0 的机制型里程碑。

本文档不授权 Build，不实现 Skill，不创建最终模板或脚本。它负责把 Maker 已确认的方向拆成可规划、可验证、可继续拆 Ticket 的机制单元。

## 2. 里程碑总览

| 里程碑 | 名称 | 状态 | 核心问题 |
| --- | --- | --- | --- |
| R1 | 主运行链路串联 | Draft | Skill 如何把启动、恢复、协作、分叉、写回、审阅和下一轮恢复串成一条稳定流程 |
| R2 | 硬性门槛矩阵 | Draft | 哪些动作必须停，触发后默认不做什么，Maker 必须确认什么 |
| R3 | Builder 交接与验证闭环 | Draft | 什么任务可以交给 Builder，Builder 完成后如何回到 Collaborator 与 Maker 验收 |
| R4 | 最小场景验证支撑 | Draft | 用哪些真实或模拟协作场景验证 R1-R3 足以支撑后续 Builder 构建 |

R1-R3 是进入 Build 前必须优先完成的 Planning 核心。R4 不作为同级建设里程碑，而作为 `VERIFICATION_PLAN.md` 对 R1-R3 的验证支撑。

## 3. R1 - 主运行链路串联

### 3.1 目标

R1 的目标是定义 Skill 1.0 的主运行链路，让 AI 在任意项目会话中知道自己如何从恢复进入协作，再从协作回到可恢复状态。

R1 应明确：

- Skill 启动或恢复时必须读取什么；
- 如何从状态入口确认当前 Phase、AI 角色、主目标和权威文档集合；
- 如何建立本轮协作契约；
- 如何判断本轮属于只读、规划、写入、Builder 执行、阶段门检查或 Git 闭环回写；
- Phase 内协作结束后，何时需要文档写回；
- Maker 审阅后，状态入口如何收敛下一步；
- 下一轮 Agent 如何恢复。

### 3.2 非目标

R1 不创建最终 `SKILL.md`，不实现脚本，不创建完整模板体系，也不拆所有 Phase 的具体任务。

### 3.3 输入

- `DOCS/04-design/SKILL_DESIGN.md` 的总交互过程；
- `DOCS/04-design/DESIGN.md` 的 Phase 0-9 关系；
- `DOCS/04-design/INTERACTION_DESIGN.md` 的启动交互、分叉处理和阶段切换交互；
- `DOCS/04-design/TECHNICAL_DESIGN.md` 的运行时读取策略；
- 当前项目自身已经使用过的 `AGENTS.md` / `PROJECT_STATE.md` 恢复流程。

### 3.4 输出

R1 完成后，应能进入以下 Ticket 拆解：

- 主运行链路说明；
- 启动恢复判定清单；
- 本轮协作契约输出格式；
- 任务类型判定清单；
- 状态写回触发条件；
- 下一轮恢复入口检查。

### 3.5 验收方向

R1 的验收应证明：给定一个项目状态和 Maker 本轮指令，AI 能判断本轮应进入哪类协作流程，并说明下一步应读什么、写什么、不处理什么、何时停下来。

## 4. R2 - 硬性门槛矩阵

### 4.1 目标

R2 的目标是把 Phase 4 已设计的门禁交互和技术门禁，规划成 Skill 1.0 的硬性门槛矩阵。

硬性门槛应覆盖：

- Phase 切换；
- Git 写操作；
- 权威文档状态或职责变更；
- 范围、项目类型、商业化或公开程度扩大；
- Builder 交接前信息不足；
- 未闭环任务或 Git 状态异常；
- Architecture Decision 候选写回。

### 4.2 非目标

R2 不直接脚本化所有检查，不替 Maker 作决定，也不把所有普通提醒升级为门槛。

### 4.3 输入

- `DOCS/04-design/INTERACTION_DESIGN.md` 的高风险动作门禁交互；
- `DOCS/04-design/AGENT_PROTOCOL_DESIGN.md` 的高风险动作门禁；
- `DOCS/04-design/TECHNICAL_DESIGN.md` 的高风险动作门禁实现；
- `SPECS/ARCHITECTURE_DECISIONS.md` 的 AI 越界防护边界；
- 当前项目 Git 与 Diff 验收规则。

### 4.4 输出

R2 完成后，应能进入以下 Ticket 拆解：

- 硬性门槛矩阵；
- 门槛触发判定样例；
- 门槛触发后的标准回应格式；
- Maker 明确授权字段；
- 默认安全处理方式清单；
- 不应升级为硬性门槛的普通提醒清单。

### 4.5 验收方向

R2 的验收应证明：给定若干 Maker 指令和项目状态，AI 能判断是否触发门槛、触发哪类门槛、默认应暂停在哪一步，以及 Maker 必须确认什么才能继续。

## 5. R3 - Builder 交接与验证闭环

### 5.1 目标

R3 的目标是定义 Planning 与 Build 之间的交接机制，确保 AI Builder 只执行范围明确、可验证、不会重新定义方向的任务。

R3 应明确：

- Ticket 必须包含哪些字段；
- 哪些信息缺失时不得交给 Builder；
- Builder 允许修改什么、禁止修改什么；
- Builder 完成后如何报告实际结果和验证证据；
- Collaborator 如何回到 Phase 5 / Phase 6 视角检查结果；
- Maker 如何进行 Diff 或交付物验收。

### 5.2 非目标

R3 不直接创建全部 Ticket，不进入代码实现，不让 Builder 判断 Phase 是否完成。

### 5.3 输入

- `FRAMEWORK/Role-System.md` 的 AI Builder 边界；
- `FRAMEWORK/Phase-System.md` 的 Phase 5 / Phase 6 规则；
- `DOCS/04-design/SKILL_DESIGN.md` 的 Builder 交接条件；
- `DOCS/04-design/INTERACTION_DESIGN.md` 的 Builder 交接交互。

### 5.4 输出

R3 完成后，应能进入以下 Ticket 拆解：

- Ticket 必备字段清单；
- Builder 启动前检查清单；
- Builder 完成后报告格式；
- Collaborator 验收回看清单；
- Maker Diff 审阅提示。

### 5.5 验收方向

R3 的验收应证明：任一 Ticket 如果缺少目标、非目标、范围、验收标准或验证步骤，AI 必须拒绝交给 Builder，并回到 Planning 补齐。

## 6. R4 - 最小场景验证支撑

### 6.1 目标

R4 的目标是定义一组最小真实或模拟场景，用于验证 R1-R3 的机制是否能在实际协作中防止跑偏、越权和 Builder 交接失控。

R4 应主要进入 `VERIFICATION_PLAN.md`，用于证明 R1-R3 足以支撑后续 Build，而不是单独形成一批同级建设 Ticket。

### 6.2 场景候选

最小场景集应至少覆盖：

| 场景 | 验证问题 |
| --- | --- |
| 新会话恢复 | AI 是否能从 `AGENTS.md` 和 `PROJECT_STATE.md` 恢复当前 Phase、角色和下一步 |
| Maker 说“继续” | AI 是否能判断这是方向确认、Diff 接受、Git 授权还是普通推进 |
| Git 未闭环 | AI 是否会停止新写入任务并报告状态 |
| 想切换 Phase | AI 是否输出阶段门检查，而不是直接切换 |
| 新想法出现 | AI 是否分类为立即处理、记录后续、请求决定或拒绝展开 |
| Builder 任务不完整 | AI 是否拒绝交接并补齐 Ticket 边界 |
| 权威文档冲突 | AI 是否停止并报告冲突，而不是自行选择版本 |

### 6.3 非目标

R4 不要求完整外部用户验证，不补齐 Phase 3 `VALIDATION_RESULTS.md`，不创建大型模拟项目。

### 6.4 输出

R4 完成后，应能支撑以下验证拆解：

- 最小场景验证表；
- 每个场景的输入状态、Maker 指令、预期 AI 行为和通过标准；
- 失败时应回到哪个机制或文档修正；
- 是否需要脚本辅助验证的判断。

### 6.5 验收方向

R4 的验收应证明：R1-R3 不是抽象口号，而能在具体指令和状态下产生稳定、可检查的 AI 行为，并能为 Builder 阶段提供足够清楚的进入门槛。

## 7. 首批 Ticket 建议

首批 Ticket 应优先围绕 R1、R2 和 R3，而不是模板文件完整性：

1. 定义 Skill 主运行链路和任务类型判定；
2. 定义硬性门槛矩阵和触发规则；
3. 定义门槛触发后的标准回应格式；
4. 定义 Builder 交接前最小检查清单；
5. 定义 Builder 完成后回到 Collaborator 验收的闭环；
6. 在 `VERIFICATION_PLAN.md` 中定义最小场景验证支撑。

只有当这些机制清楚后，才继续拆：

- `SKILL.md` 入口正文；
- Skill references 目录结构；
- `AGENTS.md` 生产模板；
- `PROJECT_STATE.md` 生产模板；
- 可选脚本或检查工具。

## 8. 已确认规划方向

- R1-R3 是 Phase 5 进入 Build 前必须优先完成的机制型核心里程碑；
- R1、R2 与 R3 是首批 Ticket 的主要对象；
- 模板与脚本推迟到核心机制规划之后；
- R4 作为 `VERIFICATION_PLAN.md` 中验证 R1-R3 的支撑，而不是同级建设里程碑。
