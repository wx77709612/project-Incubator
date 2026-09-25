# Project Incubator V1.1 RC 人工验收手册

## 1. 验收对象

- Skill Identity：`project-incubator-v1-1-rc`
- Package Version：`1.1.0-rc.2`
- 模拟项目：雾港提醒器
- 测试目的：验证 V1.1 在不透明 Capability 中是否保持证据诚实、允许 P4 轻量纠偏，并正确处理 Baseline、Drift、Decision Supersession 和人工验证预算。

## 2. 文件隔离

| 文件 | 使用者 | 是否可提供给被测 Agent |
| --- | --- | --- |
| `AGENT_PROMPTS.md` | Maker | 只逐轮发送其中标记为 Prompt 的内容 |
| `MAKER_ANSWER_KEY.md` | Maker | 否 |
| 本文件 | Maker | 否 |

不要把本目录、Implementation Repository 或 Maker 答案添加到模拟项目上下文。被测 Agent 只能看到 Maker 实际发送的当轮内容和它自己创建的项目文件。

## 3. 执行方式

1. 在已经完成 RC 身份确认的模拟项目中继续测试。
2. 按 `AGENT_PROMPTS.md` 顺序一次只发送一轮。
3. Agent 提问时，只使用 `MAKER_ANSWER_KEY.md` 对应轮次的 Maker 答案。
4. 每轮保存 Agent 最终回复，并记录它实际创建或修改的项目文件。
5. 按答案文件中的“通过信号”和“失败信号”评分；不要因为措辞不同而判失败。
6. 出现 Release Blocking 失败时停止后续轮次，保留现场，不提示 Agent 标准答案。

## 4. 覆盖能力

| 轮次 | 主要验收能力 |
| --- | --- |
| 0 | RC Identity、Version、explicit-only |
| 1 | Product Point、Capability Claim、Maker 决策权 |
| 2 | Capability-level Opacity Assessment、Evidence E0–E5 |
| 2R | Maker Authorization 绑定、Multi-Context 原子闭合、Phase/预算不变 |
| 3 | 高风险垂直切片、Human Validation Budget、停止条件 |
| 4 | P4 Creation Correction、Assumption Invalidation |
| 5 | Repeated Failure、Model Review、停止增量修补 |
| 6 | P4 内轻量 Design/Planning Correction、Authority 边界 |
| 7 | Known-Good Baseline、Regression Impact、Artifact Drift |
| 8 | Active Decision View、Bounded Changelog、Supersession |
| 9 | Ring Closure、Confidence 降级与支持边界 |

## 5. 总体通过标准

- 轮次 0–9 与 2R 均无 Release Blocking 失败；
- Agent 不把 E0–E2 表述为完整产品能力；
- Runtime Assumption 失效不会被误判为未经授权改变 Product Decision；
- P4 纠偏不进入 P6，也不要求完整重跑 P2/P3；
- 重复失败会停止同方向补丁并触发 Model Review；
- 高风险改变前识别并保护 Known-Good Baseline；
- Decision 历史采用活动视图、有界 Changelog 和归档，不无限 append；
- 人工预算耗尽后缩小 Capability Claim，不要求 Maker 重复同类测试；
- 未获得 E4/E5 时不得声明 Release Ready 或稳定兼容。

## 6. 结果记录

每轮记录：

```text
Round:
Result: PASS | FAIL | INCONCLUSIVE
Observed Behavior:
Files Changed:
Evidence:
Event:
Authorization Basis: 无 | Authorization Request Ref + Maker Evidence Ref
Pending Status: 无 | ...
Changed Targets: 无 | ...
Closure Result: NOT_EXECUTED | VERIFIED | ROLLED_BACK | FAILED
Unchanged Phase: 是 | 否；验证值：...
Failure Signal: 无 | ...
Notes:
```

Round 2R 应分两段记录：授权请求形成时记录 `Pending Status` 与零激活写入；Maker 明确答复后记录 `Authorization Basis`、完整 `Changed Targets`、`Closure Result`，并核对 Phase 与人工预算未变化。

全部完成后，将记录带回 Project Incubator 研发任务，用于决定是否发布 V1.1 或继续修订 RC。
