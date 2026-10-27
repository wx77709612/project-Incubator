# Codex 协作入口与权威恢复验收计划

状态：PASSED；Maker 于 2026-10-23 批准本验收计划并授权实施，2026-10-27 已完成自动化、Legacy、仓库外候选、正式安装与真实 Codex 新任务验收。上游：[Implementation Plan](CODEX_PROJECT_AGENT_ENTRY_IMPLEMENTATION_PLAN.md)。

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

执行日期：2026-10-23 至 2026-10-27。候选分发实现提交：`23f3932e95e800c9625bd8b45745d8ea71b5100b`；首轮独立审查修复提交：`1bb2717e4e960cc20d340616b9b2ec7d73d3afee`；真实宿主授权上下文最终实现提交：`9937427213211ffef7ded975a6363c10b652902b`。

### 自动化与回归

| 范围 | 结果 | 证据 |
| --- | --- | --- |
| A01–A11 | PASS | Plugin 单元、集成、Contract 与 E2E 覆盖首次创建、已有文件保留、当前任务入口指导、授权补建、路径竞争、只读 Inspect、诊断、两类恢复基线、源变化和回滚／残留报告。新增 `ADOPT_EXISTING` 缺文件场景单测通过。 |
| A12 | PASS | 模板进入白名单和聚合哈希；缺失、链接、包外回退与旧指令均失败关闭。最终相关专项回归 `93/93`。 |
| Plugin 全量 | PASS | 最终运行 `npm test`，退出码 0，`399/399`。 |
| Legacy unit | PASS | `python -m unittest discover -s TESTS/unit -p "test_*.py"`，退出码 0，`133/133`。 |
| Legacy integration | PASS | `python -m unittest discover -s TESTS/integration -p "test_*.py"`，退出码 0，`32/32`。 |
| Legacy e2e | PASS | `python -m unittest discover -s TESTS/e2e -p "test_*.py"`，退出码 0，`3/3`。 |

首次在受限环境调用 Windows Python 应用别名时，进程因系统权限未启动；在允许访问系统 Python 后以相同参数和 `-B` 重跑，三组均通过。该次启动失败不计为测试失败。早期 Legacy 回归留下一个已跟踪 `pyc` 工作树变化；它不属于本次实现，未纳入提交。

### 仓库外候选进程

- 候选来源：提交 `9937427213211ffef7ded975a6363c10b652902b` 所含 Plugin 文件；由 `scripts/package-candidate.mjs` 生成到仓库外目录 `project-incubator-agent-entry-candidate-20261027131324`。
- 候选与正式安装版本：`0.3.0+codex.20261027131324`；包版本：`0.3.0`。持久来源为 `C:\Users\Xenia_Woo\plugins\project-incubator-plugin-0.3.0+codex.20261027131324`，实际加载路径为 `C:\Users\Xenia_Woo\.codex\plugins\cache\personal\project-incubator-plugin\0.3.0+codex.20261027131324`。
- 聚合算法：`SHA-256-AGGREGATE-V1`；候选与安装目录最终哈希均为 `0f74e867e55dd1e82260b4f787fd899d71df626bbf9c23c17e50068daf0aaebf`。
- `npm ci --omit=dev` 退出码 0；审计报告 2 个 moderate 和 3 个 high 依赖漏洞。本任务未执行自动升级，以免越过锁文件与获批范围。
- Candidate 自带校验器 `--structure-only` 与 `--full` 均退出码 0，`source_fallback_detected=false`。
- Full 通过真实 stdio MCP 验证三种 Route、Web Host Forbidden、首次激活、`AGENTS.md` 创建与回读、删除后授权补建、损坏 Receipt 后 `CONTINUED` 恢复到 revision 1，以及新 Receipt 验证。

首轮独立只读审查发现的三个 Important 已以 RED→GREEN 闭合：损坏项目的第一条恢复消息可达、恢复候选不可用空后继绕过 Workflow 校验、AGENTS 回滚不会误删同字节替代文件。Task 6 又针对真实 Hook 并发、陈旧锁／意图、冲突确认和旧批准复用进行了多轮复现与修复；最后一项“旧调用在新 Prompt 回收后不得恢复执行”已有确定性回归测试。最终相关专项 `93/93`、Plugin 全量 `399/399`、Legacy `168/168`、仓库外 Candidate Structure/Full 均通过。

### 安装后宿主验收

| 步骤 | 状态 | 说明 |
| --- | --- | --- |
| 1 | PASS | 已记录源码提交、候选／安装版本、最终聚合哈希、持久来源路径与实际加载路径；安装前 Marketplace 配置已备份。 |
| 2 | PASS | Candidate Full 在临时 Managed Project 完成首次激活、入口创建、授权补建和权威恢复；候选与安装目录聚合哈希一致。 |
| 3 | PASS | 补建后的全新 Codex 任务 `01a17bfd-8f8c-7541-a11d-3d6a8724c3c4` 自动加载已安装 Router，在同一任务先调用一次 `prepare_agent_entry` 得到 `CURRENT`，再调用 `inspect_project`，未重复入口检查。 |
| 4 | PASS | 真实宿主先产生补建请求 `request-df90b5f0-0001-4ede-926d-86bdf4ba8cf5`；Maker 下一轮以精确 `scope_digest=794ea19b8fc4bf85e6e28ca910e901210f85c6e6e796c8c29ea5ca777975a8ae` 批准后，`install_agent_entry` 在不传 `turn_id` 的情况下返回 `CREATED`，当前 Agent 随后读取新文件。第一次继续宿主会话时，补建提交被宿主审批策略拦截，Kernel 未执行；以 Maker 已允许的宿主模式重试后成功。 |
| 5 | PASS | Candidate Full 已在独立临时项目完成损坏 Receipt 的准备、精确授权、`CONTINUED` 恢复、revision 1 与新 Receipt 回读；安装目录与该候选字节一致。 |
| 6 | PASS | 源码测试、候选进程、正式安装和两个真实 Codex 任务结果均已记录并闭合。 |

补建文件 SHA-256 为 `5452e13b1d6cc8f0f6b6e7ef3b159644a396aa2a13564a6ccaf4711e5ad9016a`，与已安装模板一致。补建后只读 `inspect_project` 返回 project `candidate-web-smoke`、revision `1`、Receipt `receipt-47fff2ad-e774-4c94-8cfc-e00b321f1c4d` 且 `receipt_verified=true`。三个权威 JSON 的最后写入时间均为 `2026-10-27T05:15:22Z` 左右，早于 `AGENTS.md` 的 `2026-10-27T06:11:49Z`；补建与后续只读检查没有改写权威集合。

总状态：`PASSED`。本轮只改变新增的 Agent Entry、权威恢复和相应授权上下文；未改变 Activation、普通 Mutation、Gate、阶段、P0–P6 或 `SPECS/_V*`。
