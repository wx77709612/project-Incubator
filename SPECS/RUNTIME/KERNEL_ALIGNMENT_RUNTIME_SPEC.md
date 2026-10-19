# MCP Kernel 唯一现行运行规范

状态：APPROVED；上游：[Contract](../CONTRACTS/KERNEL_ALIGNMENT_CONTRACT.md)。

## 执行序列

1. Plugin Router 根据项目是否激活区分 route proposal 与已激活恢复；不通过 Markdown 文件存在性判断激活。
2. 首次激活保持 prepare_activation / 下一轮 Maker 批准 / initialize_project；Pending Activation Bootstrap 是现行受限机制，不是 BOOTSTRAP_HOST_INTEGRATION。
3. 已激活恢复和状态查询调用 inspect_project；失败停止受影响推进，报告 Runtime 错误，不用旧 Context 或聊天重建状态。
4. 从已验证 Activation 分派 Child 与 Host，保持 Registry 的 REQUIRED/OPTIONAL/FORBIDDEN 语义。
5. 受控变更继续使用 prepare_change / commit_change 或 decline_change；Runtime Data 不构成持久业务状态。
6. 提交后验证当前 Receipt 与 revision、state_hash、last_change.receipt_id 对应；Stop Hook 继续执行现有闭合约束。

## 分发与失败

禁止现行指导要求 Python runtime/、BOOTSTRAP_HOST_INTEGRATION、Markdown Core Context 或逐文件 Multi-Context Mutation。Legacy 资产只用于兼容回归，现行候选白名单不含 PROJECT_INCUBATOR、SPECS/_V* 或 tests。

缺 Plugin/MCP、Receipt 无法验证、路由不匹配、部分控制文件、Request 过期/重放/作用域不符，都失败关闭。不得为“修复安装”直接编辑缓存或 Managed Project 控制文件。

## 运行版本

本轮基线 package 0.3.0，已安装 manifest 0.3.0+codex.20261014142716。修复候选使用新的 0.3.0+codex.<14位构建标识>，保留现行 Schema；不能把旧安装版本当作新验收结果。

版本、候选聚合 SHA-256、权威源码 commit、marketplace source、安装路径、实际 MCP 来源及 Hook 加载证据必须关联。同一进程无法刷新宿主加载时，单独标为待新会话验收，不把候选进程烟雾结果表述为宿主更新成功。

## 正式批准记录

Maker 于 2026-10-19 对本 chat 上轮列出的正式规格、逐项 Invariant 调整及实施/验收计划回复“确认”，批准本轮范围实施。该批准不授权更改任何真实 Managed Project 状态。
