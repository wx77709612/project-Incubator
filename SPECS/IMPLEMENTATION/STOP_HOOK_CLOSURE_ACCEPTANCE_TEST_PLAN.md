# Stop Hook 续轮闭合修复验收计划

状态：PASSED；上游：[实施计划](STOP_HOOK_CLOSURE_IMPLEMENTATION_PLAN.md)。

| ID | 场景 | 通过条件 |
| --- | --- | --- |
| SHC-01 | 正常用户轮次 | 精确 marker 被读取；revision 未变化时放行 |
| SHC-02 | 无状态变更的宿主自动续轮 | 精确 marker 缺失；最近同 project/session marker 的 revision 与 receipt ID 均等于当前值时放行 |
| SHC-03 | marker 缺失且无同 session 基线 | 失败关闭，返回稳定原因；其他 session marker 不被复用 |
| SHC-04 | marker 缺失且权威 revision 已变化 | 即使当前 Receipt 有效也失败关闭，不把旧基线当作本轮变更证明 |
| SHC-05 | marker 缺失且 Receipt ID 不一致 | 失败关闭，不以相同 revision 单独放行 |
| SHC-06 | 精确 marker 下的受控状态变更 | 保持现有 Receipt 时间与最终消息 receipt ID 要求 |
| SHC-07 | Receipt/hash/revision 损坏 | 在 marker 解析前失败关闭；不因兼容路径跳过校验 |
| SHC-08 | 真实缺陷资产保护 | 不创建 `turn-53fcd0ff...json`；`Player_Needs_Hunter` 三个权威 JSON 哈希不变 |
| SHC-09 | 全量回归 | Plugin 全量测试 0 failures；活动规格引用与状态一致 |

## 旧轮次处理

已经结束的旧轮次不回放、不迁移，也不补 marker。若宿主仍对一个缺失精确 marker 的续轮执行 Stop，只能用最近同 project/session marker 证明“自该基线以来零状态变化”；证明失败即阻断并要求由新的真实用户轮次重新建立 marker。旧 marker 不能授权操作，也不能为历史状态变更补作闭合证据。

## Maker Approval

Maker 于 2026-10-31 确认本验收语义及失败关闭边界。

## 实际验收结果

| 范围 | 结果 | 证据 |
| --- | --- | --- |
| SHC-01–SHC-07 | PASS | `hooks.test.mjs`：RED 10 pass / 4 fail；GREEN 14/14，0 fail |
| SHC-08 | PASS | 三个权威 JSON 哈希与修复前一致；指定 `turn-53fcd0ff...json` 仍不存在；Managed Project Git 状态为空 |
| SHC-09 | PASS | Plugin `npm test`：403/403；`git diff --check` 通过；活动规格无新增历史运行来源 |
| 真实缺陷只读重放 | PASS | 原 `session_id=01a15850...`、`turn_id=01a18c41...` 返回 `{ "continue": true }`，revision 6 与 Receipt ID 基线双重一致 |

受限环境中的首轮全量基线因 Windows Sandbox 阻止系统临时目录原子 `rename` 而出现 EPERM；在允许测试使用系统临时目录后，修复前 399/399、修复后 403/403 均通过。该环境差异未被当作产品失败或成功替代品。

尚未执行候选打包、正式插件安装与新宿主加载重放，因此本验收只证明源码修复和真实资产只读重放，不证明已安装版本已经更新。
