function timeAgo(ts) {
  const diff = Math.floor(Date.now() / 1000 - ts);
  if (diff < 5)  return "just now";
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export default function AlertFeed({ alerts }) {
  return (
    <div className="panel alert-feed-panel">
      <div className="panel-title">
        Alert Feed
        {alerts.length > 0 && (
          <span style={{
            marginLeft: "auto", fontSize: 9, padding: "2px 7px",
            borderRadius: 99, background: "rgba(239,68,68,.15)",
            color: "#ef4444", fontWeight: 700,
          }}>
            {alerts.length} EVENTS
          </span>
        )}
      </div>

      <div className="alert-list">
        {alerts.length === 0 ? (
          <div className="alert-empty">No alerts yet — system nominal</div>
        ) : (
          alerts.map((a) => (
            <div key={a.id} className="alert-item" data-sev={a.severity}>
              <div className="alert-item__row">
                <span className="sev-badge" data-sev={a.severity}>{a.severity}</span>
                <span className="alert-device">{a.device_name}</span>
                <span className="alert-time">{timeAgo(a.timestamp)}</span>
              </div>
              <div className="alert-msg">{a.message}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
