# Codex 协作入口与权威恢复运行规范

状态：APPROVED；Maker 于 2026-10-23 批准本运行规范及配套实施与验收计划，并于 2026-10-26 批准真实宿主授权上下文修正。上游：[Contract](../CONTRACTS/CODEX_PROJECT_AGENT_ENTRY_CONTRACT.md)。

## 1. Agent Entry

候选包包含 `templates/codex/AGENTS.md`。Runtime 只从当前插件根目录读取模板，验证非空、关键 Router／Kernel／中文规则齐全且无 Legacy 正向指令。

首次接入在现有授权完成后、消费 Activation Request 前处理入口：`lstat` 确认目标类型；不存在时使用 `open("wx")` 排他创建、同步和逐字节回读；普通文件按模板哈希返回 `CURRENT` 或 `EXISTING_REVIEW_REQUIRED`；目录、链接和不可读对象失败关闭。随后执行现有三 JSON 初始化和 Receipt 验证。后续权威写入失败时，只撤销仍可证明为本次创建且字节未变化的入口。

已接入项目由 Router 在任务首次进入时调用 `prepare_agent_entry`。同一任务后续调用不重复检查；Runtime 不为此建立持久业务标记。Router 从 `CODEX_SESSION_ID` 取得真实 session。缺失时生成绑定规范项目路径、session、模板 SHA-256 和 24 小时有效期的 Runtime Data 请求。Maker 下一轮回复由 Hook 记录规范项目根与真实 turn，并在同一项目根、项目 ID、session 的排他锁内以 `PENDING → READY` 发布最新 Prompt；`captured_at` 只供过期判断。每个调用在第一次异步清理前先登记临时写入意图；锁、意图目录、竞争标记或遗留 `claimed-*` 目录存在时，授权读取都失败关闭。锁包含随机所有者与创建时间，释放时只删除自己的所有者记录与意图；30 秒以上的陈旧锁可由后续调用隔离。意图记录进程 ID 仅供诊断；超过 30 秒、元数据损坏或时钟反向超过容差的意图，持锁方一律先写冲突事件再删除，不依赖可能复用的 PID。被删除 intent 的旧调用恢复时必须因文件缺失或 token 不匹配而失败；取得锁、清除冲突以及每次 `PENDING/READY` 发布前都复核 owner 与自身 intent。若两个记录调用重叠，后到调用立即在冲突目录写入唯一事件并失败，持锁调用只能发布歧义状态。后续第一条无并发 Prompt 原子搬走旧冲突目录后立即在原路径写入 `CLAIM` 屏障，再等待 100 毫秒静默窗口；窗口无新竞争时只写入确认标记并仍返回 `PROMPT_ORDER_AMBIGUOUS`。确认写入失败时保留 `CLAIM`，不得删除唯一冲突证据。再下一条独立、无并发且明确的 Prompt 将当前 `CLAIM` 原子搬至单独 `claimed-*` 屏障，再等待第二个 100 毫秒窗口；搬走目录内混入事件、标准冲突目录重建或其他意图任一出现时，都先在标准路径保留冲突再失败。仅在第二次复查仍无竞争时，才先把旧指针写为 `AMBIGUOUS`，只清理本调用的屏障并发布新的 `READY`。异常退出遗留的 `claimed-*` 由后续持锁调用先转成标准冲突再清理。陈旧锁与崩溃意图恢复也遵循这套两步确认语义。`install_agent_entry` 不依赖 Agent 回传 turn，而是按规范项目根、项目 ID、session、request、scope 与批准意图读取该指针。不同根目录不共享批准；锁存在、写入意图存在、竞争标记存在、指针不完整、损坏、记录缺失或消费前被替代时失败关闭，不得扫描回退旧记录。随后重新检查目标仍不存在和模板 SHA 未变化，经既有 Prompt 授权后创建、回读并消费请求。

## 2. 权威诊断

`prepare_authority_recovery` 不调用 `readProjectSnapshot` 作为唯一入口，因为它必须在部分文件缺失时仍能报告逐文件事实。它对三个固定路径分别执行：读取原始字节、计算 SHA-256、解析对应 Schema，并在可行时验证项目 ID 与 Receipt。诊断过程只读。

完整集合通过 `readProjectSnapshot` 与 `verifyLatestReceipt` 时拒绝准备恢复。其他情况由 Server 校验候选 Route、Workflow、revision 和空 Pending Request，然后把诊断指纹与候选写入 Plugin Runtime Data。Runtime Data 不是项目权威。

## 3. 恢复提交

`recover_project_authority` 按以下顺序执行：

1. 读取未过期的恢复请求并验证 request、digest、来自 `CODEX_SESSION_ID` 的 session；按规范项目根、项目 ID、session、request、scope 与批准意图从 Hook 记录定位唯一最新 Prompt 和真实 turn；
2. 重新计算三个路径的“缺失或 SHA-256”指纹，与准备时逐项比较；
3. 进入现有按规范项目路径串行化队列，并再次比较指纹；
4. 生成新 Receipt ID，规范化 Activation 与 State，设置 `last_change.operation=RECOVER_PROJECT_AUTHORITY`、当前时间和 Receipt ID；
5. 依次安全写入 Activation、State、Receipt，逐字节回读，然后执行 Receipt 验证；
6. 成功后消费 Runtime 请求并返回结果。

可解析旧 State 作为 Receipt 的 `previousState`，候选使用下一 revision；不可解析或缺失 State 时 `previousState=null`，候选 revision 0。所有旧 Pending Request 在规范化时清空。

Runtime 在写入前保存三个路径的原始字节。可捕获错误发生时按原值恢复：原来缺失的路径删除本次文件，原来存在的路径原子写回；全部回读一致时返回 `RECOVERY_WRITE_FAILED`，否则返回 `RECOVERY_ROLLBACK_INCOMPLETE` 和残留路径。无论何种失败都不消费请求。

## 4. 正常路径与调用成本

`inspect_project` 和普通 Mutation 继续直接读取并验证权威集合，不先调用恢复诊断。Agent Entry 检查不嵌入所有 MCP Tool，也不嵌入 `inspect_project`。因此正常任务除首次进入时的一次轻量入口检查外，没有新增调用；三个 JSON 的读取次数与现行按需行为一致。

状态提交后的回读和 Receipt 校验必须保留，因为它证明本次写入闭合，不属于重复入口检查。发生 revision、Receipt 或文件错误时才向 Router 暴露恢复选择。

## 5. 分发与验证

模板、Agent Entry 模块、恢复 Runtime Data 模块和新 Tool 必须进入候选白名单与聚合哈希。候选验证拒绝模板缺失、链接、包外回退和旧指令。自动化分别覆盖首次接入、任务首次检查、补建授权、两种恢复基线、来源变化、故障回滚和正常路径无额外预检；安装后在临时项目验证，不改真实 Managed Project。
