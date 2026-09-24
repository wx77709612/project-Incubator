"""Frozen definition loading for Project Incubator V1 runtime."""

from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PROJECT_INCUBATOR.runtime.core.contracts import (
    ContextAccessResultStatus,
    GateEvaluationResult,
    ScriptExecutionStatus,
    ScriptValidationResult,
    WorkflowResultStatus,
)
from PROJECT_INCUBATOR.runtime.core.runtime_types import RuntimeExecutionState
from PROJECT_INCUBATOR.runtime.core.mutation_orchestration_types import (
    AuthorityRequirement,
    ClosureOperator,
)


RUNTIME_DEPENDENCY_FAILURE = "RUNTIME_DEPENDENCY_FAILURE"


@dataclass(frozen=True)
class RuntimeContractTypes:
    context_access_result_status: type[ContextAccessResultStatus]
    workflow_result_status: type[WorkflowResultStatus]
    gate_evaluation_result: type[GateEvaluationResult]
    script_execution_status: type[ScriptExecutionStatus]
    script_validation_result: type[ScriptValidationResult]
    runtime_execution_state: type[RuntimeExecutionState]


@dataclass(frozen=True)
class FrozenDefinitionSet:
    workflow_definition: dict[str, Any]
    gate_definition: dict[str, Any]
    context_definition: dict[str, Any]
    advisory_definition: dict[str, Any]
    runtime_contract_types: RuntimeContractTypes


@dataclass(frozen=True)
class DefinitionResolutionResult:
    runtime_state: RuntimeExecutionState
    frozen_definition_set: FrozenDefinitionSet | None = None
    failure_reason: str | None = None
    missing_requirement: str | None = None


class DefinitionLoadError(Exception):
    def __init__(self, missing_requirement: str) -> None:
        super().__init__(missing_requirement)
        self.missing_requirement = missing_requirement


class DefinitionResolver:
    required_reference_keys = (
        "workflow_definition",
        "gate_definition",
        "context_definition",
        "advisory_definition",
    )

    required_contract_type_keys = (
        "context_access_result_status",
        "workflow_result_status",
        "gate_evaluation_result",
        "script_execution_status",
        "script_validation_result",
        "runtime_execution_state",
    )

    def __init__(
        self,
        config_path: str | Path | None = None,
        config_data: dict[str, Any] | None = None,
    ) -> None:
        self.config_path = Path(config_path) if config_path else self.default_config_path()
        self.config_data = config_data
        self.package_root = self.config_path.parent.parent

    @staticmethod
    def default_config_path() -> Path:
        return Path(__file__).resolve().parents[1] / "config.json"

    def resolve(self) -> DefinitionResolutionResult:
        try:
            return DefinitionResolutionResult(
                runtime_state=RuntimeExecutionState.COMPLETED,
                frozen_definition_set=self.load_frozen_definition_set(),
            )
        except DefinitionLoadError as exc:
            return DefinitionResolutionResult(
                runtime_state=RuntimeExecutionState.FAILED,
                failure_reason=RUNTIME_DEPENDENCY_FAILURE,
                missing_requirement=exc.missing_requirement,
            )

    def load_frozen_definition_set(self) -> FrozenDefinitionSet:
        config = self._load_config()
        workflow_definition = self._load_json_definition(config, "workflow_definition")
        gate_definition = self._load_json_definition(config, "gate_definition")
        context_definition = self._load_json_definition(config, "context_definition")
        advisory_definition = self._load_json_definition(config, "advisory_definition")
        self.validate_context_event_recipes(context_definition)
        return FrozenDefinitionSet(
            workflow_definition=workflow_definition,
            gate_definition=gate_definition,
            context_definition=context_definition,
            advisory_definition=advisory_definition,
            runtime_contract_types=self._load_runtime_contract_types(config),
        )

    def context_event_recipe(self, event_type: str) -> dict[str, Any]:
        context_definition = self.load_frozen_definition_set().context_definition
        recipes = context_definition["context_model"]["multi_context_event_recipes"]
        recipe = recipes.get(event_type)
        if not isinstance(recipe, dict):
            raise DefinitionLoadError(f"unknown context event recipe: {event_type}")
        return recipe

    @staticmethod
    def validate_context_event_recipes(context_definition: dict[str, Any]) -> None:
        context_model = context_definition.get("context_model")
        recipes = context_model.get("multi_context_event_recipes") if isinstance(context_model, dict) else None
        if not isinstance(recipes, dict) or not recipes:
            raise DefinitionLoadError("missing context event recipes")

        valid_authorities = {item.value for item in AuthorityRequirement}
        valid_operators = {item.value for item in ClosureOperator}
        for event_type, recipe in recipes.items():
            if not isinstance(event_type, str) or not event_type or not isinstance(recipe, dict):
                raise DefinitionLoadError("invalid context event recipe")
            authority = recipe.get("authority_requirement")
            if authority not in valid_authorities:
                raise DefinitionLoadError(f"invalid authority requirement: {event_type}")

            required = recipe.get("required_targets")
            allowed = recipe.get("allowed_targets")
            commit_order = recipe.get("commit_order")
            for name, values in (
                ("required target", required),
                ("allowed target", allowed),
                ("commit order", commit_order),
            ):
                if not isinstance(values, list) or not values or any(
                    not isinstance(value, str) or not value for value in values
                ):
                    raise DefinitionLoadError(f"invalid {name}: {event_type}")
                if len(values) != len(set(values)):
                    raise DefinitionLoadError(f"duplicate {name}: {event_type}")
            if not set(required).issubset(allowed):
                raise DefinitionLoadError(f"required target is not allowed: {event_type}")
            if set(commit_order) != set(allowed):
                raise DefinitionLoadError(f"commit order must cover allowed targets: {event_type}")
            if "PROJECT_STATE" in commit_order and commit_order[-1] != "PROJECT_STATE":
                raise DefinitionLoadError(f"PROJECT_STATE must commit last: {event_type}")

            assertions = recipe.get("closure_assertions")
            if not isinstance(assertions, list) or not assertions:
                raise DefinitionLoadError(f"missing closure assertions: {event_type}")
            assertion_ids: list[str] = []
            for assertion in assertions:
                if not isinstance(assertion, dict):
                    raise DefinitionLoadError(f"invalid closure assertion: {event_type}")
                assertion_id = assertion.get("assertion_id")
                if not isinstance(assertion_id, str) or not assertion_id:
                    raise DefinitionLoadError(f"invalid closure assertion id: {event_type}")
                assertion_ids.append(assertion_id)
                if assertion.get("operator") not in valid_operators:
                    raise DefinitionLoadError(f"invalid closure operator: {event_type}")
            if len(assertion_ids) != len(set(assertion_ids)):
                raise DefinitionLoadError(f"duplicate closure assertion: {event_type}")

    def _load_config(self) -> dict[str, Any]:
        if self.config_data is not None:
            return self.config_data
        if not self.config_path.exists():
            raise DefinitionLoadError(f"missing runtime config: {self.config_path}")
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DefinitionLoadError(f"invalid runtime config: {self.config_path}") from exc
        if not isinstance(loaded, dict):
            raise DefinitionLoadError("runtime config must be a JSON object")
        return loaded

    def _load_json_definition(self, config: dict[str, Any], key: str) -> dict[str, Any]:
        reference_locations = config.get("reference_locations")
        if not isinstance(reference_locations, dict) or key not in reference_locations:
            raise DefinitionLoadError(f"missing reference location: {key}")

        definition_path = self.package_root / reference_locations[key]
        if not definition_path.exists():
            raise DefinitionLoadError(f"missing required reference: {key}")

        try:
            definition = json.loads(definition_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DefinitionLoadError(f"invalid required reference: {key}") from exc

        if not isinstance(definition, dict):
            raise DefinitionLoadError(f"required reference is not an object: {key}")

        expected_id = self._expected_definition_id(config, key)
        if definition.get("definition_id") != expected_id:
            raise DefinitionLoadError(f"definition identity mismatch: {key}")

        return definition

    def _expected_definition_id(self, config: dict[str, Any], key: str) -> str:
        identity_mapping = config.get("definition_identity_mapping")
        if not isinstance(identity_mapping, dict):
            raise DefinitionLoadError("missing definition identity mapping")
        expected_id = identity_mapping.get(key)
        if not isinstance(expected_id, str) or not expected_id:
            raise DefinitionLoadError(f"missing definition identity: {key}")
        return expected_id

    def _load_runtime_contract_types(self, config: dict[str, Any]) -> RuntimeContractTypes:
        identity_mapping = config.get("definition_identity_mapping")
        if not isinstance(identity_mapping, dict):
            raise DefinitionLoadError("missing definition identity mapping")

        type_mapping = identity_mapping.get("runtime_contract_types")
        if not isinstance(type_mapping, dict):
            raise DefinitionLoadError("missing runtime contract type mapping")

        loaded_types: dict[str, Any] = {}
        for key in self.required_contract_type_keys:
            dotted_path = type_mapping.get(key)
            if not isinstance(dotted_path, str) or not dotted_path:
                raise DefinitionLoadError(f"missing runtime contract type: {key}")
            loaded_types[key] = self._load_symbol(dotted_path, key)

        return RuntimeContractTypes(**loaded_types)

    def _load_symbol(self, dotted_path: str, key: str) -> Any:
        module_name, separator, symbol_name = dotted_path.rpartition(".")
        if not separator:
            raise DefinitionLoadError(f"invalid runtime contract type: {key}")

        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            raise DefinitionLoadError(f"missing runtime contract module: {key}") from exc

        try:
            return getattr(module, symbol_name)
        except AttributeError as exc:
            raise DefinitionLoadError(f"missing runtime contract symbol: {key}") from exc


__all__ = [
    "DefinitionLoadError",
    "DefinitionResolutionResult",
    "DefinitionResolver",
    "FrozenDefinitionSet",
    "RUNTIME_DEPENDENCY_FAILURE",
    "RuntimeContractTypes",
]
