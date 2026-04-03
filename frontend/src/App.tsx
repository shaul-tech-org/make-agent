import { useState } from "react";
import { api, Agent, Skill, Rule, GitHubLoadResponse } from "./api";

type Tab = "agents" | "skills" | "rules";

function App() {
  const [url, setUrl] = useState("");
  const [project, setProject] = useState<GitHubLoadResponse | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [rules, setRules] = useState<Rule[]>([]);
  const [tab, setTab] = useState<Tab>("agents");
  const [selected, setSelected] = useState<Agent | Skill | Rule | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLoad = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const proj = await api.loadProject(url);
      setProject(proj);
      const [a, s, r] = await Promise.all([
        api.getAgents(),
        api.getSkills(),
        api.getRules(),
      ]);
      setAgents(a);
      setSkills(s);
      setRules(r);
      setSelected(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
    setLoading(false);
  };

  const tabItems: { key: Tab; label: string; count: number }[] = [
    { key: "agents", label: "Agents", count: agents.length },
    { key: "skills", label: "Skills", count: skills.length },
    { key: "rules", label: "Rules", count: rules.length },
  ];

  const currentList = tab === "agents" ? agents : tab === "skills" ? skills : rules;

  return (
    <div className="h-screen flex flex-col bg-surface text-text-primary">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 border-b border-border bg-surface-raised">
        <h1 className="text-sm font-semibold font-mono whitespace-nowrap">make-agent</h1>
        <form
          onSubmit={(e) => { e.preventDefault(); handleLoad(); }}
          className="flex-1 flex gap-2"
        >
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            className="flex-1 px-3 py-1.5 text-sm bg-surface border border-border rounded
                       text-text-primary placeholder:text-text-muted
                       focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-1.5 text-sm font-medium bg-accent hover:bg-accent-hover
                       text-white rounded transition-colors disabled:opacity-50"
          >
            {loading ? "Loading..." : "Load"}
          </button>
        </form>
        {project && (
          <span className="text-xs text-text-muted font-mono">
            {project.owner}/{project.repo}
          </span>
        )}
      </header>

      {error && (
        <div className="px-4 py-2 text-sm bg-error/10 text-error border-b border-error/20">
          {error}
        </div>
      )}

      {!project ? (
        <div className="flex-1 flex items-center justify-center text-text-muted text-sm">
          GitHub repo URL을 입력하여 .claude 설정을 조회하세요
        </div>
      ) : (
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <aside className="w-64 border-r border-border flex flex-col bg-surface">
            {/* Tabs */}
            <div className="flex border-b border-border">
              {tabItems.map((t) => (
                <button
                  key={t.key}
                  onClick={() => { setTab(t.key); setSelected(null); }}
                  className={`flex-1 px-2 py-2 text-xs font-medium transition-colors ${
                    tab === t.key
                      ? "text-accent border-b-2 border-accent"
                      : "text-text-muted hover:text-text-secondary"
                  }`}
                >
                  {t.label}
                  <span className="ml-1 text-text-muted">{t.count}</span>
                </button>
              ))}
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto">
              {currentList.map((item) => {
                const name = item.name;
                const isSelected = selected?.name === name;
                return (
                  <button
                    key={name}
                    onClick={() => setSelected(item)}
                    className={`w-full text-left px-3 py-2 text-sm border-b border-border-subtle transition-colors ${
                      isSelected
                        ? "bg-accent/10 text-accent"
                        : "text-text-secondary hover:bg-surface-raised"
                    }`}
                  >
                    <div className="font-mono font-medium text-xs">{name}</div>
                    <div className="text-text-muted text-xs truncate mt-0.5">
                      {"description" in item ? (item as Agent | Skill).description : ""}
                      {"category" in item ? (item as Rule).category : ""}
                    </div>
                  </button>
                );
              })}
              {currentList.length === 0 && (
                <div className="px-3 py-8 text-center text-text-muted text-xs">
                  No {tab} found
                </div>
              )}
            </div>
          </aside>

          {/* Detail Panel */}
          <main className="flex-1 overflow-y-auto p-4">
            {!selected ? (
              <div className="flex items-center justify-center h-full text-text-muted text-sm">
                좌측에서 항목을 선택하세요
              </div>
            ) : (
              <DetailPanel item={selected} tab={tab} />
            )}
          </main>
        </div>
      )}
    </div>
  );
}

function DetailPanel({ item, tab }: { item: Agent | Skill | Rule; tab: Tab }) {
  return (
    <div className="max-w-3xl">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-lg font-mono font-semibold">{item.name}</h2>
        <p className="text-sm text-text-muted mt-1">{item.file_path}</p>
      </div>

      {/* Frontmatter */}
      <div className="mb-4 p-3 bg-surface-raised rounded-lg border border-border">
        <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
          Frontmatter
        </h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          {tab === "agents" && (
            <>
              <Field label="model" value={(item as Agent).model} />
              <Field label="memory" value={(item as Agent).memory || "—"} />
              <Field label="description" value={(item as Agent).description} span2 />
            </>
          )}
          {tab === "skills" && (
            <>
              <Field label="user-invocable" value={(item as Skill).user_invocable ? "true" : "false"} />
              <Field label="argument-hint" value={(item as Skill).argument_hint || "—"} />
              <Field label="description" value={(item as Skill).description} span2 />
              {(item as Skill).references.length > 0 && (
                <div className="col-span-2">
                  <span className="text-text-muted text-xs">references: </span>
                  <span className="text-xs font-mono">
                    {(item as Skill).references.join(", ")}
                  </span>
                </div>
              )}
            </>
          )}
          {tab === "rules" && (
            <>
              <Field label="category" value={(item as Rule).category} />
              <Field
                label="loading"
                value={(item as Rule).always_loaded ? "always" : "path-matched"}
              />
              {(item as Rule).paths.length > 0 && (
                <div className="col-span-2">
                  <span className="text-text-muted text-xs">paths: </span>
                  <span className="text-xs font-mono">
                    {(item as Rule).paths.join(", ")}
                  </span>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Body */}
      <div>
        <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
          Body
        </h3>
        <pre className="p-3 bg-surface-raised rounded-lg border border-border text-sm font-mono whitespace-pre-wrap leading-relaxed overflow-x-auto">
          {item.body}
        </pre>
      </div>
    </div>
  );
}

function Field({ label, value, span2 }: { label: string; value: string; span2?: boolean }) {
  return (
    <div className={span2 ? "col-span-2" : ""}>
      <span className="text-text-muted text-xs">{label}: </span>
      <span className="text-text-primary text-xs font-mono">{value}</span>
    </div>
  );
}

export default App;
