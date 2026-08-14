"""Layer 2 Stage A Runtime Foundation Acceptance Tests.

本文件是 Maker-driven Runtime Acceptance Test Code。
它不属于 Product Runtime Feature，也不修改 PROJECT_INCUBATOR 产品代码。
"""

from __future__ import annotations

import json
import shutil
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


from PROJECT_INCUBATOR.runtime.adapters.file_store import FileStore
from PROJECT_INCUBATOR.runtime.components.context_coordinator import (
    AccessTarget,
    AccessType,
    AuthorizationEvidence,
    ContextAccessRequest,
    ContextCoordinator,
    ContextType,
    MutationIntent,
    MutationType,
    RequestSource,
)
from PROJECT_INCUBATOR.runtime.components.definition_resolver import (
    DefinitionResolver,
    RUNTIME_DEPENDENCY_FAILURE,
)
from PROJECT_INCUBATOR.runtime.components.workflow_coordinator import (
    PhaseResult,
    WorkflowCoordinator,
)
from PROJECT_INCUBATOR.runtime.core.contracts import (
    ContextAccessResultStatus,
    GateEvaluationResult,
    ScriptExecutionStatus,
    ScriptValidationResult,
    WorkflowResultStatus,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState


SKILL_PACKAGE_ROOT = REPOSITORY_ROOT / "PROJECT_INCUBATOR"
RUNTIME_CONFIG_PATH = SKILL_PACKAGE_ROOT / "runtime" / "config.json"
ACCEPTANCE_TEMP_ROOT = (
    REPOSITORY_ROOT
    / "ACCEPTANCE_TESTS"
    / "layer2"
    / "stage_a"
    / ".tmp_runtime_foundation_acceptance"
)


class RuntimeFoundationAcceptanceTest(unittest.TestCase):
    """Stage A 验证 TASK-011 至 TASK-015 的 Runtime Foundation 能力。"""

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
            shutil.rmtree(workspace, ignore_errors=True)
            try:
                temp_root.rmdir()
            except OSError:
                pass

    def _copy_skill_package(self, temp_root: Path) -> Path:
        package_copy = temp_root / "PROJECT_INCUBATOR"
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
        shutil.copytree(SKILL_PACKAGE_ROOT, package_copy, ignore=ignore)
        return package_copy

    def _write_core_context_fixture(self, project_root: Path) -> None:
        files = {
            "PROJECT_PROFILE.md": "# PROJECT_PROFILE\n\n项目身份：Stage A 临时项目\n",
            "PROJECT_STATE.md": "# PROJECT_STATE\n\nCurrent Phase: P3\n",
            "PROJECT_PLAN.md": "# PROJECT_PLAN\n\n当前计划：执行 Stage A 验收。\n",
            "PROJECT_DECISIONS.md": "# PROJECT_DECISIONS\n\n已确认决策：初始占位。\n",
        }
        for file_name, content in files.items():
            (project_root / file_name).write_text(content, encoding="utf-8")

    def _context_coordinator(self, project_root: Path) -> ContextCoordinator:
        return ContextCoordinator(FileStore(project_root))

    def _phase_result(
        self,
        current_phase: str,
        requested_next_phase: str,
        *,
        process_completed: bool = True,
        required_artifact_requirement_satisfied: bool = True,
        state_change_requirement_formed: bool = True,
        gate_requirement_resolved: bool = True,
    ) -> PhaseResult:
        return PhaseResult(
            current_phase=current_phase,
            requested_next_phase=requested_next_phase,
            process_completed=process_completed,
            required_artifact_requirement_satisfied=required_artifact_requirement_satisfied,
            state_change_requirement_formed=state_change_requirement_formed,
            gate_requirement_resolved=gate_requirement_resolved,
            artifact_evidence=("acceptance-fixture-artifact",),
            state_change_reference="acceptance-fixture-state-change",
            gate_resolution_reference="acceptance-fixture-gate-resolution",
        )

    def _evaluate_transition(
        self,
        coordinator: WorkflowCoordinator,
        current_phase: str,
        requested_next_phase: str,
    ):
        phase_result = self._phase_result(current_phase, requested_next_phase)
        transition_request = coordinator.create_transition_request(
            request_id=f"L2-A-transition-{current_phase}-{requested_next_phase}",
            phase_result=phase_result,
        )
        return coordinator.evaluate_transition(transition_request)

    def test_l2_a01_contract_type_integrity(self):
        """
        Test Case:
        L2-A01

        测试目标：
        确认 Project Incubator 不同 Runtime Component 使用同一套冻结状态语言，
        防止 Context、Workflow、Gate、Script、Runtime 对同一个执行状态产生不同理解。

        真实运行场景：
        任何 Runtime Component 产生 Contract Result 后，后续 Component 会消费这个 Result。
        如果 Result 类型缺值、多值，或把 Script Validation Result 与 Gate Evaluation Result 混为一类，
        Runtime 主链即使能继续运行，也会在真实项目推进时解释错边界。

        System Layer：
        Runtime Foundation / Contract Projection

        Runtime Flow Position：
        基础类型层，支撑 Runtime Request 到 Runtime Result 的完整流程；
        它不是独立执行步骤，而是所有 Runtime Component 共享的状态语言。

        测试隔离边界：
        本测试假设各 Component 已经完成自己的业务判断。
        本测试不验证 Component 逻辑，只直接检查冻结 Contract Enum 与 Runtime State Enum。

        Semantic Input：
        Runtime 需要一套固定的 Context Access、Workflow、Gate、Script、Runtime 状态词表。

        业务期望：
        Runtime Component 之间必须用完全一致且互不混淆的结果类型交流。
        Script Validation Result 不能等同于 Gate Evaluation Result。
        """
        expected_context = {
            "ACCEPTED",
            "REJECTED",
            "AUTHORIZATION_REQUIRED",
            "GATE_REQUIREMENT_UNRESOLVED",
            "BOUNDARY_VIOLATION",
            "CONTEXT_CONFLICT",
        }
        expected_workflow = {
            "NOT_READY",
            "READY_FOR_TRANSITION",
            "TRANSITION_NOT_ALLOWED",
        }
        expected_gate = {
            "REQUIREMENT_SATISFIED",
            "REQUIREMENT_UNSATISFIED",
            "AUTHORIZATION_REQUIRED",
            "EVIDENCE_INSUFFICIENT",
            "ACTION_BLOCKED",
        }
        expected_script_status = {
            "COMPLETED",
            "INVALID_INPUT",
            "UNSUPPORTED_INVOCATION",
            "EXECUTION_ERROR",
        }
        expected_script_validation = {
            "REQUIREMENT_SATISFIED",
            "REQUIREMENT_UNSATISFIED",
            "VALIDATION_NOT_COMPLETED",
        }
        expected_runtime_state = {
            "EXECUTING",
            "WAITING_FOR_MAKER",
            "BLOCKED_BY_GATE",
            "SUSPENDED",
            "FAILED",
            "COMPLETED",
        }

        self.assertEqual(expected_context, {item.value for item in ContextAccessResultStatus})
        self.assertEqual(expected_workflow, {item.value for item in WorkflowResultStatus})
        self.assertEqual(expected_gate, {item.value for item in GateEvaluationResult})
        self.assertEqual(expected_script_status, {item.value for item in ScriptExecutionStatus})
        self.assertEqual(expected_script_validation, {item.value for item in ScriptValidationResult})
        self.assertEqual(expected_runtime_state, {item.value for item in RuntimeExecutionState})
        self.assertIsNot(ScriptValidationResult, GateEvaluationResult)

    def test_l2_a02_frozen_definition_loading(self):
        """
        Test Case:
        L2-A02

        测试目标：
        验证 Runtime 开始确定性执行前，能够从正式 Skill Package 加载完整 Frozen Definition Set。
        如果加载失败，后续 Context、Workflow、Gate、Advisory 将失去共同依据。

        真实运行场景：
        Runtime Request 进入后，Runtime 先读取 runtime/config.json，
        定位 references/*.json，确认 definition_id，
        再形成 Frozen Definition Set 供后续 Context / Workflow / Gate / Advisory 使用。

        System Layer：
        Runtime Foundation / Definition Resolution

        Runtime Flow Position：
        Runtime Request
        ↓
        [Definition Resolution] ← 当前测试
        ↓
        Context Establish / Restore

        测试隔离边界：
        本测试假设 Agent 已经正确解析 Maker 请求。
        本测试不验证自然语言理解、Gate 执行或 Context Mutation，只验证定义加载入口。

        Semantic Input：
        使用正式 Skill Package 的 runtime/config.json 与 references 目录。

        业务期望：
        Runtime 能获得完整冻结定义集合，并确认每个 Definition 的身份与配置一致。
        """
        resolver = DefinitionResolver(RUNTIME_CONFIG_PATH)
        result = resolver.resolve()
        config = json.loads(RUNTIME_CONFIG_PATH.read_text(encoding="utf-8"))
        identities = config["definition_identity_mapping"]

        self.assertIs(result.runtime_state, RuntimeExecutionState.COMPLETED)
        self.assertIsNone(result.failure_reason)
        self.assertIsNotNone(result.frozen_definition_set)
        frozen = result.frozen_definition_set
        assert frozen is not None

        self.assertEqual(identities["workflow_definition"], frozen.workflow_definition["definition_id"])
        self.assertEqual(identities["gate_definition"], frozen.gate_definition["definition_id"])
        self.assertEqual(identities["context_definition"], frozen.context_definition["definition_id"])
        self.assertEqual(identities["advisory_definition"], frozen.advisory_definition["definition_id"])
        self.assertIs(frozen.runtime_contract_types.context_access_result_status, ContextAccessResultStatus)
        self.assertIs(frozen.runtime_contract_types.workflow_result_status, WorkflowResultStatus)
        self.assertIs(frozen.runtime_contract_types.gate_evaluation_result, GateEvaluationResult)
        self.assertIs(frozen.runtime_contract_types.script_execution_status, ScriptExecutionStatus)
        self.assertIs(frozen.runtime_contract_types.script_validation_result, ScriptValidationResult)
        self.assertIs(frozen.runtime_contract_types.runtime_execution_state, RuntimeExecutionState)

    def test_l2_a03_missing_required_reference(self):
        """
        Test Case:
        L2-A03

        测试目标：
        验证 Required Reference 缺失时 Runtime 会停止，而不是猜测、回退默认值或从其他文档推导。

        真实运行场景：
        Runtime 准备执行时需要加载冻结机器 Definition。
        如果某个 references/*.json 缺失，后续 Component 不应该带着不完整规则继续推进真实项目。

        System Layer：
        Runtime Foundation / Definition Resolution

        Runtime Flow Position：
        Runtime Request
        ↓
        [Definition Resolution] ← 当前测试
        ↓
        Context Establish / Restore

        测试隔离边界：
        本测试假设 Agent 已经形成结构化 Runtime Request。
        本测试只在临时 Skill Package 副本中删除一个 Required Reference，
        不修改正式 PROJECT_INCUBATOR/references。

        Semantic Input：
        临时 Skill Package 中缺失 workflow_definition 指向的 core_workflow.json。

        业务期望：
        Runtime 必须报告依赖失败，明确缺失项，并停止 Definition Resolution。
        """
        with self._temporary_workspace() as temp_dir:
            package_copy = self._copy_skill_package(temp_dir)
            config_path = package_copy / "runtime" / "config.json"
            (package_copy / "references" / "workflow" / "core_workflow.json").unlink()

            result = DefinitionResolver(config_path).resolve()

        self.assertIs(result.runtime_state, RuntimeExecutionState.FAILED)
        self.assertEqual(RUNTIME_DEPENDENCY_FAILURE, result.failure_reason)
        self.assertEqual("missing required reference: workflow_definition", result.missing_requirement)
        self.assertIsNone(result.frozen_definition_set)

    def test_l2_a04_definition_identity_mismatch(self):
        """
        Test Case:
        L2-A04

        测试目标：
        验证文件存在但 definition_id 与 runtime/config.json 不一致时，
        Runtime 仍然拒绝加载，防止错误 Definition 被当成冻结规则使用。

        真实运行场景：
        Runtime 读取 references/*.json 后，不只检查文件存在，
        还要确认它就是配置声明的那份冻结 Definition。

        System Layer：
        Runtime Foundation / Definition Resolution

        Runtime Flow Position：
        Runtime Request
        ↓
        [Definition Resolution] ← 当前测试
        ↓
        Context Establish / Restore

        测试隔离边界：
        本测试只在临时 Skill Package 副本中篡改 definition_id。
        本测试不修改正式 Reference，也不测试后续 Workflow 行为。

        Semantic Input：
        workflow reference 文件存在，但 definition_id 被替换为错误身份。

        业务期望：
        Runtime 必须拒绝身份不匹配的 Definition，并报告 Runtime Dependency Failure。
        """
        with self._temporary_workspace() as temp_dir:
            package_copy = self._copy_skill_package(temp_dir)
            config_path = package_copy / "runtime" / "config.json"
            workflow_path = package_copy / "references" / "workflow" / "core_workflow.json"
            workflow_definition = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow_definition["definition_id"] = "WRONG_DEFINITION_ID"
            workflow_path.write_text(
                json.dumps(workflow_definition, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            result = DefinitionResolver(config_path).resolve()

        self.assertIs(result.runtime_state, RuntimeExecutionState.FAILED)
        self.assertEqual(RUNTIME_DEPENDENCY_FAILURE, result.failure_reason)
        self.assertEqual("definition identity mismatch: workflow_definition", result.missing_requirement)
        self.assertIsNone(result.frozen_definition_set)

    def test_l2_a05_file_store_read_write_verification(self):
        """
        Test Case:
        L2-A05

        测试目标：
        验证 Runtime 与文件系统交互的底层能力可信，
        因为后续 Reference Read、Context Read、Context Mutation Persistence、
        PROJECT_STATE Commit 和 Read-back Verification 都依赖 File Store。

        真实运行场景：
        Runtime 需要保存或读取 Managed Project 的 Context 文件时，
        File Store 负责确定性读写，但不决定项目应该做什么。

        System Layer：
        Runtime Adapter

        Runtime Flow Position：
        File Store 不是独立 Domain Decision Layer。
        它支撑 Definition Resolution、Context Read、Context Mutation、
        PROJECT_STATE Commit 与 Read-back Verification。

        测试隔离边界：
        本测试使用 Temporary Directory。
        本测试不验证 Maker Authorization、Gate 或 Context Mutation 是否应该发生。

        Semantic Input：
        临时文件依次经历 exists、atomic_write、read_file、atomic overwrite、append、read_file。

        业务期望：
        Runtime 写入的内容必须真实落盘，读取内容必须与写入内容完全一致，
        append 不能覆盖已有内容。
        """
        with self._temporary_workspace() as temp_dir:
            store = FileStore(temp_dir)
            path = Path("runtime-state.txt")

            self.assertFalse(store.exists(path))
            first = store.atomic_write(path, "第一版状态\n")
            self.assertTrue(first.verified)
            self.assertTrue(store.exists(path))
            self.assertEqual("第一版状态\n", store.read_file(path))

            second = store.atomic_write(path, "第二版状态\n")
            self.assertTrue(second.verified)
            self.assertEqual("第二版状态\n", store.read_file(path))

            appended = store.append(path, "追加记录\n")
            self.assertTrue(appended.verified)
            self.assertEqual("第二版状态\n追加记录\n", store.read_file(path))

    def test_l2_a06_context_legal_read(self):
        """
        Test Case:
        L2-A06

        测试目标：
        验证 Runtime 能合法读取 Core Context，
        防止真实使用时 Runtime 依赖历史聊天、Agent Memory 或 Runtime State 替代 PROJECT_STATE。

        真实运行场景：
        Agent 已解析请求后，Runtime 需要恢复 Managed Project 当前上下文，
        Context Coordinator 负责从 PROJECT_PROFILE、PROJECT_STATE、PROJECT_PLAN、
        PROJECT_DECISIONS 等 Context 文件读取真实内容。

        System Layer：
        Context Runtime

        Runtime Flow Position：
        Definition Resolution
        ↓
        [Context Establish / Restore] ← 当前测试
        ↓
        Current Phase Resolution

        测试隔离边界：
        本测试假设 Agent 已经正确理解 Maker 请求。
        本测试直接构造 READ 请求，不测试自然语言理解或 Workflow Evaluation。

        Semantic Input：
        Temporary Managed Project 存在 PROJECT_STATE.md；
        Runtime 请求读取 PROJECT_STATE。

        业务期望：
        Context Coordinator 应返回 ACCEPTED，
        且读取内容来自目标 Context File。
        """
        with self._temporary_workspace() as project_root:
            self._write_core_context_fixture(project_root)
            coordinator = self._context_coordinator(project_root)
            request = ContextAccessRequest(
                request_id="L2-A06",
                access_target=AccessTarget(ContextType.PROJECT_STATE),
                access_type=AccessType.READ,
                request_source=RequestSource.RUNTIME,
                access_purpose="恢复当前项目状态",
            )

            result = coordinator.handle(request)

        self.assertIs(result.status, ContextAccessResultStatus.ACCEPTED)
        self.assertIn("Current Phase: P3", result.content or "")

    def test_l2_a07_agent_direct_write_boundary(self):
        """
        Test Case:
        L2-A07

        测试目标：
        验证 Agent 不能绕过 Runtime 直接执行持久化 Context Mutation，
        防止 Agent 把未经过 Runtime Contract 的判断直接写入 Managed Project。

        真实运行场景：
        Agent 已经理解 Maker 想修改项目状态，
        但真实持久化写入必须由 Runtime 在满足 Contract / Gate / Authorization 后执行。

        System Layer：
        Context Runtime

        Runtime Flow Position：
        Maker Requirement
        ↓
        [Context Mutation Boundary] ← 当前测试
        ↓
        Transition Eligibility

        测试隔离边界：
        本测试假设 Agent 已解析出一个 PROJECT_STATE 修改意图。
        本测试不验证 Agent Reasoning，只直接构造 Actor = Agent、
        Operation = EXECUTE_MUTATION 的非法边界输入。

        Semantic Input：
        Agent 尝试直接把 PROJECT_STATE.md 写成新的阶段内容。

        业务期望：
        Context Coordinator 必须拒绝该请求，
        文件不得产生持久化变化，结果不得是 ACCEPTED。
        """
        with self._temporary_workspace() as project_root:
            self._write_core_context_fixture(project_root)
            before = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")
            coordinator = self._context_coordinator(project_root)
            target = AccessTarget(ContextType.PROJECT_STATE)
            intent = MutationIntent(
                mutation_type=MutationType.UPDATE_CONTEXT,
                target_context=target,
                change_purpose="Agent 尝试直接推进阶段",
                change_basis="WORKFLOW_STATE_CHANGE_REQUIREMENT",
                proposed_content="# PROJECT_STATE\n\nCurrent Phase: P4\n",
                execute_eligibility_granted=True,
            )
            request = ContextAccessRequest(
                request_id="L2-A07",
                access_target=target,
                access_type=AccessType.EXECUTE_MUTATION,
                request_source=RequestSource.AGENT,
                access_purpose="绕过 Runtime 直接持久化",
                mutation_intent=intent,
            )

            result = coordinator.handle(request)
            after = (project_root / "PROJECT_STATE.md").read_text(encoding="utf-8")

        self.assertIs(result.status, ContextAccessResultStatus.REJECTED)
        self.assertEqual("Runtime Execution Authority", result.missing_requirement)
        self.assertEqual(before, after)

    def test_l2_a08_script_direct_context_read_boundary(self):
        """
        Test Case:
        L2-A08

        测试目标：
        验证 Script 不能直接读取 Core Context，
        防止确定性脚本越过 Runtime 输入边界，获得不应拥有的项目上下文权限。

        真实运行场景：
        Runtime 后续可能调用 Script 形成 Evidence。
        Script 只能消费 Runtime 提供的有限结构化输入，不能自己读取 PROJECT_STATE 或其他 Core Context。

        System Layer：
        Context Runtime

        Runtime Flow Position：
        Definition Resolution
        ↓
        Context Establish / Restore
        ↓
        [Script Direct Context Read Boundary] ← 当前测试支撑后续 Script Evidence
        ↓
        Script Evidence

        测试隔离边界：
        本测试假设 Runtime 已经准备调用 Script。
        本测试不执行 Script，只构造 Actor = Script、Request = Direct Core Context Read。

        Semantic Input：
        Script 请求直接读取 PROJECT_STATE。

        业务期望：
        Context Coordinator 必须拒绝 Script 直接读取，
        且不得返回 Core Context 内容。
        """
        with self._temporary_workspace() as project_root:
            self._write_core_context_fixture(project_root)
            coordinator = self._context_coordinator(project_root)
            request = ContextAccessRequest(
                request_id="L2-A08",
                access_target=AccessTarget(ContextType.PROJECT_STATE),
                access_type=AccessType.READ,
                request_source=RequestSource.SCRIPT,
                access_purpose="Script 直接读取 Core Context",
            )

            result = coordinator.handle(request)

        self.assertIs(result.status, ContextAccessResultStatus.REJECTED)
        self.assertEqual("Runtime-provided limited input", result.missing_requirement)
        self.assertIsNone(result.content)

    def test_l2_a09_profile_mutation_without_maker_authorization(self):
        """
        Test Case:
        L2-A09

        测试目标：
        验证 PROJECT_PROFILE 修改必须保持 Maker Authorization Boundary，
        防止项目身份、长期目标或成功标准在 Maker 未确认时被写入。

        真实运行场景：
        Agent 已解析出一个会影响 PROJECT_PROFILE Authority 的修改请求，
        Runtime 需要通过 Context Coordinator 检查 Gate Evidence 与 Maker Authorization。

        System Layer：
        Context Runtime

        Runtime Flow Position：
        Maker Requirement
        ↓
        [Context Mutation] ← 当前测试
        ↓
        Transition Eligibility

        测试隔离边界：
        本测试假设 Agent 已经形成 PROFILE Mutation Intent。
        本测试提供 Gate Evidence，但不提供 Maker Authorization，
        以隔离验证 Maker Authorization Boundary。

        Semantic Input：
        PROJECT_PROFILE 将被更新为新的项目身份内容；
        没有 Maker 授权确认。

        业务期望：
        Runtime 不得接受该 Mutation Request，
        应返回 AUTHORIZATION_REQUIRED，且文件不发生持久化变化。
        """
        with self._temporary_workspace() as project_root:
            self._write_core_context_fixture(project_root)
            before = (project_root / "PROJECT_PROFILE.md").read_text(encoding="utf-8")
            coordinator = self._context_coordinator(project_root)
            target = AccessTarget(ContextType.PROJECT_PROFILE)
            intent = MutationIntent(
                mutation_type=MutationType.UPDATE_CONTEXT,
                target_context=target,
                change_purpose="修改项目长期身份",
                change_basis="MAKER_REQUESTED_CORRECTION",
                proposed_content="# PROJECT_PROFILE\n\n项目身份：未经 Maker 授权的新身份\n",
                gate_evidence_reference="GATE-AUTHORITY-DOCUMENT:satisfied",
            )
            request = ContextAccessRequest(
                request_id="L2-A09",
                access_target=target,
                access_type=AccessType.REQUEST_MUTATION,
                request_source=RequestSource.AGENT,
                access_purpose="请求修改 PROFILE",
                mutation_intent=intent,
            )

            result = coordinator.handle(request)
            after = (project_root / "PROJECT_PROFILE.md").read_text(encoding="utf-8")

        self.assertIs(result.status, ContextAccessResultStatus.AUTHORIZATION_REQUIRED)
        self.assertEqual("Maker Authorization", result.authorization_requirement)
        self.assertEqual(before, after)

    def test_l2_a10_decisions_append_without_maker_confirmation(self):
        """
        Test Case:
        L2-A10

        测试目标：
        验证 PROJECT_DECISIONS 只能记录 Maker Confirmed Decision，
        防止普通讨论、Agent 判断或未确认方案被写成项目决策历史。

        真实运行场景：
        Agent 已识别出一个重要选择可能需要记录，
        Runtime 必须确认它来自 Maker Confirmed Decision 后，才允许追加到 PROJECT_DECISIONS。

        System Layer：
        Context Runtime

        Runtime Flow Position：
        Maker Requirement
        ↓
        [Context Mutation] ← 当前测试
        ↓
        Transition Eligibility

        测试隔离边界：
        本测试假设 Agent 已经形成 Decision Append Request。
        本测试提供 Gate Evidence，但不提供 Maker Confirmation。

        Semantic Input：
        准备向 PROJECT_DECISIONS.md 追加一条新 Decision；
        Maker 未确认该 Decision。

        业务期望：
        Context Coordinator 必须要求 Maker Authorization，
        PROJECT_DECISIONS.md 历史内容保持不变。
        """
        with self._temporary_workspace() as project_root:
            self._write_core_context_fixture(project_root)
            before = (project_root / "PROJECT_DECISIONS.md").read_text(encoding="utf-8")
            coordinator = self._context_coordinator(project_root)
            target = AccessTarget(ContextType.PROJECT_DECISIONS)
            intent = MutationIntent(
                mutation_type=MutationType.APPEND_RECORD,
                target_context=target,
                change_purpose="追加项目决策",
                change_basis="MAKER_CONFIRMED_DECISION_REQUIRED",
                proposed_content="\n## Decision X\n未确认决策。\n",
                gate_evidence_reference="GATE-AUTHORITY-DOCUMENT:satisfied",
            )
            request = ContextAccessRequest(
                request_id="L2-A10",
                access_target=target,
                access_type=AccessType.REQUEST_MUTATION,
                request_source=RequestSource.AGENT,
                access_purpose="请求追加 Decision",
                mutation_intent=intent,
            )

            result = coordinator.handle(request)
            after = (project_root / "PROJECT_DECISIONS.md").read_text(encoding="utf-8")

        self.assertIs(result.status, ContextAccessResultStatus.AUTHORIZATION_REQUIRED)
        self.assertEqual(before, after)

    def test_l2_a11_optional_context_authority_boundary(self):
        """
        Test Case:
        L2-A11

        测试目标：
        验证 Optional Context 永远不能覆盖 Core Context Authority，
        尤其不能替代 PROJECT_STATE 作为 Current Project State Source of Truth。

        真实运行场景：
        某类项目可能需要 PROJECT_ARTIFACTS 等 Optional Context。
        即使 Optional Context 包含类似“当前阶段”的信息，
        Runtime 也不能让它覆盖 PROJECT_STATE 的权威地位。

        System Layer：
        Context Runtime

        Runtime Flow Position：
        Definition Resolution
        ↓
        [Context Establish / Restore]
        以及
        Maker Requirement
        ↓
        [Context Mutation] ← 当前测试
        ↓
        Transition Eligibility

        测试隔离边界：
        本测试假设 Agent 已经形成 Optional Context Mutation Intent。
        本测试不验证 Optional Context 的业务内容，只验证 Core Authority Boundary。

        Semantic Input：
        Optional Context PROJECT_ARTIFACTS 试图声明覆盖 PROJECT_STATE 的 Current Phase。

        业务期望：
        Context Coordinator 必须返回 BOUNDARY_VIOLATION，
        Optional Context 不得成为 PROJECT_STATE 的替代 Source of Truth。
        """
        with self._temporary_workspace() as project_root:
            self._write_core_context_fixture(project_root)
            coordinator = self._context_coordinator(project_root)
            target = AccessTarget(
                ContextType.OPTIONAL_CONTEXT,
                optional_context_identity="PROJECT_ARTIFACTS",
            )
            intent = MutationIntent(
                mutation_type=MutationType.UPDATE_CONTEXT,
                target_context=target,
                change_purpose="Optional Context 声明当前状态",
                change_basis="PROJECT_TYPE_SPECIFIC_EXTENSION",
                proposed_content="# PROJECT_ARTIFACTS\n\nCurrent Phase: P4\n",
                overrides_core_context_authority=True,
            )
            request = ContextAccessRequest(
                request_id="L2-A11",
                access_target=target,
                access_type=AccessType.REQUEST_MUTATION,
                request_source=RequestSource.AGENT,
                access_purpose="请求修改 Optional Context",
                mutation_intent=intent,
            )

            result = coordinator.handle(request)

        self.assertIs(result.status, ContextAccessResultStatus.BOUNDARY_VIOLATION)
        self.assertEqual("Optional Context core authority boundary", result.boundary_reference)

    def test_l2_a12_legal_workflow_transition_matrix(self):
        """
        Test Case:
        L2-A12

        测试目标：
        验证冻结 Workflow 允许的 Transition Matrix 在 Runtime 中返回 READY_FOR_TRANSITION，
        同时确认该结果只代表 Workflow 规则允许继续，不代表 PROJECT_STATE 已经被修改。

        真实运行场景：
        Maker 表达推进意图后，Agent 已解析为 Transition Request。
        Runtime 从 PROJECT_STATE 得到 Current Phase，
        Workflow Coordinator 判断目标 Phase 是否允许，
        后续 Runtime 才有资格继续 Gate / Mutation / Commit。

        System Layer：
        Workflow Runtime

        Runtime Flow Position：
        Context Establish / Restore
        ↓
        Current Phase Resolution
        ↓
        [Workflow Evaluation] ← 当前测试
        ↓
        后续 Runtime Flow

        测试隔离边界：
        本测试假设 Agent 已经正确理解 Maker 的阶段推进意图，
        且当前 Phase 所需 Requirement 已满足。
        本测试不执行 Gate、不写 PROJECT_STATE、不提交 Transition。

        Semantic Input：
        当前项目状态分别为 P0、P1、P2、P3、P4、P5、P6；
        Agent 已解析出的结构化意图是请求进入冻结规则允许的下一阶段。

        业务期望：
        Workflow Coordinator 只能确认合法 Transition 已经满足 Workflow Eligibility，
        不能直接完成阶段迁移。
        """
        coordinator = WorkflowCoordinator()
        legal_transitions = (
            ("P0", "P1"),
            ("P1", "P2"),
            ("P2", "P3"),
            ("P3", "P4"),
            ("P4", "P5"),
            ("P5", "P6"),
            ("P6", "P2"),
            ("P6", "P3"),
            ("P6", "P4"),
            ("P6", "P5"),
        )

        for current_phase, requested_next_phase in legal_transitions:
            with self.subTest(current_phase=current_phase, requested_next_phase=requested_next_phase):
                result = self._evaluate_transition(coordinator, current_phase, requested_next_phase)
                self.assertIs(result.status, WorkflowResultStatus.READY_FOR_TRANSITION)
                self.assertEqual((), result.missing_requirements)

    def test_l2_a13_illegal_workflow_transition(self):
        """
        Test Case:
        L2-A13

        测试目标：
        验证非法 Transition 必须返回 TRANSITION_NOT_ALLOWED，
        防止 Runtime “聪明地”替 Maker 或 Agent 改成另一个 Phase。

        真实运行场景：
        Maker 表达推进意图后，Agent 已解析为 Transition Request。
        如果请求路径不在冻结 Workflow Matrix 中，
        Workflow Coordinator 必须拒绝该路径，后续 Runtime 不得继续 Commit。

        System Layer：
        Workflow Runtime

        Runtime Flow Position：
        Context Establish / Restore
        ↓
        Current Phase Resolution
        ↓
        [Workflow Evaluation] ← 当前测试
        ↓
        后续 Runtime Flow

        测试隔离边界：
        本测试假设 Agent 已经正确解析出非法目标 Phase。
        本测试直接构造 Current Phase 与 Requested Transition，
        不测试自然语言理解、Gate 或 Context Mutation。

        Semantic Input：
        P0→P2、P1→P3、P5→P4、P6→P0、P6→P1、P6→P6。

        业务期望：
        Workflow Coordinator 必须返回 TRANSITION_NOT_ALLOWED，
        不得自动选择其他 Phase，不得修改 Allowed Transition。
        """
        coordinator = WorkflowCoordinator()
        illegal_transitions = (
            ("P0", "P2"),
            ("P1", "P3"),
            ("P5", "P4"),
            ("P6", "P0"),
            ("P6", "P1"),
            ("P6", "P6"),
        )

        for current_phase, requested_next_phase in illegal_transitions:
            with self.subTest(current_phase=current_phase, requested_next_phase=requested_next_phase):
                result = self._evaluate_transition(coordinator, current_phase, requested_next_phase)
                self.assertIs(result.status, WorkflowResultStatus.TRANSITION_NOT_ALLOWED)

    def test_l2_a14_legal_transition_but_workflow_not_ready(self):
        """
        Test Case:
        L2-A14

        测试目标：
        验证一个 Transition 即使属于合法 Workflow Path，也不代表当前已经具备推进条件。
        Project Incubator 必须区分“Transition 本身不合法”和“Transition 合法但当前条件尚未满足”。
        前者应返回 TRANSITION_NOT_ALLOWED，后者应返回 NOT_READY。

        真实运行场景：
        Maker 希望从 P3 推进到 P4，Agent 已正确解析为 P3 → P4 Transition Request。
        P3 → P4 本身属于合法 Transition，但当前 Required Artifact、Process Completion、
        State Change Requirement 或 Gate Requirement 中某一项尚未满足。
        Workflow Coordinator 不得返回 READY_FOR_TRANSITION，也不得返回 TRANSITION_NOT_ALLOWED，
        必须返回 NOT_READY，并指出缺失条件。

        System Layer：
        Workflow Runtime

        Runtime Flow Position：
        Context Establish / Restore
        ↓
        Current Phase Resolution
        ↓
        [Workflow Evaluation] ← 当前测试
        ↓
        后续 Runtime Flow

        测试隔离边界：
        本测试假设 Agent 已正确解析 Maker Intent，且 Requested Transition 本身合法。
        本测试不验证 Agent Natural Language Understanding、Gate Coordinator、Context Commit
        或 Runtime Coordinator。测试直接构造 Current Phase = P3、Requested Next Phase = P4，
        并分别让四种 Workflow Readiness Requirement 中的一项不满足。

        Semantic Input：
        当前项目状态为 P3 — Execution Planning。
        Maker 意图为推进进入 P4 — Creation。
        Agent 已解析出的结构化意图为 Request Transition P3 → P4。
        测试分别构造 process_completed=False、
        required_artifact_requirement_satisfied=False、
        state_change_requirement_formed=False、
        gate_requirement_resolved=False。

        业务期望：
        Workflow Coordinator 应确认 P3 → P4 是合法路径，
        但由于当前 readiness requirement 未满足，必须返回 NOT_READY。
        missing_requirements 必须包含当前故意设为未满足的 Requirement。
        """
        coordinator = WorkflowCoordinator()
        readiness_cases = (
            (
                "Process Completion Missing",
                {"process_completed": False},
                "Process Completion",
            ),
            (
                "Required Artifact Requirement Missing",
                {"required_artifact_requirement_satisfied": False},
                "Required Artifact Requirement",
            ),
            (
                "State Change Requirement Missing",
                {"state_change_requirement_formed": False},
                "State Change Requirement",
            ),
            (
                "Gate Requirement Missing",
                {"gate_requirement_resolved": False},
                "Gate Requirement",
            ),
        )

        for label, overrides, expected_missing_requirement in readiness_cases:
            with self.subTest(readiness_failure=label):
                phase_result = self._phase_result("P3", "P4", **overrides)
                transition_request = coordinator.create_transition_request(
                    request_id=f"L2-A14-{label.replace(' ', '-')}",
                    phase_result=phase_result,
                )

                result = coordinator.evaluate_transition(transition_request)

                self.assertIs(result.status, WorkflowResultStatus.NOT_READY)
                self.assertIn(expected_missing_requirement, result.missing_requirements)
                self.assertIsNot(result.status, WorkflowResultStatus.READY_FOR_TRANSITION)
                self.assertIsNot(result.status, WorkflowResultStatus.TRANSITION_NOT_ALLOWED)

    def test_l2_a15_authorized_context_mutation_lifecycle(self):
        """
        Test Case:
        L2-A15

        测试目标：
        验证当所有合法条件真的满足以后，Runtime 可以完成一次合法 Context Mutation，
        并且持久化结果经过 Read-back Verification。现有 Stage A 已证明非法操作会被挡住；
        本测试证明合法操作真的可以完成。

        真实运行场景：
        Maker 希望修改 PROJECT_PROFILE。
        Agent 已正确解析 Mutation Intent，并发出 REQUEST_MUTATION。
        Context Coordinator 检查后要求 Maker Authorization。
        Maker 提供明确 Authorization 后，Runtime 获得合法执行条件并发出 EXECUTE_MUTATION。
        Context Coordinator 调用 File Store Persist，完成 Read-back Verification，
        返回合法结果，PROJECT_PROFILE.md 内容真实变化。

        System Layer：
        Context Runtime

        Runtime Flow Position：
        Maker Requirement
        ↓
        [Context Mutation Request]
        ↓
        [Maker Authorization]
        ↓
        [Runtime Execute Mutation]
        ↓
        Persisted Result Verification
        ↓
        后续 Runtime Flow

        测试隔离边界：
        本测试使用 Temporary Managed Project，不修改真实项目文件。
        本测试假设 Agent 已正确解析 Maker 的 PROFILE 修改意图。
        本测试不验证 Agent Natural Language Understanding、Gate Coordinator、
        Runtime Coordinator 或 Workflow Transition Commit。

        Semantic Input：
        初始 PROJECT_PROFILE.md 已存在。
        Agent 请求将 PROJECT_PROFILE 更新为 Maker 已确认的新内容。
        Gate Evidence 已满足。
        Maker Authorization Evidence 明确来自 Maker 且 confirmed=True。
        最终持久化执行者为 Runtime。

        业务期望：
        未提供 Maker Authorization 时，REQUEST_MUTATION 必须返回 AUTHORIZATION_REQUIRED，
        且 PROJECT_PROFILE.md 不变化。Maker 提供 Authorization 后，
        AUTHORIZE_MUTATION 必须被接受。最终只有 Runtime 发起 EXECUTE_MUTATION 时，
        才能持久化写入，并且磁盘回读内容必须与授权后的 proposed content 完全一致。
        """
        with self._temporary_workspace() as project_root:
            self._write_core_context_fixture(project_root)
            profile_path = project_root / "PROJECT_PROFILE.md"
            before = profile_path.read_text(encoding="utf-8")
            coordinator = self._context_coordinator(project_root)
            target = AccessTarget(ContextType.PROJECT_PROFILE)
            expected_content = (
                "# PROJECT_PROFILE\n\n"
                "项目身份：Stage A 已授权修改后的项目身份\n"
                "Maker Confirmed Information：L2-A15 authorized lifecycle\n"
            )

            request_intent = MutationIntent(
                mutation_type=MutationType.UPDATE_CONTEXT,
                target_context=target,
                change_purpose="Maker 请求修改 PROJECT_PROFILE",
                change_basis="MAKER_REQUESTED_CORRECTION",
                proposed_content=expected_content,
                gate_evidence_reference="GATE-AUTHORITY-DOCUMENT:satisfied",
            )
            request_mutation = ContextAccessRequest(
                request_id="L2-A15-request-mutation",
                access_target=target,
                access_type=AccessType.REQUEST_MUTATION,
                request_source=RequestSource.AGENT,
                access_purpose="Agent 提出 PROJECT_PROFILE 修改请求",
                mutation_intent=request_intent,
            )

            request_result = coordinator.handle(request_mutation)
            after_request = profile_path.read_text(encoding="utf-8")

            self.assertIs(request_result.status, ContextAccessResultStatus.AUTHORIZATION_REQUIRED)
            self.assertEqual("Maker Authorization", request_result.authorization_requirement)
            self.assertEqual(before, after_request)

            authorized_intent = MutationIntent(
                mutation_type=MutationType.UPDATE_CONTEXT,
                target_context=target,
                change_purpose="Maker 已授权修改 PROJECT_PROFILE",
                change_basis="MAKER_REQUESTED_CORRECTION",
                proposed_content=expected_content,
                maker_authorization=AuthorizationEvidence(
                    source=RequestSource.MAKER,
                    confirmed=True,
                    reference="L2-A15 Maker Authorization",
                ),
                gate_evidence_reference="GATE-AUTHORITY-DOCUMENT:satisfied",
                execute_eligibility_granted=True,
            )
            authorize_mutation = ContextAccessRequest(
                request_id="L2-A15-authorize-mutation",
                access_target=target,
                access_type=AccessType.AUTHORIZE_MUTATION,
                request_source=RequestSource.MAKER,
                access_purpose="Maker 提供明确授权",
                mutation_intent=authorized_intent,
            )

            authorization_result = coordinator.handle(authorize_mutation)
            after_authorization = profile_path.read_text(encoding="utf-8")

            self.assertIs(authorization_result.status, ContextAccessResultStatus.ACCEPTED)
            self.assertEqual(before, after_authorization)

            execute_mutation = ContextAccessRequest(
                request_id="L2-A15-execute-mutation",
                access_target=target,
                access_type=AccessType.EXECUTE_MUTATION,
                request_source=RequestSource.RUNTIME,
                access_purpose="Runtime 执行已授权持久化修改",
                mutation_intent=authorized_intent,
            )

            execute_result = coordinator.handle(execute_mutation)
            persisted_content = profile_path.read_text(encoding="utf-8")

        self.assertIs(execute_result.status, ContextAccessResultStatus.ACCEPTED)
        self.assertIsNotNone(execute_result.persisted_result)
        self.assertTrue(execute_result.persisted_result_verified)
        self.assertNotEqual(before, persisted_content)
        self.assertEqual(expected_content, persisted_content)


if __name__ == "__main__":
    unittest.main()
