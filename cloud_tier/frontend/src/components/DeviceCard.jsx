const STATE_COLOR = {
  Normal:     "#10b981",
  Observed:   "#06b6d4",
  Suspicious: "#f59e0b",
  Contained:  "#f97316",
  Critical:   "#ef4444",
};

const TOPIC_EMOJI = {
  "sensor/temperature": "🌡️",
  "sensor/humidity":    "💧",
  "device/status":      "🚪",
  "device/camera":      "📷",
  "device/plug":        "🔌",
};

const ALERT_STATES = new Set(["Suspicious", "Contained", "Critical"]);

/* ── Sparkline ─────────────────────────────────────────────────────────────── */
function Sparkline({ data, color }) {
  if (!data || data.length < 2) return null;
  const W = 100, H = 26;
  const max = Math.max(...data, 1);
  const pts = data
    .map((v, i) => `${(i / (data.length - 1)) * W},${H - (v / max) * H * 0.9}`)
    .join(" ");
  const area = `0,${H} ${pts} ${W},${H}`;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" className="sparkline-wrap">
      <polygon points={area} fill={`${color}18`} />
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  );
}

/* ── Trust Score Gauge (imported inline to keep one file) ─────────────────── */
function TrustGauge({ score, color }) {
  const r  = 42, cx = 58, cy = 58;
  const C  = 2 * Math.PI * r;
  const pct = 270 / 360;
  const arc = C * pct;
  const gap = C - arc;
  const fill = (score / 100) * arc;
  return (
    <svg viewBox="0 0 116 96" className="trust-gauge">
      {/* track */}
      <circle cx={cx} cy={cy} r={r}
        fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={8}
        strokeDasharray={`${arc} ${gap}`} strokeLinecap="round"
        transform={`rotate(135 ${cx} ${cy})`}
      />
      {/* value */}
      <circle cx={cx} cy={cy} r={r}
        fill="none" stroke={color} strokeWidth={8}
        strokeDasharray={`${fill} ${C - fill}`} strokeLinecap="round"
        transform={`rotate(135 ${cx} ${cy})`}
        style={{
          transition: "stroke-dasharray .6s cubic-bezier(.4,0,.2,1), stroke .6s ease",
          filter: `drop-shadow(0 0 5px ${color})`,
        }}
      />
      <text x={cx} y={cy + 7}  textAnchor="middle" className="gauge-score" fill={color}>{score}</text>
      <text x={cx} y={cy + 20} textAnchor="middle" className="gauge-label" fill="rgba(78,101,128,.9)">TRUST</text>
    </svg>
  );
}

/* ── DeviceCard ────────────────────────────────────────────────────────────── */
export default function DeviceCard({ device }) {
  const { name, ip, topic, state, trust_score, metrics, packetHistory } = device;
  const color   = STATE_COLOR[state] || "#10b981";
  const emoji   = TOPIC_EMOJI[topic] || "📡";
  const isAlert = ALERT_STATES.has(state);
  const lastSeenSec = Math.floor((Date.now() / 1000) - metrics.last_seen);

  return (
    <div className="device-card" data-state={state}>
      {/* Header */}
      <div className="device-card__header">
        <span className="device-card__emoji">{emoji}</span>
        <div className="device-card__info">
          <span className="device-card__name">{name}</span>
          <span className="device-card__ip">{ip}</span>
        </div>
        <div className="online-dot" />
      </div>

      {/* Gauge */}
      <div className="device-card__gauge">
        <TrustGauge score={trust_score} color={color} />
      </div>

      {/* State badge */}
      <div className="state-badge">
        <div className={`state-badge__dot ${isAlert ? "state-badge__dot--pulse" : ""}`} />
        {state}
      </div>

      {/* Metrics */}
      <div className="metrics-row">
        <div className="metric-box">
          <span className="metric-box__label">PKT / s</span>
          <span className="metric-box__value">{metrics.packet_rate}</span>
        </div>
        <div className="metric-box">
          <span className="metric-box__label">Anomaly</span>
          <span className="metric-box__value" style={{ color }}>
            {(metrics.anomaly_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Sparkline */}
      <Sparkline data={packetHistory} color={color} />

      {/* Topic + last seen */}
      <div className="device-card__topic">
        {topic} &nbsp;·&nbsp; {lastSeenSec < 2 ? "just now" : `${lastSeenSec}s ago`}
      </div>
    </div>
  );
}
