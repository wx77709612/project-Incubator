# Capability Spiral Record

## 模板使用规则

本记录是 Optional Context，仅为高不透明 Capability 创建。透明、低风险 Capability 保持 Core 轻量路径，不需要创建本文件。

本记录保存能力级 Claim、Candidate Model、Evidence 和 Baseline 细节；不得复制 Current Phase、Project Goal 或 Active Maker Decision，也不得覆盖任何 Core Context Authority。

## 能力声明

- `capability_id`：待填写
- `product_point`：待填写
- `claim_status`：`HYPOTHESIZED`
- `confidence`：`LOW`
- 预期用户结果：待填写
- 失败结果：待填写

## 不透明度评估

<!-- 对契约、状态、执行权、确定性、可观察性、可自动化、可归因性和版本稳定性分别填写 LOW / ELEVATED / HIGH / UNKNOWN，并引用依据。 -->

- 评估结果：待填写
- Evidence Ref：待填写
- Extension 建议：待填写
- Maker 接受的验证成本与风险：待填写

## 当前验证轮

- `ring_type`：`DISCOVERY_RING` / `VALIDATION_RING`
- `ring_id`：待填写
- 本圈主要风险维度：待填写
- 本圈状态：待填写

## 支持边界

- 待填写

## 排除边界

- 待填写

## 候选模型

- `candidate_model_version`：待填写
- 最小模型说明：待填写
- 当前模型能够解释的行为：待填写

## 已观察事实

<!-- 只记录 Observation，不在此处写入原因解释。 -->

- 待填写

## 运行时假设

<!-- 每项包含 Assumption ID、状态、适用范围、Evidence Ref、依赖 Artifact 和失效信号。 -->

- 待填写

## 竞争假设

| Hypothesis | 成立信号 | 不成立信号 | 区分 Evidence |
| --- | --- | --- | --- |
| 待填写 | 待填写 | 待填写 | 待填写 |

## 证据等级

- `evidence_level`：`E0`
- `evaluated_scope`：待填写
- Evidence Ref：待填写
- 结论上限：待填写

## 可重复验证

- Model Verification：待填写
- Decision Verification：待填写
- Trace Replay：待填写
- Boundary Contract Verification：待填写
- Delivery Artifact Verification：待填写

## 目标环境证据

- 环境与版本：待填写
- 场景与执行引用：待填写
- Maker Observation：待填写
- 限制：待填写

## 已知可用基线

- `baseline_id`：待填写
- `baseline_status`：`CURRENT`
- 版本或修订：待填写
- 场景集：待填写
- Delivery Artifact Ref：待填写
- Evidence Ref：待填写
- 已知限制：待填写

## 失效信号

- 待填写

## 单圈闭合

- [ ] Capability Claim 与 Excluded Boundary 明确
- [ ] Candidate Model 能解释本圈 Observation
- [ ] Implementation 未超出 Claim
- [ ] 已知规则具有 Repeatable Verification
- [ ] 目标环境路径可观察并已执行
- [ ] Delivery Artifact 已检查
- [ ] 没有未解释的高严重性异常
- [ ] Known-Good Baseline 已建立，或阻塞原因已记录

## 兼容性扩圈

- 目标环境或外部平台版本：待填写
- 兼容范围：待填写
- 代表性变体：待填写
- 退出条件：待填写

## 人工验证预算

- 可用次数或时间：待填写
- 每次验证的区分目标：待填写
- 预计 Maker 操作：待填写
- 预算耗尽停止条件：待填写

## 下一扩展维度

- 下一圈只扩展的主要风险维度：待填写
- 所需新 Evidence：待填写
- 开始条件：待填写
