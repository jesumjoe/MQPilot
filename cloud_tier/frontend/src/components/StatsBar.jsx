const STATE_COLORS = {
  Normal:     "#10b981",
  Observed:   "#06b6d4",
  Suspicious: "#f59e0b",
  Contained:  "#f97316",
  Critical:   "#ef4444",
};

export default function StatsBar({ devices }) {
  const counts = { Normal:0, Observed:0, Suspicious:0, Contained:0, Critical:0 };
  devices.forEach((d) => { if (counts[d.state] !== undefined) counts[d.state]++; });

  const pills = [
    { label: "Total",      count: devices.length, color: "#64748b" },
    { label: "Normal",     count: counts.Normal,     color: STATE_COLORS.Normal },
    { label: "Observed",   count: counts.Observed,   color: STATE_COLORS.Observed },
    { label: "Suspicious", count: counts.Suspicious, color: STATE_COLORS.Suspicious },
    { label: "Contained",  count: counts.Contained,  color: STATE_COLORS.Contained },
    { label: "Critical",   count: counts.Critical,   color: STATE_COLORS.Critical },
  ];

  return (
    <div className="stats-bar">
      {pills.map((p) => (
        <div className="stat-pill" key={p.label}>
          <div className="stat-pill__dot" style={{ background: p.color, boxShadow: `0 0 5px ${p.color}` }} />
          <span className="stat-pill__count" style={{ color: p.color }}>{p.count}</span>
          <span className="stat-pill__label">{p.label}</span>
        </div>
      ))}
    </div>
  );
}
