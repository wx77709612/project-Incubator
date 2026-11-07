# 待批准变更回复实施计划

状态：IMPLEMENTED / TARGETED TESTS PASSED / FULL SUITE NOT GREEN；依据 Maker 于 2026-11-06 确认的[架构提案](../ARCHITECTURE/PREPARED_CHANGE_REPLY_CHANGE_PROPOSAL.md)和用户给出的逐项验收标准。上游：[Design](../DESIGN/PREPARED_CHANGE_REPLY_DESIGN.md) → [Contract](../CONTRACTS/PREPARED_CHANGE_REPLY_CONTRACT.md) → [Runtime](../RUNTIME/PREPARED_CHANGE_REPLY_RUNTIME_SPEC.md)。

## Task 1：确定性批准句

文件：`project-incubator-plugin/src/server.mjs`、`src/kernel/approval-message.mjs`、`templates/codex/AGENTS.md`、相应集成与模板测试。先写失败测试，再给 `CHANGE_PREPARED` 增加 `approval_message`；验证句子包含与权威待批准请求相同的两个标识，并可被现有 Maker Prompt 解析器接受。模板提示 Agent 原样展示批准句与回执，并等待 Maker 下一轮明确批准。

## Task 2：Stop 闭合与 Agent 引导

文件：`project-incubator-plugin/hooks/stop.mjs`、相应集成测试。先覆盖漏请求 ID、漏或错摘要、漏完整批准句、漏 Receipt、全部正确、只查询旧请求、其他 session、续轮警告；再实现最小检查。不改变现有 Receipt 验证和防循环规则。

## Task 3：验收与状态报告

执行[验收计划](PREPARED_CHANGE_REPLY_ACCEPTANCE_TEST_PLAN.md)中的定向及插件全量测试，检查 `git diff --check`、活动层引用和改动范围。报告测试环境限制与仍不能保证的宿主边界；不修改或激活真实 Managed Project。

## 实施记录（2026-11-06）

Task 1：COMPLETED。`prepare_change` 返回由共享函数生成的 `approval_message`；包内 `AGENTS.md` 提醒 Agent 原样展示并等待下一轮 Maker 授权。

Task 2：COMPLETED。Stop 对本轮当前请求逐项检查并给出准确补写提示；宿主换 `turn_id` 的续轮保持 marker 失败规则，但警告附同 session 请求的准确文本。

Task 3：COMPLETED（有界验证）；全量无排除验收仍未通过。定向 Hook 18/18（排除 1 个当前环境无法创建符号链接的测试）、Web E2E 20/20、模板定向 1/1；候选结构验证通过并包含新模块。最终代码排除已确认符号链接用例和既有回滚竞争用例后，回归 398/398 通过。无排除运行仍遇到 Windows `symlink` 的 `EPERM` 和既有 `agent-entry` 回滚竞争测试的 `ENOENT`，不能把无排除全量验收标记为通过。未修改真实 Managed Project。

## 候选包记录（2026-11-06）

Maker 要求打包和推送。源码 manifest 构建号提升为 `0.3.0+codex.20261106223727`；白名单打包后安装锁定生产依赖，`verify-candidate --structure-only` 和隔离临时项目上的 `--full` 均通过。候选聚合 SHA-256 为 `30dd5bc00b704a8552662c9f0039c3d93c0983382fb139b8b95c9b3a571df67b`，`source_fallback_detected=false`。ZIP 位于 `project-incubator-plugin/dist/project-incubator-plugin-0.3.0+codex.20261106223727.zip`，SHA-256 为 `84b336bf16659945d73516478999852cdab8d57f232b0a68c3b7c77ba71844d1`。打包时尚未安装；安装结果见下节。

## 正式安装记录（2026-11-07）

Maker 要求安装。先备份 `C:/Users/Xenia_Woo/.agents/plugins/marketplace.json` 到 `C:/Users/Xenia_Woo/.codex/backups/prepared-change-reply/0.3.0+codex.20261106223727/marketplace.json`；原文件 SHA-256 为 `b244e537dceb375f2183e64f21b05169b021e35a9be7d0ae1168c5d66f741fd6`。将已验证候选复制到版本化 personal source，结构聚合哈希仍为 `30dd5bc00b704a8552662c9f0039c3d93c0983382fb139b8b95c9b3a571df67b`；marketplace 仅将该插件 source 精确切换到新版本目录。

`codex plugin add project-incubator-plugin@personal --json` 返回安装路径 `C:/Users/Xenia_Woo/.codex/plugins/cache/personal/project-incubator-plugin/0.3.0+codex.20261106223727`。随后 `codex plugin list --marketplace personal --json` 显示新版本 `installed=true`、`enabled=true`。安装目录的结构聚合哈希与候选相同，`server.mjs`、批准句模块、Stop Hook 和 Agent Entry 模板逐文件 SHA-256 相同；从安装目录启动独立 MCP 子进程运行 `verify-candidate --full` 通过，`source_fallback_detected=false`。验证仅使用已清理的隔离临时项目；未修改真实 Managed Project。当前已存在的聊天不作为热加载证据，新任务需由宿主重新加载新版本。
