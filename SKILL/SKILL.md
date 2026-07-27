---
name: project-incubator
description: 当用户想把一个想法、目标、问题、个人工具、App、内容作品、工作流、自动化、方法论或决策项目，从初始想法推进为可设计、可规划、可构建、可验收的真实项目或阶段性成果时使用；当用户说想开始一个项目、梳理项目、孵化项目、明确下一步、验证想法、设计方案、拆解任务、推进构建、发布使用、迭代复盘时使用；当用户已有写了一部分的项目、半成品、原型、代码库、文档集合或长期迭代项目，并想接入项目孵化流程、补齐项目状态或阶段文档、判断当前 Phase、建立权威文档集合、恢复主线或治理后续迭代时使用；当当前工作区或用户请求显示存在 Project Incubator 风格的 AGENTS.md、DOCS/PROJECT_STATE.md、Phase 文档、权威文档集合、Maker / AI Collaborator / AI Builder 角色、状态写回、Git 闭环或 Builder 交接时，也用于恢复、继续、治理或交接该项目。
---

# Project Incubator

## 路径语义

本文中的路径分为三类：

- 目标项目路径：除明确标为 Skill 资产路径或当前 Project Incubator 仓库路径外，Skill 为被孵化或接入项目读取、创建或更新的项目文件路径，均相对目标项目根目录解析；例如 `AGENTS.md`、`DOCS/PROJECT_STATE.md`、`DOCS/<phase>/`、`README.md`、其他项目文件、代码、配置或素材路径。
- Skill 资产路径：`references/...`、`assets/...`，均相对本 `SKILL.md` 所在目录解析。
- 当前 Project Incubator 仓库路径：只在维护 Project Incubator Framework、Skill、references、模板或治理规则时使用，不作为未来目标项目的默认状态来源。

## 入口判断

进入本 Skill 后，按目标项目状态选择入口：

- 新想法或新项目孵化：用户只有想法、目标、问题或待孵化对象，尚未确认目标项目工作区；先澄清项目名称、项目类型、目标工作区和是否创建承载物。
- 既有非 Project Incubator 项目接入：目标项目已有代码、文档、素材、原型、半成品或长期迭代材料，但缺少可用的 `AGENTS.md` 或 `DOCS/PROJECT_STATE.md`；先进入接入盘点和补齐流程。
- 已接入项目恢复或续作：目标项目存在且可读取 `AGENTS.md` 与 `DOCS/PROJECT_STATE.md`；按目标项目本地协议和状态入口恢复。
- Project Incubator 自身维护：任务对象是 Project Incubator Framework、Skill、references、模板、门槛、写回规则或协作协议；按本仓库协议和当前项目状态执行。

## 启动

1. 先根据 Maker 指令和当前工作区判断目标项目是否已接入 Project Incubator。
2. 如果目标项目存在可读取的 `AGENTS.md` 与 `DOCS/PROJECT_STATE.md`，按该项目本地协议恢复；本地项目协议指目标项目根目录的 `AGENTS.md`。
3. 如果目标项目缺少目标项目路径 `AGENTS.md` 或 `DOCS/PROJECT_STATE.md`，不要读取不存在的本地协议或状态入口；读取 Skill 资产路径 `references/project-intake-and-initialization.md`，进入新项目启动或既有项目接入流程。
4. 创建 `AGENTS.md`、`DOCS/PROJECT_STATE.md`、Phase 目录或阶段文档前，必须获得 Maker 对目标项目、目标路径、接入范围和写入权限的明确确认。
5. 写入任何输出前，先判定产物承载类型、路径域和适用写法，再检查已加载协议或接入流程中的语言、格式、内容承载和工具边界；缺失或冲突时，触发硬性门槛，不得按通用 Skill 写法或其他承载物规则自行决定。
6. 先用入口类型、已加载协议、状态入口或接入盘点结果判断任务类型；只有无法判断任务类型、需要恢复主链路，或要检查启动到收尾的完整流程时，才读取 Skill 资产路径 `references/main-runtime-chain.md`。

## 路由

- 新项目启动、既有非 Project Incubator 项目接入、模板实例化、目录创建、状态入口补齐或目标项目 `DOCS/` 权威文档创建：读取 Skill 资产路径 `references/project-intake-and-initialization.md`，并按需使用 Skill 资产路径 `assets/templates/AGENTS.template.md`、`assets/templates/PROJECT_STATE.template.md` 与 `assets/templates/DOCUMENT-METADATA.template.md`。
- 启动、恢复、协作契约、Phase 内工作、Maker 审阅、状态收敛或下一轮恢复的完整链路不清楚时：读取 Skill 资产路径 `references/main-runtime-chain.md`。
- 任务分类、读写判断、状态收敛、上下文恢复或 Maker 任务 Prompt：读取 Skill 资产路径 `references/task-type-and-writeback.md`。
- Phase、Git、权威、范围、Builder、未闭环任务、上下文完整性、本地协议与输出约束、纠偏沉淀或架构决策风险：读取 Skill 资产路径 `references/hard-gate-matrix.md`。
- 门槛回应、授权字段、安全替代动作、Prompt 搬运卫生或本地协议冲突回应：读取 Skill 资产路径 `references/gate-response-and-authorization.md`。
- 交给 Builder 前：读取 Skill 资产路径 `references/builder-handoff-checklist.md`。
- Builder 返回后：读取 Skill 资产路径 `references/builder-return-and-review.md`。

## 渐进读取

不要因为本入口列出了所有 reference，就一次性全部读取。每轮只读取本地协议、状态入口、本轮任务直接命中的 reference 和目标文件。只有当路径缺失、任务类型无法判断、规则冲突、上下文完整性风险或 Maker 要求完整审阅时，才扩大读取范围。

## 边界

保持本入口短小，不把 reference 细节复制进 `SKILL.md`。

当 Maker 提出质疑、反驳或要求解释原因时，先从“合理时如何改”和“不合理时为什么不改”两面判断，再决定是否修改；不得为了迎合质疑而直接改写协作方式、门槛或长期规则。

不得在 Maker 未确认目标项目、目标路径、接入范围和写入权限时，实例化模板、创建目录、覆盖文件或写入目标项目。不得实现安装流程、发布流程、未规划脚本、Git 写操作或新的长期架构规则，除非 Maker 对对应任务另行明确授权。
