import { useEffect, useState } from "react";
import { api, OrgChartNode, OrgChartData } from "../api";

const MODEL_STYLES: Record<string, { bg: string; border: string; text: string; badge: string }> = {
  board: { bg: "bg-warning/10", border: "border-warning/30", text: "text-warning", badge: "BOARD" },
  opus: { bg: "bg-accent/10", border: "border-accent/30", text: "text-accent", badge: "opus" },
  sonnet: { bg: "bg-info/10", border: "border-info/30", text: "text-info", badge: "sonnet" },
};

function getStyle(model: string) {
  if (model === "board") return MODEL_STYLES.board;
  if (model.includes("opus")) return MODEL_STYLES.opus;
  return MODEL_STYLES.sonnet;
}

export default function OrgChartView() {
  const [data, setData] = useState<OrgChartData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api.getOrgChart()
      .then(setData)
      .catch(e => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-full text-text-muted text-sm">
      조직도 로딩 중...
    </div>
  );

  if (error) return (
    <div className="flex items-center justify-center h-full">
      <div className="text-error text-sm">{error}</div>
    </div>
  );

  if (!data) return null;

  return (
    <div className="h-full overflow-auto overscroll-contain p-4 sm:p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-widest mb-1">
            Organization Chart
          </h2>
          <p className="text-xs text-text-muted">rules/governance/org-chart.md 기반 조직 구성도</p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 mb-6 text-xs text-text-muted">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-warning/20 border border-warning/30" />
            Board
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-accent/20 border border-accent/30" />
            Opus
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-info/20 border border-info/30" />
            Sonnet
          </span>
        </div>

        <OrgNode node={data.tree} depth={0} isLast={true} />
      </div>
    </div>
  );
}

function OrgNode({ node, depth }: { node: OrgChartNode; depth: number; isLast?: boolean }) {
  const style = getStyle(node.model);
  const hasChildren = node.children.length > 0;

  return (
    <div className={depth > 0 ? "ml-4 sm:ml-8" : ""}>
      {/* Connector line */}
      {depth > 0 && (
        <div className="flex items-center h-4 ml-4">
          <div className="w-px h-full bg-border" />
        </div>
      )}

      {/* Node card */}
      <div className={`${style.bg} border ${style.border} rounded-xl p-3 sm:p-4 transition-all
                        hover:brightness-110`}>
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Avatar */}
          <div className={`w-8 h-8 sm:w-10 sm:h-10 rounded-lg ${style.bg} border ${style.border}
                          flex items-center justify-center flex-shrink-0`}>
            <span className={`${style.text} font-mono font-bold text-xs sm:text-sm`}>
              {node.name.charAt(0).toUpperCase()}
            </span>
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm sm:text-base text-text-primary truncate">
                {node.name}
              </span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium flex-shrink-0
                              ${style.bg} ${style.text} border ${style.border}`}>
                {style.badge}
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-text-muted mt-0.5 truncate">{node.role}</p>
          </div>

          {hasChildren && (
            <span className="text-[10px] text-text-muted flex-shrink-0">
              {node.children.length}
            </span>
          )}
        </div>
      </div>

      {/* Children */}
      {hasChildren && (
        <div className="relative">
          {/* Vertical connector */}
          <div className="absolute left-4 top-0 w-px bg-border"
               style={{ height: "100%" }} />

          {node.children.map((child, i) => (
            <OrgNode
              key={child.name}
              node={child}
              depth={depth + 1}
              isLast={i === node.children.length - 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}
