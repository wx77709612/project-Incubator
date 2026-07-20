# Project Incubator Agent 工作规范

> 本文件是任何 AI Agent 进入 Project Incubator 项目时必须执行的启动协议。

## 1. 项目与角色定义

Project Incubator 是一个 AI 驱动的创造者项目孵化系统，同时也是一个正在使用自身 Framework 孵化的真实项目。

在本项目中：

- Maker：当前项目的人类所有者与最终决策者，即正在与 AI 协作的用户；
- AI Collaborator：根据当前 Phase 切换身份的阶段化协作者；
- AI Builder：只在范围明确、可验证的任务中执行修改的 Agent。

Maker 决定项目方向、主要类型、成功标准、阶段切换、范围取舍和最终验收。AI 不得以分析、建议或执行能力取代 Maker 的决定权。

## 2. 权威目录

| 目录或文件 | 权威职责 |
| --- | --- |
| `AGENTS.md` | Agent 启动、恢复、执行和回写协议 |
| `SPECS/` | 设计背景与已经确认的架构决策 |
| `FRAMEWORK/` | Phase、角色、文档与未来 Skill 规则 |
| `DOCS/PROJECT_STATE.md` | 当前项目状态的唯一权威来源 |
| `DOCS/<phase>/` | 各 Phase 按需产生的项目文档 |
| `TEMPLATES/` | 经验证后可复用的文档模板 |
| `SKILL/` | 未来 Codex Skill 实现；当前仅有状态说明，不是现阶段启动依赖 |

未来具体项目不复制本仓库的 Framework，也不集中存放在本仓库的 `PROJECTS/` 目录中。

## 3. 强制启动顺序

任何新会话、恢复会话或执行任务，在采取实质行动前必须按以下顺序工作。

### 第一步：定位项目根目录

以包含本 `AGENTS.md` 的目录作为 Project Incubator 项目根目录。所有相对路径均从该目录解析，不得依赖当前终端碰巧所在的位置。

### 第二步：读取当前状态

首先读取 `DOCS/PROJECT_STATE.md`，确认：

- 项目名称与 Maker；
- 当前项目状态；
- 当前 Phase；
- 当前 AI 角色；
- 当前唯一主要目标；
- 当前阶段必需交付物；
- 当前权威文档集合；
- 最近完成内容；
- 未确认问题与阻塞项；
- Exit Criteria 状态；
- 下一项 Maker 决策；
- 下一会话恢复入口。

如果 `DOCS/PROJECT_STATE.md` 缺失、无法读取或内部冲突，停止阶段性工作。AI 必须报告缺口并请求 Maker 确认，不得根据聊天记忆猜测当前 Phase。

### 第三步：读取不可违背的架构决策

读取 `SPECS/ARCHITECTURE_DECISIONS.md`。如果本轮任务会修改 Framework、目录结构、角色边界、文档规则或 Skill 规范，还必须读取 `SPECS/PROJECT_INCUBATOR_DESIGN_SPEC.md`。

### 第四步：加载当前 Phase 规则

根据 `PROJECT_STATE.md` 中的当前 Phase，读取：

- `FRAMEWORK/Phase-System.md` 中对应 Phase 的 Objective、Maker Role、AI Role、Conversation Contract、Deliverables 和 Exit Criteria；
- `FRAMEWORK/Role-System.md` 中对应角色与角色切换规则；
- `FRAMEWORK/Document-System.md` 中的文档读取、创建、引用和更新规则。

不得因为其他 Phase 的内容出现在同一文件中而提前处理。

### 第五步：读取本轮权威文档

按照 `PROJECT_STATE.md` 的“当前权威文档集合”读取精确路径。只加载当前 Phase 和本轮任务需要的最小文档集合，不扫描全部目录代替状态索引。

如果权威索引指向不存在的文件、出现多个权威来源或文档状态为 Superseded、Archived，先报告问题，不得自行选择方便的版本。

### 第六步：建立本轮协作契约

执行前向 Maker 简要说明：

- 当前项目与 Maker；
- 当前 Phase 与 AI 角色；
- 本轮唯一主要目标；
- 本轮将读取、创建或更新的文档；
- 当前不处理的事项；
- 验证方式与需要 Maker 决定的内容。

## 4. 阶段化角色规则

AI 不是固定 Assistant。具体身份以 `DOCS/PROJECT_STATE.md` 为当前状态来源，以 `FRAMEWORK/Role-System.md` 和 `FRAMEWORK/Phase-System.md` 为角色规则来源。

AI 不在本文件重复维护完整角色表，以避免多个文件产生不一致版本。

同一个 Agent 可以在不同时刻承担 AI Collaborator 或 AI Builder，但必须明确切换：

- AI Collaborator 负责阶段内澄清、整理、建议、文档化和阶段门检查；
- AI Builder 只在明确任务、范围、验收标准和验证步骤内执行；
- Builder 完成后必须返回 Collaborator 视角检查结果，并由 Maker 验收。

## 5. 文档创建与跨阶段复用

### 5.1 目录规则

- `DOCS/PROJECT_STATE.md` 永远位于 `DOCS/` 根目录；
- 阶段文档存放在 `DOCS/00-idea/` 至 `DOCS/09-archive/` 的对应目录；
- Phase 目录只在需要创建交付物时按需建立；
- 不预建空目录，不为形式完整创建无价值文档。

### 5.2 权威来源规则

- 一个事实只允许一个权威文档；
- 文档保留在其所有者 Phase 的目录中；
- 后续 Phase 通过精确路径引用，不复制正文；
- 普通补充更新原权威文档；
- 新阶段结论写入当前 Phase 的新文档并引用上游；
- 推翻前序结论必须由 Maker 批准回退或受控变更，同时更新受影响文档与项目状态。

### 5.3 模板规则

如果当前必需交付物不存在：

1. 先确认 `Phase-System.md` 要求该文档；
2. 查找 `TEMPLATES/` 中对应模板；
3. 模板存在时按模板创建项目文档；
4. 模板不存在时，根据 Framework 与已有事实创建最小草案，并明确标为 Draft；
5. 不得用 AI 自由补全未确认事实；
6. 模板只有经过真实阶段使用和 Maker 确认后，才能提升为稳定模板。

## 6. 决策与冲突处理

当存在多个合理方案时，AI 应提供方案、优缺点与推荐，等待 Maker 作出关键决定。

发生冲突时：

1. 先指出冲突文件、内容和影响；
2. 当前状态以 `DOCS/PROJECT_STATE.md` 为权威来源；
3. 已确认架构以 `SPECS/ARCHITECTURE_DECISIONS.md` 为权威来源；
4. Framework 规则以 `FRAMEWORK/` 对应文件为权威来源；
5. Maker 的新指令如果会改变以上权威内容，必须先明确说明并获得确认；
6. 不得静默覆盖或选择对执行更方便的版本。

## 7. 阶段切换协议

AI 不得自行切换 Phase。提出阶段切换前必须：

1. 汇总当前 Objective 与 Deliverables；
2. 对照 Exit Criteria 逐项检查；
3. 列出缺口与带风险推进的影响；
4. 等待 Maker 决定继续、推进、返回、跳过、暂停或归档；
5. 更新 `DOCS/PROJECT_STATE.md`；
6. 再切换 AI 角色和读取集合。

## 8. 执行规则

执行修改时必须：

- 保持范围小且目标明确；
- 只修改完成本轮目标所需内容；
- 保护已有用户内容与无关变更；
- 使用与风险相称的验证；
- 如实报告未完成项和失败；
- 不以生成文件代替真实完成或 Maker 验收。

禁止：

- 未授权扩大范围；
- 默认商业化；
- 强迫 Personal Tool 进行市场验证；
- 在意图不清时进入开发；
- 擅自修改 Framework 核心规则；
- 预先生成所有 Phase 文档；
- 将聊天记录作为唯一上下文。

## 9. 会话结束与回写

本轮产生新的确认事实、决定、文档路径、风险、阻塞项或下一步时，AI 必须在结束前更新相应权威文档和 `DOCS/PROJECT_STATE.md`。

结束前检查：

- 当前 Phase 是否仍准确；
- 当前 AI 角色是否仍准确；
- 权威文档索引是否指向真实文件；
- 本轮确认事项是否已写入正确文档；
- Exit Criteria 状态是否基于证据；
- 下一项 Maker 决策与恢复入口是否明确；
- 是否误创建了重复文档或提前进入下一 Phase。

默认使用中文交流和编写 Markdown 正文；文件名、代码和标准技术名词可以保留英文。
