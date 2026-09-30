#!/usr/bin/env node
import { randomUUID } from "node:crypto";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { authorizePreparedChange, prepareChange } from "./kernel/authorization.mjs";
import { hashJson } from "./kernel/canonical-json.mjs";
import { findPromptRef } from "./kernel/prompt-events.mjs";
import { buildProjectSummary, renderProjectSummary, writeProjectOverview } from "./kernel/project-summary.mjs";
import { loadRegistry, resolveRoute } from "./kernel/registry.mjs";
import {
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
  initializeProjectState,
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
  const value = { error: { code: stableCode(error), message: String(error?.message ?? error) } };
  return {
    isError: true,
    content: [{ type: "text", text: JSON.stringify(value) }],
    structuredContent: value,
  };
}

export async function createKernelService(options = {}) {
  const pluginRoot = options.pluginRoot
    ?? path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const runtimeDataRoot = options.runtimeDataRoot ?? resolveRuntimeDataRoot(options.env ?? process.env);
  const registry = await loadRegistry(pluginRoot);

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
      const request = await prepareActivationRequest({
        runtimeDataRoot, projectRoot: args.project_root, projectId: args.project_id,
        route, sessionId: args.session_id, summary: args.summary,
        initialState: state, productDecisions, now: context.now ?? new Date(),
      });
      return {
        event: "ACTIVATION_PREPARED",
        request_id: request.request_id,
        scope_digest: request.scope_digest,
        route,
        summary: request.summary,
        product_decisions: request.product_decisions,
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
      const promptRef = await findPromptRef(runtimeDataRoot, {
        project_id: request.project_id, session_id: args.session_id, turn_id: args.turn_id,
      });
      const activation = {
        schema_version: "1.0", project_id: request.project_id,
        plugin_id: "project-incubator-plugin", plugin_version: "0.1.0", status: "ACTIVE",
        project_type_id: request.route.project_type_id,
        child_skill_id: request.route.child_skill_id,
        host_profile_id: request.route.host_profile_id,
      };
      const state = parseProjectState(request.initial_state);
      const productDecisions = parseActivationProductDecisions(request.product_decisions);
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
      const receipt = await initializeProjectState(
        args.project_root, activation, initializedState, authorizationRef,
      );
      await consumeActivationRequest(request);
      return { activation, receipt };
    },

    async prepare_change(args, context) {
      const snapshot = await readProjectSnapshot(args.project_root);
      const proposedState = parseProjectState(args.proposed_state);
      if (proposedState.project_id !== snapshot.state.project_id) throw new Error("PROJECT_ID_MISMATCH");
      const requestId = `request-${randomUUID()}`;
      const scopeDigest = hashJson({
        operation: args.operation, change_kind: args.change_kind, proposed_state: proposedState,
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
              session_id: args.session_id, requires_authorization: true,
            },
          });
          current.last_change = {
            operation: "PREPARE_CHANGE", changed_at: createdAt, summary: `准备变更：${args.operation}`,
          };
          return current;
        },
      });
      return { event: "CHANGE_PREPARED", request_id: requestId, scope_digest: scopeDigest, receipt };
    },

    async commit_change(args, context) {
      const snapshot = await readProjectSnapshot(args.project_root);
      const pending = snapshot.state.pending_requests.find((item) => item.request_id === args.request_id);
      if (!pending || pending.status !== "PENDING") throw new Error("PENDING_REQUEST_NOT_FOUND");
      if (pending.scope_digest !== args.scope_digest) throw new Error("SCOPE_DIGEST_MISMATCH");
      if (pending.payload?.session_id !== args.session_id) throw new Error("PROMPT_CONTEXT_MISMATCH");
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
        now: context.now ?? new Date(),
      });
      const proposedState = parseProjectState(pending.payload.proposed_state);
      const receipt = await commitProjectState(args.project_root, {
        operation: pending.operation, expectedRevision: snapshot.state.revision, authorizationRef,
        mutate(current) {
          const next = structuredClone(proposedState);
          next.pending_requests = current.pending_requests.filter((item) => item.request_id !== args.request_id);
          return next;
        },
      });
      return { receipt };
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
  const server = new McpServer({ name: "project-incubator-plugin", version: "0.1.0" });
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
    prepare_change: {
      project_root: z.string(), operation: z.string(), change_kind: z.string(),
      session_id: z.string(), proposed_state: z.record(z.unknown()),
    },
    commit_change: {
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
