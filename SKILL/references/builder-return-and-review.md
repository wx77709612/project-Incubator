# Builder Return And Review Reference

用于 Project Incubator Skill 在 AI Builder 完成、失败或暂停后，回到 AI Collaborator 视角检查结果、验证证据、Diff 范围、Maker 审阅入口和状态写回需求。

读取时机：当 Builder 返回结果、报告失败、请求暂停，或 Maker 需要审阅 Builder 产物时读取。

相关 Skill 资产：

- `references/builder-handoff-checklist.md`
- `references/task-type-and-writeback.md`
- `references/gate-response-and-authorization.md`

## 1. 文档职责

本文档承载 R3-02 的 Build 输出：定义 AI Builder 完成任务、验证失败或无法继续时，如何返回 AI Collaborator 视角，如何报告实际结果与证据，如何让 Maker 进入 Diff 审阅，以及何时更新状态入口。

本文档不执行 Build，不替 Maker 接受 Diff，不自动提交、推送或合并，不宣布 Phase 完成，也不把 Builder 的“已生成”当作项目完成。

## 2. 返回原则

Builder 完成任务只代表执行步骤结束，不代表任务被 Maker 接受，也不代表 Phase 可切换。

Builder 返回后必须先由 Collaborator 回看：

- 是否符合原 Ticket 或等价执行边界；
- 产物承载类型、路径域和适用写法是否与交接边界一致；
- 是否符合上游设计、Phase 目标和禁止范围；
- 是否提供了验证证据；
- Diff 是否只包含本任务范围；
- 是否存在失败、风险、未完成项或需要 Maker 决策的事项；
- 是否需要更新 `DOCS/PROJECT_STATE.md` 或其他权威文档。

Maker 审阅前，任务不得标记为 Accepted 或 Merged。Git 写操作仍受 Maker 手动验收门约束。

## 3. Builder 返回报告格式

Builder 返回时应提供以下信息：

```text
Builder 返回报告：
- 任务边界：
- 产物承载类型：
- 路径域与适用写法：
- 实际修改：
- 验证证据：
- 未完成项：
- 风险和阻塞：
- Diff 范围：
- 偏离 Ticket 或设计的内容：
- 完成后建议更新的文档：
```

其中：

- `任务边界` 引用启动前交接边界，不重新定义目标；
- `产物承载类型` 与 `路径域与适用写法` 引用启动前交接边界，用于检查是否把一种产物格式规则套到另一种产物上；
- `实际修改` 列出文件、资产或文档变化；
- `验证证据` 包含命令、检查、手工验证或无法验证的原因；
- `未完成项` 必须如实列出；
- `Diff 范围` 用于 Maker 审阅和后续 Git 闭环准备；
- `偏离 Ticket 或设计的内容` 触发 Collaborator 回看，不得静默接受；
- `完成后建议更新的文档` 只作为候选，写回仍按写回规则判断。

## 4. Collaborator 回看清单

Builder 返回后，AI Collaborator 按以下顺序回看：

| 检查项 | 必须判断 | 失败时动作 |
| --- | --- | --- |
| 任务边界一致性 | 实际结果是否符合目标、非目标、输入、输出和允许范围 | 标记未完成或要求 Builder 修正 |
| 承载类型一致性 | 实际产物是否符合交接时声明的承载类型、路径域和适用写法；是否误套项目文档、Skill reference、模板、代码、配置或 Prompt 的规则 | 触发承载类型错位门槛，报告错位并等待修正或 Maker 决定 |
| 禁止范围 | 是否修改了项目方向、Phase、成功标准、Git 状态或权威规则 | 触发对应硬性门槛 |
| 验证证据 | 验证是否执行，结果是否支持验收标准 | 验证失败或缺失时不得宣称完成 |
| Diff 范围 | Diff 是否只包含本任务范围 | 报告越界 Diff，等待 Maker 决定 |
| 设计一致性 | 是否符合上游设计文档和当前 Phase 目标 | 列出偏离与风险 |
| 未完成项 | 是否仍有明确缺口或阻塞 | 保持 Working 或 Blocked |
| Maker 审阅入口 | Maker 需要在 IDE Diff 中检查什么 | 进入 Ready for Maker Review |
| 状态回写 | 是否影响路径、状态、阻塞、下一步或恢复入口 | 只写回必要状态 |

## 5. Maker 审阅入口

当 Collaborator 回看通过且没有阻断风险时，AI 应向 Maker 报告：

- 修改文件和范围；
- 验证结果；
- 未完成项、风险或无风险说明；
- 需要 Maker 在 IDE Diff 中检查的内容；
- 当前任务状态：Ready for Maker Review；
- 不提交、不推送、不合并。

Maker 审阅可以产生三种结果：

| Maker 结果 | AI 行为 |
| --- | --- |
| 要求修改 | 在当前任务边界内继续修改，不创建新任务 |
| 内容方向接受但未授权 Git | 保留 Diff，状态可继续等待 Maker Review 或进入下一同里程碑任务，具体按状态入口记录 |
| 明确接受里程碑 Diff 或要求稳定检查点 | 进入 Git 闭环准备流程，但仍不自动执行 Git 写操作 |

## 6. 状态回写判断

Builder 返回后，只有以下变化需要考虑写回：

- 任务状态变化为 Working、Blocked、Ready for Maker Review、Accepted 或 Merged；
- 新增或更新了需要下轮恢复的产物路径；
- 验证失败影响当前任务能否继续；
- 出现真实阻塞或阻塞解除；
- 下一项 Maker 决策发生变化；
- 下一轮恢复入口发生变化；
- 权威文档集合发生变化。

以下内容不写入 `PROJECT_STATE.md`：

- Builder 执行过程流水；
- 验证命令的长输出；
- 单次 Diff 审阅细节；
- 可由 Git 历史追溯的文件变化过程；
- 未经 Maker 确认的成功判断；
- 只是临时建议或一次性解释。

## 7. 失败与风险处理

| 场景 | 任务状态 | AI 行为 |
| --- | --- | --- |
| 验证失败 | Working 或 Blocked | 报告失败命令或手工检查结果，说明能否在当前范围修复 |
| 验证未执行 | Working | 不宣称完成，说明未执行原因和后续验证方式 |
| Diff 越界 | Blocked 或 Working | 报告越界文件和影响，等待 Maker 决定是否拆分或回退 |
| 承载类型错位 | Blocked 或 Working | 报告错位产物、被误套的规则和正确承载类型；不进入 Maker Review，除非 Maker 明确接受该例外 |
| 违反禁止范围 | Blocked | 触发硬性门槛，不继续扩大 |
| Builder 报告不完整 | Working | 要求补充实际修改、验证证据、风险或 Diff 范围 |
| 需要 Maker 决策 | Ready for Maker Review 或 Blocked | 明确列出决策点，不替 Maker 判断 |

## 8. 验证场景映射

### S7 Builder 完成后

**输入场景**

- Builder 报告修改完成；
- 存在验证证据和 Diff。

**预期行为**

- AI 返回 Collaborator 视角；
- 检查结果、验证证据、Diff 范围和状态回写需求；
- 不直接宣布项目完成；
- 进入 Maker Diff 审阅入口。

### 验证失败场景

**输入场景**

- Builder 修改了文件；
- 验证命令失败或手工验证未通过。

**预期行为**

- AI 报告失败证据；
- 不将任务标记为 Ready for Maker Review；
- 判断是否可在当前范围修复，或是否 Blocked；
- 不隐藏失败。

### Diff 等待审阅场景

**输入场景**

- Builder 完成并通过回看；
- Diff 等待 Maker 审阅。

**预期行为**

- AI 报告修改范围和验证结果；
- 提醒 Maker 在 IDE Diff 中检查；
- 不自动暂存、提交、推送或合并；
- 任务状态为 Ready for Maker Review。

### 承载类型错位场景

**输入场景**

- Builder 返回的产物路径或正文看似完成；
- 但 Skill reference 使用了项目 Phase 文档的“文档状态”表，或不会实例化为目标项目 `DOCS/` 权威文档的模板、代码、配置、Prompt 正文套用了其他承载物的格式规则。

**预期行为**

- AI 返回 Collaborator 视角并触发承载类型错位门槛；
- 报告错位产物、路径域、误套规则和正确适用写法；
- 不进入 Ready for Maker Review，除非 Maker 明确接受该例外或要求按当前范围修正。

### 状态回写卫生场景

**输入场景**

- Builder 返回报告包含大量过程和验证输出；
- 只有产物路径、任务状态和下一步影响恢复。

**预期行为**

- 规则正文或任务报告保留必要证据；
- `PROJECT_STATE.md` 只收敛路径、状态、阻塞、下一步或恢复入口；
- 不把过程流水写入状态入口。

## 9. R3-02 边界检查

本文档满足 R3-02 的输出要求：

- 定义 Builder 实际修改报告；
- 定义验证命令或手工验证结果要求；
- 定义未完成项和风险报告；
- 定义 Diff 范围报告；
- 定义 Collaborator 回看清单；
- 定义承载类型错位的返回复核；
- 定义 Maker 审阅提示；
- 定义是否需要更新 `PROJECT_STATE.md` 的判断；
- 覆盖 S7、验证失败、Diff 等待审阅、承载类型错位和状态回写卫生场景；
- 不执行 Build；
- 不替 Maker 接受 Diff；
- 不自动提交、推送或合并；
- 不宣布 Phase 完成。

## 10. 后续消费关系

最终 `SKILL.md` 可把 R3-01 与本文档合并为 Builder 交接与返回闭环的短入口。后续如需将检查清单固化进 Ticket 模板，应另开 Build Ticket，并经 Maker 明确确认。
