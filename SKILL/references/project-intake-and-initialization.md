# Project Intake and Initialization Reference

用于 Project Incubator Skill 进入新项目、既有非 Project Incubator 项目或已接入项目时，判断入口、确认写入授权、实例化启动模板和创建最小目录结构。

读取时机：当 `SKILL.md` 判定本轮涉及新项目启动、既有项目接入、模板实例化、目录创建或状态入口补齐时读取。

相关 Skill 资产：

- `assets/templates/AGENTS.template.md`
- `assets/templates/PROJECT_STATE.template.md`
- `assets/templates/DOCUMENT-METADATA.template.md`

## 1. 文档职责

本文档定义 Project Incubator Skill 进入一个目标项目时，如何判断该项目是新项目、既有非 Project Incubator 项目，还是已接入 Project Incubator 的项目。

本文档允许定义模板实例化和目录创建流程，但不自动执行写入。创建或补齐 `AGENTS.md`、`DOCS/PROJECT_STATE.md`、Phase 目录或阶段文档前，必须获得 Maker 对目标项目、接入范围和写入位置的明确确认。

## 2. 路径语义

本文中的路径分为三类：

- 目标项目路径：除明确标为 Skill 资产路径或当前 Project Incubator 仓库路径外，Skill 为被孵化或接入项目读取、创建或更新的项目文件路径，均相对目标项目根目录解析；例如 `AGENTS.md`、`DOCS/PROJECT_STATE.md`、`DOCS/<phase>/`、`README.md`、其他项目文件、代码、配置或素材路径。
- Skill 资产路径：`references/...`、`assets/...`，均相对本 Skill 根目录解析；其中 `references/...` 是运行时读取材料，不实例化为目标项目文件，`assets/templates/...` 只有在 Maker 授权后才可复制或改写到目标项目路径。
- 当前 Project Incubator 仓库路径：`DOCS/04-design/...` 等设计依据只在维护本仓库 Framework / Skill 自身时读取，不作为未来目标项目的默认状态来源。

## 3. 入口类型

| 入口类型 | 判断依据 | 默认动作 |
| --- | --- | --- |
| 新项目启动 | 用户只有想法、目标、问题或待孵化对象，目标工作区尚未建立 Project Incubator 结构 | 先确认项目名称、项目类型、目标工作区、初始 Phase 和是否创建启动模板 |
| 既有非 Project Incubator 项目接入 | 目标工作区已有代码、文档、素材、半成品或长期迭代项目，但缺少 Project Incubator 状态入口 | 先盘点既有材料，再提出接入缺口、可能 Phase 和最小补齐清单 |
| 已接入项目恢复 | 目标工作区存在可读取的目标项目路径 `AGENTS.md` 与 `DOCS/PROJECT_STATE.md` | 按目标项目本地 `AGENTS.md` 和状态入口恢复，不重新初始化 |
| Project Incubator 自身维护 | 任务指向本仓库 Framework、Skill、references、模板或治理规则 | 按当前 Project Incubator 仓库路径中的 `AGENTS.md` 和 `DOCS/PROJECT_STATE.md` 执行 |

## 4. 新项目启动流程

新项目启动时，先收集以下最小信息：

- 项目名称；
- Maker 定义；
- 项目类型；
- 目标工作区或是否先只做对话澄清；
- 初始想法、目标或问题；
- 是否允许创建 `AGENTS.md`、`DOCS/PROJECT_STATE.md` 和必要目录。

若 Maker 尚未确认写入位置或创建权限，只能继续澄清，不创建文件。

获得确认后，最小目录结构为：

```text
<project-root>/
├── AGENTS.md
└── DOCS/
    └── PROJECT_STATE.md
```

只有当前 Phase 确认需要交付物时，才按需创建 `DOCS/<phase>/`。不要预建全部 Phase 目录。

实例化模板：

- Skill 资产路径 `assets/templates/AGENTS.template.md` -> 目标项目路径 `<project-root>/AGENTS.md`
- Skill 资产路径 `assets/templates/PROJECT_STATE.template.md` -> 目标项目路径 `<project-root>/DOCS/PROJECT_STATE.md`
- Skill 资产路径 `assets/templates/DOCUMENT-METADATA.template.md` -> 目标项目路径 `<project-root>/DOCS/<phase>/<document>.md` 的文档状态元数据块

Skill 资产路径 `references/...` 不进入上述实例化映射。它们只提供运行时流程、门槛和检查规则，不能被复制为目标项目 `DOCS/` 权威文档。

## 4.1 `DOCS/` 文档元数据要求

凡由本 Skill 在目标项目 `DOCS/` 下创建并作为权威项目文档消费的文件，必须包含 `## 文档状态` 元数据表。

适用对象：

- 目标项目路径 `<project-root>/DOCS/PROJECT_STATE.md`；
- 目标项目路径 `<project-root>/DOCS/<phase>/<document>.md`；
- 既有项目接入时补齐或修复的目标项目权威文档。

不适用对象：

- 目标项目路径 `<project-root>/AGENTS.md`；
- Skill 资产路径 `references/...`；
- Skill 资产路径 `assets/...` 中不会实例化为目标项目 `DOCS/` 权威文档的资产；
- 代码、脚本、配置或 Prompt 正文。

如果当前没有对应阶段文档模板，先使用 Skill 资产路径 `assets/templates/DOCUMENT-METADATA.template.md` 生成文档状态块，再根据当前 Phase 规则和 Maker 已确认事实创建最小正文草案。不得为了形式完整预建无价值阶段文档。

## 5. 既有项目接入流程

既有项目接入时，先只读盘点目标工作区：

- 是否已有 README、需求文档、设计文档、任务列表或发布说明；
- 是否已有代码、素材、数据、脚本或构建配置；
- 是否已有 Git 仓库、分支、未提交修改或远端；
- 是否已有项目状态、路线图、Issue、TODO 或交接文档；
- 是否已有类似 `AGENTS.md`、`PROJECT_STATE.md` 或阶段目录的结构。

盘点后输出接入报告：

- 已确认材料；
- 缺失的 Project Incubator 承载物；
- 可能的当前 Phase 及依据；
- 不能确定的 Phase 或事实；
- 建议创建或补齐的最小文件；
- 需要 Maker 确认的写入位置、覆盖策略和初始化范围。

不得仅凭代码成熟度自动判定 Phase。Phase 只能作为“候选 Phase”提出，由 Maker 确认后写入状态入口。

## 6. 已接入项目恢复流程

若目标项目存在 `AGENTS.md` 与 `DOCS/PROJECT_STATE.md`：

1. 读取目标项目路径 `AGENTS.md`；
2. 按其指向读取目标项目路径 `DOCS/PROJECT_STATE.md`；
3. 确认当前 Phase、AI 角色、主目标、权威文档集合和下一步；
4. 若状态入口缺失、冲突或指向不存在文件，停止并报告；
5. 不重新实例化模板，除非 Maker 明确要求修复接入结构。

## 7. 写入授权边界

以下动作都需要 Maker 明确确认目标路径和范围：

- 创建 `AGENTS.md`；
- 创建 `DOCS/PROJECT_STATE.md`；
- 创建 `DOCS/<phase>/` 目录；
- 从模板生成阶段文档；
- 覆盖、移动或重命名既有项目文件；
- 将候选 Phase 写为当前 Phase；
- 将既有材料标记为权威文档。

若目标路径已有同名文件，不得覆盖。先报告冲突、现有文件用途和可选处理方式。

## 8. 最小验证场景

| 场景 | 输入 | 预期行为 |
| --- | --- | --- |
| V1 新想法无工作区 | Maker 只有想法 | 先澄清目标工作区和是否创建承载物，不读取不存在的 `AGENTS.md` |
| V2 旧代码库接入 | 工作区有代码但无 `DOCS/PROJECT_STATE.md` | 先盘点材料并提出候选 Phase，不自动创建或覆盖 |
| V3 已接入项目恢复 | 工作区有 `AGENTS.md` 与 `DOCS/PROJECT_STATE.md` | 按本地协议恢复，不重新初始化 |
| V4 旧项目已有同名文件 | 已存在 `AGENTS.md` 或 `DOCS/PROJECT_STATE.md` | 报告冲突并等待 Maker 决定，不覆盖 |
