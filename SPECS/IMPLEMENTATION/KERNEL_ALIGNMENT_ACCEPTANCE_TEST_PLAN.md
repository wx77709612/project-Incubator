# Kernel 与 Skill 对齐验收计划

状态：APPROVED / ACCEPTANCE AUTHORIZED；上游：[实施计划](KERNEL_ALIGNMENT_IMPLEMENTATION_PLAN.md)。

| ID | 验证方式 | 通过条件 |
| --- | --- | --- |
| A01 | 新漂移测试 RED → GREEN | 修改前真实失败、修改后通过；反注入旧规则时能捕获 |
| A02 | Router、三个 Child、两个 Host 与全部 references/分发 AGENTS/模板扫描 | 唯一入口、Kernel 权威、无旧活动流程；Legacy 分类完整，无漏扫 |
| A03 | 状态/恢复集成测试 | Mod/Desktop/Web 使用 inspect_project；Receipt hash/revision/ref 篡改失败关闭，查询前后零写入 |
| A04 | Router/Registry/Activation | Mod/Sims 4、Desktop/Windows、Web/null 正确；Desktop 缺 Host、Web 非空 Host 拒绝；已激活和部分文件拒绝重新初始化 |
| A05 | prepare_activation → next-turn authorization → initialize_project | 三文件合法、revision 0、产品决定绑定真实测试 PromptRef、Receipt 验证；无授权不激活 |
| A06 | prepare_change / commit_change / decline_change | 精确作用域授权、revision、Decision 引用、拒绝与重放/过期/错误 scope 拒绝；失败不泄漏拟议业务状态 |
| A07 | Receipt 与真实 Stop Hook | 未闭合阻止；有效当前 Receipt 放行；回读失败与回滚证据明确 |
| A08 | 候选结构、负向指导、白名单与仓库外 --full | 不带 Legacy Runtime/_V*、不回退源码、三路由及 Activation/Receipt 成功；记录聚合 SHA-256 |
| A09 | 正式安装及新会话 | 权威 source→候选→安装一致；实际加载新版本 MCP 与六 Skill；旧全局入口只路由或不再发现；Hook 来源已验证 |
| A10 | npm test + 既有 Legacy/Acceptance 回归 | 所有适用测试通过，计数、命令、退出码、环境限制分别记录；无删除失败测试冒充成功 |
| A11 | 文档图与保护资产 | ACP→Design→Contract→Runtime→两 Plan 可追踪；索引状态一致；_V*、scriverse、用户文件不变 |

## 执行与证据规则

所有写状态实验只在新建临时 Managed Project；模拟 Maker Prompt 仅供测试。本计划不授权接管或变更 scriverse。不要求为仓库规格审批复制 request_id/scope_digest。

基线与实施后的 npm test 分开记录。沙箱 EPERM、依赖准备失败或宿主尚未刷新不能算业务测试失败已修复。安装工具不可用时记录阻塞，不编辑缓存替代。

A09 的宿主实际加载与候选独立进程烟雾验收分别报告；缺任一必需结果，相关 Task 保持 BLOCKED。通过本轮不代表 V1.1 Round 2R、Web 真实产品现场验证或发布归档完成。

## 退出标准

A01–A11 全通过且证据可重放；所有实施 Task 完成；无未解决授权或安装来源问题。Maker 再决定发布。正式计划审批前，本轮只收集审计与基线证据。

## 正式批准记录

Maker 于 2026-10-19 对本 chat 上轮列出的正式规格、逐项 Invariant 调整及实施/验收计划回复“确认”，批准本轮范围实施。该批准不授权更改任何真实 Managed Project 状态。
