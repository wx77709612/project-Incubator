#!/usr/bin/env node
import { randomUUID } from "node:crypto";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import {
  createAgentEntry,
  inspectAgentEntry,
  loadAgentEntryTemplate,
  rollbackAgentEntry,
} from "./kernel/agent-entry.mjs";
import {
  diagnoseAuthority,
  normalizeRecoveryCandidate,
  recoverProjectAuthority,
} from "./kernel/authority-recovery.mjs";
import {
  authorizePreparedChange,
  authorizePreparedDecline,
  prepareChange,
} from "./kernel/authorization.mjs";
import { changeApprovalMessage } from "./kernel/approval-message.mjs";
import { hashJson } from "./kernel/canonical-json.mjs";
import {
  consumeMaintenanceRequest,
  getMaintenanceRequest,
  prepareMaintenanceRequest,
} from "./kernel/maintenance-requests.mjs";
import { findAuthorizedPromptRef, findPromptRef } from "./kernel/prompt-events.mjs";
import { buildProjectSummary, renderProjectSummary, writeProjectOverview } from "./kernel/project-summary.mjs";
import { loadRegistry, loadWorkflowEvaluators, resolveRoute } from "./kernel/registry.mjs";
import {
  activationScopeDigest,
  consumeActivationRequest,
  getPendingActivation,
  prepareActivationRequest,
  proposeRoute,
} from "./kernel/router.mjs";
import { resolveRuntimeDataRoot } from "./kernel/runtime-paths.mjs";
import {
  parseActivationProductDecisions,
  parsePostActivationInitialState,
  parseProjectState,
} from "./kernel/schemas.mjs";
import {
  assertProjectUninitialized,
  commitProjectState,
  initializeProjectWithAgentEntry,
  readProjectSnapshot,
  verifyLatestReceipt,
} from "./kernel/state-store.mjs";

function stableCode(error) {
  if (error?.name === "ZodError") return "INVALID_ARGUMENT";
  const message = String(error?.message ?? "");
  return /^[A-Z][A-Z0-9_]+$/.test(message) ? message : "INTERNAL_ERROR";
}

function success(value) {
  return {
    content: [{ type: "text", text: JSON.stringify(value) }],
    structuredContent: value,
  };
}

function failure(error) {
  const details = Array.isArray(error?.residual_paths)
    ? { residual_paths: error.residual_paths }
    : {};
  const value = {
    error: { code: stableCode(error), message: String(error?.message ?? error), ...details },
  };
  return {
    isError: true,
    content: [{ type: "text", text: JSON.stringify(value) }],
    structuredContent: value,
  };
}

function sameValues(left, right) {
  return hashJson(left) === hashJson(right);
}

function decisionMeaning(decision) {
  return {
    decision_id: decision.decision_id,
    kind: decision.kind,
    status: decision.status,
    statement: decision.statement,
  };
}

function bindChangedDecisions(currentDecisions, proposedDecisions, authorizationRef, confirmedAt) {
  const currentById = new Map(currentDecisions.map((decision) => [decision.decision_id, decision]));
  return proposedDecisions.map((decision) => {
    const current = currentById.get(decision.decision_id);
    if (current && sameValues(decisionMeaning(current), decisionMeaning(decision))) return decision;
    return {
      ...decision,
      authorization_ref: authorizationRef.authorization_id,
      confirmed_at: confirmedAt,
    };
  });
}

function assertWorkflowShape(proposed, evaluated) {
  if ((proposed.return_stage ?? null) !== (evaluated.return_stage ?? null)) {
    throw new Error("WORKFLOW_RETURN_STAGE_MISMATCH");
  }
  if (!sameValues(proposed.allowed_next, evaluated.allowed_next)) {
    throw new Error("WORKFLOW_ALLOWED_NEXT_MISMATCH");
  }
}

function validateWorkflowEntry(initialState, evaluator) {
  if (typeof evaluator?.evaluateEntry !== "function") throw new Error("WORKFLOW_EVALUATOR_NOT_FOUND");
  const evaluation = evaluator.evaluateEntry(initialState);
  if (!evaluation.allowed) throw new Error(evaluation.code);
  assertWorkflowShape(initialState.workflow, evaluation.workflow);
  return evaluation;
}

function validateRecoveryWorkflow(state, evaluator) {
  if (typeof evaluator?.evaluateEntry !== "function"
    || typeof evaluator?.evaluateTransition !== "function") {
    throw new Error("WORKFLOW_EVALUATOR_NOT_FOUND");
  }
  if (state.schema_version === "1.1") {
    const entryState = structuredClone(state);
    entryState.workflow.stage = entryState.workflow.entry.initial_stage;
    const entryEvaluation = evaluator.evaluateEntry(entryState);
    if (!entryEvaluation.allowed) throw new Error(entryEvaluation.code);
  }

  const currentProbe = structuredClone(state);
  currentProbe.workflow.entry = {
    mode: "ADOPT_EXISTING",
    initial_stage: state.workflow.stage,
    assessment_summary: "权威恢复期间验证当前阶段。",
    evidence_refs: ["authority-recovery"],
    assessed_at: state.last_change.changed_at,
  };
  const currentEvaluation = evaluator.evaluateEntry(currentProbe);
  if (currentEvaluation.allowed) {
    try {
      assertWorkflowShape(state.workflow, currentEvaluation.workflow);
    } catch {
      throw new Error("WORKFLOW_ALLOWED_NEXT_MISMATCH");
    }
    return;
  }

  const returnStage = state.workflow.return_stage ?? null;
  if (!returnStage || !sameValues(state.workflow.allowed_next, [returnStage])) {
    throw new Error("WORKFLOW_ALLOWED_NEXT_MISMATCH");
  }
  const reviewEvaluation = evaluator.evaluateTransition(state, {
    target_stage: returnStage,
    completion_satisfied: true,
    model_invalidated: true,
    model_updated: true,
    maker_authorized: true,
    changes_boundary: false,
  });
  if (!reviewEvaluation.allowed) throw new Error("WORKFLOW_ALLOWED_NEXT_MISMATCH");
}

function assertWorkflowEntryImmutable(currentState, proposedState) {
  if (currentState.schema_version !== "1.1") return;
  if (proposedState.schema_version !== "1.1" || proposedState.workflow.entry === undefined) {
    throw new Error("WORKFLOW_ENTRY_IMMUTABLE");
  }
  if (!sameValues(currentState.workflow.entry, proposedState.workflow.entry)) {
    throw new Error("WORKFLOW_ENTRY_IMMUTABLE");
  }
}

function validateWorkflowTransition(snapshot, proposedState, transition, evaluator, options = {}) {
  const stageChanged = snapshot.state.workflow.stage !== proposedState.workflow.stage;
  if (!stageChanged) {
    if (transition !== undefined) throw new Error("WORKFLOW_TRANSITION_UNEXPECTED");
    return null;
  }
  if (!transition) throw new Error("WORKFLOW_TRANSITION_REQUIRED");
  if (transition.target_stage !== proposedState.workflow.stage) {
    throw new Error("WORKFLOW_TARGET_MISMATCH");
  }
  if (typeof evaluator?.evaluateTransition !== "function") throw new Error("WORKFLOW_EVALUATOR_NOT_FOUND");

  const request = {
    ...transition,
    changes_boundary: !sameValues(snapshot.state.boundary, proposedState.boundary),
    maker_authorized: options.makerAuthorized === true,
  };
  let evaluation = evaluator.evaluateTransition(snapshot.state, request);
  let requiresMakerAuthorization = false;
  if (!evaluation.allowed && evaluation.code === "MAKER_AUTHORIZATION_REQUIRED" && options.allowAuthorizationPending) {
    requiresMakerAuthorization = true;
    evaluation = evaluator.evaluateTransition(snapshot.state, { ...request, maker_authorized: true });
  }
  if (!evaluation.allowed) throw new Error(evaluation.code);
  assertWorkflowShape(proposedState.workflow, evaluation.workflow);
  return { evaluation, requires_maker_authorization: requiresMakerAuthorization };
}

export async function createKernelService(options = {}) {
  const pluginRoot = options.pluginRoot
    ?? path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const packageMetadata = JSON.parse(await readFile(path.join(pluginRoot, "package.json"), "utf8"));
  if (typeof packageMetadata.version !== "string" || packageMetadata.version.length === 0) {
    throw new Error("PLUGIN_PACKAGE_VERSION_INVALID");
  }
  const pluginVersion = packageMetadata.version;
  const runtimeDataRoot = options.runtimeDataRoot
    ?? resolveRuntimeDataRoot(options.env ?? process.env, pluginRoot);
  const registry = await loadRegistry(pluginRoot);
  const workflowEvaluators = await loadWorkflowEvaluators(pluginRoot, registry);
  const agentEntryTemplate = await loadAgentEntryTemplate(pluginRoot);
  const diagnoseAuthorityRuntime = options.diagnoseAuthority ?? diagnoseAuthority;

  const handlers = {
    async propose_route(args) {
      return proposeRoute(registry, args);
    },

    async prepare_activation(args, context) {
      await assertProjectUninitialized(args.project_root);
      const route = resolveRoute(registry, args.project_type_id, args.host_profile_id ?? null);
      const state = parsePostActivationInitialState(args.state);
      const productDecisions = parseActivationProductDecisions(args.product_decisions);
      if (state.project_id !== args.project_id || state.revision !== 0) {
        throw new Error("INITIAL_STATE_ID_OR_REVISION_INVALID");
      }
      validateWorkflowEntry(state, workflowEvaluators.get(route.project_type_id));
      const request = await prepareActivationRequest({
        runtimeDataRoot, projectRoot: args.project_root, projectId: args.project_id,
        route, sessionId: args.session_id, summary: args.summary,
        initialState: state, productDecisions,
        agentEntry: {
          path: "AGENTS.md",
          policy: "CREATE_IF_MISSING_PRESERVE_EXISTING",
          template_sha256: agentEntryTemplate.sha256,
        },
        now: context.now ?? new Date(),
      });
      return {
        event: "ACTIVATION_PREPARED",
        request_id: request.request_id,
        scope_digest: request.scope_digest,
        route,
        summary: request.summary,
        product_decisions: request.product_decisions,
        agent_entry: request.agent_entry,
        expires_at: request.expires_at,
      };
    },

    async initialize_project(args, context) {
      const now = context.now ?? new Date();
      const request = await getPendingActivation(
        runtimeDataRoot, args.project_root, args.request_id, now,
      );
      if (request.scope_digest !== args.scope_digest) throw new Error("SCOPE_DIGEST_MISMATCH");
      if (request.session_id !== args.session_id) throw new Error("PROMPT_CONTEXT_MISMATCH");
      const route = resolveRoute(
        registry, request.route.project_type_id, request.route.host_profile_id ?? null,
      );
      if (!sameValues(route, request.route)) throw new Error("ACTIVATION_ROUTE_MISMATCH");
      const state = parsePostActivationInitialState(request.initial_state);
      if (state.project_id !== request.project_id || state.revision !== 0) {
        throw new Error("INITIAL_STATE_ID_OR_REVISION_INVALID");
      }
      validateWorkflowEntry(state, workflowEvaluators.get(route.project_type_id));
      const productDecisions = parseActivationProductDecisions(request.product_decisions);
      if (request.agent_entry?.path !== "AGENTS.md"
        || request.agent_entry?.policy !== "CREATE_IF_MISSING_PRESERVE_EXISTING"
        || request.agent_entry?.template_sha256 !== agentEntryTemplate.sha256) {
        throw new Error("AGENT_ENTRY_TEMPLATE_INVALID");
      }
      if (request.scope_digest !== activationScopeDigest(request)) {
        throw new Error("SCOPE_DIGEST_MISMATCH");
      }
      const promptRef = await findPromptRef(runtimeDataRoot, {
        project_id: request.project_id, session_id: args.session_id, turn_id: args.turn_id,
      });
      const activation = {
        schema_version: "1.0", project_id: request.project_id,
        plugin_id: "project-incubator-plugin", plugin_version: pluginVersion, status: "ACTIVE",
        project_type_id: route.project_type_id,
        child_skill_id: route.child_skill_id,
        host_profile_id: route.host_profile_id,
      };
      const pending = {
        request_id: request.request_id, operation: request.operation,
        scope_digest: request.scope_digest, status: "PENDING",
        created_at: request.created_at, project_revision: 0,
      };
      const prepared = prepareChange({
        activation,
        state: { ...state, pending_requests: [pending] },
      }, {
        request_id: request.request_id, scope_digest: request.scope_digest,
        operation: request.operation, change_kind: "PRODUCT_DECISION",
        project_id: request.project_id, session_id: args.session_id, turn_id: args.turn_id,
      });
      const authorizationRef = await authorizePreparedChange(prepared, promptRef, { now });
      const initializedState = {
        ...state,
        decisions: {
          ...state.decisions,
          active: productDecisions.map((decision) => ({
            ...decision,
            kind: "PRODUCT",
            status: "ACTIVE",
            authorization_ref: authorizationRef.authorization_id,
            confirmed_at: now.toISOString(),
          })),
        },
        pending_requests: [],
        last_change: {
          operation: "INITIALIZE_PROJECT",
          changed_at: now.toISOString(),
          summary: "项目已按 Maker 授权完成初始化。",
        },
      };
      const initialized = await initializeProjectWithAgentEntry(
        args.project_root, activation, initializedState, authorizationRef, agentEntryTemplate,
      );
      await consumeActivationRequest(request);
      return { activation, receipt: initialized.receipt, agent_entry: initialized.agent_entry };
    },

    async prepare_agent_entry(args, context) {
      const inspected = await inspectAgentEntry(args.project_root, agentEntryTemplate);
      if (inspected.status !== "MISSING") {
        return { event: "AGENT_ENTRY_INSPECTED", agent_entry: inspected };
      }
      const request = await prepareMaintenanceRequest({
        runtimeDataRoot,
        projectRoot: args.project_root,
        sessionId: args.session_id,
        operation: "AGENT_ENTRY_INSTALL",
        requestPrefix: "request",
        payload: { template_sha256: agentEntryTemplate.sha256 },
        now: context.now ?? new Date(),
      });
      return {
        event: "AGENT_ENTRY_INSTALL_PREPARED",
        request_id: request.request_id,
        scope_digest: request.scope_digest,
        expires_at: request.expires_at,
        agent_entry: inspected,
      };
    },

    async install_agent_entry(args, context) {
      const now = context.now ?? new Date();
      const request = await getMaintenanceRequest({
        runtimeDataRoot,
        projectRoot: args.project_root,
        requestId: args.request_id,
        scopeDigest: args.scope_digest,
        sessionId: args.session_id,
        operation: "AGENT_ENTRY_INSTALL",
        now,
      });
      if (request.payload.template_sha256 !== agentEntryTemplate.sha256) {
        throw new Error("AGENT_ENTRY_SOURCE_CHANGED");
      }
      const inspected = await inspectAgentEntry(args.project_root, agentEntryTemplate);
      if (inspected.status !== "MISSING") throw new Error("AGENT_ENTRY_SOURCE_CHANGED");
      const snapshot = await readProjectSnapshot(args.project_root);
      const promptRef = await findAuthorizedPromptRef(runtimeDataRoot, {
        project_root: request.project_root,
        project_id: snapshot.state.project_id,
        session_id: args.session_id,
        request_id: request.request_id,
        scope_digest: request.scope_digest,
        intent: "APPROVE",
      });
      await authorizePreparedChange({
        request_id: request.request_id,
        scope_digest: request.scope_digest,
        project_id: snapshot.state.project_id,
        session_id: args.session_id,
        turn_id: promptRef.turn_id,
        requires_authorization: true,
      }, promptRef, { now });
      const created = await createAgentEntry(args.project_root, agentEntryTemplate);
      try {
        await consumeMaintenanceRequest(request);
      } catch (error) {
        const rollback = await rollbackAgentEntry(args.project_root, created.rollbackToken);
        if (rollback.residual_paths.length) {
          const rollbackError = new Error("AGENT_ENTRY_ROLLBACK_INCOMPLETE", { cause: error });
          rollbackError.residual_paths = rollback.residual_paths;
          throw rollbackError;
        }
        throw error;
      }
      return { event: "AGENT_ENTRY_INSTALLED", agent_entry: created.result };
    },

    async prepare_authority_recovery(args, context) {
      const diagnostics = await diagnoseAuthorityRuntime(args.project_root);
      if (diagnostics.snapshot_valid) throw new Error("AUTHORITY_RECOVERY_NOT_REQUIRED");
      const proposedState = parseProjectState(args.proposed_state);
      if (proposedState.pending_requests.length !== 0) {
        throw new Error("RECOVERY_CANDIDATE_INVALID");
      }
      const candidate = normalizeRecoveryCandidate(
        diagnostics, args.proposed_activation, proposedState, context.now ?? new Date(),
      );
      const route = resolveRoute(
        registry,
        candidate.activation.project_type_id,
        candidate.activation.host_profile_id ?? null,
      );
      if (candidate.activation.plugin_id !== "project-incubator-plugin"
        || candidate.activation.plugin_version !== pluginVersion
        || candidate.activation.status !== "ACTIVE"
        || candidate.activation.child_skill_id !== route.child_skill_id) {
        throw new Error("ACTIVATION_ROUTE_MISMATCH");
      }
      validateRecoveryWorkflow(candidate.state, workflowEvaluators.get(route.project_type_id));
      const request = await prepareMaintenanceRequest({
        runtimeDataRoot,
        projectRoot: args.project_root,
        projectId: candidate.activation.project_id,
        sessionId: args.session_id,
        operation: "AUTHORITY_RECOVERY",
        requestPrefix: "recovery",
        payload: {
          summary: args.summary,
          authority_diagnostics: diagnostics.items,
          fingerprints: diagnostics.fingerprints,
          candidate,
        },
        now: context.now ?? new Date(),
      });
      return {
        event: "AUTHORITY_RECOVERY_PREPARED",
        request_id: request.request_id,
        scope_digest: request.scope_digest,
        authority_diagnostics: diagnostics.items,
        proposed_revision: candidate.state.revision,
        expires_at: request.expires_at,
      };
    },

    async recover_project_authority(args, context) {
      const now = context.now ?? new Date();
      const request = await getMaintenanceRequest({
        runtimeDataRoot,
        projectRoot: args.project_root,
        requestId: args.request_id,
        scopeDigest: args.scope_digest,
        sessionId: args.session_id,
        operation: "AUTHORITY_RECOVERY",
        now,
      });
      const currentDiagnostics = await diagnoseAuthorityRuntime(request.project_root);
      if (!sameValues(currentDiagnostics.fingerprints, request.payload.fingerprints)) {
        throw new Error("RECOVERY_SOURCE_CHANGED");
      }
      const promptRef = await findAuthorizedPromptRef(runtimeDataRoot, {
        project_root: request.project_root,
        project_id: request.project_id,
        session_id: args.session_id,
        request_id: request.request_id,
        scope_digest: request.scope_digest,
        intent: "APPROVE",
      });
      const authorizationRef = await authorizePreparedChange({
        request_id: request.request_id,
        scope_digest: request.scope_digest,
        project_id: request.project_id,
        session_id: args.session_id,
        turn_id: promptRef.turn_id,
        requires_authorization: true,
      }, promptRef, { now });
      const recovered = await recoverProjectAuthority(
        request.project_root,
        request.payload.candidate,
        request.payload.fingerprints,
        authorizationRef,
      );
      await consumeMaintenanceRequest(request);
      return recovered;
    },

    async prepare_change(args, context) {
      const snapshot = await readProjectSnapshot(args.project_root);
      const proposedState = parseProjectState(args.proposed_state);
      if (proposedState.project_id !== snapshot.state.project_id) throw new Error("PROJECT_ID_MISMATCH");
      assertWorkflowEntryImmutable(snapshot.state, proposedState);
      validateWorkflowTransition(
        snapshot, proposedState, args.workflow_transition,
        workflowEvaluators.get(snapshot.activation.project_type_id), {
        allowAuthorizationPending: true,
        },
      );
      const requestId = `request-${randomUUID()}`;
      const scopeDigest = hashJson({
        operation: args.operation, change_kind: args.change_kind, proposed_state: proposedState,
        workflow_transition: args.workflow_transition ?? null,
      });
      const createdAt = (context.now ?? new Date()).toISOString();
      const receipt = await commitProjectState(args.project_root, {
        operation: "PREPARE_CHANGE", expectedRevision: snapshot.state.revision, authorizationRef: null,
        mutate(current) {
          current.pending_requests.push({
            request_id: requestId, operation: args.operation, scope_digest: scopeDigest,
            status: "PENDING", created_at: createdAt, project_revision: current.revision + 1,
            payload: {
              change_kind: args.change_kind, proposed_state: proposedState,
              workflow_transition: args.workflow_transition,
              session_id: args.session_id, requires_authorization: true,
            },
          });
          current.last_change = {
            operation: "PREPARE_CHANGE", changed_at: createdAt, summary: `准备变更：${args.operation}`,
          };
          return current;
        },
      });
      return {
        event: "CHANGE_PREPARED", request_id: requestId, scope_digest: scopeDigest,
        approval_message: changeApprovalMessage(requestId, scopeDigest), receipt,
      };
    },

    async commit_change(args, context) {
      const now = context.now ?? new Date();
      const snapshot = await readProjectSnapshot(args.project_root);
      const pending = snapshot.state.pending_requests.find((item) => item.request_id === args.request_id);
      if (!pending || pending.status !== "PENDING") throw new Error("PENDING_REQUEST_NOT_FOUND");
      if (pending.scope_digest !== args.scope_digest) throw new Error("SCOPE_DIGEST_MISMATCH");
      if (pending.payload?.session_id !== args.session_id) throw new Error("PROMPT_CONTEXT_MISMATCH");
      const proposedState = parseProjectState(pending.payload.proposed_state);
      assertWorkflowEntryImmutable(snapshot.state, proposedState);
      const promptRef = await findPromptRef(runtimeDataRoot, {
        project_id: snapshot.state.project_id, session_id: args.session_id, turn_id: args.turn_id,
      });
      const prepared = prepareChange(snapshot, {
        request_id: args.request_id, scope_digest: args.scope_digest,
        operation: pending.operation, change_kind: pending.payload.change_kind,
        project_id: snapshot.state.project_id, session_id: args.session_id, turn_id: args.turn_id,
        requires_authorization: pending.payload.requires_authorization,
      });
      const authorizationRef = await authorizePreparedChange(prepared, promptRef, {
        now,
      });
      validateWorkflowTransition(
        snapshot, proposedState, pending.payload.workflow_transition,
        workflowEvaluators.get(snapshot.activation.project_type_id), {
        makerAuthorized: true,
        },
      );
      const receipt = await commitProjectState(args.project_root, {
        operation: pending.operation, expectedRevision: snapshot.state.revision, authorizationRef,
        mutate(current) {
          const next = structuredClone(proposedState);
          next.decisions.active = bindChangedDecisions(
            current.decisions.active,
            next.decisions.active,
            authorizationRef,
            now.toISOString(),
          );
          next.pending_requests = current.pending_requests.filter((item) => item.request_id !== args.request_id);
          return next;
        },
      });
      return { receipt };
    },

    async decline_change(args, context) {
      const now = context.now ?? new Date();
      const snapshot = await readProjectSnapshot(args.project_root);
      const pending = snapshot.state.pending_requests.find((item) => item.request_id === args.request_id);
      if (!pending || pending.status !== "PENDING") throw new Error("PENDING_REQUEST_NOT_FOUND");
      if (pending.scope_digest !== args.scope_digest) throw new Error("SCOPE_DIGEST_MISMATCH");
      const promptRef = await findPromptRef(runtimeDataRoot, {
        project_id: snapshot.state.project_id, session_id: args.session_id, turn_id: args.turn_id,
      });
      const prepared = prepareChange(snapshot, {
        request_id: args.request_id, scope_digest: args.scope_digest,
        operation: pending.operation, change_kind: pending.payload.change_kind,
        project_id: snapshot.state.project_id, session_id: args.session_id, turn_id: args.turn_id,
        requires_authorization: true,
      });
      const authorizationRef = await authorizePreparedDecline(prepared, promptRef, { now });
      const receipt = await commitProjectState(args.project_root, {
        operation: "DECLINE_CHANGE", expectedRevision: snapshot.state.revision, authorizationRef,
        mutate(current) {
          current.pending_requests = current.pending_requests.filter(
            (item) => item.request_id !== args.request_id,
          );
          current.last_change = {
            operation: "DECLINE_CHANGE",
            changed_at: now.toISOString(),
            summary: `Maker 已拒绝变更：${pending.operation}`,
          };
          return current;
        },
      });
      return { event: "CHANGE_DECLINED", request_id: args.request_id, receipt };
    },

    async get_project_state(args) {
      return readProjectSnapshot(args.project_root);
    },

    async verify_receipt(args) {
      return verifyLatestReceipt(args.project_root, args.receipt_id);
    },

    async inspect_project(args) {
      const snapshot = await readProjectSnapshot(args.project_root);
      const receipt = await verifyLatestReceipt(args.project_root);
      if (!receipt.verified) throw new Error("RECEIPT_UNVERIFIABLE");
      const summary = buildProjectSummary(snapshot, receipt);
      return { summary, markdown: renderProjectSummary(summary) };
    },

    async export_project_overview(args, context) {
      const snapshot = await readProjectSnapshot(args.project_root);
      const receipt = await verifyLatestReceipt(args.project_root);
      if (!receipt.verified) throw new Error("RECEIPT_UNVERIFIABLE");
      const promptRef = await findPromptRef(runtimeDataRoot, {
        project_id: snapshot.state.project_id, session_id: args.session_id, turn_id: args.turn_id,
      });
      const summary = buildProjectSummary(snapshot, receipt);
      const projection = await writeProjectOverview(args.project_root, summary, promptRef, {
        now: context.now ?? new Date(),
      });
      return { summary, markdown: renderProjectSummary(summary), projection };
    },
  };

  return {
    pluginVersion,
    registry,
    async callTool(name, args, context = {}) {
      try {
        const handler = handlers[name];
        if (!handler) throw new Error("TOOL_NOT_FOUND");
        return success(await handler(args, context));
      } catch (error) {
        return failure(error);
      }
    },
  };
}

export async function createMcpServer(options = {}) {
  const service = await createKernelService(options);
  const server = new McpServer({ name: "project-incubator-plugin", version: service.pluginVersion });
  const definitions = {
    propose_route: {
      project_root: z.string(), project_type_id: z.string(), host_profile_id: z.string().nullable().optional(),
    },
    prepare_activation: {
      project_root: z.string(), project_id: z.string(), project_type_id: z.string(),
      host_profile_id: z.string().nullable().optional(), session_id: z.string(), summary: z.string(),
      state: z.record(z.unknown()),
      product_decisions: z.array(z.object({
        decision_id: z.string(), statement: z.string(),
      }).strict()).min(1).max(100),
    },
    initialize_project: {
      project_root: z.string(), request_id: z.string(), scope_digest: z.string(),
      session_id: z.string(), turn_id: z.string(),
    },
    prepare_agent_entry: {
      project_root: z.string(), session_id: z.string(),
    },
    install_agent_entry: {
      project_root: z.string(), request_id: z.string(), scope_digest: z.string(),
      session_id: z.string(), turn_id: z.string().optional(),
    },
    prepare_authority_recovery: {
      project_root: z.string(), session_id: z.string(), summary: z.string(),
      proposed_activation: z.record(z.unknown()), proposed_state: z.record(z.unknown()),
    },
    recover_project_authority: {
      project_root: z.string(), request_id: z.string(), scope_digest: z.string(),
      session_id: z.string(), turn_id: z.string().optional(),
    },
    prepare_change: {
      project_root: z.string(), operation: z.string(), change_kind: z.string(),
      session_id: z.string(), proposed_state: z.record(z.unknown()),
      workflow_transition: z.object({
        target_stage: z.string(), completion_satisfied: z.boolean(),
        model_invalidated: z.boolean().optional(), model_updated: z.boolean().optional(),
      }).strict().optional(),
    },
    commit_change: {
      project_root: z.string(), request_id: z.string(), scope_digest: z.string(),
      session_id: z.string(), turn_id: z.string(),
    },
    decline_change: {
      project_root: z.string(), request_id: z.string(), scope_digest: z.string(),
      session_id: z.string(), turn_id: z.string(),
    },
    get_project_state: { project_root: z.string() },
    verify_receipt: { project_root: z.string(), receipt_id: z.string().optional() },
    inspect_project: { project_root: z.string() },
    export_project_overview: {
      project_root: z.string(), session_id: z.string(), turn_id: z.string(),
    },
  };
  for (const [name, inputSchema] of Object.entries(definitions)) {
    server.registerTool(name, { description: `Project Incubator ${name}`, inputSchema },
      async (args) => service.callTool(name, args));
  }
  return server;
}

async function main() {
  const server = await createMcpServer();
  await server.connect(new StdioServerTransport());
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
