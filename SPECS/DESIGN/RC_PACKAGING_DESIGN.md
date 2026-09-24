# Project Incubator RC Packaging Design

> Specification Version: V1.1
> Status: APPROVED / IMPLEMENTED / INSTALLED SMOKE PASSED / DISCOVERY PENDING
> Scope: Release Candidate 打包、并行安装与隔离人工验收
> Related Plan: `SPECS/IMPLEMENTATION/RC_PACKAGING_IMPLEMENTATION_PLAN.md`
> Related Acceptance Plan: `SPECS/IMPLEMENTATION/LAYER2_RUNTIME_ACCEPTANCE_TEST_PLAN.md`

## 1. 背景

V1.1 Runtime、Skill 指引和自动化验收已经在 Implementation Repository 内通过，但尚未形成可脱离研发仓库运行的候选发布包。

对当前全局安装的 V1.0 Skill 执行仓库外脚本探测时，出现：

```text
ModuleNotFoundError: No module named 'PROJECT_INCUBATOR'
```

该结果证明现有安装结构隐式依赖 Implementation Repository 或其父目录处于 Python 模块搜索路径。仓库内测试不能证明安装后的 Skill Package 自包含，因此该问题属于 Delivery Artifact / Installation Verification Gap，并阻止 V1.1 发布。

## 2. 目标

本设计要求形成一个可与 V1.0 并行存在的 V1.1 RC Skill Package，并满足：

- 不覆盖当前全局 `project-incubator` V1.0；
- 在任意无关工作目录中仍可加载 Runtime 和执行确定性 Script；
- 不依赖 Implementation Repository 路径；
- 能明确报告 Skill Identity、Package Version 和 RC Build Identity；
- 只能由 Maker 或测试 Prompt 显式调用，避免与 V1.0 自动匹配冲突；
- 可被完整卸载，不修改 V1.0 安装内容；
- 可供隔离的模拟 Managed Project 完成人工行为验收。

## 3. 非目标

- 不改变 P0–P6 Phase Set；
- 不改变 Transition、Gate、Context、Advisory 或 Runtime Authority；
- 不将 RC 标记为正式 V1.1 Release；
- 不在本任务中替换全局 V1.0；
- 不因打包需要复制或重定义 Runtime Domain Rule；
- 不把模拟项目或 Maker 测试答案装入 RC Skill Package。

## 4. 版本与身份

### 4.1 并行身份

| 用途 | Skill Identity | Package Version | 自动调用 |
| --- | --- | --- | --- |
| 已发布基线 | `project-incubator` | `1.0` | 保持现状 |
| V1.1 候选版 | `project-incubator-v1-1-rc` | `1.1.0-rc.1` | 禁止，只允许显式调用 |
| 后续正式版 | `project-incubator` | `1.1` | 通过发布决策后替换 |

RC 的 `SKILL.md` Frontmatter、`agents/openai.yaml`、Runtime Config 和 Build Manifest 必须表达同一身份。任何一处不一致均视为打包失败。

### 4.2 Managed Project 声明

模拟项目必须在项目级协作入口和项目资料中声明：

```text
Required Skill: project-incubator-v1-1-rc
Required Version: 1.1.0-rc.1
Invocation Policy: explicit-only
```

人工验收首条 Prompt 必须显式使用 `$project-incubator-v1-1-rc`，并要求 Agent 在执行前报告实际加载的 Skill Identity 与 Package Version。

## 5. Source、Distribution 与 Installation 边界

必须区分三类对象：

| 对象 | 位置 | 职责 |
| --- | --- | --- |
| Source Package | `PROJECT_INCUBATOR/` | V1.1 当前实现 Source of Truth |
| Distribution Artifact | 构建输出目录 | 自包含、可校验、可安装的 RC 快照 |
| Installed RC | `$CODEX_HOME/skills/project-incubator-v1-1-rc/` | 新任务实际发现和加载的候选 Skill |

Distribution Artifact 与 Installed RC 均不得反向成为 Source of Truth。任何修复必须先进入 Source Package，经测试后重新构建，不得直接热修全局安装目录。

## 6. Distribution Artifact 结构

候选包必须具有清晰的 Skill 入口和保持原包名的 Python Runtime：

```text
project-incubator-v1-1-rc/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── BUILD_MANIFEST.json
└── PROJECT_INCUBATOR/
    ├── AGENTS.md
    ├── README.md
    ├── SKILL.md
    ├── references/
    ├── runtime/
    ├── scripts/
    └── templates/
```

顶层 `SKILL.md` 是 Codex Skill Discovery 入口。嵌套的 `PROJECT_INCUBATOR/` 保留 Python Package Identity，避免将内部绝对导入与 Skill 展示名称耦合。

`BUILD_MANIFEST.json` 至少记录：

- Skill Identity；
- Package Version；
- RC Build Identity；
- Source Commit；
- 构建时间；
- 文件清单及内容摘要；
- 排除规则；
- Smoke Test 结果引用。

## 7. Runtime 自包含要求

候选包必须提供稳定的 Runtime Bootstrap 机制，使调用方无需知道 Implementation Repository 路径。

Bootstrap 必须：

1. 从自身安装位置解析 RC Root；
2. 将包含 `PROJECT_INCUBATOR` 的目录加入当前执行的模块搜索路径；
3. 只影响当前子进程或当前调用，不修改系统级 Python 配置；
4. 不依赖当前工作目录；
5. 不把研发仓库路径写入 Build Artifact；
6. 允许 Runtime Library 和五个确定性 Script 使用同一 Package Identity；
7. 在依赖缺失时返回明确失败，不静默回退到全局 V1.0 或研发仓库副本。

具体采用启动器、受控环境变量或模块入口属于 Implementation Choice，但必须由安装烟雾测试证明上述行为。

## 8. 显式调用政策

RC 的 `agents/openai.yaml` 必须配置：

```yaml
policy:
  allow_implicit_invocation: false
```

这样 V1.0 与 V1.1 RC 可以同时存在，而普通项目仍只会自动匹配正式的 `project-incubator`。只有显式 `$project-incubator-v1-1-rc` 才能加载候选版。

RC 顶层说明必须要求：如果 Managed Project 声明的 Required Version 与实际包版本不一致，Agent 停止受影响工作并报告版本冲突。

## 9. 构建与安装流程

构建流程必须是确定性的：

```text
校验 Source Package
→ 创建干净的 Distribution Artifact
→ 重写 RC 展示身份，不改内部 Runtime Identity
→ 生成文件清单与摘要
→ 在仓库外临时目录执行 Smoke Test
→ 安装到并行全局目录
→ 从另一个干净目录执行 Installed Smoke Test
→ 记录结果
```

构建默认排除：

- `__pycache__` 与 `*.pyc`；
- `SPECS/_V*`；
- `TESTS/` 与 `ACCEPTANCE_TESTS/`；
- `.git/`；
- 临时目录和测试 Fixture；
- Maker 专用人工验收答案。

## 10. 安装烟雾测试

以下测试均为 Release Blocking：

### 10.1 身份测试

- Codex 可发现 `project-incubator-v1-1-rc`；
- RC 只能显式调用；
- `package_version` 为 `1.1.0-rc.1`；
- Build Manifest 与包内身份一致；
- 正式 V1.0 目录及文件摘要保持不变。

### 10.2 仓库隔离测试

- 将 Distribution Artifact 复制到随机临时目录；
- 将当前工作目录切换到另一个无关目录；
- 环境中不加入 Implementation Repository；
- Runtime Core Import 成功；
- Definition Resolver 成功加载四类 Definition；
- 不存在对研发仓库绝对路径的读取。

### 10.3 Script 测试

五个确定性 Script 必须从仓库外完成最小合法调用：

- `VALIDATE_CONTRACT_PAYLOAD`；
- `INSPECT_GIT_EVIDENCE`；
- `VALIDATE_ARTIFACT_EVIDENCE`；
- `VALIDATE_CONTEXT_INTEGRITY_EVIDENCE`；
- `BOOTSTRAP_HOST_INTEGRATION`。

测试必须区分“脚本按 Contract 返回业务拒绝”和“脚本因 Import / Package Resolution 失败”。后者阻止安装。

### 10.4 Installed Smoke Test

安装完成后必须重新运行身份、Runtime Import、Definition Resolution 和 Script 测试。只验证构建目录而未验证全局安装目录，不构成安装验收。

## 11. 回滚与卸载

RC 安装不得修改 V1.0 文件，因此回滚只允许：

1. 删除或卸载 `project-incubator-v1-1-rc`；
2. 验证 `project-incubator` V1.0 仍可发现；
3. 验证 V1.0 文件摘要与安装前一致；
4. 保留 RC 构建记录和失败 Evidence，不删除验收历史。

不得通过覆盖 V1.0 后再从备份恢复的方式实现“并行测试”。

## 12. 模拟人工验收衔接

只有 Installed Smoke Test 通过后，才创建模拟 Managed Project。

模拟项目与 Maker 专用验收包必须分离：

- Agent 可见项目只包含项目 Context、Artifact、虚构平台资料和逐步产生的 Evidence；
- Maker 专用包包含 Prompt、标准回答、预期行为、禁止行为和评分表；
- 模拟 Agent 不得读取 Maker 专用包或 Implementation Repository；
- 人工验收结论记录实际输出，不把标准答案注入 Agent Context。

## 13. 验收标准

本设计完成的判定条件是：

- V1.0 与 V1.1 RC 同时可被 Codex 发现；
- 普通隐式匹配不会加载 RC；
- 显式调用能报告正确版本；
- RC 在仓库外可独立加载 Runtime；
- 五个确定性 Script 不再出现 `ModuleNotFoundError`；
- Installed Smoke Test 通过；
- V1.0 安装内容未改变；
- 模拟项目能明确绑定 RC；
- 未创建 V1.1 正式发布归档。

## 14. 后续步骤

本设计经 Maker 书面审阅后：

1. 编写 RC Packaging Implementation Plan；
2. 先建立能够复现当前安装失败的自动化测试；
3. 实现最小自包含打包与 Bootstrap；
4. 构建并安装 `project-incubator-v1-1-rc`；
5. 执行仓库外 Installed Smoke Test；
6. 再生成“雾港提醒器”模拟项目和 Maker 专用测试包。

## 15. 实施证据

2026-09-24 已完成以下实施与验证：

- 生成 `project-incubator-v1-1-rc`，Package Version 为 `1.1.0-rc.1`；
- Distribution Artifact 与 Installed RC 的九项隔离检查全部通过；
- Runtime 实际加载路径来自 Installed RC，不依赖 Implementation Repository；
- 五个确定性 Script 均返回 `COMPLETED`；
- V1.0 全局 Skill 摘要在安装前后保持 `c01fe91e476e52b3f590e37b04f6bbd1208eeec3eded30a771f0bdaac6b41cf5`；
- RC Skill Discovery 仍需在不加载 Implementation Repository 的新任务中验证。

在 Skill Discovery 完成前，本设计不宣称全部验收标准已经满足，Packaging Gap 保持开放。
