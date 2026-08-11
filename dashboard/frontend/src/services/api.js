// 治理中心 API 客户端 (S67 spec §5 契约)
const BASE = '/api/governance';

async function get(path) {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

async function post(path, body) {
  const r = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

export const governanceApi = {
  agents: () => get('/agents'),
  agentAudit: (agentId, limit = 50) => get(`/agents/${agentId}/audit?limit=${limit}`),
  policies: () => get('/policies'),
  protocol: (name) => get(`/policies/${name}`),
  audit: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return get(`/audit?${q}`);
  },
  auditOne: (id) => get(`/audit/${id}`),
  vceLatest: () => get('/vce/latest'),
  vceHistory: (limit = 20) => get(`/vce/history?limit=${limit}`),
  vceScan: () => post('/vce/scan'),
  evaluate: (payload) => post('/evaluate', payload),
  // S69 策略编辑器
  protocolSource: (name) => get(`/policies/${name}/source`),
  policyValidate: (payload) => post('/policies/validate', payload),
  policyDeploy: (payload) => post('/policies/deploy', payload),
};
