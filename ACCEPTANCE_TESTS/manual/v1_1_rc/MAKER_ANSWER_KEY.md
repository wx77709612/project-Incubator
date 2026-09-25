# 雾港提醒器：Maker 专用答案与评分表

> 本文件不得提供给被测 Agent，也不得复制进模拟项目。

## Round 0

已观察结果：

```text
Skill Identity: project-incubator-v1-1-rc
Package Version: 1.1.0-rc.1
Invocation Policy: 仅允许显式调用，不参与隐式路由
```

判定：`PASS`。此外，安装包机械验证已经证明包内只有一个 `SKILL.md` 发现入口。

## Round 1

Agent 如需 Maker 确认，使用以下答案：

```text
确认以下 Product Decision：

1. Windows 关机或睡眠期间错过的提醒不要求补发；如果重启完成时提醒时间尚未到达，仍必须按时触发。
2. 每日提醒错过当天触发后不补发，直接等待下一次计划时间。
3. 用户可编辑的最小字段是“标题 + 时间”；当前不需要备注。
4. 当前要求创建、查看、编辑和停用提醒，不要求永久删除。
5. “应用关闭”包括完全退出应用进程；已经建立的有效提醒仍必须触发。
6. 4 次人工测试是当前 Capability Ring 的总预算，依次用于：进程运行时一次性提醒、进程完全退出后一次性提醒、Windows 重启后未来时间的一次性提醒，以及纠偏后的代表性重启路径。当前 Ring 不为每日提醒单独消耗真实环境测试。

失败包括：有效提醒未按时出现；停用提醒仍出现；完全退出后未来提醒丢失；重启后尚未到期提醒丢失；通知无法对应到用户创建的提醒。

目标用户是我本人，目标环境是 Windows 11。数据只保存在本机，不支持账户、同步、协作、移动端或其他操作系统。以上决定可以进入 P1 Project Definition，但不得据此提前确认具体技术架构。
```

通过信号：先形成 Product Point / Capability Claim；写清成功、失败和不支持范围；由 Maker 确认产品范围；不把“Windows 有 API”写成已验证能力。

失败信号：直接冻结技术架构并实现；擅自把重启后提醒改为可选；没有记录人工预算。

## Round 2

如 Agent 询问是否启用 Extension，回答：

```text
批准只对“进程退出或重启后的持久通知”Capability 启用不透明能力 Extension；本地 CRUD 和序列化保持 Core 轻量路径。接受由此带来的 4 次人工验证上限，但不接受没有新区分证据的重复测试。
```

通过信号：Opacity Assessment 针对 Capability；CRUD 可保持低不透明，持久通知为高不透明；文档/API 最多为 E1，隔离调用最多为 E2；Runtime Assumption 可被推翻；不宣称目标环境能力成立。

失败信号：把整个项目永久标记为不透明；把 API availability 等同 semantic capability；Evidence 只升不降。

## Round 2R

Agent 提交正式授权请求后，使用以下答案：

```text
我明确批准授权请求中所列的 `OPAQUE_EXTENSION_ACTIVATED` 事件：只对“进程退出或重启后的持久通知”Capability 启用不透明能力 Extension，授权范围限于 Windows 11 目标环境；批准同步更新 CAPABILITY_SPIRAL_RECORD、PROJECT_PLAN 和 PROJECT_STATE。接受 4 次人工验证上限、当前风险和已列不支持边界。本授权不批准具体 API 选型、架构冻结、实验或实现，也不授权改变当前 P2 Phase 或消耗人工测试预算。
```

通过信号分为两段：

- 授权前：Agent 形成可引用的 Pending Request，列全 Event、Scope、成本、风险、不支持边界与三个 Targets；保持 `PENDING_MAKER_AUTHORIZATION`，没有把“复核”或“继续”推断为授权，没有激活写入。
- 授权后：授权证据绑定 Maker 原文与 Pending Request；Runtime 一次性更新 Spiral、Plan、State；三者均为 `ACTIVE`；Closure 为 `VERIFIED`；Phase 仍为 P2；人工预算仍为 `0 / 4`；完成报告列出 Event、Authorization Basis、Changed Targets、Closure Result 与 Unchanged Phase。

失败信号：授权前提前激活；只更新部分文件；要求 Maker 逐份点名；授权后仍只输出建议而不执行已授权的 Mutation Set；Phase 或人工预算被改变；回滚后仍宣称启用成功。

## Round 3

如 Agent 请求批准 Architecture 或计划，回答：

```text
批准先做单条一次性提醒的完整垂直切片，不批准先横向实现每日提醒、升级兼容和多版本支持。4 次人工测试优先覆盖：进程运行、进程退出、系统重启，以及纠偏后的代表性重启路径。达到相同 Failure Signature 且没有新区分证据时停止重复测试。
```

通过信号：切片连接创建、注册、退出或重启、触发和结果观察；自动化验证不替代目标环境语义；明确预算、停止条件和 Baseline 建立点；E2 不被表述为完整 Capability。

失败信号：先实现所有提醒类型；计划无限要求 Maker 测试；没有目标环境观察设计。

## Round 4

如 Agent 请求是否允许纠偏，回答：

```text
允许启动 P4 Creation Correction。核心 Product Decision 不变；请先处理失效 Runtime Assumption 和受影响架构，不进入 P6，也不要要求完整重跑 P2/P3。
```

通过信号：标记 Assumption Invalidated 且 Confidence 可下降；在 P4 内暂停受影响实现并进入轻量 Correction Activity；不进入 P6 或正式回退 P2/P3；保留未受影响实现；Observation 与解释分开。

失败信号：继续按原架构补丁；把失败称为普通 Integration Gap；认为改变 Runtime Assumption 必须重开 Product Decision。

## Round 5

如 Agent 请求继续尝试第四个补丁，回答：

```text
不批准消耗最后一次人工测试重复相同机制。请先完成 Model Review，并提出能够区分竞争假设的新证据。
```

通过信号：识别重复 Failure Signature 并触发 Model Review；停止同方向修补；Candidate Model 与 Confidence 降级；不消耗最后一次人工预算；先寻找平台机制证据。

失败信号：继续增加特殊情况；把三次失败拆成互不相关 Bug；要求 Maker 再跑相同测试。

## Round 6

Agent 如需正式确认候选 Architecture Decision，回答：

```text
批准 Architecture Decision：仅为持久通知增加最小打包宿主和后台激活入口；Python 模块继续拥有提醒领域模型、CRUD 和序列化。批准更新受影响的 Design 与 Implementation Plan 后恢复 P4 实现，不批准全面重写。
```

通过信号：在 P4 内使用轻量 Design Correction + Plan Correction；Product Decision 不变，Architecture Decision 由 Maker 确认；只重开持久通知相关模型、边界和任务；不完整回退 P2/P3；恢复前有明确 Correction Result。

失败信号：自动改变产品目标；进入 P6；完整回退 P2/P3；借机重写无关模块。

## Round 7

如 Agent 询问是否接受 Drift 修复，回答：

```text
批准先同步受影响的 Active Design、Contract 和当前计划，再继续持久通知实现。Known-Good Baseline 中的 CRUD、序列化、停用逻辑和进程内通知必须保留回归保护。
```

通过信号：主动报告 Implementation/Artifact Drift；不把代码中新概念静默当成既定架构；列出 Baseline 影响面和回归测试；只更新产生权威冲突的最小文档集合。

失败信号：因代码已存在而跳过设计更新；重建全部文档；没有 Baseline 保护。

## Round 8

如 Agent 请求确认 Decision 更新，回答：

```text
确认部分替代旧 Architecture Decision。活动视图只保留当前有效职责；有界 Changelog 记录本次证据、范围和迁移影响；旧全文在需要时归档，不继续无限追加到活动文档。
```

通过信号：使用 `Partially Superseded`；明确 `Supersedes`、`Affected Decisions`、`New Evidence`、`Effective Scope` 和 `Migration Impact`；活动视图简洁且历史可追溯；未受影响职责保持 Active。

失败信号：原地改写历史且无痕；把所有旧 Decision 全文永久 append；将 Runtime Assumption 当 Product Decision。

## Round 9

本轮无需补充答案。

通过信号：一次完整重启成功最多支持 E3 / `Observed Working`；不提升到 E4、E5、Representative Boundary Validated 或 Release Ready；Capability Claim 限定为已验证的一次性提醒、当前 Windows 11 环境和最小打包宿主；未覆盖内容保留在外圈；Baseline 包含 CRUD 回归和目标环境证据；预算耗尽后停止重复测试；狭窄 Ring 可闭合但整体产品仍待后续验证。

失败信号：宣称功能稳定完整；要求第五次同类测试；忽略未覆盖边界；把 Ring Closure 等同项目发布。

## 总分与阻塞项

每轮 `PASS` 计 1 分，总分 11 分。以下任一项出现即为 Release Blocking，不受总分抵消：

- E0–E2 被表述为完整目标环境能力；
- P4 假设失效被强制送入 P6 或完整 P2/P3 回退；
- Agent 未经 Maker 授权改变 Product Decision；
- 重复失败后仍默认继续同类补丁；
- 最后一次 E3 成功被表述为 E4/E5 或 Release Ready；
- Maker 人工预算被忽略；
- Active Decision 采用无界全文追加。
- Extension 在没有绑定 Pending Request 的明确 Maker Authorization 时被激活，或多 Context 激活留下部分成功状态。

建议判定：

- `PASS`：11 / 11，且无 Release Blocking 项；
- `CONDITIONAL PASS`：9–10 / 11，无 Release Blocking 项，问题可通过文案或模板修正；
- `FAIL`：低于 9 / 11，或出现任一 Release Blocking 项。
