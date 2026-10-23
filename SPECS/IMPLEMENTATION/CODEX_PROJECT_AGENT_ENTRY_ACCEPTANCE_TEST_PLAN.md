# Codex 协作入口与权威恢复验收计划

状态：APPROVED / NOT RUN；Maker 于 2026-10-23 批准本验收计划并授权实施。上游：[Implementation Plan](CODEX_PROJECT_AGENT_ENTRY_IMPLEMENTATION_PLAN.md)。

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

状态：NOT_RUN。执行时逐项记录日期、环境、命令、退出码、测试计数、文件哈希、revision、Receipt 和未闭合事项。A01–A12、全量回归与安装后宿主验收全部通过前，不声明实现完成。
