const REQUIRED_CONSTRAINTS = Object.freeze({
  maker_authorization: "REQUIRED", state_mutation: "MCP_ONLY", receipt: "REQUIRED",
});

export function applySims4Profile(modPolicy, capability) {
  for (const [key, value] of Object.entries(REQUIRED_CONSTRAINTS)) {
    if (modPolicy.kernel_constraints?.[key] !== value) throw new Error("MOD_POLICY_WEAKENS_KERNEL");
  }
  if (!Array.isArray(capability.mod_types) || capability.mod_types.length === 0
    || capability.mod_types.some((type) => !["SCRIPT", "PACKAGE"].includes(type))) {
    throw new Error("SIMS4_MOD_TYPE_REQUIRED");
  }
  const checks = ["build_artifact_contents", "mods_install_structure", "loading_logs", "exceptions"];
  const facets = capability.facets ?? {};
  if (facets.ui) checks.push("ui_observation");
  if (facets.interaction) checks.push("interaction_observation");
  if (facets.persistence) checks.push("save_compatibility");
  if (facets.version_sensitive) checks.push("cross_version_matrix");
  return {
    host_profile_id: "sims-4",
    capability_id: capability.capability_id,
    kernel_constraints: { ...REQUIRED_CONSTRAINTS },
    minimum_evidence: modPolicy.minimum_evidence,
    gates: [...new Set([...(modPolicy.gates ?? []), "SIMS4_DELIVERY_VERIFIED"])],
    required_context: ["game_version", "patch_version", "mod_types"],
    verification_checks: checks,
    maker_observation_fields: [
      "scenario", "game_version", "patch_version", "observed_result",
      "failure_or_side_effect", "evidence_ref",
    ],
  };
}
