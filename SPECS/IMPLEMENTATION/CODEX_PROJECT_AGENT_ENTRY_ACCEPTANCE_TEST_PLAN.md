# Codex 项目级 AGENTS 初始化验收计划

状态：DRAFT / MAKER REVIEW REQUIRED；实施前不得把本计划当作通过证据。上游：[Implementation Plan](CODEX_PROJECT_AGENT_ENTRY_IMPLEMENTATION_PLAN.md)。

## 验收目标与边界

证明新 Codex Plugin 的 `initialize_project` 在无项目级 `AGENTS.md` 的新项目中实际创建、回读并交付该文件，同时保持三个 JSON 权威、授权、Receipt 与既有文件保护。仅使用临时 Managed Project；不修改 Player Needs Hunter、其他已激活项目、插件缓存或 `_V*`。

## 自动化矩阵

| ID | 输入/故障 | 必须观察到的结果 | 证据 |
| --- | --- | --- | --- |
| A01 | `mod`、desktop、web 的有效新激活 | 各项目根目录生成相同稳定中文模板；`agent_entry.status=CREATED`；revision 0、Receipt 验证通过 | MCP E2E 与文件字节比较 |
| A02 | 已有可读普通 `AGENTS.md`，包括含旧标记的文件 | 内容和文件身份不变；`EXISTING_REVIEW_REQUIRED`；Router 提醒人工核对 | 快照/哈希、返回值 |
| A03 | 授权缺失、错误 request/digest、过期或路由不匹配 | 无新入口、无权威写入、Pending 规则不放宽 | MCP 错误码、目录检查 |
| A04 | 目录、链接、不可读目标 | `AGENT_ENTRY_PATH_UNSAFE`；不跟随、不覆盖、不写权威文件 | 临时夹具、错误码 |
| A05 | 创建时 `EEXIST` 或写入/回读故障 | 稳定错误；竞争者文件不变；无成功 Receipt；安全撤销 | 故障注入、字节/身份检查 |
| A06 | 入口已新建后 JSON/Receipt 故障 | 只撤销仍可证明属于本次写入的入口；三个 JSON 恢复；Pending 未消费 | Kernel 故障注入、残留检查 |
| A07 | 回滚前入口被外部修改或替换 | 不删除外部内容；`AGENT_ENTRY_ROLLBACK_INCOMPLETE` 与残留路径；不报告完整初始化 | 并发故障注入 |
| A08 | 候选模板缺失、篡改、链接或源码回退 | 结构/完整验证失败；候选哈希覆盖模板；不加载包外文件 | 仓库外候选测试 |
| A09 | 旧 Legacy 资产和已有四参 State Store API | 旧回归通过；现行包不含旧 Bootstrap，旧 API 调用不改变 | 全量测试与包清单 |

## 安装与宿主验收

1. 记录源 commit、候选版本、候选聚合 SHA-256、安装来源和实际加载的插件路径；必须使用正式插件管理器或当前受支持的安装流程，不能复制文件到缓存伪装安装。
2. 在新 Codex 任务使用临时目录走 `prepare_activation`、Maker 授权、`initialize_project`；保存工具返回、文件内容哈希、权威 Snapshot 和 Receipt 回读结果。不得使用真实项目作为试验对象。
3. 打开后续 Codex 任务，观察其是否原生接收项目级 `AGENTS.md` 指导；当前已启动任务不作为该项成功证据。
4. 分别报告源码测试、候选进程、安装后宿主三个层级的结果。任一层缺证据时标 `BLOCKED` 或 `NOT_RUN`，不得把前一层的通过上升为后一层的通过。

## 结果记录

状态：NOT_RUN。逐项填入执行日期、环境、命令、退出码、测试计数、实际文件/Receipt 证据和问题。全部 A01–A09 与安装后宿主验收通过前，不声明本能力实现完成。
