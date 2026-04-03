import { useState, useEffect } from "react";
import { api, Agent, Skill, Rule, GitHubLoadResponse } from "./api";
import DiagramView from "./components/DiagramView";
import LoadingSpinner from "./components/LoadingSpinner";

type Tab = "agents" | "skills" | "rules" | "diagram";

const STORAGE_KEY = "make-agent:cache";

interface CachedData {
  url: string;
  project: GitHubLoadResponse;
  agents: Agent[];
  skills: Skill[];
  rules: Rule[];
  savedAt: number;
}

function loadCache(): CachedData | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function saveCache(data: CachedData) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch { /* quota exceeded — ignore */ }
}

const TAB_CONFIG: Record<string, { label: string; icon: string; color: string }> = {
  agents: { label: "Agents", icon: "A", color: "agent" },
  skills: { label: "Skills", icon: "S", color: "skill" },
  rules: { label: "Rules", icon: "R", color: "rule" },
  diagram: { label: "Diagram", icon: "D", color: "accent" },
};

function App() {
  const cached = loadCache();
  const [url, setUrl] = useState(cached?.url ?? "");
  const [project, setProject] = useState<GitHubLoadResponse | null>(cached?.project ?? null);
  const [agents, setAgents] = useState<Agent[]>(cached?.agents ?? []);
  const [skills, setSkills] = useState<Skill[]>(cached?.skills ?? []);
  const [rules, setRules] = useState<Rule[]>(cached?.rules ?? []);
  const [tab, setTab] = useState<Tab>("agents");
  const [selected, setSelected] = useState<Agent | Skill | Rule | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mobileView, setMobileView] = useState<"list" | "detail">("list");

  useEffect(() => {
    if (cached?.url && cached?.project) {
      api.loadProject(cached.url).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
      setTab("agents");
      setMobileView("list");
      saveCache({ url, project: proj, agents: a, skills: s, rules: r, savedAt: Date.now() });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
    setLoading(false);
  };

  const handleSelect = (item: Agent | Skill | Rule) => {
    setSelected(item);
    setMobileView("detail");
  };

  const handleBack = () => {
    setSelected(null);
    setMobileView("list");
  };

  const tabItems: { key: Tab; count: number | null }[] = [
    { key: "agents", count: agents.length },
    { key: "skills", count: skills.length },
    { key: "rules", count: rules.length },
    { key: "diagram", count: null },
  ];

  const currentList = tab === "agents" ? agents : tab === "skills" ? skills : rules;

  /*
   * Layout (mobile):
   *   h-screen flex flex-col
   *   ├── header        (auto height)
   *   ├── content        (flex-1, min-h-0 → 남은 공간 전체)
   *   └── bottom-nav     (auto height, flex-shrink-0)
   *
   * Layout (desktop):
   *   h-screen flex flex-col
   *   ├── header
   *   └── content        (flex-1, min-h-0, flex-row)
   *       ├── left-nav   (w-14)
   *       ├── sidebar    (w-72)
   *       └── main       (flex-1)
   */

  return (
    <div className="app-shell bg-surface text-text-primary">
      {/* ─── Header ─── */}
      <header className="flex-shrink-0 flex items-center gap-2 sm:gap-4 px-3 sm:px-5 py-2.5 sm:py-3
                          border-b border-border bg-surface-raised/80 backdrop-blur-sm">
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="w-7 h-7 rounded-lg bg-accent/20 flex items-center justify-center">
            <span className="text-accent font-bold text-xs font-mono">M</span>
          </div>
          <h1 className="text-sm font-semibold tracking-tight hidden sm:block">make-agent</h1>
        </div>
        <form
          onSubmit={(e) => { e.preventDefault(); handleLoad(); }}
          className="flex-1 flex gap-2"
        >
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="github.com/owner/repo"
            className="flex-1 min-w-0 pl-3 pr-3 py-2 text-base sm:text-sm bg-surface border border-border rounded-lg
                       text-text-primary placeholder:text-text-muted
                       focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-4 sm:px-5 py-2 text-sm font-medium bg-accent hover:bg-accent-hover
                       text-white rounded-lg transition-all disabled:opacity-50 active:scale-[0.98] flex-shrink-0"
          >
            {loading ? <LoadingSpinner size="sm" /> : "Load"}
          </button>
        </form>
        {project && (
          <div className="items-center gap-2 text-xs hidden md:flex">
            <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
            <span className="text-text-secondary font-mono">{project.owner}/{project.repo}</span>
          </div>
        )}
      </header>

      {error && (
        <div className="flex-shrink-0 px-3 sm:px-5 py-2 text-sm bg-error/5 text-error border-b border-error/10
                        flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-error flex-shrink-0" />
          <span className="truncate">{error}</span>
        </div>
      )}

      {/* ─── Content ─── */}
      {!project ? (
        <Landing />
      ) : (
        <div className="flex-1 min-h-0 flex flex-col md:flex-row overflow-hidden">

          {/* Desktop: Left Nav (in-flow) */}
          <nav className="hidden md:flex md:w-14 md:flex-col items-center py-3 gap-1
                          border-r border-border bg-surface flex-shrink-0">
            {tabItems.map((t) => {
              const cfg = TAB_CONFIG[t.key];
              const isActive = tab === t.key;
              return (
                <button
                  key={t.key}
                  onClick={() => { setTab(t.key); setSelected(null); setMobileView("list"); }}
                  className={`w-10 h-10 rounded-lg flex flex-col items-center justify-center gap-0.5
                              transition-all text-xs relative
                              ${isActive
                                ? `bg-${cfg.color}/15 text-${cfg.color}`
                                : "text-text-muted hover:text-text-secondary hover:bg-surface-raised"
                              }`}
                  title={cfg.label}
                >
                  <span className="font-mono font-bold text-[11px]">{cfg.icon}</span>
                  {t.count !== null && (
                    <span className="text-[9px] leading-none opacity-60">{t.count}</span>
                  )}
                  {isActive && (
                    <span className={`absolute left-0 top-2 bottom-2 w-0.5 rounded-r bg-${cfg.color}`} />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Main content area — flex-1 between desktop-nav and (nothing on desktop / bottom-nav on mobile) */}
          <div className="flex-1 min-h-0 min-w-0 flex flex-col md:flex-row overflow-hidden">
            {tab === "diagram" ? (
              <DiagramView />
            ) : (
              <>
                {/* Sidebar */}
                <aside className={`md:w-72 md:border-r border-border flex flex-col bg-surface min-h-0
                                   ${mobileView === "detail" ? "hidden md:flex" : "flex"} flex-1 md:flex-none`}>
                  <div className="flex-shrink-0 px-3 py-2.5 border-b border-border flex items-center justify-between">
                    <h2 className="text-xs font-semibold text-text-secondary uppercase tracking-widest">
                      {TAB_CONFIG[tab].label}
                    </h2>
                    {project && (
                      <span className="text-[10px] text-text-muted font-mono md:hidden">
                        {project.owner}/{project.repo}
                      </span>
                    )}
                  </div>
                  <div className="flex-1 min-h-0 overflow-y-auto overscroll-contain">
                    {currentList.map((item) => (
                      <SidebarItem
                        key={item.name}
                        item={item}
                        tab={tab}
                        isSelected={selected?.name === item.name}
                        onSelect={() => handleSelect(item)}
                      />
                    ))}
                    {currentList.length === 0 && (
                      <div className="px-4 py-12 text-center text-text-muted text-xs">
                        No {tab} found
                      </div>
                    )}
                  </div>
                </aside>

                {/* Detail */}
                <main className={`flex-1 min-h-0 overflow-y-auto overscroll-contain
                                  ${mobileView === "list" ? "hidden md:block" : "block"}`}>
                  {!selected ? (
                    <EmptyDetail tab={tab} />
                  ) : (
                    <DetailPanel item={selected} tab={tab} onBack={handleBack} />
                  )}
                </main>
              </>
            )}
          </div>
        </div>
      )}

      {/* ─── Mobile Bottom Nav (in-flow, flex-shrink-0) ─── */}
      {project && (
        <nav className="md:hidden flex-shrink-0 flex items-center justify-around
                        py-1.5 bg-surface border-t border-border safe-bottom">
          {tabItems.map((t) => {
            const cfg = TAB_CONFIG[t.key];
            const isActive = tab === t.key;
            return (
              <button
                key={t.key}
                onClick={() => { setTab(t.key); setSelected(null); setMobileView("list"); }}
                className={`w-12 h-10 rounded-lg flex flex-col items-center justify-center gap-0.5
                            transition-all text-xs relative
                            ${isActive
                              ? `bg-${cfg.color}/15 text-${cfg.color}`
                              : "text-text-muted hover:text-text-secondary hover:bg-surface-raised"
                            }`}
              >
                <span className="font-mono font-bold text-[11px]">{cfg.icon}</span>
                <span className="text-[9px] leading-none opacity-60">{cfg.label}</span>
                {isActive && (
                  <span className={`absolute bottom-0 left-3 right-3 h-0.5 rounded-t bg-${cfg.color}`} />
                )}
              </button>
            );
          })}
        </nav>
      )}
    </div>
  );
}

/* ─── Landing ─── */
function Landing() {
  return (
    <div className="flex-1 flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-accent/10 flex items-center justify-center mx-auto mb-5 sm:mb-6">
          <span className="text-accent font-bold text-xl sm:text-2xl font-mono">M</span>
        </div>
        <h2 className="text-lg sm:text-xl font-semibold mb-2">Claude Code Configuration Viewer</h2>
        <p className="text-text-muted text-sm leading-relaxed mb-6 sm:mb-8">
          GitHub repository URL을 입력하면<br />
          .claude 디렉토리의 에이전트, 스킬, 규칙을 분석합니다.
        </p>
        <div className="flex flex-col gap-2 text-xs text-text-muted">
          <div className="flex items-center gap-3 justify-center">
            <span className="w-5 h-5 rounded bg-agent/15 text-agent flex items-center justify-center font-mono font-bold text-[10px]">A</span>
            <span>Agents — 에이전트 계층 구조</span>
          </div>
          <div className="flex items-center gap-3 justify-center">
            <span className="w-5 h-5 rounded bg-skill/15 text-skill flex items-center justify-center font-mono font-bold text-[10px]">S</span>
            <span>Skills — 스킬 파이프라인</span>
          </div>
          <div className="flex items-center gap-3 justify-center">
            <span className="w-5 h-5 rounded bg-rule/15 text-rule flex items-center justify-center font-mono font-bold text-[10px]">R</span>
            <span>Rules — 규칙 적용 범위</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── Sidebar Item ─── */
function SidebarItem({
  item, tab, isSelected, onSelect,
}: {
  item: Agent | Skill | Rule;
  tab: Tab;
  isSelected: boolean;
  onSelect: () => void;
}) {
  const cfg = TAB_CONFIG[tab];
  return (
    <button
      onClick={onSelect}
      className={`w-full text-left px-3 py-2.5 border-b border-border-subtle transition-all
                  ${isSelected
                    ? `bg-${cfg.color}/8 border-l-2 border-l-${cfg.color}`
                    : "hover:bg-surface-raised border-l-2 border-l-transparent"
                  }`}
    >
      <div className="flex items-center gap-2">
        {tab === "agents" && <ModelBadge model={(item as Agent).model} />}
        {tab === "skills" && (
          <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium flex-shrink-0
                          ${(item as Skill).user_invocable ? "bg-skill/15 text-skill" : "bg-surface-overlay text-text-muted"}`}>
            {(item as Skill).user_invocable ? "CMD" : "INT"}
          </span>
        )}
        {tab === "rules" && (
          <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium flex-shrink-0
                          ${(item as Rule).always_loaded ? "bg-warning/15 text-warning" : "bg-surface-overlay text-text-muted"}`}>
            {(item as Rule).always_loaded ? "ALL" : "PATH"}
          </span>
        )}
        <span className={`font-mono text-xs font-medium truncate ${isSelected ? `text-${cfg.color}` : "text-text-primary"}`}>
          {item.name}
        </span>
        <span className="ml-auto text-text-muted text-xs md:hidden">&rsaquo;</span>
      </div>
      <p className="text-text-muted text-[11px] mt-1 truncate pl-0.5">
        {"description" in item ? (item as Agent | Skill).description : ""}
        {"category" in item ? (item as Rule).category : ""}
      </p>
    </button>
  );
}

function ModelBadge({ model }: { model: string }) {
  const isOpus = model.includes("opus");
  return (
    <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium font-mono flex-shrink-0
                    ${isOpus ? "bg-accent/15 text-accent" : "bg-surface-overlay text-text-secondary"}`}>
      {model}
    </span>
  );
}

function EmptyDetail({ tab }: { tab: Tab }) {
  const cfg = TAB_CONFIG[tab];
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className={`w-12 h-12 rounded-xl bg-${cfg.color}/10 flex items-center justify-center mx-auto mb-3`}>
          <span className={`text-${cfg.color} font-mono font-bold`}>{cfg.icon}</span>
        </div>
        <p className="text-text-muted text-sm">좌측에서 {cfg.label.toLowerCase()}을 선택하세요</p>
      </div>
    </div>
  );
}

function DetailPanel({ item, tab, onBack }: { item: Agent | Skill | Rule; tab: Tab; onBack: () => void }) {
  const cfg = TAB_CONFIG[tab];
  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6">
      <button
        onClick={onBack}
        className="md:hidden flex items-center gap-1.5 text-xs text-text-muted mb-4
                   hover:text-text-secondary transition-colors"
      >
        <span>&lsaquo;</span>
        <span>{TAB_CONFIG[tab].label} 목록</span>
      </button>

      <div className="flex items-start gap-3 sm:gap-4 mb-5 sm:mb-6">
        <div className={`w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-${cfg.color}/15 flex items-center justify-center flex-shrink-0 mt-0.5`}>
          <span className={`text-${cfg.color} font-mono font-bold text-sm`}>{cfg.icon}</span>
        </div>
        <div className="min-w-0">
          <h2 className="text-base sm:text-lg font-semibold tracking-tight break-words">{item.name}</h2>
          <p className="text-[11px] sm:text-xs text-text-muted font-mono mt-0.5 break-all">{item.file_path}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-3 mb-5 sm:mb-6">
        {tab === "agents" && (
          <>
            <MetaCard label="Model" value={(item as Agent).model} accent={(item as Agent).model.includes("opus")} />
            <MetaCard label="Memory" value={(item as Agent).memory || "none"} />
            <MetaCard label="Description" value={(item as Agent).description} wide />
          </>
        )}
        {tab === "skills" && (
          <>
            <MetaCard label="Invocable" value={(item as Skill).user_invocable ? "User-invocable" : "Internal"} accent={(item as Skill).user_invocable} />
            <MetaCard label="Argument" value={(item as Skill).argument_hint || "none"} />
            <MetaCard label="Description" value={(item as Skill).description} wide />
            {(item as Skill).references.length > 0 && (
              <MetaCard label="References" value={(item as Skill).references.join(", ")} wide />
            )}
          </>
        )}
        {tab === "rules" && (
          <>
            <MetaCard label="Category" value={(item as Rule).category} />
            <MetaCard label="Loading" value={(item as Rule).always_loaded ? "Always" : "Path-matched"} accent={(item as Rule).always_loaded} />
            {(item as Rule).paths.length > 0 && (
              <MetaCard label="Paths" value={(item as Rule).paths.join(", ")} wide />
            )}
          </>
        )}
      </div>

      <div>
        <div className="flex items-center gap-2 mb-3">
          <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-widest">Body</h3>
          <span className="flex-1 h-px bg-border" />
        </div>
        <pre className="p-3 sm:p-4 bg-surface-raised rounded-xl border border-border text-xs sm:text-sm font-mono
                        whitespace-pre-wrap leading-relaxed overflow-x-auto text-text-secondary">
          {item.body}
        </pre>
      </div>
    </div>
  );
}

function MetaCard({ label, value, wide, accent }: {
  label: string; value: string; wide?: boolean; accent?: boolean;
}) {
  return (
    <div className={`p-3 bg-surface-raised rounded-xl border border-border ${wide ? "sm:col-span-2 lg:col-span-3" : ""}`}>
      <div className="text-[10px] text-text-muted uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-sm font-mono break-words ${accent ? "text-accent" : "text-text-primary"}`}>{value}</div>
    </div>
  );
}

export default App;
