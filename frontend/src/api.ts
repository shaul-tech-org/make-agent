const BASE = "/api/v1";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

// Types
export interface Agent {
  id: number;
  name: string;
  description: string;
  model: string;
  skills: string[];
  status: string;
}

export interface RouteResult {
  request: string;
  category: string;
  complexity: string;
  agent: string;
  delegation_plan: DelegationPlan | null;
}

export interface DelegationPlan {
  ceo_tasks: CeoTask[];
  cto_tasks: CtoTask[];
  phases: Phase[];
  agent_summary: AgentSummary[];
}

export interface CeoTask {
  id: number;
  name: string;
  type: string;
  depends_on: number[];
}

export interface CtoTask {
  id: number;
  ceo_task_id: number;
  name: string;
  agent: string;
  file_path: string | null;
  test_criteria: string | null;
}

export interface Phase {
  phase: number;
  tasks: string[];
  parallel: boolean;
}

export interface AgentSummary {
  agent: string;
  task_count: number;
}

export interface Comment {
  id: number;
  agent: string;
  task_id: string;
  type: string;
  content: string;
  escalate_to: string | null;
  timestamp: string;
}

// API calls
export const api = {
  getAgents: () => fetchJson<Agent[]>(`${BASE}/agents`),

  sendRequest: (request: string) =>
    fetchJson<RouteResult>(`${BASE}/request`, {
      method: "POST",
      body: JSON.stringify({ request }),
    }),

  getComments: (taskId?: string) => {
    const params = taskId ? `?task_id=${taskId}` : "";
    return fetchJson<Comment[]>(`${BASE}/communication/comments${params}`);
  },
};
