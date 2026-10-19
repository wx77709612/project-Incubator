# Kernel / Skill 对齐验收结果

日期：2026-10-19（Asia/Hong_Kong）。正式规格、逐项 Invariant 调整及两份 Plan 已获 Maker 回复“确认”。

## Task 1：自动化漂移检查

Status: COMPLETED

Changed Files：Plugin tests/contract/runtime-guidance-drift.test.mjs、scripts/runtime-guidance.mjs；候选包负向测试。

Validation：初始 9 项检查 8 失败、1 控制通过；修改后全部通过。源码与候选共享校验器。独立审查发现的同行否定、相对/Windows/绝对规格路径漏检均先红后绿，见 review-red.log / review-green.log。不是依赖或沙箱错误造成的假红灯。

Issues：静态规则不等于任意自然语言的完备语义证明；已覆盖本轮确认漂移及明确反注入样本。

## Task 2：指导、治理与兼容资产

Status: COMPLETED

Changed Files：根 AGENTS.md；PROJECT_INCUBATOR 的最小 SKILL、AGENTS、README、全部模板及 references/legacy；Plugin Router、三个 Child、两个 Host；活动规格索引/作用域/Decision 015 与七份 Kernel Alignment 规格；TOOLS 的显式 RC 兼容构建；对应文案与兼容测试。

Validation：Mod/Desktop/Web 恢复均使用 inspect_project；Receipt hash/revision/ref 三种篡改在三类项目均拒绝且零状态写入。领域实现/Profile 字节锁保留。旧 RC 根 Skill、AGENTS、README、集成模板从明确 Legacy 参考构建，新增一致性测试先失败后通过。

Issues：无未修复的审查问题；历史 _V* 与实际 Kernel、领域代码、Schema 未改。

## Task 3：打包与正式安装

Status: IN_PROGRESS — 新宿主只读重放待结果

Changed Files：Plugin manifest、scripts/verify-candidate.mjs 与共享指导校验；personal marketplace 仅更换本插件 source 指针；旧全局 Skill 备份后部署源码最小 shim。

Validation：

- 新候选/正式安装版本：0.3.0+codex.20261019210340；package/MCP 版本仍为 0.3.0。
- 源码与候选 41 文件逐字节一致。
- 候选与安装聚合 SHA-256：45611fe83af98d32ca4e3b43cb0c8517c06e26b60c4d4c0c3c96f289af93f894。
- node scripts/verify-candidate.mjs --structure-only <candidate> 和 --full <candidate> <temporary-root>：exit0。
- 从正式安装目录运行同一 --full：exit0，真实 stdio MCP 启动、三类型路由、Web Host Forbidden、激活与 Receipt 均通过，无源码回退。
- codex plugin add project-incubator-plugin@personal --json：exit0；codex mcp list --json 解析的 cwd 指向新构建安装路径。
- Plugin Hook 文件哈希逐份与候选一致；旧全局 Skill 全目录备份在活动 skills 外，新活动目录只有一个 SKILL.md，哈希与源码一致。

Issues：首轮新宿主 CLI 使用默认 never 策略，MCP 调用在执行前被平台拒绝；随后模型容量错误。已改用正常 --approve-for-me 重放，不使用绕过审批/信任选项。当前不把独立进程验收冒充新宿主四调用成功。

## Task 4：回归与保护范围

Status: IN_PROGRESS — A09 新宿主结果待闭合

Validation：

| 命令/测试 | 最终结果 |
| --- | --- |
| Plugin npm test | 342/342；0 failed/cancelled/skipped |
| python -m unittest discover -s tests/unit -p test_*.py | 133/133 |
| 同上 tests/integration | 32/32 |
| 同上 tests/e2e | 3/3 |
| 同上 ACCEPTANCE_TESTS/layer2/stage_a–e | 15/5/8/9/3 全过 |
| 同上 ACCEPTANCE_TESTS/v1_1/stage_a–f | 6/8/7/8/8/2 全过 |
| Receipt 恢复集成测试 | 14/14，含三项目 × 三种篡改 |
| 独立审查 | Critical0 / Important3均修复 / Minor0 |
| 活动规格链接 | 48文件、0断链；七份新增规格均APPROVED |
| git diff --check | exit0，仅LF/CRLF提示 |

最终 Legacy/Acceptance 子进程使用 PYTHONDONTWRITEBYTECODE=1；Git 夹具需仅在测试进程设置 GIT_CONFIG_COUNT=1 / GIT_CONFIG_KEY_0=core.longpaths / GIT_CONFIG_VALUE_0=true，未改全局 Git 设置。旧失败日志保留，不隐藏失败；最终日志使用 final- 前缀。四个由早期测试生成的 tracked pyc 已恢复。

原 main-restruct 的 Manual_Test_Result_Record.md 保留；来源分支工作区保持 clean；scriverse 未被读取、写入、接管或用于验收。V1.1 RC Round2R、V1.2 真实产品验收和发布归档未被关闭。

## 证据与路径

- [执行记录](PROGRESS.md)
- [Plugin 最终全量](plugin-reviewed-final.log)
- [安装结果](plugin-install.json)
- [来源变更及备份](installation-source.json)
- [最小兼容入口部署](compatibility-install.json)
- [正式安装包 MCP 验证](installed-full.json)
- [实际 MCP 启动路径](installed-mcp-config.json)
- [完整失败基线](drift-red.log)
- [独立审查问题红灯](review-red.log)
- [独立审查问题绿灯](review-green.log)

市场旧 source 目录完整保留，新 source 是版本化持久候选，不直接改插件缓存。旧全局目录和 marketplace.before.json 的备份在 C:/Users/Xenia_Woo/.codex/backups/kernel-alignment/0.3.0+codex.20261019210340/。
