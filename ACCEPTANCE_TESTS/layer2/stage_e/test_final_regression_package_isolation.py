"""Layer 2 Stage E Final Regression and Package Isolation Acceptance Tests.

本文件是 Maker-driven Runtime Acceptance Test Code。
它只验证 Layer 2 最终回归与发布包隔离，不修改 Product Runtime。
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import sys
import textwrap
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


ACCEPTANCE_TEMP_ROOT = (
    REPOSITORY_ROOT
    / "ACCEPTANCE_TESTS"
    / "layer2"
    / "stage_e"
    / ".tmp_final_regression_package_isolation"
)

STAGE_A_MODULE = "ACCEPTANCE_TESTS.layer2.stage_a.test_runtime_foundation_acceptance"
STAGE_B_MODULE = "ACCEPTANCE_TESTS.layer2.stage_b.test_deterministic_capability_acceptance"
STAGE_C_MODULE = "ACCEPTANCE_TESTS.layer2.stage_c.test_gate_advisory_runtime_result_acceptance"
STAGE_D_MODULE = "ACCEPTANCE_TESTS.layer2.stage_d.test_runtime_orchestration_acceptance"


class FinalRegressionPackageIsolationAcceptanceTest(unittest.TestCase):
    """Stage E 验证 Layer 2 回归来源与发布包隔离边界。"""

    maxDiff = None

    @contextmanager
    def _isolated_environment(self) -> Iterator[tuple[Path, Path]]:
        temp_root = ACCEPTANCE_TEMP_ROOT.resolve()
        temp_root.mkdir(parents=True, exist_ok=True)
        isolation_root = (temp_root / f"run_{uuid.uuid4().hex}").resolve()
        if not str(isolation_root).startswith(str(temp_root)):
            raise RuntimeError("acceptance temp workspace escaped temp root")
        isolation_root.mkdir(mode=0o777, exist_ok=False)
        try:
            shutil.copytree(
                REPOSITORY_ROOT / "PROJECT_INCUBATOR",
                isolation_root / "PROJECT_INCUBATOR",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            managed_project = isolation_root / "managed_project"
            managed_project.mkdir(mode=0o777, exist_ok=False)
            self._write_core_context(managed_project, "P3")
            yield isolation_root, managed_project
        finally:
            shutil.rmtree(isolation_root, ignore_errors=True)
            try:
                temp_root.rmdir()
            except OSError:
                pass

    def _write_core_context(self, project_root: Path, current_phase: str) -> None:
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "PROJECT_PROFILE.md").write_text(
            "# Project Profile\n\nStage E isolated managed project\n",
            encoding="utf-8",
        )
        (project_root / "PROJECT_STATE.md").write_text(
            self._project_state_content(current_phase),
            encoding="utf-8",
        )
        (project_root / "PROJECT_PLAN.md").write_text(
            "# Project Plan\n\n- Stage E temporary plan\n",
            encoding="utf-8",
        )
        (project_root / "PROJECT_DECISIONS.md").write_text(
            "# Project Decisions\n\n- Decision ID: stage-e-temporary\n",
            encoding="utf-8",
        )

    def _project_state_content(self, phase: str) -> str:
        return f"# Project State\n\nCurrent Phase: {phase}\nCurrent Phase State: {phase}_READY\n"

    def _load_regression_suite(self, module_name: str) -> unittest.TestSuite:
        module = importlib.import_module(module_name)
        return unittest.defaultTestLoader.loadTestsFromModule(module)

    def _iter_tests(self, suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                yield from self._iter_tests(item)
            else:
                yield item

    def _run_regression_suite(self, suite: unittest.TestSuite) -> None:
        result = unittest.TestResult()
        suite.run(result)
        if result.wasSuccessful():
            return

        details: list[str] = []
        for test, traceback_text in result.failures + result.errors:
            details.append(f"{test.id()}\n{traceback_text}")
        self.fail(
            "Layer 2 regression source test failed or errored:\n"
            + "\n".join(details),
        )

    def _assert_clean_package_copy(self, isolation_root: Path) -> None:
        self.assertTrue((isolation_root / "PROJECT_INCUBATOR").is_dir())
        for forbidden_name in (
            "SPECS",
            "ACCEPTANCE_TESTS",
            "tests",
            "backup",
            "zzztemp",
            "AGENTS.md",
        ):
            self.assertFalse(
                (isolation_root / forbidden_name).exists(),
                f"isolated package copied forbidden development file: {forbidden_name}",
            )

    def _run_isolated_runtime(
        self,
        isolation_root: Path,
        managed_project: Path,
        *,
        audit_reads: bool = False,
    ) -> dict[str, Any]:
        code = self._isolated_runtime_code(managed_project, audit_reads=audit_reads)
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=isolation_root,
            env=env,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        if completed.returncode != 0:
            self.fail(
                "isolated Runtime process failed\n"
                f"STDOUT:\n{completed.stdout}\n"
                f"STDERR:\n{completed.stderr}",
            )
        return self._extract_child_json(completed.stdout)

    def _extract_child_json(self, stdout: str) -> dict[str, Any]:
        for line in reversed(stdout.splitlines()):
            if line.startswith("STAGE_E_JSON="):
                return json.loads(line.removeprefix("STAGE_E_JSON="))
        self.fail(f"isolated Runtime process did not emit STAGE_E_JSON payload:\n{stdout}")

    def _isolated_runtime_code(self, managed_project: Path, *, audit_reads: bool) -> str:
        audit_block = ""
        if audit_reads:
            audit_block = """
read_paths = []

def _audit_runtime_reads(event, args):
    if event != "open" or not args:
        return
    raw_path = args[0]
    raw_mode = args[1] if len(args) > 1 else None
    if isinstance(raw_mode, str) and not any(token in raw_mode for token in ("r", "+")):
        return
    try:
        resolved = Path(raw_path).resolve()
    except (TypeError, OSError, ValueError):
        return
    read_paths.append(str(resolved))

sys.addaudithook(_audit_runtime_reads)
"""

        return textwrap.dedent(
            f"""
            from __future__ import annotations

            import json
            import sys
            from pathlib import Path

            {textwrap.indent(textwrap.dedent(audit_block), "            ").strip()}

            from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
                AccessTarget,
                ContextType,
                MutationIntent,
                MutationType,
            )
            from PROJECT_INCUBATOR.runtime.components.script_coordinator import ScriptInvocationRequest
            from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import PhaseResult
            from PROJECT_INCUBATOR.runtime.core.coordinator import RuntimeCoordinator, RuntimeRequest

            project_root = Path({str(managed_project)!r}).resolve()
            contract_payload = {{
                "invocation_id": "L2-E-isolated-contract-payload",
                "contract_type": "WORKFLOW",
                "input_data": {{
                    "workflow_result": "READY_FOR_TRANSITION",
                    "request_id": "L2-E-isolated-transition",
                }},
                "required_field_set": ["workflow_result", "request_id"],
                "allowed_value_set": {{}},
                "required_type_set": {{"request_id": "string"}},
            }}
            script_request = ScriptInvocationRequest(
                invocation_id="L2-E-isolated-script",
                script_identity="VALIDATE_CONTRACT_PAYLOAD",
                invocation_purpose="VALIDATION",
                input_data=contract_payload,
            )
            phase_result = PhaseResult(
                current_phase="P3",
                requested_next_phase="P4",
                process_completed=True,
                required_artifact_requirement_satisfied=True,
                state_change_requirement_formed=True,
                gate_requirement_resolved=True,
                artifact_evidence=("isolated artifact evidence",),
                state_change_reference="isolated state change requirement",
                gate_resolution_reference="isolated gate resolution",
            )
            state_intent = MutationIntent(
                mutation_type=MutationType.UPDATE_CONTEXT,
                target_context=AccessTarget(ContextType.PROJECT_STATE),
                change_purpose="Persist isolated transition to P4",
                change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
                proposed_content="# Project State\\n\\nCurrent Phase: P4\\nCurrent Phase State: P4_READY\\n",
                proposed_change_reference="isolated-transition-to-P4",
            )
            gate_evidence = {{
                "gate_id": "GATE-GIT",
                "evidence_id": "L2-E-isolated-gate-evidence",
                "evidence_type": "GATE_EVALUATION",
                "current_branch": "main",
                "working_tree_has_changes": False,
                "untracked_files_present": False,
                "staged_changes_present": False,
                "gate_result": "REQUIREMENT_SATISFIED",
            }}
            result = RuntimeCoordinator().execute(
                RuntimeRequest(
                    request_id="L2-E-isolated-runtime",
                    requested_action="transition P3 to P4 with script and gate evidence",
                    project_root=project_root,
                    phase_result=phase_result,
                    context_mutation_intents=(state_intent,),
                    gate_trigger_event="git evidence collected",
                    requested_gate_ids=("GATE-GIT",),
                    gate_evaluation_evidence=(gate_evidence,),
                    script_invocation_requests=(script_request,),
                )
            )
            output = {{
                "runtime_state": result.runtime_execution_state.name,
                "runtime_reason": result.runtime_reason,
                "current_phase": getattr(result.current_phase_reference, "phase_id", None),
                "workflow_result": (
                    result.workflow_result_reference.status.name
                    if result.workflow_result_reference is not None
                    else None
                ),
                "script_result_count": len(result.script_output_reference),
                "script_execution_status": [
                    item.execution_status.name if item.execution_status is not None else None
                    for item in result.script_output_reference
                ],
                "script_validation_result": [
                    item.validation_result.name if item.validation_result is not None else None
                    for item in result.script_output_reference
                ],
                "gate_result": (
                    result.gate_output_reference.aggregate_gate_result.name
                    if result.gate_output_reference is not None
                    else None
                ),
                "gate_triggered_ids": (
                    list(result.gate_output_reference.triggered_gate_ids)
                    if result.gate_output_reference is not None
                    else []
                ),
                "context_result_count": len(result.context_access_result_reference),
                "completed_action_count": len(result.completed_action_reference or ()),
                "project_state_content": (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8"),
                "sys_path": [str(item) for item in sys.path],
                "read_paths": read_paths if {audit_reads!r} else [],
            }}
            print("STAGE_E_JSON=" + json.dumps(output, ensure_ascii=False, sort_keys=True))
            """
        )

    def _path_is_relative_to(self, path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
        except ValueError:
            return False
        return True

    def test_l2_e01_layer2_regression(self):
        """
        Test Case:
        L2-E01

        测试目标：
        Stage E 作为 Layer 2 最终回归入口，必须重新运行已经冻结并接受的前序 Acceptance Test。
        它防止 TASK-025～TASK-027 的自动化测试实现或后续整理工作，让 Stage A～D 已经证明过的
        Runtime Foundation、Deterministic Capability、Gate / Advisory / Runtime Result、Runtime Orchestration 回归。

        真实运行场景：
        Project Incubator 准备进入发布前最终 Layer 2 验收。
        ↓
        Stage E 不重新复制 A～D 的断言逻辑，而是把既有 Acceptance Test 作为 Regression Source。
        ↓
        任何被纳入的原始 Layer 2 Acceptance Test 失败，Stage E Regression 必须失败。
        ↓
        Maker 才能确认后续 Package Isolation 不是建立在已经回归的 Runtime 上。

        System Layer：
        Layer 2 Acceptance / Final Regression

        Runtime Flow Position：
        Stage A Runtime Foundation
        ↓
        Stage B Deterministic Capability
        ↓
        Stage C Gate / Advisory / Runtime Result
        ↓
        Stage D Runtime Orchestration
        ↓
        [Stage E Layer 2 Regression] ← 当前测试

        测试隔离边界：
        本测试不重新实现 A～D 的业务断言，不测试 Maker Natural Language 或 Agent Understanding。
        Stage B 使用全部现有 Test Method；Stage D 使用全部 9 个现有 Test Method。
        Stage A / Stage C 若没有现成 Critical Case 标记，则纳入全部现有 Test Method。

        Semantic Input：
        已冻结的 Stage A、Stage B、Stage C、Stage D Acceptance Test Module。

        业务期望：
        Stage E 只承认真实前序 Acceptance Test 的执行结果。
        任何纳入回归集合的 FAIL / ERROR 都必须导致 L2-E01 失败。
        """
        suite = unittest.TestSuite()
        suite.addTest(self._load_regression_suite(STAGE_A_MODULE))
        suite.addTest(self._load_regression_suite(STAGE_B_MODULE))
        suite.addTest(self._load_regression_suite(STAGE_C_MODULE))
        suite.addTest(self._load_regression_suite(STAGE_D_MODULE))

        self.assertGreater(suite.countTestCases(), 0)
        self._run_regression_suite(suite)

    def test_l2_e02_clean_package_isolation(self):
        """
        Test Case:
        L2-E02

        测试目标：
        Project Incubator 发布包必须能够脱离 Implementation Repository 独立运行。
        这个测试防止 Runtime 在真实使用时意外依赖 SPECS、Acceptance Test、开发用 tests、根目录 AGENTS.md
        或其他开发仓库文件。否则 Maker 拿到的 Skill Package 看似完整，实际运行却需要开发环境兜底。

        真实运行场景：
        Runtime Package 准备交给真实 Managed Project 使用。
        ↓
        只复制 PROJECT_INCUBATOR/ 到一个全新隔离环境。
        ↓
        在隔离环境里创建独立 Managed Project Core Context。
        ↓
        通过隔离包中的 RuntimeCoordinator 执行真实 Runtime Request。
        ↓
        Runtime 必须能加载 Configuration / Reference / Contract Types，建立 Context，
        执行 Workflow，调用 Script，执行 Gate Flow，并形成 Runtime Result。

        System Layer：
        Runtime Package / Clean Package Isolation

        Runtime Flow Position：
        Isolated Package Load
        ↓
        Runtime Request
        ↓
        Definition Resolution
        ↓
        Context Establish / Restore
        ↓
        Script Evidence
        ↓
        Gate Evaluation
        ↓
        Workflow Evaluation
        ↓
        Context Mutation / PROJECT_STATE Commit
        ↓
        Runtime Result

        测试隔离边界：
        本测试假设 Agent 已经形成结构化 Runtime Request。
        本测试不复制 SPECS、ACCEPTANCE_TESTS、tests 或开发仓库根文件；不测试 Maker Natural Language。
        本测试直接构造一个 P3 → P4 的合法 Runtime Request，并由隔离包 RuntimeCoordinator 执行。

        Semantic Input：
        只包含 PROJECT_INCUBATOR/ 的隔离环境，以及一个拥有四个 Core Context 文件的 Temporary Managed Project。

        业务期望：
        Runtime 不需要 Implementation Repository 即可完成一次包含 Definition、Context、Workflow、Script、Gate
        和 Runtime Result 的确定性运行链路。
        """
        with self._isolated_environment() as (isolation_root, managed_project):
            self._assert_clean_package_copy(isolation_root)
            self.assertFalse((isolation_root / "SPECS").exists())

            payload = self._run_isolated_runtime(isolation_root, managed_project)

            self.assertEqual("COMPLETED", payload["runtime_state"])
            self.assertEqual("RUNTIME_COMPLETED", payload["runtime_reason"])
            self.assertEqual("P4", payload["current_phase"])
            self.assertEqual("READY_FOR_TRANSITION", payload["workflow_result"])
            self.assertEqual("REQUIREMENT_SATISFIED", payload["gate_result"])
            self.assertEqual(["GATE-GIT"], payload["gate_triggered_ids"])
            self.assertEqual(1, payload["script_result_count"])
            self.assertEqual(["COMPLETED"], payload["script_execution_status"])
            self.assertEqual(["REQUIREMENT_SATISFIED"], payload["script_validation_result"])
            self.assertGreaterEqual(payload["context_result_count"], 1)
            self.assertGreaterEqual(payload["completed_action_count"], 1)
            self.assertIn("Current Phase: P4", payload["project_state_content"])

            implementation_root = str(REPOSITORY_ROOT.resolve())
            isolated_root = str(isolation_root.resolve())
            for path_entry in payload["sys_path"]:
                if not path_entry:
                    continue
                resolved = str(Path(path_entry).resolve())
                self.assertFalse(
                    resolved.startswith(implementation_root)
                    and not resolved.startswith(isolated_root),
                    f"isolated Runtime sys.path reached development repository: {resolved}",
                )

    def test_l2_e03_no_development_repository_dependency(self):
        """
        Test Case:
        L2-E03

        测试目标：
        即使 Clean Package Isolation 能运行，也必须确认 Runtime 实际读取的 Project Incubator 依赖来自发布包自身
        或 Temporary Managed Project，而不是偷偷回读 Implementation Repository、SPECS、backup、zzztemp 或历史开发文件。
        这保护 Maker 未来使用的 Package 边界，避免“只有在开发仓库旁边才跑得起来”的隐性依赖。

        真实运行场景：
        Stage E 在隔离环境中执行真实 Runtime Request。
        ↓
        测试 Harness 记录 Runtime 运行期间可观察的文件读取路径。
        ↓
        只允许读取隔离包 PROJECT_INCUBATOR/runtime、references、templates、scripts，
        以及 Temporary Managed Project 的四个 Core Context 文件。
        ↓
        若读取来自 SPECS、backup、zzztemp、原 Implementation Repository Root 或历史开发文件，测试必须失败。

        System Layer：
        Runtime Package / Development Repository Dependency Boundary

        Runtime Flow Position：
        Isolated Runtime Execution
        ↓
        [Runtime Dependency Read Observation] ← 当前测试
        ↓
        Package Boundary Verification

        测试隔离边界：
        本测试使用 Python runtime audit hook 从测试外部观察文件读取，不新增 Product Interface，
        不修改 Product Runtime。它不把 Python 标准库、解释器、site-packages 等宿主环境读取误判为
        Project Incubator Development Repository Dependency。

        Semantic Input：
        与 L2-E02 相同的隔离 Runtime Request，并额外记录 Runtime 执行期间的项目相关读取路径。

        业务期望：
        Runtime 的项目依赖读取只来自隔离发布包或 Temporary Managed Project。
        Reference 中的 source_document 只能作为 traceability metadata，不得变成 Runtime Dependency。
        """
        with self._isolated_environment() as (isolation_root, managed_project):
            self._assert_clean_package_copy(isolation_root)
            payload = self._run_isolated_runtime(
                isolation_root,
                managed_project,
                audit_reads=True,
            )

            self.assertEqual("COMPLETED", payload["runtime_state"])
            implementation_root = REPOSITORY_ROOT.resolve()
            isolated_root = isolation_root.resolve()
            allowed_package_roots = tuple(
                (isolated_root / "PROJECT_INCUBATOR" / name).resolve()
                for name in ("runtime", "references", "templates", "scripts")
            )
            core_context_names = (
                "PROJECT_PROFILE.md",
                "PROJECT_STATE.md",
                "PROJECT_PLAN.md",
                "PROJECT_DECISIONS.md",
            )
            managed_project_root = managed_project.resolve()
            allowed_context_files = {
                (managed_project / name).resolve()
                for name in core_context_names
            }

            def is_allowed_managed_context_path(candidate: Path) -> bool:
                if candidate in allowed_context_files:
                    return True
                if candidate.parent != managed_project_root:
                    return False
                for context_name in core_context_names:
                    temp_prefix = f".{context_name}."
                    if candidate.name.startswith(temp_prefix) and candidate.name.endswith(".tmp"):
                        return len(candidate.name) > len(temp_prefix) + len(".tmp")
                return False

            forbidden_segments = {"SPECS", "backup", "zzztemp", "tests"}
            project_reads: list[Path] = []
            forbidden_reads: list[str] = []

            for raw_path in payload["read_paths"]:
                path = Path(raw_path).resolve()
                if not (
                    self._path_is_relative_to(path, isolated_root)
                    or self._path_is_relative_to(path, implementation_root)
                ):
                    continue
                if path.name.endswith(".pyc") or "__pycache__" in path.parts:
                    continue
                project_reads.append(path)

                allowed = any(
                    self._path_is_relative_to(path, root)
                    for root in allowed_package_roots
                ) or is_allowed_managed_context_path(path)
                under_development_repo_outside_isolation = (
                    self._path_is_relative_to(path, implementation_root)
                    and not self._path_is_relative_to(path, isolated_root)
                )
                contains_forbidden_segment = bool(forbidden_segments.intersection(path.parts))
                if not allowed or under_development_repo_outside_isolation or contains_forbidden_segment:
                    forbidden_reads.append(str(path))

            self.assertTrue(project_reads, "dependency read observation did not capture project paths")
            self.assertEqual([], forbidden_reads)


if __name__ == "__main__":
    unittest.main()
