# Kernel 与 Skill 系统性对齐实施计划

状态：APPROVED / IMPLEMENTATION AUTHORIZED；2026-10-19。

供执行 Agent：获批后采用 superpowers:executing-plans 按任务实施；本计划不要求分派子 Agent。

Goal：从唯一 Plugin Router 经现行 Kernel 恢复与推进，关闭旧入口、模板和安装源造成的行为漂移。

Architecture：保留 0.3.x Kernel；只修正入口、分发指导与验证约束，旧运行资产明确隔离。Tech Stack：Node >=24、现有 Node test runner、现有 Python Legacy 回归工具。

Spec：[Runtime](../RUNTIME/KERNEL_ALIGNMENT_RUNTIME_SPEC.md) → [Contract](../CONTRACTS/KERNEL_ALIGNMENT_CONTRACT.md) → [Design](../DESIGN/KERNEL_ALIGNMENT_DESIGN.md) → [ACP](../ARCHITECTURE/KERNEL_ALIGNMENT_CHANGE_PROPOSAL.md)。

## 全局约束与审阅重点

- 审批本正式规格与两份 Plan 后方可修改产品行为、模板语义及测试。
- 不改 _V*、scriverse、原 checkout 未跟踪文件及其他 chat 的工作区。
- 不新增 Runtime/Schema/工具，不复制 Router，不代替 Maker 授权。
- 重点覆盖 Receipt 被篡改、旧入口插件缺失、Host 不匹配、包外规格依赖、安装来源与加载版本不一致。
- Legacy 模板可保留历史语义，但必须明确为非现行且不被 Plugin 默认分发；扫描不得因 Legacy 目录存在而误报全部旧词。

## Task 1：先建立失败的漂移测试

Files：新增 project-incubator-plugin/tests/contract/runtime-guidance-drift.test.mjs；修改候选验证相关测试与 scripts/verify-candidate.mjs（后续 Task 3 实现）。

接口：输入仓库入口、递归 skills/**/*.md、AGENTS 分发文件、模板分类与安装源；输出逐文件违约与非零退出。扫描默认排除 _V*、node_modules、冻结日志与 Legacy-only 正文；必须显式检查这些正文不会被现行入口加载/分发。

- [x] 新增断言：旧入口只有 Router 路由；所有 Child 恢复包含 inspect_project；Mod 不再以 get_project_state 恢复；Host 依赖验证路由；活动指导不要求 Markdown 权威、旧 Python、旧 Host Bootstrap 或多 Context 执行；包内不依赖包外规格。
- [x] 运行 node --test tests/contract/runtime-guidance-drift.test.mjs；记录对原始 Skill 的预期失败列表。失败必须来自语义违约，不能来自依赖缺失或 EPERM。
- [x] 加入负向样本，证明检测能捕获旧流程回注，并允许“禁止旧流程”的合法说明与 Legacy 标签。

## Task 2：修正全量入口与分发

依赖 Task 1 红灯证据和正式 Gate。Files：PROJECT_INCUBATOR/SKILL.md、AGENTS.md、README.md、templates/**/*.md；project-incubator-plugin/skills/ 下全部六个 SKILL.md 及 references；根 AGENTS.md；SPECS/README.md、ARCHITECTURE/ARCHITECTURE_DECISIONS.md、DOCUMENT_ARCHITECTURE.md 和影响清单所列活动旧规格；project-incubator-plugin/ARCHITECTURE.md。

- [x] 实施 KAC-01–07；Mod 使用 inspect_project；其他 Child/Host 明确验证与权威。
- [x] 旧全局入口最小化，旧模板明确 Legacy，集成 AGENTS 指向 Router；不自动覆盖已有 Managed Project。
- [x] 按 ACP 逐项更新根 Invariant 与 Decision 015；旧活动文档加准确作用域/替代说明，修正索引授权矛盾，不改历史证据正文。
- [x] 更新 tests/contract/legacy-invariants.test.mjs：只解除获批修改指导的字节锁；保留领域实现/Profile 锁，新增 Mod/Host 行为语义断言。
- [x] 漂移测试绿灯，npm test 全量通过。

## Task 3：权威源打包、安装与来源核验

依赖 Task 2。Files：Plugin manifest、必要的 package 元数据、scripts/package-candidate.mjs、verify-candidate.mjs 与 tests/integration/candidate-package.test.mjs；TOOLS 旧 RC 入口增加非默认说明；新增 TOOLS 安装来源核验/最小兼容入口部署工具（仅在现有安装机制无法复用时）。

- [x] 先测试候选中含旧指导、外部依赖或来源错误时拒绝；再实现候选漂移校验。
- [x] 确认 personal marketplace 权威 source 与受支持安装命令；不能证明来源则停止安装并报告阻塞。
- [x] 生成新候选版本，从源码白名单打包至全新仓库外目录；在执行现有含递归清理的 packager 前确认目标绝对路径仅为本轮候选目录且不含已有用户内容。
- [x] npm ci --omit=dev；node scripts/verify-candidate.mjs --structure-only <candidate>；--full <candidate> <temporary-managed-root>。
- [x] 经正式安装机制更新；旧全局 Skill 如有用户改动则备份并比较，不静默覆盖；禁止直接改缓存。
- [ ] 记录源码/候选/安装文件哈希、版本和 MCP 来源；真实宿主刷新与 Hook 未确认时保持待验收。

## Task 4：全量验收与证据

依赖 Task 3。Files：新增 ACCEPTANCE_TESTS/kernel_alignment/RESULTS.md；更新本计划、Acceptance Plan 与 SPECS/README 的实际状态。

- [ ] 执行 [Acceptance Plan](KERNEL_ALIGNMENT_ACCEPTANCE_TEST_PLAN.md) 全部矩阵，使用临时项目覆盖三路由、激活、授权、拒绝、重放拒绝、Receipt 篡改及 Stop 闭合。
- [ ] 执行 Plugin npm test；按现有测试入口运行 Legacy 全量与 Acceptance 回归，分别记录数量和环境失败，不虚构通过。
- [ ] 核验 _V* 与原 checkout 未变化；记录旧真实产品验收仍待处理，不关闭 V1.1 Round 2R/V1.2 现场验收。
- [ ] 按仓库 Task 格式报告 Changed Files、命令、实际结果、安装版本、剩余问题；无 Maker 发布批准则不归档或声称发布。

## Maker Approval

Maker 于 2026-10-19 确认正式文档及本计划，授权按依赖顺序执行 Task 1–4。

## 正式批准记录

Maker 于 2026-10-19 对本 chat 上轮列出的正式规格、逐项 Invariant 调整及实施/验收计划回复“确认”，批准本轮范围实施。该批准不授权更改任何真实 Managed Project 状态。
