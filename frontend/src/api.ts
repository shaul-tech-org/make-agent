const BASE = "/api/v1";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || body.error || `${res.status} ${res.statusText}`);
  }
  return res.json();
}

export interface GitHubLoadResponse {
  owner: string;
  repo: string;
  branch: string | null;
  claude_dir_exists: boolean;
}

export interface FileTreeItem {
  path: string;
  type: "file" | "dir";
  size: number | null;
}

export interface Agent {
  name: string;
  description: string;
  model: string;
  memory: string | null;
  body: string;
  file_path: string;
}

export interface Skill {
  name: string;
  description: string;
  user_invocable: boolean;
  argument_hint: string | null;
  body: string;
  references: string[];
  file_path: string;
}

export interface Rule {
  name: string;
  category: string;
  paths: string[];
  body: string;
  file_path: string;
  always_loaded: boolean;
}

export interface FileContent {
  path: string;
  content: string;
  size: number;
}

export interface DiagramNode {
  id: string;
  type: string;
  name: string;
  label: string;
  metadata: Record<string, unknown>;
}

export interface DiagramEdge {
  source: string;
  target: string;
  type: string;
  label: string;
}

export interface DiagramData {
  nodes: DiagramNode[];
  edges: DiagramEdge[];
  mermaid: string;
  logs: string[];
}

export interface OrgChartNode {
  name: string;
  model: string;
  role: string;
  children: OrgChartNode[];
}

export interface OrgChartData {
  tree: OrgChartNode;
  mermaid: string;
}

export const api = {
  loadProject: (url: string) =>
    fetchJson<GitHubLoadResponse>(`${BASE}/github/load`, {
      method: "POST",
      body: JSON.stringify({ url }),
    }),

  getTree: () => fetchJson<{ files: FileTreeItem[] }>(`${BASE}/github/tree`),

  getFile: (path: string) =>
    fetchJson<FileContent>(`${BASE}/github/file?path=${encodeURIComponent(path)}`),

  getAgents: () => fetchJson<Agent[]>(`${BASE}/github/agents`),
  getSkills: () => fetchJson<Skill[]>(`${BASE}/github/skills`),
  getRules: () => fetchJson<Rule[]>(`${BASE}/github/rules`),
  getDiagram: () => fetchJson<DiagramData>(`${BASE}/github/diagram`),
  getOrgChart: () => fetchJson<OrgChartData>(`${BASE}/github/org-chart`),
};
