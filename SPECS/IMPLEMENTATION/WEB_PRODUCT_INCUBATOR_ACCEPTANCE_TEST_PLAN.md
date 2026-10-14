# Web Product Incubator Acceptance Test Plan

> Specification Version: Plugin Web Product V1.2
> Status: APPROVED
> Approved By: Maker，2026-10-14
> Acceptance Authorization: GRANTED
> Depends On: `SPECS/IMPLEMENTATION/WEB_PRODUCT_INCUBATOR_IMPLEMENTATION_PLAN.md`

## 1. 验收目标

本计划证明 Web Product Incubator 不只是“注册了一个名字”，而是能够在不分叉 Core Runtime 的前提下：

- 正确路由并激活通用 Web Product；
- 接管新项目和已有项目；
- 维持 P0–P6、Maker Authority、State 1.1、Receipt 与失败关闭；
- 指导并约束 Build、localhost、真实浏览器和适用次级界面验证；
- 形成可安装 Candidate；
- 在首个真实已有 Web 项目上留下可复核 Evidence；
- 不把本地验证冒充部署或 Production Ready。

自动化测试证明结构与控制语义；真实项目验收证明方法能在非测试夹具中工作。两者不能互相替代。

## 2. 验收对象与固定边界

验收对象：

- 实现仓库中的 Plugin 源码与自动化测试；
- `0.3.0` Candidate Package；
- 安装后的仓库外 Plugin 副本；
- Maker 指定的一个真实已有 Web Product。

不在本轮验收：

- 互联网发布、生产部署、域名、TLS、CDN、监控、扩缩容；
- 浏览器扩展、纯静态前端、纯后端服务、独立 MCP Product；
- V1.1 RC Manual Round 2R；
- 对目标 Web Product 业务质量作超出其 Product Boundary 的评判。

## 3. Evidence 记录格式

每个验收项至少记录：

```text
Acceptance ID:
Revision / Candidate Version:
Channel:
Environment and Tool Versions:
Artifact / Endpoint:
Scenario and Steps:
Observed Result:
Evidence Refs:
Claim Scope:
Known Limitations:
Status: PASS | FAIL | BLOCKED | NOT_APPLICABLE
```

真实项目材料还必须记录依赖与关键工具版本、关键配置摘要、localhost URL/端口/协议、浏览器名称与版本、前端/后端/数据/外部依赖状态；敏感值只写来源类别或脱敏标识。

## 4. 自动化验收矩阵

### Stage A：基线与保护边界

| ID | 验收项 | 通过条件 |
| --- | --- | --- |
| A1 | 工作树与基线 | 明确记录起始 Commit；无意外未提交变更 |
| A2 | 历史归档 | `_V*` 无修改，活动引用不把归档作为运行时来源 |
| A3 | 既有领域资产 | Mod/Sims 4、Desktop/Windows 受保护文件摘要不变 |
| A4 | 实现前回归 | 当前 Plugin 全量测试通过并记录总数 |

### Stage B：Registry、Profile 与 Workflow

| ID | 验收项 | 通过条件 |
| --- | --- | --- |
| B1 | Registry | `web-product` 指向可读的 Web Child Skill、Profile 与 Workflow；缺失/不可读/逃逸 Plugin Root 的任一 Registry 引用使启动失败关闭；Registry 仍为 1.1 |
| B2 | Host Forbidden | 空 Host 路由成功；任何非空 Host 返回 `HOST_PROFILE_FORBIDDEN` |
| B3 | 无 Web Host | Host Profile 列表没有 Browser、localhost、OS 或 Deployment 项 |
| B4 | 新项目 Entry | `NEW_PROJECT` 仅 P0 成功 |
| B5 | 已有项目 Entry | `ADOPT_EXISTING` 对 P0–P6 均可结构化评估，缺 Evidence 失败 |
| B6 | Transition | P0→…→P6 与 P6→P2–P5 成功；其他跳转失败 |

### Stage C：Router 与 Child Skill 契约

| ID | 验收项 | 通过条件 |
| --- | --- | --- |
| C1 | Web 判定 | Router 明确浏览器主界面、前端、后端和跨边界核心旅程 |
| C2 | 排除边界 | 浏览器扩展、静态前端、纯后端、独立 MCP、CLI/SDK/库等不会误路由 |
| C3 | P4 | 两个 Checkpoint 均不形成 Stage；各自绑定 Evidence Refs、Claim Scope、Known Limitations、Failure Routing 与独立 Gate；只有两项都为 `REQUIREMENT_SATISFIED` 才不阻止 P4→P5 |
| C4 | P5 | 六个 Channel 及绑定字段齐全；Build、Local Integration、Local Browser 和适用 Secondary Interface Requirement 分别为 `REQUIREMENT_SATISFIED`；Build/Browser/MCP/Human 不互相替代 |
| C5 | MCP 归属 | 绑定后端的 MCP 保持 Web 类型；独立化只提出 Maker Review |
| C6 | 部署边界 | 明确 `DEFERRED_CAPABILITY`，禁止 Production Ready Claim |

### Stage D：Activation、Authority 与失败关闭

| ID | 验收项 | 通过条件 |
| --- | --- | --- |
| D1 | Prepare | Entry 与完整 Initial State 纳入 `scope_digest`，只产生 Pending Request |
| D2 | Maker Authorization | 无真实 Maker 回复不能 Initialize；摘要漂移不能提交 |
| D3 | Commit | Activation、State、Decision 与 Receipt 原子写入并可 Read-back |
| D4 | Entry 不可变 | 激活后的任何 Entry 变化返回 `WORKFLOW_ENTRY_IMMUTABLE` |
| D5 | State 兼容 | 新 Web 激活要求 1.1；旧 1.0 项目既有行为保持 |
| D6 | 无部分成功 | Host/Entry/Workflow/Digest/Authorization 失败均无部分状态或成功 Receipt |

### Stage E：端到端与结论上限

| ID | 验收项 | 通过条件 |
| --- | --- | --- |
| E1 | 新项目 E2E | Route→Prepare→Authorization→Initialize→Receipt→Transition 闭环 |
| E2 | Completion 与 Runtime 边界 | Child Skill 的 Contract content test 要求逐项 Gate 满足后才声明 Completion；Runtime E2E 只验证 `completion_satisfied = false` 阻断、`true` 仍需正常授权，且 Kernel 不解释具体 Gate Result、不自动推导 Completion 或修改状态 |
| E3 | 已有项目 E2E | 中后期 ADOPT 激活成功且 Entry 保持不可变 |
| E4 | Build-only | 不得满足完整 P5 或产生浏览器/部署结论 |
| E5 | localhost-only | 端口或 HTTP 成功不得替代真实浏览器旅程 |
| E6 | Browser-only | 浏览器结果不得替代适用的次级界面 Evidence |
| E7 | Secondary-only | MCP/其他 Client 结果不得替代 Browser Evidence |
| E8 | Runtime Shape | 无 Web Checkpoint/Channel/MCP/Deployment 专用 Stage、Schema 或 Tool |

### Stage F：全量回归

必须执行并记录实际输出：

```powershell
Push-Location project-incubator-plugin
npm test
Pop-Location
```

还必须运行仓库既有 Legacy、Mod、Desktop、Hook、Receipt、候选打包相关验证。通过条件：

- 所有测试零失败；
- 已有项目类型的 Route、Activation、Workflow 与 Host 语义未改变；
- V1.1 RC 人工验收状态未被改写；
- 无 `_V*` 被扫描、配置或打包；
- 没有依赖网络服务才能完成的仓库内测试。

确认当前目录已回到 Implementation Repository 根目录后执行 Legacy 回归：

```powershell
python -m unittest discover -s tests/unit -p "test_*.py"
python -m unittest discover -s tests/integration -p "test_*.py"
python -m unittest discover -s tests/e2e -p "test_*.py"
```

当前已接受基线为 unit `132/132`、integration `32/32`、e2e `3/3`。若数量因本任务以外的已批准变化而不同，必须先记录来源并复核覆盖项，不能直接修改预期数字。

三个命令必须分别报告实际运行 `132`、`32`、`3` 项；退出码为零但运行数量为零或不匹配仍判定 FAIL。

## 5. Candidate 与仓库外安装验收

### Stage G：Candidate Package

在 Implementation Repository 根目录的同一个 PowerShell 会话执行：

```powershell
$candidateRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("project-incubator-web-candidate-" + [guid]::NewGuid().ToString("N"))
$managedRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("project-incubator-web-smoke-" + [guid]::NewGuid().ToString("N"))

Push-Location project-incubator-plugin
node scripts/package-candidate.mjs $candidateRoot
node scripts/verify-candidate.mjs --structure-only $candidateRoot
Pop-Location

Push-Location $candidateRoot
npm ci --omit=dev
node scripts/verify-candidate.mjs --full $candidateRoot $managedRoot
Pop-Location
```

`--structure-only` 与 `--full` 必须分别输出一条可解析 JSON；Stage G Evidence 保存原始 JSON。完整模式至少返回并校验：

```text
candidate_root = <resolved candidateRoot>
candidate_hash_algorithm = SHA-256-AGGREGATE-V1
candidate_hash = <64 lowercase hex>
manifest_version = 0.3.0+codex.<timestamp>
package_version = 0.3.0
source_fallback_detected = false
web_profile_verified = true
web_skill_verified = true
web_workflow_verified = true
mcp_server_version = 0.3.0
web_route.host_profile_id = null
host_forbidden_verified = true
activation.plugin_version = 0.3.0
receipt_verified = true
```

Verifier 的聚合哈希算法固定为：按规范化相对路径排序，对除 `node_modules/` 外的 Candidate 文件逐个计算 SHA-256，再对 `relative-path:file-hash` 清单计算最终 SHA-256。Structure 与 Full 输出的 `candidate_hash` 必须一致。

然后核对：

1. Candidate 与 Managed Smoke Project 均位于仓库外系统临时目录。
2. 核对 Manifest `0.3.0+codex.<timestamp>`、Package/Lock `0.3.0`。
3. 核对运行时白名单只包含 Plugin 必需内容，不包含 `SPECS`、tests、历史归档、Legacy Runtime 或 Managed Project。
4. 在 Candidate 中执行全新 `npm ci --omit=dev`。
5. 记录 Candidate 根目录、Manifest/Package 版本和完整 Candidate 内容哈希，形成后续 Field Validation 的固定标识。
6. 从 Candidate 路径加载 Registry 和所有 Workflow evaluator。
7. 在 Candidate 路径内解析 `web-product.profile_path` 与 `web-product-incubator` 的 `skill_path`，验证两份文件存在、可读、ID 一致且没有回退读取源码工作树。
8. 验证 Mod、Desktop、Web 三种 Route；Web Host 必须为 null。
9. 执行 MCP Handshake，Server Version 与 Package Version 一致。
10. 运行一个最小 Web 激活烟雾流程并验证 Receipt 与 Activation `plugin_version = 0.3.0`。
11. 在 Stage H 完成前保留该只读 Candidate 安装；Stage H 完成后再清理临时 Candidate 和安装缓存，并在 Log 中保留命令摘要、哈希和结果。

Stage G 失败时不得进入真实项目验收。

## 6. 真实已有 Web 项目验收

### Stage H：ADOPT_EXISTING Field Validation

前置输入：Maker 指定一个可本地访问、允许构建和运行的已有 Web Product 仓库。该项目的技术栈、SPA/SSR、前后端是否分离均不作为分类条件。

Stage H 必须由 Stage G 产生的同一个仓库外已安装 Candidate 驱动，不得调用源码工作树或另一个 Plugin 版本。开始前记录 Candidate 安装路径、Manifest/Package 版本和内容哈希；结束时把相同标识写入每一项 Field Evidence。

#### H1：路由与接管

- 确认浏览器为主要用户界面，项目有前端和后端职责；
- 确认至少一条核心旅程穿过浏览器与后端或数据边界；
- 提议 `web-product`、Host null、`ADOPT_EXISTING`；
- Agent 基于已有 Artifact/Evidence 判断 P0–P6，Maker 确认完整 Activation Scope；
- 验证 Activation、State 1.1、Entry、Decision、Receipt 和 Read-back；Activation 必须显示 `plugin_version = 0.3.0`，Evidence 必须引用 Stage G 的 Candidate 内容哈希。

#### H2：Build Validation

- 使用项目声明的标准构建入口；
- 记录源码 Revision、构建命令、依赖与关键工具版本、Artifact 路径和退出结果；
- 验证构建成功可重复；
- 构建失败时保留 Failure Signature，不通过修改验收口径绕过。

#### H3：Local Integration Validation

- 使用项目声明的本地启动方式；
- 记录 localhost URL、端口、协议和非敏感配置摘要；
- 记录前端、后端、数据和适用外部依赖状态；
- 验证服务间协作，不把“进程存在”或单个 HTTP 200 当成核心旅程成立；
- 停止本地进程后验证无遗留服务或临时权威状态。

#### H4：Local Browser Validation

至少执行一条核心旅程和一条关键失败路径：

- 真实浏览器打开 localhost 入口；
- 按用户可理解的步骤完成操作；
- 观察页面可见结果；
- 同时验证对应后端或数据结果；
- 验证至少一个错误、拒绝、空状态或恢复反馈；
- 记录浏览器名称/版本、URL、步骤、截图或日志引用、后端/数据 Evidence 和限制。

禁止仅使用 DOM 单测、无头请求、端口探测或接口调用替代本项。

#### H5：Secondary Interface Validation（条件适用）

若 Product Boundary 包含 MCP 或其他次级界面：

- 使用真实 Client 及实际 Transport；
- 记录 Client 名称/版本、Capability、非敏感授权上下文和输入；
- 验证允许路径及业务结果；
- 验证未授权或越权拒绝；
- 区分协议失败与业务失败；
- 验证审计结果、外部副作用及其与后端授权政策的一致性；
- 明确该 Evidence 不替代 H4。

若项目无次级界面，记录 `NOT_APPLICABLE` 及其与 Product Boundary 一致的理由，不能伪造测试。

#### H6：Human Validation

- Maker 或指定观察者按核心旅程独立观察一次；
- 记录观察者角色、环境、场景和具体观察；
- 人工结论只支持其观察范围，不替代 Build、Browser、Secondary Interface 或 Gate Result。

#### H7：Deployment Deferral

验收记录必须明确：

```text
Deployment: NOT TESTED / DEFERRED_CAPABILITY
Production Ready Claim: NOT MADE
```

即使已有线上地址，也不能用其可访问性替代本计划未执行的部署验证。

## 7. 失败处理

- 自动化失败：保留失败输出，按系统化调试定位；修复后重跑受影响测试与全量回归。
- Candidate 失败：不得使用源码目录结果代替安装后结果。
- 真实项目 Build/Browser 失败：记录为 Evidence 和 Gate Input；不自动改 Stage、不伪造通过。
- 目标项目缺少运行条件：状态为 `BLOCKED`，列出缺失输入；不能降级为仅阅读代码即通过。
- 发现需要修改 Product Boundary、Core Schema、Tool Shape 或 Deployment Boundary：标记 `DESIGN_GAP` 或 Maker Scope Review，停止受影响部分。

## 8. Exit Criteria

V1.2 Web Product Candidate 只有在以下条件全部满足时可判定 `ACCEPTED`：

1. Stage A–G 全部 PASS；
2. Stage H1–H4、H6、H7 全部 PASS；
3. H5 为 PASS 或有真实且充分的 NOT_APPLICABLE 理由；
4. 全量自动化零失败，受保护资产无漂移；
5. Candidate 在仓库外全新安装并从 Candidate 路径加载 Web Registry、Profile、Skill 与 Workflow；
6. 真实项目 Build 成功、localhost 可访问、真实浏览器核心旅程和关键失败路径均有 Evidence；
7. 浏览器与次级界面 Evidence 没有互相替代；
8. 没有 Deployment Validated 或 Production Ready 越界结论；
9. Stage H 全程绑定 Stage G 的同一 Candidate 安装路径、`0.3.0` 版本和内容哈希，Activation Read-back 与之相符；
10. `ACCEPTANCE_TEST_LOG.md` 包含可复核的版本、命令摘要、环境、Evidence、限制和最终判定；
11. Maker 审阅验收结果后决定发布、继续修复或保持候选状态。

## 9. Maker Approval

Maker 于 2026-10-14 批准本计划和 Implementation Plan，并要求按依赖关系串行、无依赖关系并行执行。

本批准只授权按既定边界实施和验证，不预先授予发布、推送、部署或 Production Ready 声明权限。

