# Codex 项目级协作入口运行规范

状态：DRAFT / MAKER REVIEW REQUIRED；上游：[Contract](../CONTRACTS/CODEX_PROJECT_AGENT_ENTRY_CONTRACT.md)。仅适用于现行 `.codex-plugin` 分发的首次初始化。

## 1. 执行序列

1. `initialize_project` 完成原有请求、作用域、路由、PromptRef 与 Maker Authorization 检查；从当前插件根目录加载包内模板并验证基本内容。模板不可用时，返回 `AGENT_ENTRY_TEMPLATE_INVALID`，不写目标项目。
2. 进入现有按项目根目录串行化队列；检查 `.project-incubator/` 三个权威文件均不存在，保持已有 `PROJECT_ALREADY_INITIALIZED` 和 `PROJECT_CONTROL_STATE_INCOMPLETE` 判定。
3. 使用 `lstat` 检查根目录 `AGENTS.md`。可读普通文件仅记录 `EXISTING_REVIEW_REQUIRED`，不修改；其他现存类型失败关闭。不存在时用排他创建模式写入模板、同步并回读逐字节比较。`EEXIST` 是竞争冲突，不可退化为覆盖或成功。
4. 沿用 Kernel 的 activation、state、latest-receipt 原子写入和 Receipt 验证。所有结果闭合后返回 `{ activation, receipt, agent_entry }`，随后消费 Pending Activation。`agent_entry` 不写入权威 JSON。
5. Router 报告 Receipt 与 Agent Entry 独立结果；`EXISTING_REVIEW_REQUIRED` 需提示人工核对。新入口通常从后续 Codex 任务才作为原生指导加载。

## 2. 失败恢复

任何入口操作失败均不得进入权威文件写入。入口新建后，任何 JSON 写入或 Receipt 验证失败须先恢复权威文件，再核对本次新建入口的对象身份和字节内容；仅在两者均未变化时删除它。不能核对或发生外部修改时保留文件，返回 `AGENT_ENTRY_ROLLBACK_INCOMPLETE` 与残留路径。入口写入中途失败也遵循同一安全撤销限制。

权威恢复失败时不得覆盖错误为一般入口错误；统一返回 `AGENT_ENTRY_ROLLBACK_INCOMPLETE` 和已知残留路径，并保留原始原因供诊断。Pending Activation 不消费。若留下部分控制文件，后续 `prepare_activation` 或 `initialize_project` 继续按现行控制状态规则失败关闭；不通过 Agent 私自删除真实项目文件。

现有项目串行化只覆盖同一插件进程内请求；文件排他创建处理外部进程竞争。没有跨进程锁保证，因而不能用先 `exists()` 再普通写入的方式模拟排他创建。链接不得跟随。Windows 上对文件身份不可可靠确认时，宁可保留本次文件并报告残留，也不能删除可能被 Maker 或其他进程修改的文件。

## 3. 分发与验证

包内模板加入候选白名单并经候选验证器检查：文件存在、仍位于候选根目录内、中文规则和 Router/Kernel 关键语义齐全、无旧 Markdown/Python 正向执行指令。旧 `PROJECT_INCUBATOR/` 模板仍是 Legacy 兼容资产，不复制进现行候选。

验收至少包括单元故障注入、三类项目的新激活、已有文件保护、链接/目录/不可读路径、并发 `EEXIST`、JSON/Receipt 失败回滚、候选包外运行，以及新 Codex 任务对生成文件的实际加载观察。源码测试通过不等于已安装 Plugin 更新成功；安装和宿主验证结果分别报告。
