const STATES = [
  { id: "Normal",     color: "#10b981", label: "Normal"     },
  { id: "Observed",   color: "#06b6d4", label: "Observed"   },
  { id: "Suspicious", color: "#f59e0b", label: "Suspicious" },
  { id: "Contained",  color: "#f97316", label: "Contained"  },
  { id: "Critical",   color: "#ef4444", label: "Critical"   },
];

const NODE_POSITIONS = [80, 210, 340, 470, 600]; // cx values
const CY = 62, R = 28;

export default function StateMachineDiagram({ devices }) {
  // Count devices per state
  const counts = {};
  devices.forEach((d) => { counts[d.state] = (counts[d.state] || 0) + 1; });

  // Device avatars per state (first letter of name)
  const avatars = {};
  devices.forEach((d) => {
    if (!avatars[d.state]) avatars[d.state] = [];
    avatars[d.state].push(d.name[0]);
  });

  return (
    <div className="panel">
      <div className="panel-title">Device State Machine</div>
      <svg viewBox="0 0 680 120" className="sm-svg">
        <defs>
          {STATES.map((s) => (
            <filter key={`glow-${s.id}`} id={`glow-${s.id}`} x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          ))}
          <marker id="arr" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
            <polygon points="0 0, 7 3.5, 0 7" fill="rgba(255,255,255,0.12)" />
          </marker>
        </defs>

        {/* Connector lines */}
        {STATES.slice(0, -1).map((s, i) => (
          <line
            key={`line-${i}`}
            x1={NODE_POSITIONS[i] + R} y1={CY}
            x2={NODE_POSITIONS[i + 1] - R} y2={CY}
            stroke="rgba(255,255,255,0.1)" strokeWidth={1.5}
            markerEnd="url(#arr)"
          />
        ))}

        {/* Nodes */}
        {STATES.map((s, i) => {
          const cx = NODE_POSITIONS[i];
          const active = !!counts[s.id];
          return (
            <g key={s.id}>
              {/* Outer glow ring when active */}
              {active && (
                <circle cx={cx} cy={CY} r={R + 9}
                  fill="none"
                  stroke={s.color}
                  strokeWidth={1}
                  opacity={0.25}
                  style={{ animation: "glow-breathe 2s ease-in-out infinite" }}
                />
              )}

              {/* Node circle */}
              <circle cx={cx} cy={CY} r={R}
                fill={active ? `${s.color}18` : "rgba(255,255,255,0.02)"}
                stroke={active ? s.color : "rgba(255,255,255,0.1)"}
                strokeWidth={active ? 2 : 1}
                filter={active ? `url(#glow-${s.id})` : undefined}
                style={{ transition: "all .5s ease" }}
              />

              {/* State initial */}
              <text x={cx} y={CY + 5} textAnchor="middle"
                fill={active ? s.color : "rgba(255,255,255,0.18)"}
                fontSize="13" fontWeight="700" fontFamily="Inter, sans-serif"
                style={{ transition: "fill .5s ease" }}
              >
                {s.label[0]}
              </text>

              {/* Device count badge */}
              {active && (
                <g>
                  <circle cx={cx + R - 2} cy={CY - R + 2} r={10} fill={s.color} />
                  <text x={cx + R - 2} y={CY - R + 6} textAnchor="middle"
                    fill="#fff" fontSize="9" fontWeight="700" fontFamily="Inter, sans-serif">
                    {counts[s.id]}
                  </text>
                </g>
              )}

              {/* State label below */}
              <text x={cx} y={CY + R + 16} textAnchor="middle"
                fill={active ? s.color : "rgba(255,255,255,0.2)"}
                fontSize="10" fontFamily="Inter, sans-serif"
                style={{ transition: "fill .5s ease" }}
              >
                {s.label}
              </text>

              {/* Device avatar chips below label */}
              {(avatars[s.id] || []).map((ch, j) => (
                <g key={`av-${s.id}-${j}`}>
                  <circle
                    cx={cx + (j - (avatars[s.id].length - 1) / 2) * 18}
                    cy={CY + R + 32}
                    r={8}
                    fill={`${s.color}25`}
                    stroke={s.color}
                    strokeWidth={1}
                  />
                  <text
                    x={cx + (j - (avatars[s.id].length - 1) / 2) * 18}
                    y={CY + R + 36}
                    textAnchor="middle"
                    fill={s.color}
                    fontSize="8" fontWeight="600" fontFamily="Inter, sans-serif"
                  >
                    {ch}
                  </text>
                </g>
              ))}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
