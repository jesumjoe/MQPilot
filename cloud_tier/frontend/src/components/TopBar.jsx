import { useState, useEffect } from "react";

export default function TopBar({ connected, lastUpdated }) {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const fmt = (d) =>
    d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  const fmtUpdated = (d) => {
    if (!d) return "—";
    const diff = Math.floor((Date.now() - d) / 1000);
    if (diff < 5)  return "just now";
    if (diff < 60) return `${diff}s ago`;
    return `${Math.floor(diff/60)}m ago`;
  };

  return (
    <header className="topbar">
      <div className="topbar__brand">
        <div className="topbar__shield">🛡️</div>
        <div className="topbar__titles">
          <span className="topbar__title">MQPilot</span>
          <span className="text-xs text-orange-400 font-bold uppercase tracking-wider">⚠️ Simulated Demo Data Layer</span>
          <span className="topbar__subtitle">Real-time Device Trust &amp; Containment Dashboard</span>
        </div>
      </div>

      <div className="topbar__right">
        <span className="topbar__updated">
          Updated: {fmtUpdated(lastUpdated)}
        </span>
        <span className="topbar__clock">{fmt(time)}</span>
        <div className="conn-status">
          <div className={`conn-dot ${connected ? "" : "conn-dot--off"}`} />
          <span className={connected ? "conn-label--on" : "conn-label--off"}>
            {connected ? "API LIVE" : "OFFLINE"}
          </span>
        </div>
      </div>
    </header>
  );
}
