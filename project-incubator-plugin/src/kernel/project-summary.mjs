import { randomUUID } from "node:crypto";
import { rename, rm, writeFile } from "node:fs/promises";
import path from "node:path";

import { consumePrompt, promptAgeMs, promptPolicy, readPrompt } from "./prompt-events.mjs";

const EVIDENCE_ORDER = ["E0", "E1", "E2", "E3", "E4", "E5"];

function evidenceCeiling(capabilities) {
  return capabilities.reduce((highest, capability) => (
    EVIDENCE_ORDER.indexOf(capability.evidence_level) > EVIDENCE_ORDER.indexOf(highest)
      ? capability.evidence_level : highest
  ), "E0");
}

export function buildProjectSummary(snapshot, receiptVerification) {
  const { activation, state } = snapshot;
  return {
    project: { project_id: state.project_id, revision: state.revision },
    boundary: structuredClone(state.boundary),
    routing: {
      project_type_id: activation.project_type_id,
      child_skill_id: activation.child_skill_id,
      host_profile_id: activation.host_profile_id,
    },
    workflow: structuredClone(state.workflow),
    recent_completed: structuredClone(state.workflow.completed),
    evidence_ceiling: evidenceCeiling(state.capabilities),
    actions: {
      current: state.plan.current_action,
      next: state.plan.next_action,
      completion_conditions: structuredClone(state.plan.completion_conditions),
    },
    blockers: state.gates.filter((gate) => gate.status === "BLOCKED").map((gate) => structuredClone(gate)),
    risks: state.risks.filter((risk) => risk.status === "OPEN").map((risk) => structuredClone(risk)),
    maker_decisions: state.pending_requests.filter((request) => request.status === "PENDING").map((request) => ({
      request_id: request.request_id, operation: request.operation, scope_digest: request.scope_digest,
    })),
    capabilities: state.capabilities.map((capability) => ({
      capability_id: capability.capability_id,
      claim: capability.claim,
      evidence_level: capability.evidence_level,
      status: capability.status ?? "HYPOTHESIZED",
      confidence: capability.confidence ?? "LOW",
      baseline_id: capability.baseline_id ?? null,
    })),
    baselines: state.baselines.map((baseline) => structuredClone(baseline)),
    human_validation: structuredClone(state.human_validation),
    last_change: structuredClone(state.last_change),
    integrity: {
      receipt_verified: receiptVerification.verified,
      receipt_reason: receiptVerification.reason,
      receipt_id: snapshot.receipt?.receipt_id ?? null,
    },
  };
}

function list(items, empty = "无") {
  return items.length ? items.map((item) => `- ${item}`).join("\n") : `- ${empty}`;
}

export function renderProjectSummary(summary) {
  const baselineText = summary.baselines.length
    ? summary.baselines.map((item) => `${item.baseline_id}（${item.evidence_level}，${item.environment}）`)
    : ["未建立"];
  const budget = summary.human_validation.limit === "UNSET"
    ? "未由 Maker 设置"
    : `${summary.human_validation.consumed} / ${summary.human_validation.limit}`;
  return [
    "# 项目状态摘要",
    "",
    "## 项目与边界",
    `- 项目：${summary.project.project_id}（revision ${summary.project.revision}）`,
    `- 目标：${summary.boundary.objective}`,
    `- 支持：${summary.boundary.supported.join("；") || "无"}`,
    `- 排除：${summary.boundary.excluded.join("；") || "无"}`,
    "",
    "## 路由与阶段",
    `- 项目类型：${summary.routing.project_type_id}`,
    `- Child Skill：${summary.routing.child_skill_id}`,
    `- Host Profile：${summary.routing.host_profile_id ?? "未设置"}`,
    `- 阶段：${summary.workflow.stage} / ${summary.workflow.status}`,
    `- 合法下一步：${summary.workflow.allowed_next.join("；") || "无"}`,
    "",
    "## 最近完成与证据上限",
    list(summary.recent_completed),
    `- 当前最高证据等级：${summary.evidence_ceiling}`,
    "",
    "## 当前行动",
    `- 当前：${summary.actions.current}`,
    `- 下一步：${summary.actions.next}`,
    `- 完成条件：${summary.actions.completion_conditions.join("；") || "无"}`,
    "",
    "## 阻塞与风险",
    list(summary.blockers.map((item) => `${item.gate_id}：${item.reason ?? item.status}`)),
    list(summary.risks.map((item) => `${item.risk_id}（${item.severity}）：${item.summary}`)),
    "",
    "## 待 Maker 决策",
    list(summary.maker_decisions.map((item) => `${item.request_id}：${item.operation}`)),
    "",
    "## 能力、基线与人工验证",
    list(summary.capabilities.map((item) => `${item.capability_id}：${item.claim} [${item.evidence_level}/${item.confidence}]`)),
    `- Known-Good Baseline：${baselineText.join("；")}`,
    `- 人工验证预算：${budget}`,
    "",
    "## 最近变更与完整性",
    `- 最近变更：${summary.last_change.operation}；${summary.last_change.summary}`,
    `- Receipt：${summary.integrity.receipt_verified ? "已验证" : `不可验证（${summary.integrity.receipt_reason}）`}`,
    `- receipt_id：${summary.integrity.receipt_id ?? "无"}`,
    "",
  ].join("\n");
}

export async function writeProjectOverview(root, summary, promptRef, options = {}) {
  const stored = await readPrompt(promptRef);
  if (stored.project_id !== summary.project.project_id) throw new Error("PROMPT_CONTEXT_MISMATCH");
  const age = await promptAgeMs(promptRef, options.now ?? new Date());
  if (age < 0 || age > promptPolicy.maxAgeMs) {
    await consumePrompt(promptRef);
    throw new Error("PROMPT_EXPIRED");
  }
  if (!/(?:明确)?导出[^。\n]*(?:项目)?(?:状态)?概览|export[^\n]*project[^\n]*overview/iu.test(stored.excerpt)) {
    throw new Error("EXPLICIT_EXPORT_REQUEST_REQUIRED");
  }
  const target = path.join(root, "PROJECT_OVERVIEW.md");
  const temporary = `${target}.${randomUUID()}.tmp`;
  const content = [
    "> 本文件是非权威、可重建的人读视图；项目判断只以 `.project-incubator/` 中经过校验的机器状态为准。",
    "",
    renderProjectSummary(summary),
  ].join("\n");
  try {
    await writeFile(temporary, content, "utf8");
    await rename(temporary, target);
  } catch (error) {
    await rm(temporary, { force: true });
    throw error;
  }
  await consumePrompt(promptRef);
  return { path: target, project_id: summary.project.project_id, revision: summary.project.revision };
}
