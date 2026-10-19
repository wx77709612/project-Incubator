# Kernel 对齐事实与影响清单

状态：APPROVED / AUDIT EVIDENCE；2026-10-19。上游：[ACP](KERNEL_ALIGNMENT_CHANGE_PROPOSAL.md)。

## 审计范围与分类

| 来源/资产 | 当前事实 | 分类与处置 |
| --- | --- | --- |
| project-incubator-plugin/src/server.mjs、kernel/、hooks/ | 注册 Router、激活、变更、查询及 Receipt 工具；Kernel 持久化三个 JSON | 现行实现，保留；本轮默认不改 Kernel 行为 |
| Plugin Router Skill 与 references/status-summary.md | 查询明确使用 inspect_project；激活经 prepare_activation / initialize_project | 现行入口；补充唯一入口与恢复统一约束 |
| Desktop Child Skill | 恢复已用 inspect_project；显式 windows-desktop；P0–P6 | 现行；统一权威说明，保留领域语义 |
| Web Child Skill | 恢复已用 inspect_project；Host FORBIDDEN；仍引用包外 SPECS 路径 | 现行；不得要求安装包解析研发仓库路径，包内指导需自包含 |
| Mod Child Skill | 开始前用 get_project_state | 已确认漂移：该工具只 readProjectSnapshot，未执行 verifyLatestReceipt，不能满足恢复契约 |
| Windows Host Profile | 收紧 Windows Evidence，不独立定义阶段 | 现行；明确从已验证激活读取 Host，不单独激活 |
| Sims 4 Host Profile | 要求确认激活类型与 Host，未明确验证入口 | 现行；明确经 inspect_project 验证，保留宿主规则 |
| PROJECT_INCUBATOR/SKILL.md | 广泛触发、Markdown 权威、Python runtime/、旧 Host Bootstrap、多 Context 流程 | 退出现行路径；改为最小兼容路由，不复制 Runtime |
| PROJECT_INCUBATOR/AGENTS.md | Markdown 状态权威及旧 Runtime 执行说明 | 兼容分发面；审批后改为 Router/Kernel 指引，禁止为新项目分发旧行为 |
| templates/integrations/codex/AGENTS.template.md | 触发旧全局 Skill、四 Markdown、Multi-Context Trigger | 兼容分发面；审批后替换为最小 Router/Kernel 入口；不写已有项目 AGENTS |
| templates/context/PROJECT_STATE、PROJECT_PROFILE、PROJECT_PLAN、DECISION_RECORD、CAPABILITY_SPIRAL_RECORD | Markdown Core/Optional Context 模板 | Legacy 兼容；标示非现行，不从 Plugin 入口加载或安装 |
| templates/artifacts/IMPLEMENTATION_PLAN.template.md | 阶段 Artifact 模板 | 兼容参考；审查并删除现行权威暗示，不变成状态来源 |
| PROJECT_INCUBATOR/runtime/、scripts/、JSON 定义与旧集成 | Python V1.x 实现与配置 | Legacy 兼容测试输入；不继续作为 Plugin 运行依赖 |
| TOOLS/build_rc_skill.py、install_rc_skill.py、verify_rc_skill.py 及 rc_skill_common.py | 独立 RC 打包/安装/验证路径，保护旧 stable Skill | Legacy 兼容工具；显式标识非默认安装，不破坏历史测试 |
| Plugin scripts/package-candidate.mjs、verify-candidate.mjs | 白名单打包；候选验证排除旧 Runtime、SPECS、tests 与 _V* | 现行打包源；增加指导漂移检查，结构与实际 MCP 验证保留 |
| 根 AGENTS、SPECS/README、活动旧 Design/Contract/Runtime/Plan、PROJECT_INCUBATOR/README | 旧 Markdown Invariant 与 Plugin Track 并列，索引 Web 授权叙述自相矛盾 | 审批后明确作用域和被替代条款；不能简单宣称所有旧文档都仍约束 Plugin |
| Plugin ARCHITECTURE.md、IMPLEMENTATION_PLAN.md、ACCEPTANCE_TEST_LOG.md | Kernel 权威定义已存在；日志是历史证据 | 架构对齐活动规格，已发生测试记录不改写 |
| Plugin tests/contract/legacy-invariants.test.mjs | 用全文 SHA-256 冻结 Mod/Desktop/Host Skill | 迁移测试约束：只解除获批指导变更的字节锁，保留领域代码与 Profile 锁及语义验证 |
| SPECS/_V* | 已发布冻结快照 | 历史冻结；本轮不改、不默认扫描、不打包 |

## 安装来源调查

源码基线：`codex/web-product-incubator-v1-2`，commit `ad54c36`。源工作区 clean；本 chat 独立工作区由该分支创建。原 `main-restruct` 的未跟踪 Manual_Test_Result_Record.md 保留。

本机全局 `C:/Users/Xenia_Woo/.codex/skills/project-incubator/SKILL.md` 仍为旧执行入口；它是漂移传播面。当前加载插件为 `personal/project-incubator-plugin/0.3.0+codex.20261014142716`，package 版本为 0.3.0。缓存还保留 0.2.0 历史版本，不能据此判断正在加载哪个版本；当前会话 Skill 路径指向 0.3.0 候选。

本机配置启用 `project-incubator-plugin@personal`。实际 personal marketplace 权威源路径及受支持重新安装命令尚须在实施前确认；本轮不将缓存当作源码。找不到受支持安装入口时登记安装阻塞，不直接复制到缓存伪装安装成功。

## 根因与风险

旧全局入口仍可被触发，旧集成模板继续生成旧入口；Plugin 的恢复契约未覆盖全部 Child；活动规格未明确两套权威模型的范围；测试只冻结旧指导字节，未检查系统漂移。修复必须贯穿入口、分发、模板、规格和自动化。

Mod 风险已由 server.mjs 证实：get_project_state 返回已解析 Snapshot，但不验证 state_hash、revision、last_change.receipt_id；inspect_project 验证失败抛 RECEIPT_UNVERIFIABLE。不能把 Schema 解析成功等同 Receipt 闭合。

本轮只在临时 Managed Project 验证；不读取或修改 scriverse 业务/权威状态，不运行旧真实项目接管验收。该限制不关闭已有 V1.2 真实产品验收待办。

## 正式批准记录

Maker 于 2026-10-19 对本 chat 上轮列出的正式规格、逐项 Invariant 调整及实施/验收计划回复“确认”，批准本轮范围实施。该批准不授权更改任何真实 Managed Project 状态。
