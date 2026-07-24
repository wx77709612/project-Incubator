# Project Incubator Roadmap

> Phase 5 - Planning 的核心机制路线图交付物

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | Project Incubator |
| 所有者 Phase | Phase 5 - Planning |
| 文档状态 | Active |
| 权威范围 | Project Incubator Skill 1.0 的核心运行链路、硬性门槛规划、机制型里程碑顺序和进入 Ticket 拆解的边界 |
| 消费 Phase | Phase 5-9，按需读取 |
| 更新条件 | Maker 调整 Skill 核心机制、硬性门槛、机制型里程碑顺序、规划边界或首批 Ticket 方向 |
| 依赖文档 | `DOCS/04-design/SKILL_DESIGN.md`、`DOCS/04-design/SCOPE.md`、`DOCS/04-design/DESIGN.md`、`DOCS/04-design/INTERACTION_DESIGN.md`、`DOCS/04-design/AGENT_PROTOCOL_DESIGN.md`、`DOCS/04-design/DOCUMENT_WRITEBACK_DESIGN.md`、`DOCS/04-design/PROJECT_STATE_DESIGN.md`、`DOCS/04-design/TECHNICAL_DESIGN.md`、`DOCS/PROJECT_STATE.md` |
| 最后更新 | 2026-07-24 |

## 1. 文档职责

本文档定义 Phase 5 中 Project Incubator Skill 1.0 的核心机制路线图。

本文档不把当前项目已经在真实协作中运行过的基础能力重新拆成常规建设里程碑，也不直接进入 Skill 实现。它只回答：已经验证出价值的协作流程，应如何被串成一条可执行的 Skill 主运行链路；哪些位置必须设置硬性门槛；后续 Ticket 应围绕哪些机制拆解。

## 2. 路线调整依据

当前 Project Incubator 不是一个从零开始的未验证项目。它已经在本项目自身协作中使用并初步验证了以下基础能力：

- 通过 `AGENTS.md` 和 `DOCS/PROJECT_STATE.md` 恢复项目状态；
- 根据 Phase 切换 AI 角色和协作边界；
- 使用权威文档集合承载上下文；
- 在写入前检查 Git 状态和工作分支；
- 在完成文档修改后保留 Diff 给 Maker 审阅；
- 在高风险 Git、Phase、文档和范围动作前触发门禁；
- 通过 `PROJECT_STATE.md` 回写下一步和恢复入口。

因此，Phase 5 不应把这些能力当作一组从零实现的功能清单，而应规划它们如何组成 Skill 1.0 的核心机制。

## 3. 规划目标

Phase 5 当前的主要规划目标是：

> 把已在真实协作中跑通的流程，抽象为 Project Incubator Skill 1.0 的主运行链路、硬性门槛和 Builder 交接闭环，并用最小验证场景检查这三项机制是否足以进入 Build。

这个目标包含四个问题：

1. Skill 被触发后，主流程如何从状态恢复一路走到下一轮恢复；
2. 哪些动作不能只靠 AI 自觉，必须设置硬性门槛；
3. Planning 如何把 Builder 任务交出去，并保证 Builder 不能重新定义项目方向；
4. 如何用少量真实场景验证 R1-R3 是否足以防止跑偏、越权和上下文漂移。

## 4. 核心运行链路

Skill 1.0 的主运行链路应优先规划为以下顺序：

```text
启动或恢复
→ 读取本地协议与状态入口
→ 定位当前 Phase、AI 角色、主目标和权威文档集合
→ 建立本轮协作契约
→ 判断本轮是只读、规划、写入、Builder 执行还是阶段门检查
→ Phase 内协作
→ 新事项分类
→ 必要时触发硬性门槛
→ 正确权威文档写回
→ Diff / 交付物交给 Maker 审阅
→ 状态入口收敛下一步
→ 下一轮可恢复
```

这条链路是后续 `VERIFICATION_PLAN.md` 和首批 Ticket 的主要拆解对象。

## 5. 硬性门槛优先级

硬性门槛不是普通提醒，而是 Skill 必须在执行前暂停、说明风险并等待 Maker 明确决定的机制。

首批规划应优先覆盖以下门槛：

| 门槛 | 触发结果 | 默认动作 |
| --- | --- | --- |
| Phase 门槛 | 改变 Phase、AI 角色、Exit Criteria 或阶段状态 | 停止推进，输出阶段门检查和 Maker 选项 |
| Git 门槛 | 改变分支、暂存、提交、推送、合并、远端或历史 | 只做只读检查或提供手动命令，除非 Maker 明确授权具体动作 |
| 权威文档门槛 | 改变文档状态、权威路径、职责归属或长期规则 | 说明影响和权威来源，等待 Maker 确认 |
| 范围门槛 | 扩大项目类型、目标用户、商业化、公开发布或实现深度 | 拒绝静默扩大，交由 Maker 决定 |
| Builder 交接门槛 | 任务缺少目标、非目标、范围、验收标准或验证步骤 | 不交给 Builder，回到 Planning 补齐任务边界 |
| 未闭环任务门槛 | 工作区、分支、未推送提交或任务状态不清楚 | 停止新写入任务，先报告 Git 和状态缺口 |

这些门槛应作为 Skill 1.0 的核心机制，而不是放到后续低优先级里程碑。

## 6. 机制型路线图

Phase 5 应按机制成熟度，而不是按普通功能模块，拆为以下路线：

| 顺序 | 机制 | 主要问题 | 后续产物 |
| --- | --- | --- | --- |
| R1 | 主运行链路串联 | Skill 如何把恢复、协作、分叉、写回、审阅和下一轮恢复串起来 | `MILESTONES.md`、`VERIFICATION_PLAN.md`、链路 Ticket |
| R2 | 硬性门槛矩阵 | 哪些动作必须停，停下后要求 Maker 确认什么 | 门槛 Ticket、验证样例 |
| R3 | Builder 交接闭环 | 什么条件下任务可以交给 Builder，完成后如何回到 Collaborator 验收 | Ticket 模板边界、Builder 交接 Ticket |
| R4 | 最小场景验证支撑 | 如何证明 R1-R3 对真实协作有用 | `VERIFICATION_PLAN.md` 中的样例指令和通过标准 |

R1-R3 是进入 Build 前必须优先完成的 Planning 核心；R4 不作为同级建设目标，而作为验证 R1-R3 的支撑机制。生产模板、脚本、Skill 文件结构和阶段交付物模板仍然重要，但它们应作为上述机制的实现载体，而不是当前路线图的第一层拆解维度。

## 7. 首批 Planning 产物顺序

当前建议的 Phase 5 产物顺序是：

1. 重写并确认 `ROADMAP.md`：以核心机制路线图替代常规建设里程碑；
2. 重写并确认 `MILESTONES.md`：定义 R1-R3 的机制型核心里程碑，并把 R4 作为验证支撑；
3. 创建 `VERIFICATION_PLAN.md`：优先验证 R1-R3 是否足以支撑 Builder 交接；
4. 创建首批 `TICKETS/`：优先围绕 R1、R2、R3 拆解，不直接实现 Skill。

## 8. 延后范围

以下事项不进入当前首批 Planning：

- Skill 最终安装、发布和版本分发；
- 完整 `SKILL.md` 正文；
- 完整脚本体系；
- 所有阶段交付物模板的一次性固化；
- 多项目工作区创建机制；
- 外部用户验证、公开发布或商业化路径；
- Phase 3 `VALIDATION_RESULTS.md` 的回收补齐。

这些事项只有在核心链路和硬性门槛规划清楚后，才适合进入具体 Ticket。

## 9. 已确认规划方向

- “主运行链路 + 硬性门槛”是 Phase 5 的首要规划对象；
- R1-R3 是进入 Build 前必须优先完成的 Planning 核心；
- R4 降级为 `VERIFICATION_PLAN.md` 中的最小场景验证支撑；
- 首批 Ticket 优先围绕 R1 主运行链路、R2 硬性门槛矩阵和 R3 Builder 交接闭环展开。
