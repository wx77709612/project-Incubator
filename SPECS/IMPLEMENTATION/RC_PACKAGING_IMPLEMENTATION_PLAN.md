# Project Incubator RC Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建、验证并全局并行安装一个可脱离研发仓库运行的 `project-incubator-v1-1-rc` Skill，同时保持现有 V1.0 安装不变。

**Architecture:** 使用外层 RC Skill Identity 与内层 `PROJECT_INCUBATOR` Python Package Identity 分离的结构。构建器复制当前 Source Package、生成显式调用元数据和内容摘要；验证器从无关工作目录执行 Runtime Import、Definition Resolution 与五个 Script；安装器以并行目录原子安装并校验 V1.0 前后摘要。

**Tech Stack:** Python 3 标准库 `argparse`、`dataclasses`、`hashlib`、`json`、`pathlib`、`shutil`、`subprocess`、`tempfile`、`unittest`。

**Spec:** `SPECS/DESIGN/RC_PACKAGING_DESIGN.md`

**Status:** DRAFT / MAKER REVIEW REQUIRED

## Global Constraints

- 正式 Skill Identity 保持 `project-incubator`，RC Identity 固定为 `project-incubator-v1-1-rc`。
- RC Package Version 固定为 `1.1.0-rc.1`。
- RC 必须设置 `allow_implicit_invocation: false`。
- Source Package 继续是 `PROJECT_INCUBATOR/`，Distribution 与 Installed RC 不成为 Source of Truth。
- 不修改 P0–P6、Transition、Gate、Context、Advisory 或 Runtime Authority。
- 不覆盖或修改 `$CODEX_HOME/skills/project-incubator/`。
- 构建和验证不得依赖 Implementation Repository 位于 `PYTHONPATH`。
- 构建产物排除缓存、测试、历史 Specs、Git 元数据和 Maker 专用答案。
- 所有行为修改先建立失败测试；全局安装只在构建目录 Smoke Test 通过后执行。
- 本计划不创建 V1.1 正式发布归档。

## Review Focus

- 路径包含空格和非 ASCII 字符时，构建、摘要与子进程调用必须成功；Task 2 和 Task 3 覆盖。
- 外部环境已设置污染性的 `PYTHONPATH` 时，Smoke Test 必须移除研发仓库路径并仍然通过；Task 3 覆盖。
- RC 目标目录已经存在且内容不同的时候，安装器必须拒绝隐式覆盖；Task 4 覆盖。
- 安装中途失败时，既有 RC 和正式 V1.0 必须保持原样；Task 4 覆盖。
- Manifest、Skill Frontmatter、Runtime Config 任一版本不一致时，验证器必须失败；Task 3 覆盖。

## File Structure

| File | Responsibility |
| --- | --- |
| `TOOLS/__init__.py` | 标记仓库级发布工具包 |
| `TOOLS/rc_skill_common.py` | RC 常量、文件摘要、排除规则和报告类型 |
| `TOOLS/build_rc_skill.py` | 从 Source Package 构建自包含 Distribution Artifact |
| `TOOLS/verify_rc_skill.py` | 执行身份、隔离 Import、Definition 与 Script Smoke Test |
| `TOOLS/install_rc_skill.py` | 将已验证 Artifact 原子安装到并行全局目录 |
| `TESTS/unit/test_rc_skill_builder.py` | 构建结构、身份、排除项与 Manifest 测试 |
| `TESTS/integration/test_rc_skill_isolation.py` | 仓库外 Runtime 与五个 Script 验证 |
| `TESTS/integration/test_rc_skill_installer.py` | 并行安装、覆盖拒绝、失败回滚和 V1.0 保护 |
| `.gitignore` | 排除本地 `DIST/` 构建产物 |

## Task Dependencies

| Task | Depends On | Deliverable |
| --- | --- | --- |
| 1 | 无 | 可复现当前扁平安装失败的回归测试 |
| 2 | 1 | 确定性 RC 构建器与 Manifest |
| 3 | 2 | 仓库外自包含验证器 |
| 4 | 3 | 并行原子安装器 |
| 5 | 4 | 实际 RC 构建、全局安装和 Installed Smoke Evidence |
| 6 | 5 | 状态回写与模拟人工验收交接 |

---

### Task 1: Installed Package Failure Regression

**Files:**
- Create: `TESTS/integration/test_rc_skill_isolation.py`

**Interfaces:**
- Consumes: 当前 `PROJECT_INCUBATOR/` Source Package。
- Produces: `RcSkillIsolationTests`，证明扁平安装失败并定义嵌套 RC 的成功行为。

- [ ] **Step 1: 写入仓库外直接执行的失败测试**

```python
class RcSkillIsolationTests(unittest.TestCase):
    def test_flattened_install_cannot_resolve_project_incubator_package(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            flattened = root / "project-incubator"
            shutil.copytree(SOURCE_PACKAGE, flattened)
            unrelated = root / "unrelated"
            unrelated.mkdir()
            result = subprocess.run(
                [sys.executable, str(flattened / "scripts" / "validate_artifact_evidence.py")],
                input="{}",
                cwd=unrelated,
                text=True,
                capture_output=True,
                env=clean_environment(),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("No module named 'PROJECT_INCUBATOR'", result.stderr)

    def test_nested_rc_layout_executes_script_outside_repository(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            skill_root = root / "project-incubator-v1-1-rc"
            shutil.copytree(SOURCE_PACKAGE, skill_root / "PROJECT_INCUBATOR")
            unrelated = root / "含空格的无关目录"
            unrelated.mkdir()
            result = run_script(
                skill_root,
                "validate_artifact_evidence.py",
                {"invocation_id": "isolation", "artifact_reference": "missing"},
                cwd=unrelated,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("INVALID_INPUT", json.loads(result.stdout)["execution_status"])
```

- [ ] **Step 2: 运行失败复现**

Run: `python TESTS/integration/test_rc_skill_isolation.py`

Expected: 扁平安装测试通过；嵌套结构测试通过；该结果只证明目录拓扑可解决 Import，不证明 RC 构建器存在。

- [ ] **Step 3: 提交失败证据测试**

```text
git add TESTS/integration/test_rc_skill_isolation.py
git commit -m "test: reproduce installed skill import isolation"
```

### Task 2: Deterministic RC Builder

**Files:**
- Create: `TOOLS/__init__.py`
- Create: `TOOLS/rc_skill_common.py`
- Create: `TOOLS/build_rc_skill.py`
- Create: `TESTS/unit/test_rc_skill_builder.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `RcBuildResult(skill_root: Path, manifest_path: Path, build_identity: str)`。
- Produces: `build_rc_skill(source_root, output_parent, source_commit, built_at) -> RcBuildResult`。
- Produces: `tree_digest(root, excluded_names=()) -> str` 和 `payload_manifest(root) -> dict[str, str]`。

- [ ] **Step 1: 写入构建器失败测试**

```python
def test_build_creates_nested_explicit_only_rc(self):
    result = build_rc_skill(
        SOURCE_PACKAGE,
        self.output,
        source_commit="abc123",
        built_at="2026-09-24T00:00:00Z",
    )
    self.assertEqual("project-incubator-v1-1-rc", result.skill_root.name)
    self.assertTrue((result.skill_root / "PROJECT_INCUBATOR" / "runtime" / "config.json").is_file())
    self.assertIn("name: project-incubator-v1-1-rc", (result.skill_root / "SKILL.md").read_text("utf-8"))
    self.assertIn("allow_implicit_invocation: false", (result.skill_root / "agents" / "openai.yaml").read_text("utf-8"))
```

同时增加以下断言：

- 嵌套 `runtime/config.json` 的 `package_version` 为 `1.1.0-rc.1`；
- `BUILD_MANIFEST.json` 的 Skill Identity、Version、Source Commit 与输入一致；
- Manifest 的 `files` 覆盖所有 Payload 文件但不包含 Manifest 自身；
- `__pycache__`、`*.pyc`、`.git`、`TESTS`、`ACCEPTANCE_TESTS`、`SPECS/_V*` 不进入产物；
- 同一 Source、Commit 和 `built_at` 产生相同文件摘要；
- 输出路径包含空格和中文时仍可构建；
- Source `SKILL.md` 与 `runtime/config.json` 不被修改。

- [ ] **Step 2: 运行测试并确认因构建模块不存在而失败**

Run: `python TESTS/unit/test_rc_skill_builder.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'TOOLS'` 或缺少 `build_rc_skill`。

- [ ] **Step 3: 实现公共常量和摘要函数**

```python
RC_SKILL_ID = "project-incubator-v1-1-rc"
RC_PACKAGE_VERSION = "1.1.0-rc.1"
PAYLOAD_EXCLUDED_DIRS = {"__pycache__", ".git", "TESTS", "ACCEPTANCE_TESTS"}
PAYLOAD_EXCLUDED_SUFFIXES = {".pyc"}

@dataclass(frozen=True)
class RcBuildResult:
    skill_root: Path
    manifest_path: Path
    build_identity: str
```

`tree_digest()` 必须按相对 POSIX 路径排序，将路径和文件内容共同输入 SHA-256，避免只比较文件内容而忽略路径变化。

- [ ] **Step 4: 实现 `build_rc_skill()`**

实现顺序：

1. 验证 Source 中存在 `SKILL.md`、`runtime/config.json`、`references/`、`scripts/` 和 `templates/`；
2. 拒绝输出目录与 Source 重叠；
3. 在输出父目录创建临时 staging；
4. 将 Source 复制到 `staging/PROJECT_INCUBATOR/` 并应用排除规则；
5. 使用 JSON API 将嵌套 Runtime Config 的 `package_version` 改为 `1.1.0-rc.1`；
6. 从 Source `SKILL.md` 生成顶层 RC `SKILL.md`，只修改 Frontmatter `name`，并加入 RC Identity、Version、显式调用和版本冲突停止规则；
7. 生成 `agents/openai.yaml`，设置 `allow_implicit_invocation: false`；
8. 生成 Payload 文件摘要和 `BUILD_MANIFEST.json`；
9. 将 staging 原子重命名为最终目录；
10. 失败时删除 staging，不留下半构建产物。

- [ ] **Step 5: 运行构建器测试**

Run: `python TESTS/unit/test_rc_skill_builder.py`

Expected: all tests PASS。

- [ ] **Step 6: 更新 `.gitignore`**

追加：

```text
DIST/
```

- [ ] **Step 7: 提交构建器**

```text
git add .gitignore TOOLS TESTS/unit/test_rc_skill_builder.py
git commit -m "feat: build isolated project incubator rc skill"
```

### Task 3: Clean-room RC Verifier

**Files:**
- Create: `TOOLS/verify_rc_skill.py`
- Modify: `TESTS/integration/test_rc_skill_isolation.py`

**Interfaces:**
- Consumes: Task 2 `RcBuildResult` 和 `payload_manifest()`。
- Produces: `RcVerificationCheck(name: str, passed: bool, detail: str)`。
- Produces: `RcVerificationReport(skill_root: Path, checks: tuple[RcVerificationCheck, ...], passed: bool)`。
- Produces: `verify_rc_skill(skill_root: Path) -> RcVerificationReport`。

- [ ] **Step 1: 写入验证器失败测试**

```python
def test_verifier_rejects_version_mismatch(self):
    built = self.build_rc()
    config = built.skill_root / "PROJECT_INCUBATOR" / "runtime" / "config.json"
    payload = json.loads(config.read_text("utf-8"))
    payload["package_version"] = "1.1"
    config.write_text(json.dumps(payload), encoding="utf-8")
    report = verify_rc_skill(built.skill_root)
    self.assertFalse(report.passed)
    self.assertIn("identity_consistency", failed_check_names(report))

def test_verifier_runs_runtime_and_all_scripts_from_unrelated_directory(self):
    report = verify_rc_skill(self.build_rc().skill_root)
    self.assertTrue(report.passed, report)
    self.assertEqual(EXPECTED_CHECKS, {check.name for check in report.checks})
```

还必须测试：Manifest 文件被篡改、隐式调用为 true、缺少嵌套 Package、污染 `PYTHONPATH` 包含研发仓库、路径包含空格和中文。

- [ ] **Step 2: 运行测试并确认因验证模块不存在而失败**

Run: `python TESTS/integration/test_rc_skill_isolation.py`

Expected: FAIL because `verify_rc_skill` is missing。

- [ ] **Step 3: 实现身份和 Manifest 验证**

验证器必须比较：

```text
顶层 SKILL name
agents/openai.yaml explicit-only policy
BUILD_MANIFEST skill_identity
BUILD_MANIFEST package_version
嵌套 runtime/config.json package_version
实际 Payload 文件摘要
```

不得只通过字符串包含关系判断版本；Runtime Config 和 Manifest 必须通过 JSON 解析。

- [ ] **Step 4: 实现 Clean-room Runtime 验证**

验证器在临时无关目录执行子进程，并构造仅保留必要系统变量的环境。子进程工作目录设为 RC Root，通过 RC Root 导入：

```python
from PROJECT_INCUBATOR.runtime.components.definition_resolver import DefinitionResolver
from PROJECT_INCUBATOR.runtime.core.coordinator import RuntimeCoordinator

resolution = DefinitionResolver().resolve()
assert resolution.frozen_definition_set is not None
```

输出必须包含实际加载模块的绝对路径；验证器确认该路径位于 RC Root 内，不能来自 Implementation Repository 或 V1.0。

- [ ] **Step 5: 实现五个 Script Smoke Payload**

使用最小合法输入：

```python
SMOKE_PAYLOADS = {
    "validate_contract_payload.py": {
        "invocation_id": "rc-contract",
        "contract_type": "WORKFLOW",
        "input_data": {"workflow_result": "READY_FOR_TRANSITION"},
        "required_field_set": ["workflow_result"],
        "allowed_value_set": {},
    },
    "validate_artifact_evidence.py": {
        "invocation_id": "rc-artifact",
        "artifact_reference": {"artifact_id": "rc-smoke-artifact"},
        "artifact_path": "__SMOKE_ARTIFACT__",
        "expected_requirement": {
            "requirement_id": "RC Artifact Mechanical Requirement",
            "must_exist": True,
            "must_be_readable": True,
            "must_be_non_empty": True,
        },
    },
    "inspect_git_evidence.py": {
        "invocation_id": "rc-git",
        "repository_path": "__SMOKE_GIT_REPOSITORY__",
        "requested_git_operation": "status",
    },
    "validate_context_integrity_evidence.py": {
        "invocation_id": "rc-context",
        "required_context_type_set": ["PROJECT_STATE"],
        "context_derived_data": {"PROJECT_STATE": {"Current Phase": "P4"}},
        "declared_context_identity": {"PROJECT_STATE": "PROJECT_STATE.md"},
        "required_structural_item": {"PROJECT_STATE": ["Current Phase"]},
    },
    "bootstrap_host_integration.py": {
        "invocation_id": "rc-bootstrap",
        "invocation_purpose": "DETERMINISTIC_OPERATION",
        "input_data": {"host_environment": "OTHER"},
    },
}
```

验证器负责把两个占位路径替换为临时 Artifact 和临时 Git 仓库根目录。每个 Script 必须返回进程码 0、合法 JSON，并且 `execution_status` 不是 `EXECUTION_ERROR`。

- [ ] **Step 6: 运行隔离验证测试**

Run: `python TESTS/integration/test_rc_skill_isolation.py`

Expected: all tests PASS；子进程输出模块路径位于临时 RC Root。

- [ ] **Step 7: 提交验证器**

```text
git add TOOLS/verify_rc_skill.py TESTS/integration/test_rc_skill_isolation.py
git commit -m "test: verify rc skill outside repository"
```

### Task 4: Parallel Atomic Installer

**Files:**
- Create: `TOOLS/install_rc_skill.py`
- Create: `TESTS/integration/test_rc_skill_installer.py`

**Interfaces:**
- Consumes: Task 2 Build Artifact、Task 3 `verify_rc_skill()`、`tree_digest()`。
- Produces: `RcInstallResult(installed_path: Path, stable_v1_digest_before: str | None, stable_v1_digest_after: str | None, verification_passed: bool)`。
- Produces: `install_rc_skill(artifact_root, codex_home, replace=False) -> RcInstallResult`。

- [ ] **Step 1: 写入安装器失败测试**

```python
def test_parallel_install_preserves_stable_v1(self):
    stable = self.skills / "project-incubator"
    stable.mkdir(parents=True)
    (stable / "SKILL.md").write_text("stable-v1", encoding="utf-8")
    before = tree_digest(stable)
    result = install_rc_skill(self.artifact, self.codex_home)
    self.assertEqual(before, result.stable_v1_digest_after)
    self.assertTrue((self.skills / "project-incubator-v1-1-rc" / "BUILD_MANIFEST.json").is_file())

def test_existing_different_rc_is_not_overwritten_without_replace(self):
    target = self.skills / "project-incubator-v1-1-rc"
    target.mkdir(parents=True)
    (target / "sentinel.txt").write_text("keep", encoding="utf-8")
    with self.assertRaises(RcInstallError):
        install_rc_skill(self.artifact, self.codex_home)
    self.assertEqual("keep", (target / "sentinel.txt").read_text("utf-8"))
```

另外覆盖：验证失败禁止安装、staging copy 失败不改变目标、`replace=True` 也必须先验证 Artifact、安装后验证失败时恢复旧 RC、V1.0 缺失时不伪造摘要。

- [ ] **Step 2: 运行测试并确认因安装模块不存在而失败**

Run: `python TESTS/integration/test_rc_skill_installer.py`

Expected: FAIL because `install_rc_skill` is missing。

- [ ] **Step 3: 实现安装事务**

顺序固定为：

1. `verify_rc_skill(artifact_root)`；
2. 计算 `skills/project-incubator` 摘要；
3. 检查目标 RC 是否存在；
4. 复制 Artifact 到同级唯一 staging 目录；
5. 对 staging 再次执行 `verify_rc_skill()`；
6. 必要时将旧 RC 原子重命名为 rollback 目录；
7. 将 staging 原子重命名为正式 RC 目录；
8. 对 Installed RC 执行验证；
9. 比较 V1.0 前后摘要；
10. 成功后删除 rollback；失败时恢复 rollback 并删除 staging。

任何异常都必须保留 V1.0，并且不得留下被 Codex 识别为正式 Skill 的半安装目录。

- [ ] **Step 4: 运行安装器测试**

Run: `python TESTS/integration/test_rc_skill_installer.py`

Expected: all tests PASS。

- [ ] **Step 5: 提交安装器**

```text
git add TOOLS/install_rc_skill.py TESTS/integration/test_rc_skill_installer.py
git commit -m "feat: install v1.1 rc skill in parallel"
```

### Task 5: Build and Install RC Candidate

**Files:**
- Generate, not commit: `DIST/project-incubator-v1-1-rc/`
- Install outside repository: `$CODEX_HOME/skills/project-incubator-v1-1-rc/`

**Interfaces:**
- Consumes: Tasks 2–4 CLI entrypoints。
- Produces: `1.1.0-rc.1` Distribution Artifact、Installed RC、构建与安装验证报告。

- [ ] **Step 1: 运行完整仓库回归**

Run the explicit 170-test matrix：

```text
python -m unittest <all TESTS/test_*.py files>
python -m unittest <all ACCEPTANCE_TESTS/layer2/test_*.py files>
python -m unittest <all ACCEPTANCE_TESTS/v1_1/test_*.py files>
```

Expected: 94 + 新增 RC tests、40、36 全部通过。

- [ ] **Step 2: 构建 RC**

Run in PowerShell:

```text
$sourceCommit = git -c safe.directory='F:/projects/Project Incubator Skill' rev-parse HEAD
python TOOLS/build_rc_skill.py --source PROJECT_INCUBATOR --output DIST --source-commit $sourceCommit
```

Expected: 生成 `DIST/project-incubator-v1-1-rc/BUILD_MANIFEST.json`，没有缓存、测试或历史 Specs。

- [ ] **Step 3: 在仓库外验证 Distribution Artifact**

Run:

```text
python TOOLS/verify_rc_skill.py DIST/project-incubator-v1-1-rc
```

Expected: 身份、Manifest、Runtime Import、Definition 和五个 Script checks 全部 PASS。

- [ ] **Step 4: 请求文件系统授权并并行安装**

Run:

```text
python TOOLS/install_rc_skill.py DIST/project-incubator-v1-1-rc --codex-home 'C:/Users/Xenia_Woo/.codex'
```

Expected: 创建 `$CODEX_HOME/skills/project-incubator-v1-1-rc/`；`project-incubator/` 摘要不变。

- [ ] **Step 5: 验证 Installed RC**

Run:

```text
python TOOLS/verify_rc_skill.py 'C:/Users/Xenia_Woo/.codex/skills/project-incubator-v1-1-rc'
```

Expected: 与 Distribution Artifact 相同的检查全部 PASS；实际模块路径来自 Installed RC。

- [ ] **Step 6: 验证 Skill Discovery**

启动一个不加载 Implementation Repository 的新任务，显式调用：

```text
$project-incubator-v1-1-rc 请只报告实际加载的 Skill Identity、Package Version 和 Invocation Policy，不执行项目变更。
```

Expected: `project-incubator-v1-1-rc`、`1.1.0-rc.1`、`explicit-only`。普通不带显式 Skill 的项目不得自动选择 RC。

### Task 6: Governance Close-out and Manual Acceptance Handoff

**Files:**
- Modify: `SPECS/DESIGN/RC_PACKAGING_DESIGN.md`
- Modify: `SPECS/IMPLEMENTATION/RC_PACKAGING_IMPLEMENTATION_PLAN.md`
- Modify: `SPECS/IMPLEMENTATION/LAYER2_RUNTIME_ACCEPTANCE_TEST_PLAN.md`
- Modify: `SPECS/README.md`

**Interfaces:**
- Consumes: Task 5 Build Manifest、Distribution Verification、Installed Verification 和 Discovery Evidence。
- Produces: RC Packaging Gap 关闭记录，以及“雾港提醒器”模拟人工验收项目的准入条件。

- [ ] **Step 1: 记录实际验证数字和 Build Identity**

必须记录：

- 新增测试数量和总测试数量；
- Source Commit；
- RC Build Identity；
- Distribution Artifact 摘要；
- Installed RC 摘要；
- V1.0 安装前后摘要；
- Installed Smoke Test 结果；
- Skill Discovery 结果。

- [ ] **Step 2: 更新文档状态**

只有 Task 5 全部通过时：

- `RC_PACKAGING_DESIGN.md` → `IMPLEMENTED / INSTALLED SMOKE PASSED`；
- 本计划 → `IMPLEMENTED / INSTALLED SMOKE PASSED`；
- Acceptance Plan 的 Packaging Gap → `CLOSED FOR RC`；
- `SPECS/README.md` 当前阶段 → `Manual Acceptance Preparation`。

任一检查失败时保留 `PACKAGING GAP OPEN`，不得生成模拟项目的通过结论。

- [ ] **Step 3: 运行文档与仓库状态检查**

Run:

```text
git diff --check
rg -n "TO[D]O|TB[D]|待填[写]" SPECS/DESIGN/RC_PACKAGING_DESIGN.md SPECS/IMPLEMENTATION/RC_PACKAGING_IMPLEMENTATION_PLAN.md
```

Expected: 无空白错误、无占位符、状态与 `SPECS/README.md` 一致。

- [ ] **Step 4: 提交治理收尾**

```text
git add SPECS
git commit -m "docs: record v1.1 rc installation evidence"
```

## Completion Criteria

- 当前扁平安装 Import Failure 有自动化回归测试；
- RC 构建器生成外层新 Skill Identity 与内层原 Python Package Identity；
- RC 明确为 `1.1.0-rc.1` 且仅显式调用；
- Clean-room Runtime Import 和 Definition Resolution 通过；
- 五个确定性 Script 在仓库外通过 Smoke Test；
- 安装器验证失败时不修改全局目录；
- V1.0 与 V1.1 RC 并行存在且 V1.0 摘要不变；
- Installed RC Smoke Test 和 Skill Discovery 通过；
- 原有 Runtime 与 V1.0/V1.1 Acceptance 不回归；
- Packaging Gap 被实际证据关闭；
- 尚未创建 V1.1 正式发布归档；
- 后续模拟项目明确绑定 `$project-incubator-v1-1-rc`。
