# Codex Managed Project 协作入口初始化影响分析

状态：DRAFT；2026-10-22。上游：[架构变更提案](CODEX_PROJECT_AGENT_ENTRY_CHANGE_PROPOSAL.md)。本分析是调查与拟议改动范围，不构成实施授权。

## 1. 已核实事实与根因

1. `PROJECT_INCUBATOR/AGENTS.md` 是旧 Skill Package 内的 Agent 边界文件，不能使其他 Managed Project 自动拥有根目录 `AGENTS.md`。
2. 活动 Feature 001 曾设计目标项目的 `AGENTS.md`，旧脚本也存在；但该文档标为 `NOT_IMPLEMENTED`、现属 Legacy 兼容语义，模板仍包含已失效的旧状态模型。不能直接恢复旧脚本或复制旧模板。
3. Kernel Alignment ACP 将 `BOOTSTRAP_HOST_INTEGRATION` 排除出 Plugin 0.3.x 现行路径；原影响分析将模板转为最小 Router/Kernel 指引并限定显式生成，却没有为新项目初始化建立替代能力。
4. `project-incubator-plugin/src/server.mjs` 的 `initialize_project` 调用 `initializeProjectState`；`src/kernel/state-store.mjs` 只持久化并验证三个 JSON。`scripts/package-candidate.mjs` 的打包白名单未包含旧模板目录。现行 Router Skill 也没有入口创建步骤。
5. 现行漂移测试仅验证兼容 AGENTS 文本不含过时指令，不检查候选包模板与 `initialize_project` 的生成结果。Player Needs Hunter 已成功初始化但无根目录 `AGENTS.md`，是该缺口的实际观察；不因此推断它的 P2 权威状态无效。

归因：0.3 迁移时正确移除了旧执行路径，却未把非权威的宿主入口能力重新纳入新初始化契约；分发清单和验收条件同步遗漏。英文计划还受计划流程文案影响，不能单独归因于本缺口。

## 2. 分层影响

| 层级 | 待处理内容 | 不得发生的变化 |
| --- | --- | --- |
| Architecture | 为 Decision 015 补充 Codex 分发边界、非权威 Agent Entry 与初始化闭合条件 | 不把 AGENTS 改成第四份项目权威；不恢复旧 Host Bootstrap |
| Design | 定义模板职责、已有文件人工核对、初始化成功的用户可见结果 | 不保存动态项目事实或阶段 |
| Contract | 明确 `initialize_project` 的 Agent Entry 结果、已有文件与失败码；评估返回形状兼容性 | 不放宽 Maker 授权或 `scope_digest` |
| Runtime | 排他创建、回读、并发竞争、失败回滚和残留报告 | 不在失败时虚报 Receipt 闭合 |
| Implementation Plan | 分解模板打包、初始化流程、Router 文案与测试任务 | 不直接写真实 Managed Project 状态 |
| Acceptance Plan | 临时项目、安装后宿主和故障注入验收 | 不以源码存在或单元测试替代安装后验证 |

## 3. 预计文件范围

- 规格：`SPECS/README.md`、活动 Architecture Decision、Design、Contract、Runtime Specification、Implementation/Acceptance Plan；旧 `_V*` 不修改。
- Plugin：`project-incubator-plugin/src/server.mjs`、`src/kernel/state-store.mjs` 或职责等价的新模块、包内 Agent Entry 模板、`scripts/package-candidate.mjs`、候选验证、Router Skill。
- 测试：初始化单元/集成/E2E、候选包安装与漂移检查；旧 Legacy 测试只用于确认未退化，不作为新机制的实现路径。
- 目标项目：本轮不修改 `F:/projects/Player_Needs_Hunter`。补齐既有项目需要另行明确授权及单独方案。

## 4. 待下游精确定义的风险

- 入口文件与三个权威 JSON 不属于同一种状态：运行失败时必须区分成功 Receipt、创建失败和部分回滚，不能混淆权威与协作 Artifact。
- 已有文件可能属于 Maker 或其他工具；任何自动覆盖、追加、删除或重命名都超出本提案。
- Windows 文件系统的排他创建、链接、大小写路径和故障注入需要实际测试；不能靠 `exists()` 后 `writeFile()` 的检查—写入序列保证不覆盖。
- 当前 Codex 任务在初始化前已启动，新文件通常只保证后续任务原生加载；本轮 Agent 仍须按当前已加载指令工作。
