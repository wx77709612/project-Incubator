"""Layer 2 Stage B Deterministic Capability Acceptance Tests.

本文件是 Maker-driven Runtime Acceptance Test Code。
它只验证 TASK-016 至 TASK-020 已实现的确定性能力，不修改 Product Runtime。
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


from PROJECT_INCUBATOR.runtime.adapters.script_runner import ScriptRunner
from PROJECT_INCUBATOR.runtime.components.script_coordinator import (
    EVIDENCE_READY,
    INVALID_SCRIPT_INPUT,
    SCRIPT_EXECUTION_ERROR,
    UNSUPPORTED_SCRIPT_INVOCATION,
    VALIDATION_NOT_COMPLETED,
    VALIDATION_UNSATISFIED,
    ScriptCoordinator,
    ScriptInvocationRequest,
)
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ScriptExecutionStatus,
    ScriptValidationResult,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState
from PROJECT_INCUBATOR.scripts.inspect_git_evidence import inspect_git_evidence
from PROJECT_INCUBATOR.scripts.validate_artifact_evidence import validate_artifact_evidence
from PROJECT_INCUBATOR.scripts.validate_context_integrity_evidence import (
    validate_context_integrity_evidence,
)
from PROJECT_INCUBATOR.scripts.validate_contract_payload import validate_contract_payload


ACCEPTANCE_TEMP_ROOT = (
    REPOSITORY_ROOT
    / "ACCEPTANCE_TESTS"
    / "layer2"
    / "stage_b"
    / ".tmp_deterministic_capability_acceptance"
)


class DeterministicCapabilityAcceptanceTest(unittest.TestCase):
    """Stage B 验证 TASK-016 至 TASK-020 的确定性 Script 能力。"""

    maxDiff = None

    @contextmanager
    def _temporary_workspace(self) -> Iterator[Path]:
        temp_root = ACCEPTANCE_TEMP_ROOT.resolve()
        workspace = (temp_root / f"run_{uuid.uuid4().hex}").resolve()
        if not str(workspace).startswith(str(temp_root)):
            raise RuntimeError("acceptance temp workspace escaped temp root")
        workspace.mkdir(parents=True, exist_ok=False)
        try:
            yield workspace
        finally:
            self._restore_permissions_for_cleanup(workspace)
            shutil.rmtree(workspace, ignore_errors=True)
            try:
                temp_root.rmdir()
            except OSError:
                pass

    def _restore_permissions_for_cleanup(self, root: Path) -> None:
        if not root.exists():
            return
        for path in root.rglob("*"):
            try:
                path.chmod(stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
        try:
            root.chmod(stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass

    def _run_git(self, repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(repository), *arguments],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )

    def _create_git_repository(self, workspace: Path) -> Path:
        repository = workspace / "git_fixture"
        repository.mkdir()
        init_result = self._run_git(repository, "init")
        self.assertEqual(0, init_result.returncode, init_result.stderr)
        self._run_git(repository, "config", "user.email", "stage-b@example.test")
        self._run_git(repository, "config", "user.name", "Stage B Acceptance")
        tracked_file = repository / "tracked.txt"
        tracked_file.write_text("initial\n", encoding="utf-8")
        self.assertEqual(0, self._run_git(repository, "add", "tracked.txt").returncode)
        commit = self._run_git(repository, "commit", "-m", "initial")
        self.assertEqual(0, commit.returncode, commit.stderr)
        return repository

    def _git_payload(self, invocation_id: str, repository_path: Path) -> dict[str, Any]:
        return {
            "invocation_id": invocation_id,
            "repository_path": str(repository_path),
            "requested_git_operation": "PUSH",
        }

    def _git_observed_fact(self, output: dict[str, Any]) -> dict[str, Any]:
        return output["evidence"][0]["observed_fact"]

    def _artifact_payload(
        self,
        invocation_id: str,
        artifact_path: Path,
        expected_requirement: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "invocation_id": invocation_id,
            "artifact_reference": {"artifact_id": invocation_id},
            "expected_requirement": expected_requirement
            or {
                "requirement_id": "Artifact Mechanical Requirement",
                "must_exist": True,
                "must_be_readable": True,
                "must_be_non_empty": True,
            },
            "artifact_path": str(artifact_path),
        }

    def _context_integrity_payload(
        self,
        invocation_id: str,
        context_derived_data: dict[str, Any],
        declared_context_identity: dict[str, str],
        required_structural_item: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        return {
            "invocation_id": invocation_id,
            "required_context_type_set": [
                "PROJECT_PROFILE",
                "PROJECT_STATE",
                "PROJECT_PLAN",
                "PROJECT_DECISIONS",
            ],
            "context_derived_data": context_derived_data,
            "declared_context_identity": declared_context_identity,
            "required_structural_item": required_structural_item
            or {
                "PROJECT_PROFILE": ["Project Name"],
                "PROJECT_STATE": ["Current Phase"],
                "PROJECT_PLAN": ["Plan Item"],
                "PROJECT_DECISIONS": ["Decision ID"],
            },
        }

    def _complete_context_data(self) -> dict[str, Any]:
        return {
            "PROJECT_PROFILE": {"structural_items": {"Project Name": True}},
            "PROJECT_STATE": {"structural_items": {"Current Phase": True}},
            "PROJECT_PLAN": {"structural_items": {"Plan Item": True}},
            "PROJECT_DECISIONS": {"structural_items": {"Decision ID": True}},
        }

    def _complete_context_identity(self) -> dict[str, str]:
        return {
            "PROJECT_PROFILE": "PROJECT_PROFILE",
            "PROJECT_STATE": "PROJECT_STATE",
            "PROJECT_PLAN": "PROJECT_PLAN",
            "PROJECT_DECISIONS": "PROJECT_DECISIONS",
        }

    def _contract_payload(self, **overrides: Any) -> dict[str, Any]:
        payload = {
            "invocation_id": "L2-B01-valid",
            "contract_type": "WORKFLOW",
            "input_data": {
                "workflow_result": "READY_FOR_TRANSITION",
                "request_id": "transition-request-1",
            },
            "required_field_set": ["workflow_result", "request_id"],
            "allowed_value_set": {},
            "required_type_set": {"request_id": "string"},
        }
        payload.update(overrides)
        return payload

    def _write_result_script(
        self,
        script_root: Path,
        script_name: str,
        output: dict[str, Any] | None = None,
        *,
        exit_code: int = 0,
        count_file: Path | None = None,
    ) -> None:
        script_path = script_root / script_name
        count_line = ""
        if count_file is not None:
            count_text = str(count_file).replace("\\", "\\\\")
            count_line = (
                f"from pathlib import Path\n"
                f"count_path = Path(r'{count_text}')\n"
                f"previous = int(count_path.read_text(encoding='utf-8')) if count_path.exists() else 0\n"
                f"count_path.write_text(str(previous + 1), encoding='utf-8')\n"
            )
        if exit_code:
            script_path.write_text(
                "import sys\n"
                f"{count_line}"
                f"sys.exit({exit_code})\n",
                encoding="utf-8",
            )
            return
        output_json = json.dumps(output or {}, ensure_ascii=False)
        script_path.write_text(
            f"{count_line}"
            f"print({output_json!r})\n",
            encoding="utf-8",
        )

    def _script_output(
        self,
        invocation_id: str,
        script_identity: str,
        execution_status: str,
        validation_result: str | None,
        *,
        evidence: list[dict[str, Any]] | None = None,
        error_information: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "invocation_id": invocation_id,
            "script_identity": script_identity,
            "execution_status": execution_status,
            "validation_result": validation_result,
            "evidence": evidence or [],
            "diagnostic_information": [],
            "error_information": error_information,
        }

    def _write_input_capture_script(self, script_root: Path, script_name: str) -> None:
        script_path = script_root / script_name
        script_path.write_text(
            "import json\n"
            "import sys\n"
            "received = json.loads(sys.stdin.read() or '{}')\n"
            "output = {\n"
            "    'invocation_id': received.get('invocation_id'),\n"
            "    'script_identity': received.get('script_identity'),\n"
            "    'execution_status': 'COMPLETED',\n"
            "    'validation_result': None,\n"
            "    'evidence': [\n"
            "        {\n"
            "            'requirement_id': 'Script Input Preparation',\n"
            "            'validation_target': 'Script Input',\n"
            "            'observed_fact': {'received_input': received},\n"
            "            'expected_condition': {'input_prepared_by_runtime': True},\n"
            "            'comparison_result': 'MATCHED',\n"
            "            'evidence_reference': received.get('script_identity'),\n"
            "        },\n"
            "    ],\n"
            "    'diagnostic_information': [],\n"
            "    'error_information': None,\n"
            "}\n"
            "print(json.dumps(output, ensure_ascii=False))\n",
            encoding="utf-8",
        )

    def test_l2_b01_contract_payload_validator(self):
        """
        Test Case:
        L2-B01

        测试目标：
        Project Incubator 的 Runtime、Workflow、Gate、Script 之间会交换结构化 Payload。
        Agent 可以理解 Maker 意图，但 Required Field 是否存在、Enum 是否属于允许集合、
        基础数据类型是否正确、Required Value 是否为空，都是机械事实。
        这些事实不能靠 Agent 觉得“差不多可以”，必须由确定性 Validator 检查。
        如果该能力失效，Runtime 可能把坏 Payload 交给后续 Component，
        造成状态语言混乱、错误 Gate 依据或错误 Runtime 结果。

        真实运行场景：
        Runtime 已经形成结构化 Payload。
        ↓
        需要确认 Payload 是否满足 Contract 的机械要求。
        ↓
        validate_contract_payload.py 执行确定性检查。
        ↓
        返回 Execution Status、Validation Result、Evidence / Diagnostic。
        ↓
        Runtime 决定后续是否允许 Component 消费该 Payload。

        System Layer：
        Deterministic Capability / Script

        Runtime Flow Position：
        Runtime 已形成 Contract Payload
        ↓
        [Contract Payload Validation] ← 当前测试
        ↓
        允许后续 Runtime Component 消费

        测试隔离边界：
        本测试假设 Agent 已经正确理解 Maker 意图，Runtime 已经准备好结构化 Payload。
        本测试直接构造 Payload 输入，不验证 Maker Natural Language、Agent Reasoning、
        Gate Risk、Project Scope 或 Workflow Domain Semantics。

        Semantic Input：
        合法 Payload、缺失 Invocation ID、错误 Gate/Workflow/Script Enum、
        空 Required Value、错误基础类型、Unsupported Contract Type、无法形成 Contract Input 的 Payload。

        业务期望：
        合法 Payload 返回 COMPLETED + REQUIREMENT_SATISFIED。
        Contract Requirement 不满足返回 COMPLETED + REQUIREMENT_UNSATISFIED。
        输入无法解析为合法 Validator Input 返回 INVALID_INPUT。
        Unsupported Contract Type 返回 UNSUPPORTED_INVOCATION。
        Validation Failure 不得被误判为 Execution Error。
        """
        valid = validate_contract_payload(self._contract_payload())
        self.assertEqual(ScriptExecutionStatus.COMPLETED.value, valid["execution_status"])
        self.assertEqual(ScriptValidationResult.REQUIREMENT_SATISFIED.value, valid["validation_result"])
        self.assertTrue(valid["evidence"])

        scenarios = (
            (
                "Missing Invocation ID",
                self._contract_payload(invocation_id=""),
                ScriptExecutionStatus.INVALID_INPUT.value,
                ScriptValidationResult.VALIDATION_NOT_COMPLETED.value,
            ),
            (
                "Invalid Gate Result Enum",
                self._contract_payload(
                    invocation_id="L2-B01-invalid-gate",
                    contract_type="GATE",
                    input_data={"gate_result": "NOT_A_GATE_RESULT"},
                    required_field_set=["gate_result"],
                    required_type_set={},
                ),
                ScriptExecutionStatus.COMPLETED.value,
                ScriptValidationResult.REQUIREMENT_UNSATISFIED.value,
            ),
            (
                "Invalid Workflow Result Enum",
                self._contract_payload(
                    invocation_id="L2-B01-invalid-workflow",
                    input_data={"workflow_result": "MAYBE_READY", "request_id": "req"},
                ),
                ScriptExecutionStatus.COMPLETED.value,
                ScriptValidationResult.REQUIREMENT_UNSATISFIED.value,
            ),
            (
                "Invalid Script Status Enum",
                self._contract_payload(
                    invocation_id="L2-B01-invalid-script-status",
                    contract_type="SCRIPT",
                    input_data={"execution_status": "HALF_DONE"},
                    required_field_set=["execution_status"],
                    required_type_set={},
                ),
                ScriptExecutionStatus.COMPLETED.value,
                ScriptValidationResult.REQUIREMENT_UNSATISFIED.value,
            ),
            (
                "Empty Required Value",
                self._contract_payload(
                    invocation_id="L2-B01-empty-required",
                    input_data={"workflow_result": "", "request_id": "req"},
                ),
                ScriptExecutionStatus.COMPLETED.value,
                ScriptValidationResult.REQUIREMENT_UNSATISFIED.value,
            ),
            (
                "Invalid Basic Data Type",
                self._contract_payload(
                    invocation_id="L2-B01-invalid-type",
                    input_data={"workflow_result": "READY_FOR_TRANSITION", "request_id": 123},
                ),
                ScriptExecutionStatus.COMPLETED.value,
                ScriptValidationResult.REQUIREMENT_UNSATISFIED.value,
            ),
            (
                "Unsupported Contract Type",
                self._contract_payload(
                    invocation_id="L2-B01-unsupported",
                    contract_type="UNKNOWN_CONTRACT",
                ),
                ScriptExecutionStatus.UNSUPPORTED_INVOCATION.value,
                ScriptValidationResult.VALIDATION_NOT_COMPLETED.value,
            ),
            (
                "Invalid Input",
                self._contract_payload(
                    invocation_id="L2-B01-invalid-input",
                    input_data="not an object",
                ),
                ScriptExecutionStatus.INVALID_INPUT.value,
                ScriptValidationResult.VALIDATION_NOT_COMPLETED.value,
            ),
        )

        for label, payload, expected_status, expected_validation in scenarios:
            with self.subTest(scenario=label):
                output = validate_contract_payload(payload)
                self.assertEqual(expected_status, output["execution_status"])
                self.assertEqual(expected_validation, output["validation_result"])
                if expected_validation == ScriptValidationResult.REQUIREMENT_UNSATISFIED.value:
                    self.assertNotEqual(ScriptExecutionStatus.EXECUTION_ERROR.value, output["execution_status"])
                    self.assertTrue(output["evidence"])
                    self.assertTrue(output["diagnostic_information"])

    def test_l2_b02_git_evidence_script(self):
        """
        Test Case:
        L2-B02

        测试目标：
        Project Incubator 的 GATE-GIT 未来需要判断受保护 Git 行为。
        在 Gate 判断之前，Runtime 必须先知道当前 Branch、Working Tree 是否有变化、
        是否存在 Untracked File、是否存在 Staged Change 等客观机械事实。
        这些事实不能由 Agent 根据聊天记录猜测，必须由 inspect_git_evidence.py 读取真实 Git Repository。
        该 Script 只收集 Evidence，不批准 push、merge 或 delete branch。

        真实运行场景：
        Runtime / Gate Flow 发现需要 Git Evidence。
        ↓
        Runtime 提供 Repository Path 和 Requested Git Operation。
        ↓
        Script Runtime 调用 inspect_git_evidence.py。
        ↓
        Script 读取真实 Git Repository 状态并返回 Git Evidence。
        ↓
        后续 Gate 使用 Evidence；Stage B 不执行完整 Gate Evaluation。

        System Layer：
        Deterministic Capability / Script Evidence

        Runtime Flow Position：
        Gate Requirement Detected
        ↓
        Collect Evidence
        ↓
        [Git Evidence Script] ← 当前测试
        ↓
        Validation Evidence
        ↓
        后续 Gate Evaluation

        测试隔离边界：
        本测试假设 Agent 已经正确理解 Maker 的 Git 相关意图，Runtime 已经准备好 Repository Path。
        本测试只在 Temporary Git Repository 中制造状态，不修改当前 Implementation Repository 的 branch、
        staging area 或 working tree。本测试不判断 Git Operation 是否允许。

        Semantic Input：
        Clean Repository、Modified Tracked File、Untracked File、Staged Change、
        Non-Git Directory / Invalid Repository Path。

        业务期望：
        合法 Git Repository 返回真实 Current Branch、Working Tree Change Presence、
        Untracked Change Presence、Staged Change Presence、Target Operation Reference 和 Git Evidence。
        非 Git 目录不得伪造 Evidence，应返回当前 Script Contract 中的执行错误形态。
        """
        with self._temporary_workspace() as workspace:
            repository = self._create_git_repository(workspace)

            clean = inspect_git_evidence(self._git_payload("L2-B02-clean", repository))
            clean_fact = self._git_observed_fact(clean)
            self.assertEqual(ScriptExecutionStatus.COMPLETED.value, clean["execution_status"])
            self.assertEqual(ScriptValidationResult.REQUIREMENT_SATISFIED.value, clean["validation_result"])
            self.assertTrue(clean_fact["current_branch"])
            self.assertFalse(clean_fact["working_tree_change_presence"])
            self.assertFalse(clean_fact["untracked_change_presence"])
            self.assertFalse(clean_fact["staged_change_presence"])
            self.assertEqual("PUSH", clean_fact["target_operation_reference"])

            (repository / "tracked.txt").write_text("modified\n", encoding="utf-8")
            modified = inspect_git_evidence(self._git_payload("L2-B02-modified", repository))
            modified_fact = self._git_observed_fact(modified)
            self.assertTrue(modified_fact["working_tree_change_presence"])
            self.assertFalse(modified_fact["staged_change_presence"])

            self._run_git(repository, "checkout", "--", "tracked.txt")
            (repository / "untracked.txt").write_text("untracked\n", encoding="utf-8")
            untracked = inspect_git_evidence(self._git_payload("L2-B02-untracked", repository))
            untracked_fact = self._git_observed_fact(untracked)
            self.assertTrue(untracked_fact["untracked_change_presence"])

            self.assertEqual(0, self._run_git(repository, "add", "untracked.txt").returncode)
            staged = inspect_git_evidence(self._git_payload("L2-B02-staged", repository))
            staged_fact = self._git_observed_fact(staged)
            self.assertTrue(staged_fact["staged_change_presence"])

            non_git = workspace / "not_git"
            non_git.mkdir()
            invalid = inspect_git_evidence(self._git_payload("L2-B02-non-git", non_git))
            self.assertEqual(ScriptExecutionStatus.EXECUTION_ERROR.value, invalid["execution_status"])
            self.assertEqual(ScriptValidationResult.VALIDATION_NOT_COMPLETED.value, invalid["validation_result"])
            self.assertEqual([], invalid["evidence"])

    def test_l2_b03_artifact_evidence_script(self):
        """
        Test Case:
        L2-B03

        测试目标：
        Project Incubator 的 Workflow / Gate 会依赖 Artifact。
        Runtime 有时只需要知道 Artifact 是否存在、是否可访问、是否为空、
        是否满足明确声明的机械 Requirement。这些事实可以确定性验证。
        但 Artifact 是否优秀、是否有创意、是否真正解决用户需求，不是 Script 的职责。
        如果该能力失效，Runtime 可能把不存在或空 Artifact 当作可用 Evidence。

        真实运行场景：
        Workflow / Gate 需要 Artifact Evidence。
        ↓
        Runtime 准备 Artifact Reference、Expected Requirement、Artifact Path。
        ↓
        Script Runtime 调用 validate_artifact_evidence.py。
        ↓
        Script 产生机械 Evidence。
        ↓
        Workflow / Gate 后续消费 Evidence。

        System Layer：
        Deterministic Capability / Artifact Evidence

        Runtime Flow Position：
        Workflow / Gate Requirement Detected
        ↓
        Collect Artifact Evidence
        ↓
        [Artifact Evidence Script] ← 当前测试
        ↓
        Validation Evidence
        ↓
        后续 Workflow / Gate

        测试隔离边界：
        本测试假设 Agent 已经正确理解 Artifact 相关意图，Runtime 已经准备好 Artifact Reference。
        本测试只在 Temporary Directory 中创建 Artifact Fixture，不读取或修改正式 Artifact。
        本测试不评价 Artifact 语义质量。

        Semantic Input：
        File Missing、Empty Artifact、Existing Non-empty Artifact、Unreadable Artifact。
        在当前实现中，Unreadable Artifact 使用“路径存在但不是可读文件”的目录 Fixture 表达，
        以验证 artifact_readable=False 的机械事实。

        业务期望：
        Script 能区分 Requirement Satisfied、Requirement Unsatisfied、Invalid Input、
        Execution / Access Failure，并在 Evidence 中返回 artifact_exists、artifact_readable、
        artifact_non_empty 和 declared_artifact_identity 等机械事实。
        """
        with self._temporary_workspace() as workspace:
            missing_path = workspace / "missing.md"
            missing = validate_artifact_evidence(
                self._artifact_payload("L2-B03-missing", missing_path),
            )
            missing_fact = missing["evidence"][0]["observed_fact"]
            self.assertEqual(ScriptExecutionStatus.COMPLETED.value, missing["execution_status"])
            self.assertEqual(ScriptValidationResult.REQUIREMENT_UNSATISFIED.value, missing["validation_result"])
            self.assertFalse(missing_fact["artifact_exists"])

            empty_path = workspace / "empty.md"
            empty_path.write_text("", encoding="utf-8")
            empty = validate_artifact_evidence(self._artifact_payload("L2-B03-empty", empty_path))
            empty_fact = empty["evidence"][0]["observed_fact"]
            self.assertEqual(ScriptValidationResult.REQUIREMENT_UNSATISFIED.value, empty["validation_result"])
            self.assertTrue(empty_fact["artifact_exists"])
            self.assertTrue(empty_fact["artifact_readable"])
            self.assertFalse(empty_fact["artifact_non_empty"])

            artifact_path = workspace / "artifact.md"
            artifact_path.write_text("# Artifact\n\nDeterministic content.\n", encoding="utf-8")
            artifact = validate_artifact_evidence(
                self._artifact_payload("L2-B03-non-empty", artifact_path),
            )
            artifact_fact = artifact["evidence"][0]["observed_fact"]
            self.assertEqual(ScriptValidationResult.REQUIREMENT_SATISFIED.value, artifact["validation_result"])
            self.assertTrue(artifact_fact["artifact_exists"])
            self.assertTrue(artifact_fact["artifact_readable"])
            self.assertTrue(artifact_fact["artifact_non_empty"])
            self.assertEqual("L2-B03-non-empty", artifact_fact["declared_artifact_identity"])

            unreadable_path = workspace / "artifact_directory"
            unreadable_path.mkdir()
            unreadable = validate_artifact_evidence(
                self._artifact_payload("L2-B03-unreadable", unreadable_path),
            )
            unreadable_fact = unreadable["evidence"][0]["observed_fact"]
            self.assertEqual(ScriptValidationResult.REQUIREMENT_UNSATISFIED.value, unreadable["validation_result"])
            self.assertTrue(unreadable_fact["artifact_exists"])
            self.assertFalse(unreadable_fact["artifact_readable"])

            invalid = validate_artifact_evidence(
                {"invocation_id": "L2-B03-invalid", "artifact_path": str(artifact_path)},
            )
            self.assertEqual(ScriptExecutionStatus.INVALID_INPUT.value, invalid["execution_status"])
            self.assertEqual(ScriptValidationResult.VALIDATION_NOT_COMPLETED.value, invalid["validation_result"])

    def test_l2_b04_context_integrity_evidence_script(self):
        """
        Test Case:
        L2-B04

        测试目标：
        Context 是 Project Incubator Runtime 判断项目当前真实状态的重要依据。
        但是 Script 没有 Core Context Direct Read Authority。
        正确流程必须是 Runtime / Context Coordinator 已经合法读取 Context，
        再把有限的 Context-derived Data 交给 Script 做机械完整性检查。
        如果该能力失效，Runtime 可能无法可靠发现缺失 Context、身份冲突或结构项缺失。

        真实运行场景：
        Runtime 已获得合法 Context 数据。
        ↓
        Runtime 形成 Required Context Type Set、Context-derived Data、
        Declared Context Identity 和 Required Structural Item。
        ↓
        validate_context_integrity_evidence.py 做机械检查。
        ↓
        返回 Validation Result + Evidence。
        ↓
        后续 GATE-CONTEXT-INTEGRITY 使用 Evidence。

        System Layer：
        Deterministic Capability / Context Integrity Evidence

        Runtime Flow Position：
        Context Establish / Restore
        ↓
        Collect Context Integrity Evidence
        ↓
        [Context Integrity Evidence Script] ← 当前测试
        ↓
        Validation Evidence
        ↓
        后续 GATE-CONTEXT-INTEGRITY

        测试隔离边界：
        本测试假设 Agent 已经正确理解 Maker 请求，Runtime 已通过合法 Context 权限读取 Context。
        本测试直接构造 Context-derived Data，不让 Script 直接打开 PROJECT_STATE.md。
        本测试不执行 Context Coordinator、Gate Coordinator 或完整 Gate Evaluation。

        Semantic Input：
        All Core Context Present、Missing PROJECT_STATE、Context Identity Mismatch、
        Required Structural Item Missing、Insufficient Input。

        业务期望：
        Script 返回 Required Context Presence、Missing Context、
        Required Structural Item Presence、Identity Conflict Evidence 和 Validation Result。
        输入不足以形成确定性判断时返回 VALIDATION_NOT_COMPLETED，不得猜测。
        """
        complete_payload = self._context_integrity_payload(
            "L2-B04-all-present",
            self._complete_context_data(),
            self._complete_context_identity(),
        )
        self.assertNotIn("PROJECT_STATE.md", json.dumps(complete_payload, ensure_ascii=False))

        complete = validate_context_integrity_evidence(complete_payload)
        complete_fact = complete["evidence"][0]["observed_fact"]
        self.assertEqual(ScriptExecutionStatus.COMPLETED.value, complete["execution_status"])
        self.assertEqual(ScriptValidationResult.REQUIREMENT_SATISFIED.value, complete["validation_result"])
        self.assertEqual([], complete_fact["missing_context"])
        self.assertEqual([], complete_fact["identity_conflict_evidence"])
        for context_type in ("PROJECT_PROFILE", "PROJECT_STATE", "PROJECT_PLAN", "PROJECT_DECISIONS"):
            self.assertIs(complete_fact["required_context_presence"][context_type], True)
        self.assertIs(
            complete_fact["required_structural_item_presence"]["PROJECT_PROFILE"]["Project Name"],
            True,
        )
        self.assertIs(
            complete_fact["required_structural_item_presence"]["PROJECT_STATE"]["Current Phase"],
            True,
        )
        self.assertIs(
            complete_fact["required_structural_item_presence"]["PROJECT_PLAN"]["Plan Item"],
            True,
        )
        self.assertIs(
            complete_fact["required_structural_item_presence"]["PROJECT_DECISIONS"]["Decision ID"],
            True,
        )

        missing_data = self._complete_context_data()
        missing_data.pop("PROJECT_STATE")
        missing = validate_context_integrity_evidence(
            self._context_integrity_payload(
                "L2-B04-missing-state",
                missing_data,
                self._complete_context_identity(),
            ),
        )
        missing_fact = missing["evidence"][0]["observed_fact"]
        self.assertEqual(ScriptValidationResult.REQUIREMENT_UNSATISFIED.value, missing["validation_result"])
        self.assertIn("PROJECT_STATE", missing_fact["missing_context"])

        mismatch_identity = self._complete_context_identity()
        mismatch_identity["PROJECT_STATE"] = "PROJECT_PLAN"
        mismatch = validate_context_integrity_evidence(
            self._context_integrity_payload(
                "L2-B04-identity-mismatch",
                self._complete_context_data(),
                mismatch_identity,
            ),
        )
        mismatch_fact = mismatch["evidence"][0]["observed_fact"]
        self.assertEqual(ScriptValidationResult.REQUIREMENT_UNSATISFIED.value, mismatch["validation_result"])
        self.assertTrue(mismatch_fact["identity_conflict_evidence"])

        missing_item_data = self._complete_context_data()
        missing_item_data["PROJECT_STATE"] = {"structural_items": {}}
        missing_item = validate_context_integrity_evidence(
            self._context_integrity_payload(
                "L2-B04-missing-item",
                missing_item_data,
                self._complete_context_identity(),
            ),
        )
        missing_item_fact = missing_item["evidence"][0]["observed_fact"]
        self.assertEqual(ScriptValidationResult.REQUIREMENT_UNSATISFIED.value, missing_item["validation_result"])
        self.assertFalse(
            missing_item_fact["required_structural_item_presence"]["PROJECT_STATE"]["Current Phase"],
        )

        insufficient_identity = self._complete_context_identity()
        insufficient_identity.pop("PROJECT_STATE")
        insufficient = validate_context_integrity_evidence(
            self._context_integrity_payload(
                "L2-B04-insufficient",
                self._complete_context_data(),
                insufficient_identity,
            ),
        )
        self.assertEqual(ScriptExecutionStatus.COMPLETED.value, insufficient["execution_status"])
        self.assertEqual(
            ScriptValidationResult.VALIDATION_NOT_COMPLETED.value,
            insufficient["validation_result"],
        )
        self.assertEqual([], insufficient["evidence"])

    def test_l2_b05_script_runner_and_coordinator_mapping(self):
        """
        Test Case:
        L2-B05

        测试目标：
        B01-B04 验证每个确定性 Script 本身能否正确工作。
        L2-B05 验证 Runtime 是否能通过统一 Script Runtime 正确调用 Script，
        并正确理解 Script Result。真实 Product Flow 不应是 Agent 直接执行 Python Script，
        而应由 Runtime 通过 Script Coordinator、Script Runner、具体 Script、Script Output、
        再回到 Script Coordinator 形成 Evidence / Runtime Reason。

        真实运行场景：
        Workflow / Gate 发现需要确定性 Evidence。
        ↓
        Runtime 形成 ScriptInvocationRequest。
        ↓
        ScriptCoordinator 准备 Script Input。
        ↓
        ScriptRunner 执行具体 Script。
        ↓
        Script Output 回到 ScriptCoordinator。
        ↓
        Coordinator 映射 Runtime State / Runtime Reason，供后续 Workflow / Gate / Runtime 使用。

        System Layer：
        Script Runtime / Deterministic Capability Coordination

        Runtime Flow Position：
        Workflow / Gate 发现需要确定性 Evidence
        ↓
        [Script Coordinator]
        ↓
        [Script Runner]
        ↓
        [Deterministic Script]
        ↓
        [Script Result Handling] ← 当前测试
        ↓
        后续 Workflow / Gate / Runtime

        测试隔离边界：
        本测试假设 Agent 已经正确理解 Maker 请求，Runtime 已经知道需要哪个 Script。
        本测试通过真实 ScriptCoordinator + ScriptRunner 调用，不用直接 import 四个 Product Script
        的结果代替 Runtime 调用链。本测试不执行完整 Gate Evaluation、Maker Authorization Flow、
        Workflow Transition Commit 或 Runtime Coordinator。

        Semantic Input：
        COMPLETED + REQUIREMENT_SATISFIED、
        COMPLETED + REQUIREMENT_UNSATISFIED、
        COMPLETED + VALIDATION_NOT_COMPLETED、
        INVALID_INPUT、
        UNSUPPORTED_INVOCATION、
        EXECUTION_ERROR、
        DETERMINISTIC_OPERATION Invocation、
        Pure DETERMINISTIC_OPERATION Without Validation Result、
        Script Input Preparation / Capture、
        Script Output Parsing Failure。
        同时验证默认不 Automatic Retry，并用 Temporary Context Sentinel 证明 Stage B 范围内的
        Validation 调用不会直接修改 Core Context 文件。

        业务期望：
        Satisfied Script Output 映射为 EVIDENCE_READY。
        Unsatisfied Validation 映射为 VALIDATION_UNSATISFIED。
        Validation Not Completed 映射为 SUSPENDED + VALIDATION_NOT_COMPLETED。
        Invalid Input 映射为 INVALID_SCRIPT_INPUT。
        Unsupported Invocation 映射为 UNSUPPORTED_SCRIPT_INVOCATION。
        Execution Error 映射为 SCRIPT_EXECUTION_ERROR，且不被误判为 Validation Unsatisfied。
        DETERMINISTIC_OPERATION 使用同一受控 Script Runtime 调用链返回符合 Contract 的结果。
        Pure DETERMINISTIC_OPERATION 允许：
        Execution Status = COMPLETED
        Script Output Validation Result = None
        本测试验证该 Contract-valid Output 可以经过 Script Runtime，
        且 Runtime 不伪造 REQUIREMENT_SATISFIED。
        当前冻结 Runtime Specification 未明确规定：
        COMPLETED + Validation Result = None
        对应的 Runtime State / Runtime Reason。
        因此实际 Runtime Mapping 只作为 Observed Implementation Behavior，
        不作为本测试的 Frozen Expected Behavior。
        Script Input Preparation 必须显式传入 Contract Input 字段。
        Malformed Script Output 不得被当成 Evidence 或合法 COMPLETED Result。
        """
        default_coordinator = ScriptCoordinator()
        satisfied_request = ScriptInvocationRequest(
            invocation_id="L2-B05-satisfied",
            script_identity="VALIDATE_CONTRACT_PAYLOAD",
            invocation_purpose="VALIDATION",
            input_data=self._contract_payload(invocation_id="L2-B05-satisfied"),
        )
        satisfied = default_coordinator.invoke(satisfied_request)
        self.assertIs(satisfied.runtime_state, RuntimeExecutionState.COMPLETED)
        self.assertEqual(EVIDENCE_READY, satisfied.result_reason)
        self.assertIs(satisfied.execution_status, ScriptExecutionStatus.COMPLETED)
        self.assertIs(satisfied.validation_result, ScriptValidationResult.REQUIREMENT_SATISFIED)
        self.assertTrue(satisfied.evidence)

        unsatisfied_request = ScriptInvocationRequest(
            invocation_id="L2-B05-unsatisfied",
            script_identity="VALIDATE_CONTRACT_PAYLOAD",
            invocation_purpose="VALIDATION",
            input_data=self._contract_payload(
                invocation_id="L2-B05-unsatisfied",
                input_data={"workflow_result": "WRONG", "request_id": "req"},
            ),
        )
        unsatisfied = default_coordinator.invoke(unsatisfied_request)
        self.assertIs(unsatisfied.runtime_state, RuntimeExecutionState.SUSPENDED)
        self.assertEqual(VALIDATION_UNSATISFIED, unsatisfied.result_reason)
        self.assertIs(unsatisfied.execution_status, ScriptExecutionStatus.COMPLETED)
        self.assertIs(unsatisfied.validation_result, ScriptValidationResult.REQUIREMENT_UNSATISFIED)

        invalid_request = ScriptInvocationRequest(
            invocation_id="L2-B05-invalid",
            script_identity="VALIDATE_CONTRACT_PAYLOAD",
            invocation_purpose="VALIDATION",
            input_data={"contract_type": "WORKFLOW", "input_data": "not an object"},
        )
        invalid = default_coordinator.invoke(invalid_request)
        self.assertIs(invalid.runtime_state, RuntimeExecutionState.SUSPENDED)
        self.assertEqual(INVALID_SCRIPT_INPUT, invalid.result_reason)
        self.assertIs(invalid.execution_status, ScriptExecutionStatus.INVALID_INPUT)

        unsupported_request = ScriptInvocationRequest(
            invocation_id="L2-B05-unsupported",
            script_identity="SCRIPT_THAT_DOES_NOT_EXIST",
            invocation_purpose="VALIDATION",
        )
        unsupported = default_coordinator.invoke(unsupported_request)
        self.assertIs(unsupported.runtime_state, RuntimeExecutionState.SUSPENDED)
        self.assertEqual(UNSUPPORTED_SCRIPT_INVOCATION, unsupported.result_reason)

        with self._temporary_workspace() as workspace:
            script_root = workspace / "scripts"
            script_root.mkdir()
            count_file = workspace / "execution_count.txt"
            self._write_result_script(
                script_root,
                "execution_error.py",
                exit_code=3,
                count_file=count_file,
            )
            runner = ScriptRunner(
                script_root=script_root,
                script_registry={"EXECUTION_ERROR_FIXTURE": "execution_error.py"},
            )
            coordinator = ScriptCoordinator(runner)
            execution_error_request = ScriptInvocationRequest(
                invocation_id="L2-B05-execution-error",
                script_identity="EXECUTION_ERROR_FIXTURE",
                invocation_purpose="VALIDATION",
            )
            execution_error = coordinator.invoke(execution_error_request)
            self.assertIs(execution_error.runtime_state, RuntimeExecutionState.FAILED)
            self.assertEqual(SCRIPT_EXECUTION_ERROR, execution_error.result_reason)
            self.assertIsNone(execution_error.execution_status)
            self.assertEqual("1", count_file.read_text(encoding="utf-8"))

        with self._temporary_workspace() as workspace:
            script_root = workspace / "scripts"
            script_root.mkdir()
            self._write_result_script(
                script_root,
                "validation_not_completed.py",
                self._script_output(
                    "L2-B05-validation-not-completed",
                    "VALIDATION_NOT_COMPLETED_FIXTURE",
                    ScriptExecutionStatus.COMPLETED.value,
                    ScriptValidationResult.VALIDATION_NOT_COMPLETED.value,
                ),
            )
            runner = ScriptRunner(
                script_root=script_root,
                script_registry={"VALIDATION_NOT_COMPLETED_FIXTURE": "validation_not_completed.py"},
            )
            coordinator = ScriptCoordinator(runner)
            not_completed_request = ScriptInvocationRequest(
                invocation_id="L2-B05-validation-not-completed",
                script_identity="VALIDATION_NOT_COMPLETED_FIXTURE",
                invocation_purpose="VALIDATION",
            )
            not_completed = coordinator.invoke(not_completed_request)
            self.assertIs(not_completed.runtime_state, RuntimeExecutionState.SUSPENDED)
            self.assertEqual(VALIDATION_NOT_COMPLETED, not_completed.result_reason)
            self.assertIs(not_completed.execution_status, ScriptExecutionStatus.COMPLETED)
            self.assertIs(not_completed.validation_result, ScriptValidationResult.VALIDATION_NOT_COMPLETED)
            self.assertNotEqual(EVIDENCE_READY, not_completed.result_reason)
            self.assertNotEqual(VALIDATION_UNSATISFIED, not_completed.result_reason)
            self.assertNotEqual(SCRIPT_EXECUTION_ERROR, not_completed.result_reason)

        with self._temporary_workspace() as workspace:
            script_root = workspace / "scripts"
            script_root.mkdir()
            self._write_result_script(
                script_root,
                "deterministic_operation.py",
                self._script_output(
                    "L2-B05-deterministic-operation",
                    "DETERMINISTIC_OPERATION_FIXTURE",
                    ScriptExecutionStatus.COMPLETED.value,
                    ScriptValidationResult.REQUIREMENT_SATISFIED.value,
                    evidence=[
                        {
                            "requirement_id": "Deterministic Operation",
                            "validation_target": "Temporary Script Fixture",
                            "observed_fact": {"operation_completed": True},
                            "expected_condition": {"operation_completed": True},
                            "comparison_result": "MATCHED",
                            "evidence_reference": "TEMPORARY_DETERMINISTIC_OPERATION_FIXTURE",
                        },
                    ],
                ),
            )
            runner = ScriptRunner(
                script_root=script_root,
                script_registry={"DETERMINISTIC_OPERATION_FIXTURE": "deterministic_operation.py"},
            )
            coordinator = ScriptCoordinator(runner)
            operation_request = ScriptInvocationRequest(
                invocation_id="L2-B05-deterministic-operation",
                script_identity="DETERMINISTIC_OPERATION_FIXTURE",
                invocation_purpose="DETERMINISTIC_OPERATION",
            )
            operation = coordinator.invoke(operation_request)
            self.assertIs(operation.runtime_state, RuntimeExecutionState.COMPLETED)
            self.assertEqual(EVIDENCE_READY, operation.result_reason)
            self.assertIs(operation.execution_status, ScriptExecutionStatus.COMPLETED)
            self.assertIs(operation.validation_result, ScriptValidationResult.REQUIREMENT_SATISFIED)
            self.assertEqual("Deterministic Operation", operation.evidence[0]["requirement_id"])
            self.assertEqual("L2-B05-deterministic-operation", operation.script_output["invocation_id"])
            self.assertEqual("DETERMINISTIC_OPERATION_FIXTURE", operation.script_output["script_identity"])

        with self._temporary_workspace() as workspace:
            script_root = workspace / "scripts"
            script_root.mkdir()
            self._write_result_script(
                script_root,
                "pure_deterministic_operation.py",
                self._script_output(
                    "L2-B05-pure-deterministic-operation",
                    "PURE_DETERMINISTIC_OPERATION_FIXTURE",
                    ScriptExecutionStatus.COMPLETED.value,
                    None,
                    evidence=[
                        {
                            "requirement_id": "Pure Deterministic Operation",
                            "validation_target": "Temporary Script Fixture",
                            "observed_fact": {"operation_completed": True},
                            "expected_condition": {"validation_requirement": None},
                            "comparison_result": "NOT_APPLICABLE",
                            "evidence_reference": "PURE_DETERMINISTIC_OPERATION_FIXTURE",
                        },
                    ],
                ),
            )
            runner = ScriptRunner(
                script_root=script_root,
                script_registry={"PURE_DETERMINISTIC_OPERATION_FIXTURE": "pure_deterministic_operation.py"},
            )
            coordinator = ScriptCoordinator(runner)
            pure_operation_request = ScriptInvocationRequest(
                invocation_id="L2-B05-pure-deterministic-operation",
                script_identity="PURE_DETERMINISTIC_OPERATION_FIXTURE",
                invocation_purpose="DETERMINISTIC_OPERATION",
            )
            pure_operation = coordinator.invoke(pure_operation_request)
            self.assertIs(pure_operation.execution_status, ScriptExecutionStatus.COMPLETED)
            self.assertIsNone(pure_operation.script_output["validation_result"])
            self.assertIsNot(pure_operation.validation_result, ScriptValidationResult.REQUIREMENT_SATISFIED)
            self.assertEqual("Pure Deterministic Operation", pure_operation.evidence[0]["requirement_id"])
            self.assertEqual("L2-B05-pure-deterministic-operation", pure_operation.script_output["invocation_id"])
            self.assertEqual("PURE_DETERMINISTIC_OPERATION_FIXTURE", pure_operation.script_output["script_identity"])

        with self._temporary_workspace() as workspace:
            script_root = workspace / "scripts"
            script_root.mkdir()
            self._write_input_capture_script(script_root, "input_capture.py")
            runner = ScriptRunner(
                script_root=script_root,
                script_registry={"INPUT_CAPTURE_FIXTURE": "input_capture.py"},
            )
            coordinator = ScriptCoordinator(runner)
            input_capture_request = ScriptInvocationRequest(
                invocation_id="L2-B05-input-preparation",
                script_identity="INPUT_CAPTURE_FIXTURE",
                invocation_purpose="DETERMINISTIC_OPERATION",
                input_data={"operation": "capture-input"},
                execution_parameter={"mode": "capture"},
            )
            input_capture = coordinator.invoke(input_capture_request)
            self.assertIs(input_capture.execution_status, ScriptExecutionStatus.COMPLETED)
            self.assertEqual(VALIDATION_NOT_COMPLETED, input_capture.result_reason)
            self.assertEqual("L2-B05-input-preparation", input_capture.script_output["invocation_id"])
            self.assertEqual("INPUT_CAPTURE_FIXTURE", input_capture.script_output["script_identity"])
            received_input = input_capture.evidence[0]["observed_fact"]["received_input"]
            expected_fields = {
                "invocation_id",
                "script_identity",
                "invocation_purpose",
                "input_data",
                "context_reference",
                "artifact_reference",
                "validation_requirement",
                "execution_parameter",
            }
            self.assertTrue(expected_fields.issubset(received_input))
            self.assertEqual("L2-B05-input-preparation", received_input["invocation_id"])
            self.assertEqual("INPUT_CAPTURE_FIXTURE", received_input["script_identity"])
            self.assertEqual("DETERMINISTIC_OPERATION", received_input["invocation_purpose"])
            self.assertEqual({"operation": "capture-input"}, received_input["input_data"])
            self.assertIsNone(received_input["context_reference"])
            self.assertIsNone(received_input["artifact_reference"])
            self.assertIsNone(received_input["validation_requirement"])
            self.assertEqual({"mode": "capture"}, received_input["execution_parameter"])
            serialized_received_input = json.dumps(received_input, ensure_ascii=False)
            for context_file in (
                "PROJECT_PROFILE.md",
                "PROJECT_STATE.md",
                "PROJECT_PLAN.md",
                "PROJECT_DECISIONS.md",
            ):
                self.assertNotIn(context_file, serialized_received_input)

        with self._temporary_workspace() as workspace:
            script_root = workspace / "scripts"
            script_root.mkdir()
            malformed_script = script_root / "malformed_output.py"
            malformed_script.write_text("print('this-is-not-valid-json')\n", encoding="utf-8")
            runner = ScriptRunner(
                script_root=script_root,
                script_registry={"MALFORMED_OUTPUT_FIXTURE": "malformed_output.py"},
            )
            coordinator = ScriptCoordinator(runner)
            malformed_request = ScriptInvocationRequest(
                invocation_id="L2-B05-malformed-output",
                script_identity="MALFORMED_OUTPUT_FIXTURE",
                invocation_purpose="VALIDATION",
            )
            malformed = coordinator.invoke(malformed_request)
            self.assertIs(malformed.runtime_state, RuntimeExecutionState.FAILED)
            self.assertEqual(SCRIPT_EXECUTION_ERROR, malformed.result_reason)
            self.assertIsNone(malformed.execution_status)
            self.assertIsNone(malformed.validation_result)
            self.assertEqual((), malformed.evidence)
            self.assertNotEqual(EVIDENCE_READY, malformed.result_reason)
            self.assertNotEqual(VALIDATION_UNSATISFIED, malformed.result_reason)

        with self._temporary_workspace() as workspace:
            sentinel = workspace / "PROJECT_STATE.md"
            sentinel.write_text("before\n", encoding="utf-8")
            before = sentinel.read_text(encoding="utf-8")
            boundary_input = self._context_integrity_payload(
                "L2-B05-authority-boundary",
                self._complete_context_data(),
                self._complete_context_identity(),
            )
            serialized_input = json.dumps(boundary_input, ensure_ascii=False)
            for context_file in (
                "PROJECT_PROFILE.md",
                "PROJECT_STATE.md",
                "PROJECT_PLAN.md",
                "PROJECT_DECISIONS.md",
            ):
                self.assertNotIn(str(workspace / context_file), serialized_input)

            boundary_request = ScriptInvocationRequest(
                invocation_id="L2-B05-authority-boundary",
                script_identity="VALIDATE_CONTEXT_INTEGRITY_EVIDENCE",
                invocation_purpose="VALIDATION",
                input_data=boundary_input,
            )
            boundary = default_coordinator.invoke(boundary_request)
            after = sentinel.read_text(encoding="utf-8")
            self.assertEqual(EVIDENCE_READY, boundary.result_reason)
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
