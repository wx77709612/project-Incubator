# Opaque Capability Extension Design

## 1. 文档状态

| 字段 | 值 |
| --- | --- |
| Specification Version | V1.1 |
| Status | APPROVED |
| Previous Baseline | 无；V1.1 新增 |
| Architecture Decision | Decision 010、011 |
| Core Evidence Model | `SPECS/DESIGN/EVIDENCE_MODEL_DESIGN.md` |

## 2. 目的与非目标

本 Extension 用于最终产品结果无法仅从稳定契约和本地确定性验证可靠推导的 Capability。

它指导 Agent 以受控成本获得下一层 Evidence，不新增 Core Phase，不替代 Maker Decision，不要求透明、低风险 Capability 创建额外 Artifact，也不把整个 Project 永久标记为不透明。

## 3. 启用单位

启用单位是 Capability，而不是 Project 或 Project Type。

同一项目可以同时包含：

- 不启用 Extension 的透明 Capability；
- 只启用不透明度评估的待判断 Capability；
- 完整启用产品点螺旋验证的高风险 Capability。

Project Type Profile 可以提供默认评估、代表性路径和更严格阈值，但不能替代具体 Capability Assessment。

## 4. 能力级不透明度评估（`OPACITY_ASSESSMENT`）

评估维度：

| 维度 | `LOW` | `ELEVATED` | `HIGH` / `UNKNOWN` |
| --- | --- | --- | --- |
| 契约 | 完整、稳定、版本化 | 部分缺失或变化 | 非公开、缺失、无兼容承诺 |
| 状态 | 可查询、可控制 | 部分间接观察 | 隐藏、延迟、不可控制 |
| 执行权 | 调用方控制 | 共享调度 | 外部系统主导 |
| 确定性 | 稳定复现 | 受有限环境因素影响 | 时序、随机或环境显著影响 |
| 可观察性 | 中间状态和原因可读 | 只能观察部分边界 | 主要只能看到最终结果 |
| 可自动化 | 可完整自动运行 | 部分依赖真实环境 | 依赖人工、设备或外部宿主 |
| 可归因性 | 失败接近根因 | 需要跨边界推断 | 异常与根因距离远 |
| 版本稳定性 | 有明确兼容承诺 | 版本差异需验证 | 内部行为可无告警改变 |

Extension 启用建议：

- 任一维度为 `HIGH` 或 `UNKNOWN`：建议启用；
- 两个及以上维度为 `ELEVATED`：建议启用；
- 最终产品语义必须由 Maker 在 Agent 不可访问环境确认：建议启用；
- 其余情况：默认不启用，保持 Core 轻量路径。

Agent 提交 Assessment 与 Evidence；Maker 确认可接受的验证成本、支持边界和风险。Runtime 只验证记录结构，不计算语义风险。

## 5. 产品点螺旋验证（`PRODUCT_POINT_SPIRAL`）

螺旋中心是 Product Point。每一圈同步维护：

- Capability Boundary；
- Candidate Model；
- Implementation；
- Repeatable Verification；
- Observability；
- Target-Environment Evidence；
- Confidence；
- Known-Good Baseline。

每圈只重点扩展一个主要风险维度：输入、参与者、状态、失败、持久化、时序、外部依赖、环境版本、性能或长期行为。

## 6. 代表性端到端切片

高不透明 Capability 在横向展开实现前，必须选择一个代表性端到端产品路径。该路径必须：

- 从用户可识别的触发条件开始；
- 穿过主要不透明边界；
- 到达用户可观察结果；
- 包含交付物或安装形态（如适用）；
- 同时具有最小可重复验证和目标环境 Evidence；
- 能暴露当前最高风险 Candidate Model。

Core 不规定安装、UI 注入、交互、存档等领域枚举；由 Project Type Profile 描述常见路径。

## 7. 发现轮（`DISCOVERY_RING`）

用于真实模型尚不明确的阶段。

输入：狭窄 Product Point、竞争 Hypothesis、观察能力和人工验证预算。

要求：完整生命周期、关键边界可观察、不预设全部字段或关系、不以一次成功宣称能力成立。

输出：Observation、Candidate Model、Runtime Assumption、未解释异常和下一轮区分证据。

## 8. 验证轮（`VALIDATION_RING`）

用于检验已经形成的 Candidate Model。

代表性范围至少包含不同因果机制的正常场景、关键变体、失败或中断场景，以及后续状态无污染检查。具体数量由 Claim、风险和人工预算决定，不作为固定全局规则。

输出：Evidence Record、反例、模型充分性结论、Claim/Confidence 变化和 Baseline 更新建议。

## 9. 假设区分设计（`HYPOTHESIS_DISCRIMINATION`）

每次高成本观察前必须建立：

| Hypothesis | 成立信号 | 不成立信号 | 区分 Evidence |
| --- | --- | --- | --- |

如果计划收集的信息不能区分当前竞争 Hypothesis，不应消耗人工验证预算。

## 10. 可观察性计划（`OBSERVABILITY_PLAN`）

观察层级：Correlation、Lifecycle、Boundary、Outcome、Anomaly。

计划必须定义关联标识、观察点、缺失字段含义、采样范围、频率、体积、版本和停止条件。诊断必须限于当前 Capability / Session，不得改变被观察行为。

## 11. 证据到可重复验证闭环（`EVIDENCE_TO_VERIFICATION_LOOP`）

```text
目标环境异常
→ 提取最小稳定 Evidence
→ 归一化为 Fixture / Trace
→ 证明当前实现不能正确处理
→ 修改模型或实现
→ 自动化回归通过
→ 返回目标环境验证 Product Point
```

自动化验证只能证明系统处理已建模输入的能力，不能证明外部环境总会产生相同输入。

## 12. 单圈闭合检查（`RING_CLOSURE_CHECK`）

一圈只有在以下条件全部满足时才能闭合：

- Capability Claim 与 Excluded Boundary 明确；
- Candidate Model 能解释本圈 Observation；
- Implementation 未超出 Claim；
- 已知规则有 Repeatable Verification；
- 目标环境路径可观察；
- Delivery Artifact 已检查；
- 完整目标环境路径已执行；
- 没有未解释的高严重性异常；
- 未覆盖内容保留在外圈；
- Known-Good Baseline 已建立或明确记录无法建立的阻塞原因。

Gate 可检查完整性和 Evidence 引用；Agent 判断模型解释力；Maker 确认需要人工判断的产品结果。

## 13. 目标环境已知可用基线（`TARGET_ENVIRONMENT_BASELINE`）

Extension 在 Core Baseline 模型上补充目标环境版本、安装或交付形态、场景、人工观察、诊断版本和兼容范围。

Baseline 只对已声明 Claim 与环境有效，不得泛化为整个产品稳定。

## 14. 人工验证预算（`HUMAN_VALIDATION_BUDGET`）

Planning 必须记录：

- Maker 需要执行或观察什么；
- 单次预计成本；
- 建议批次；
- 最大重复次数；
- 每次失败必须返回的最小 Evidence；
- 哪些结果可以复用为 Fixture；
- 停止并进入 Model Review 的条件。

达到预算上限且没有新增区分 Evidence 时，Agent 不得要求 Maker 重复相同测试。

## 15. 兼容性扩展轮（`COMPATIBILITY_EXPANSION_RING`）

只有当前 Product Point 在基准环境闭合后，才沿版本、设备、宿主或平台维度扩展。每圈只增加一个主要兼容维度，并明确代表性组合、排除范围和 Evidence Level。

## 16. Capability Spiral Record

高风险 Capability 可以创建以下 Optional Context / Extension Artifact：

```text
Capability
Product Claim
Opacity Assessment
Current Ring
Supported Boundary
Excluded Boundary
Candidate Model
Facts
Assumptions
Hypotheses
Evidence Level
Repeatable Verification
Target-Environment Evidence
Known-Good Baseline
Invalidation Signals
Human Validation Budget
Next Expansion Dimension
```

它不复制 Current Phase、Project Goal 或 Maker Decision，只保存 Extension 特有内容及对 Core Authority 的引用。

## 17. 退出与降级

当稳定契约、自动化环境和可观察性已经足以可靠推导产品结果时，Capability 可以退出完整螺旋，只保留 Core Claim、Evidence 与 Baseline。

退出由 Agent 基于 Evidence 提案；涉及支持边界变化时由 Maker 确认。历史 Extension Evidence 归档，不继续进入默认 Context。

## 18. 不变量

1. Extension 按 Capability 启用；
2. Extension 不新增 Core Phase 或 Transition；
3. Extension Artifact 不替代 Core Context；
4. 一次目标环境成功不等于稳定；
5. 自动化验证不替代目标环境产品语义；
6. 人工测试必须产生可区分 Evidence；
7. 兼容性扩展不得先于基准环境闭合；
8. Project Type Profile 只能收紧 Core 下限。
