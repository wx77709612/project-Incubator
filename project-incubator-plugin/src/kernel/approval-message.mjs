export function changeApprovalMessage(requestId, scopeDigest) {
  return `我明确批准变更请求 ${requestId}，scope_digest: ${scopeDigest}。`;
}
