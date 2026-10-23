# Codex 协作入口与权威恢复验收计划

状态：APPROVED / BLOCKED；Maker 于 2026-10-23 批准本验收计划并授权实施。自动化、Legacy 与仓库外候选进程验收已通过；安装后真实 Codex 新任务加载证据尚未取得。上游：[Implementation Plan](CODEX_PROJECT_AGENT_ENTRY_IMPLEMENTATION_PLAN.md)。

## 验收目标

证明 Plugin 能在首次接入和已接入项目中正确处理 `AGENTS.md`，能在三个权威 JSON 实际使用失败后由 Maker 授权恢复，同时不改变正常项目的调用节奏、阶段或状态变更规则。只使用临时 Managed Project。

## 自动化矩阵

| ID | 场景 | 必须观察到的结果 |
| --- | --- | --- |
| A01 | `NEW_PROJECT` 与 `ADOPT_EXISTING` 首次接入且缺 `AGENTS.md` | 创建中文模板并回读；三 JSON 与 Receipt 验证通过 |
| A02 | 首次接入已有相同或不同 `AGENTS.md` | 文件字节不变；分别返回 `CURRENT` 或 `EXISTING_REVIEW_REQUIRED` |
| A03 | 已接入项目当前任务首次进入 | 只调用一次 Agent Entry 检查；同任务后续 Plugin 调用不要求重复检查 |
| A04 | 已接入项目缺 `AGENTS.md` | 准备阶段不写文件；Maker 批准后排他创建；当前 Agent 显式读取 |
| A05 | 入口准备后目标出现，或目标为目录／链接 | 不覆盖、不删除，返回稳定错误；三个 JSON 不变 |
| A06 | 完整有效的三 JSON | `inspect_project` 与普通 Mutation 保持原调用和结果，不进入恢复诊断 |
| A07 | 任一 JSON 缺失、非法或 Receipt 不一致 | 原操作失败关闭；逐文件诊断可报告事实；准备恢复时项目零写入 |
| A08 | 有效旧 State 的恢复 | Maker 授权后使用下一 revision，清空旧 Pending Request，新 Receipt 验证通过 |
| A09 | State 缺失或不可解析的恢复 | Maker 授权后建立 revision 0 恢复基线；不得宣称补回旧历史 |
| A10 | 恢复准备后任一源文件变化 | `RECOVERY_SOURCE_CHANGED`；三个路径保持变化后的现场，无恢复写入 |
| A11 | 恢复写入或回读故障 | 能回滚则 `RECOVERY_WRITE_FAILED` 且原始字节一致；不能闭合则报告残留路径 |
| A12 | 候选包与仓库外运行 | 模板和新模块自包含、聚合哈希覆盖；缺失／链接／包外回退／旧指令均失败 |

## 安装后宿主验收

1. 记录源码 commit、候选版本、聚合 SHA-256、安装来源与实际加载路径。
2. 在临时目录完成一次全新接入和一次已有产品首次接入，核对 `AGENTS.md`、三 JSON 和 Receipt。
3. 新开 Codex 任务，证明生成的 `AGENTS.md` 被原生加载；在该任务中多次使用 Plugin，确认只执行一次入口检查。
4. 在另一个临时项目删除 `AGENTS.md`，验证下次任务首次进入时提出补建，经 Maker 确认后创建。
5. 用临时夹具制造部分／损坏 JSON，验证准备恢复、Maker 批准、恢复写入和下一次 `inspect_project` 成功。
6. 分别报告源码测试、候选进程和安装后宿主结果；任何一层缺证据均标记 `BLOCKED` 或 `NOT_RUN`。

## 回归边界

- Plugin 全量测试和现有 Legacy 回归均通过。
- 三种 Project Type 的 Router、Workflow、Gate、Transition 与正常授权行为不变。
- `inspect_project` 仍严格只读；正常项目没有新增恢复请求或重复四文件预检。
- 不修改真实 Managed Project、已安装缓存或 `SPECS/_V*`。

## 结果记录

执行日期：2026-10-23。候选分发实现提交：`23f3932e95e800c9625bd8b45745d8ea71b5100b`；最终独立审查修复提交：`1bb2717e4e960cc20d340616b9b2ec7d73d3afee`。

### 自动化与回归

| 范围 | 结果 | 证据 |
| --- | --- | --- |
| A01–A11 | PASS | Plugin 单元、集成、Contract 与 E2E 覆盖首次创建、已有文件保留、当前任务入口指导、授权补建、路径竞争、只读 Inspect、诊断、两类恢复基线、源变化和回滚／残留报告。新增 `ADOPT_EXISTING` 缺文件场景单测通过。 |
| A12 | PASS | 候选专项 `71/71`；模板进入白名单和聚合哈希，缺失、链接、包外回退与旧指令均失败关闭。 |
| Plugin 全量 | PASS | 审查修复后运行 `npm test`，退出码 0，`381/381`。 |
| Legacy unit | PASS | `python -m unittest discover -s TESTS/unit -p "test_*.py"`，退出码 0，`133/133`。 |
| Legacy integration | PASS | `python -m unittest discover -s TESTS/integration -p "test_*.py"`，退出码 0，`32/32`。 |
| Legacy e2e | PASS | `python -m unittest discover -s TESTS/e2e -p "test_*.py"`，退出码 0，`3/3`。 |

首次在受限环境调用 Windows Python 应用别名时，进程因系统权限未启动；在允许访问系统 Python 后以相同参数重跑，三组均通过。该次启动失败不计为测试失败。Legacy 回归运行产生的已跟踪 `pyc` 变化已恢复，源码工作树未保留该副作用。

### 仓库外候选进程

- 候选来源：上述候选分发实现与最终独立审查修复提交；由 `scripts/package-candidate.mjs` 生成到仓库外系统临时目录。
- 候选版本：`0.3.0+codex.20261019210340`；包版本：`0.3.0`。
- 聚合算法：`SHA-256-AGGREGATE-V1`；最终哈希：`a94bf9b2b523d90b24e6523775d39f85045fd0dc0553fb5f17ac4fb6d7618cd4`。
- `npm ci --omit=dev` 退出码 0，安装 94 个包；审计报告 1 个 moderate 和 1 个 high 依赖漏洞，本任务未执行自动升级，以免越过锁文件与获批范围。
- Candidate 自带校验器 `--structure-only` 与 `--full` 均退出码 0，`source_fallback_detected=false`。
- Full 通过真实 stdio MCP 验证三种 Route、Web Host Forbidden、首次激活、`AGENTS.md` 创建与回读、删除后授权补建、损坏 Receipt 后 `CONTINUED` 恢复到 revision 1，以及新 Receipt 验证。

最终独立只读审查发现的三个 Important 已在一次修复轮中以 RED→GREEN 闭合：损坏项目的第一条恢复消息可达、恢复候选不可用空后继绕过 Workflow 校验、AGENTS 回滚不会误删同字节替代文件。针对性测试 `16/16`，随后 Plugin 全量 `381/381`、Legacy `168/168`、仓库外 Candidate Structure/Full 均再次通过。

### 安装后宿主验收

| 步骤 | 状态 | 说明 |
| --- | --- | --- |
| 1 | PASS | 已记录源码提交、候选版本、最终聚合哈希、仓库外来源路径与候选实际运行路径。 |
| 2 | PARTIAL | 仓库外真实 MCP 进程完成全新接入；`NEW_PROJECT` 与 `ADOPT_EXISTING` 的差异由全量自动化覆盖，但尚未把候选安装进 Codex 宿主。 |
| 3 | BLOCKED | 当前任务不能证明“新开 Codex 任务后由宿主原生加载刚生成的 `AGENTS.md`”；候选进程和同一任务模拟均不能替代该证据。 |
| 4 | BLOCKED | 候选进程已证明删除后可准备并授权补建，但“下一次真实 Codex 任务首次进入时提出补建”仍依赖步骤 3 的宿主级证据。 |
| 5 | PASS | 仓库外临时项目已制造 Receipt 不一致，准备恢复、模拟精确 Maker 授权、写入、revision 1 与 Receipt 回读全部通过。 |
| 6 | BLOCKED | 源码测试与候选进程结果已记录；安装后宿主结果因步骤 3、4 未闭合而不能判定 PASS。 |

总状态：`BLOCKED`。未修改真实 Managed Project、已安装 Plugin 缓存或 `SPECS/_V*`。在候选通过受支持方式安装后，必须新开真实 Codex 任务完成步骤 3、4；在此之前不声明本版本实现完成。
