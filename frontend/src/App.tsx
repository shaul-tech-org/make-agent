import { useEffect, useState } from "react";
import AgentList from "./components/AgentList";
import RequestForm from "./components/RequestForm";

interface HealthStatus {
  status: string;
  version: string;
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then(setHealth)
      .catch(() => {});
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <header className="flex justify-between items-center mb-6 pb-4 border-b border-border">
        <div>
          <h1 className="text-lg font-semibold font-mono text-text-primary m-0">
            shaul-custom-agent
          </h1>
          <p className="text-sm text-text-muted mt-0.5">
            Coordinator Pattern Multi-Agent Dashboard
          </p>
        </div>
        {health && (
          <span className="px-2.5 py-0.5 bg-success/15 text-success text-xs font-mono rounded-full">
            v{health.version}
          </span>
        )}
      </header>

      <main className="flex flex-col gap-6">
        <RequestForm />
        <AgentList />
      </main>
    </div>
  );
}

export default App;
