import { useEffect, useState } from "react";
import { api, Agent } from "../api";

export default function AgentList() {
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    api.getAgents().then(setAgents).catch(() => {});
  }, []);

  const statusColor = (status: string) => {
    if (status === "active") return "text-success";
    if (status === "pending") return "text-warning";
    return "text-error";
  };

  const statusDot = (status: string) => {
    if (status === "active") return "bg-success";
    if (status === "pending") return "bg-warning";
    return "bg-error";
  };

  return (
    <section>
      <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">
        Agents
        <span className="ml-2 text-text-muted font-mono font-normal">
          {agents.length}
        </span>
      </h2>

      {agents.length === 0 ? (
        <div className="text-sm text-text-muted py-8 text-center">
          No agents registered
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-surface-raised text-text-secondary text-left">
                <th className="px-3 py-2 font-medium">Name</th>
                <th className="px-3 py-2 font-medium">Model</th>
                <th className="px-3 py-2 font-medium">Description</th>
                <th className="px-3 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {agents.map((a) => (
                <tr key={a.id} className="hover:bg-surface-raised/50 transition-colors">
                  <td className="px-3 py-2 font-mono font-semibold text-text-primary">
                    {a.name}
                  </td>
                  <td className="px-3 py-2 font-mono text-text-muted">
                    {a.model}
                  </td>
                  <td className="px-3 py-2 text-text-secondary">
                    {a.description}
                  </td>
                  <td className="px-3 py-2">
                    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${statusColor(a.status)}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${statusDot(a.status)}`} />
                      {a.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
