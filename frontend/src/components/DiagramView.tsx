import { useEffect, useRef, useState, useMemo } from "react";
import mermaid from "mermaid";
import { api, DiagramData } from "../api";

mermaid.initialize({
  startOnLoad: false,
  securityLevel: "loose",
  maxEdges: 500,
  maxTextSize: 100000,
  theme: "dark",
  themeVariables: {
    primaryColor: "#3b82f6",
    primaryTextColor: "#f1f5f9",
    primaryBorderColor: "#1d4ed8",
    lineColor: "#64748b",
    secondaryColor: "#10b981",
    tertiaryColor: "#f59e0b",
    background: "#1e293b",
    mainBkg: "#1e293b",
    nodeBorder: "#334155",
    clusterBkg: "#0f172a",
    titleColor: "#f1f5f9",
    edgeLabelBackground: "#1e293b",
  },
  flowchart: {
    curve: "basis",
    padding: 16,
    htmlLabels: true,
  },
});

type Filter = "all" | "agents" | "skills" | "rules" | "agents+skills";

function buildFilteredMermaid(data: DiagramData, filter: Filter): string {
  const lines = ["graph TD"];
  lines.push("    classDef agent fill:#3b82f6,stroke:#1d4ed8,color:#fff");
  lines.push("    classDef skill fill:#10b981,stroke:#047857,color:#fff");
  lines.push("    classDef rule fill:#f59e0b,stroke:#b45309,color:#fff");

  const showTypes = new Set<string>();
  if (filter === "all") { showTypes.add("agent"); showTypes.add("skill"); showTypes.add("rule"); }
  else if (filter === "agents") { showTypes.add("agent"); }
  else if (filter === "skills") { showTypes.add("skill"); }
  else if (filter === "rules") { showTypes.add("rule"); }
  else if (filter === "agents+skills") { showTypes.add("agent"); showTypes.add("skill"); }

  const visibleIds = new Set<string>();
  for (const n of data.nodes) {
    if (!showTypes.has(n.type)) continue;
    visibleIds.add(n.id);
    const safe = n.id.replace(/-/g, "_");
    if (n.type === "agent") {
      const model = (n.metadata.model as string) || "";
      lines.push(`    ${safe}["${n.name}<br/><small>${model}</small>"]:::agent`);
    } else if (n.type === "skill") {
      const inv = n.metadata.user_invocable ? "⚡" : "";
      lines.push(`    ${safe}(["${inv}${n.name}"]):::skill`);
    } else {
      const scope = n.metadata.always_loaded ? "🌐" : "📁";
      lines.push(`    ${safe}{{{"${scope}${n.name}"}}}:::rule`);
    }
  }

  for (const e of data.edges) {
    if (!visibleIds.has(e.source) || !visibleIds.has(e.target)) continue;
    const src = e.source.replace(/-/g, "_");
    const tgt = e.target.replace(/-/g, "_");
    if (e.label) {
      lines.push(`    ${src} -->|${e.label}| ${tgt}`);
    } else {
      lines.push(`    ${src} --> ${tgt}`);
    }
  }

  return lines.join("\n");
}

export default function DiagramView() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<DiagramData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [renderError, setRenderError] = useState<string | null>(null);
  const [logsOpen, setLogsOpen] = useState(false);
  const [filter, setFilter] = useState<Filter>("agents");

  const loadDiagram = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getDiagram();
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load diagram");
    }
    setLoading(false);
  };

  useEffect(() => {
    loadDiagram();
  }, []);

  const filteredMermaid = useMemo(() => {
    if (!data) return "";
    return buildFilteredMermaid(data, filter);
  }, [data, filter]);

  useEffect(() => {
    if (!filteredMermaid || !containerRef.current) return;

    const render = async () => {
      setRenderError(null);
      try {
        containerRef.current!.innerHTML = "";
        const id = `mermaid-${Date.now()}`;
        const { svg } = await mermaid.render(id, filteredMermaid);
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
          const svgEl = containerRef.current.querySelector("svg");
          if (svgEl) {
            svgEl.style.maxWidth = "100%";
            svgEl.style.height = "auto";
          }
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setRenderError(msg);
        console.error("Mermaid render error:", e);
      }
    };
    render();
  }, [filteredMermaid]);

  const filters: { key: Filter; label: string }[] = [
    { key: "agents", label: "Agents" },
    { key: "skills", label: "Skills" },
    { key: "rules", label: "Rules" },
    { key: "agents+skills", label: "Agents + Skills" },
    { key: "all", label: "All" },
  ];

  const stats = data ? {
    agents: data.nodes.filter(n => n.type === "agent").length,
    skills: data.nodes.filter(n => n.type === "skill").length,
    rules: data.nodes.filter(n => n.type === "rule").length,
    edges: data.edges.length,
  } : null;

  return (
    <div className="flex flex-col h-full">
      {/* Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between
                      px-3 sm:px-4 py-2 border-b border-border bg-surface-raised gap-2">
        <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {filters.map(f => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-2.5 sm:px-3 py-1 text-[11px] sm:text-xs rounded transition-colors whitespace-nowrap flex-shrink-0 ${
                filter === f.key
                  ? "bg-accent text-white"
                  : "bg-surface border border-border text-text-secondary hover:text-text-primary"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          {stats && (
            <div className="flex items-center gap-2 sm:gap-3 text-[11px] sm:text-xs text-text-muted">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded bg-[#3b82f6] inline-block" />
                {stats.agents}
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded bg-[#10b981] inline-block" />
                {stats.skills}
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded bg-[#f59e0b] inline-block" />
                {stats.rules}
              </span>
              <span className="hidden sm:inline">{stats.edges} edges</span>
            </div>
          )}
          <button
            onClick={() => setLogsOpen(!logsOpen)}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              logsOpen
                ? "bg-accent text-white"
                : "bg-surface border border-border text-text-secondary hover:text-text-primary"
            }`}
          >
            Logs
          </button>
          <button
            onClick={loadDiagram}
            disabled={loading}
            className="px-3 py-1 text-xs bg-surface border border-border text-text-secondary
                       hover:text-text-primary rounded transition-colors disabled:opacity-50"
          >
            {loading ? "..." : "Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <div className="px-4 py-2 text-sm bg-error/10 text-error border-b border-error/20">
          {error}
        </div>
      )}

      <div className="flex-1 flex overflow-hidden relative">
        {/* Diagram */}
        <div className="flex-1 overflow-auto p-4 flex items-start justify-center">
          {loading && !data ? (
            <div className="flex items-center justify-center h-full text-text-muted text-sm">
              다이어그램 생성 중...
            </div>
          ) : renderError ? (
            <div className="max-w-lg p-4 bg-error/10 text-error rounded text-sm">
              <p className="font-semibold mb-2">렌더링 오류</p>
              <pre className="text-xs whitespace-pre-wrap">{renderError}</pre>
            </div>
          ) : (
            <div ref={containerRef} className="min-w-0" />
          )}
        </div>

        {/* Log Panel */}
        {logsOpen && data?.logs && (
          <aside className="absolute inset-0 sm:relative sm:inset-auto w-full sm:w-80
                            border-l border-border bg-surface overflow-y-auto flex-shrink-0 z-10">
            <div className="px-3 py-2 border-b border-border sticky top-0 bg-surface-raised flex items-center justify-between">
              <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Process Logs
              </h3>
              <button
                onClick={() => setLogsOpen(false)}
                className="sm:hidden text-text-muted hover:text-text-primary text-sm px-1"
              >
                &times;
              </button>
            </div>
            <div className="p-3 space-y-1">
              {data.logs.map((log, i) => (
                <div
                  key={i}
                  className={`text-xs font-mono leading-relaxed ${
                    log.startsWith("[")
                      ? "text-accent font-semibold mt-2"
                      : "text-text-muted pl-2"
                  }`}
                >
                  {log}
                </div>
              ))}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}
