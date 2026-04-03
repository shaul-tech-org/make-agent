import { useState } from "react";
import { api, RouteResult } from "../api";

export default function RequestForm() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<RouteResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.sendRequest(input);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
      setResult(null);
    }
    setLoading(false);
  };

  const complexityColor = (c: string) => {
    if (c === "simple") return "text-success";
    if (c === "complex") return "text-error";
    return "text-text-muted";
  };

  return (
    <section>
      <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">
        Request
      </h2>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="요청을 입력하세요..."
          className="flex-1 px-3 py-2 text-sm bg-surface-raised border border-border rounded-md
                     text-text-primary placeholder:text-text-muted
                     focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 text-sm font-medium bg-accent hover:bg-accent-hover
                     text-white rounded-md transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            "Send"
          )}
        </button>
      </form>

      {error && (
        <div className="mt-3 px-3 py-2 text-sm bg-error/10 text-error border border-error/20 rounded-md">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-3 p-4 bg-surface-raised border border-border rounded-lg">
          <div className="flex gap-4 text-sm mb-3">
            <span className="text-text-secondary">
              Complexity:{" "}
              <strong className={`font-mono ${complexityColor(result.complexity)}`}>
                {result.complexity}
              </strong>
            </span>
            <span className="text-text-secondary">
              Agent:{" "}
              <strong className="font-mono text-text-primary">{result.agent}</strong>
            </span>
            <span className="text-text-secondary">
              Category:{" "}
              <strong className="font-mono text-text-primary">{result.category}</strong>
            </span>
          </div>

          {result.delegation_plan && (
            <div className="border-t border-border pt-3 mt-3">
              <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                Delegation Plan
              </h3>

              <div className="mb-3">
                <h4 className="text-xs text-text-muted mb-1">
                  CEO Tasks ({result.delegation_plan.ceo_tasks.length})
                </h4>
                <ul className="space-y-1 text-sm">
                  {result.delegation_plan.ceo_tasks.map((t) => (
                    <li key={t.id} className="flex items-center gap-2">
                      <span className="font-mono text-xs px-1.5 py-0.5 bg-surface-overlay rounded text-accent">
                        {t.type}
                      </span>
                      <span className="text-text-primary">{t.name}</span>
                      {t.depends_on.length > 0 && (
                        <span className="text-text-muted text-xs">
                          dep: {t.depends_on.join(", ")}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mb-3">
                <h4 className="text-xs text-text-muted mb-1">Execution Phases</h4>
                <div className="space-y-2">
                  {result.delegation_plan.phases.map((p) => (
                    <div key={p.phase}>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-mono font-semibold text-text-primary">
                          Phase {p.phase}
                        </span>
                        {p.parallel && (
                          <span className="text-xs px-1.5 py-0.5 bg-accent/15 text-accent rounded">
                            parallel
                          </span>
                        )}
                      </div>
                      <ul className="ml-4 mt-1 space-y-0.5 text-sm text-text-secondary">
                        {p.tasks.map((t, i) => (
                          <li key={i} className="before:content-['·'] before:mr-2 before:text-text-muted">
                            {t}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-xs text-text-muted mb-1">Agent Summary</h4>
                <div className="flex gap-2 flex-wrap">
                  {result.delegation_plan.agent_summary.map((a) => (
                    <span
                      key={a.agent}
                      className="px-2 py-0.5 bg-surface-overlay text-text-secondary text-xs font-mono rounded-full"
                    >
                      {a.agent}: {a.task_count}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
