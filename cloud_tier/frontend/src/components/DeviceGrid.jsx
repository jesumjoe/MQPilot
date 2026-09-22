import DeviceCard from "./DeviceCard";

export default function DeviceGrid({ devices }) {
  if (!devices.length) {
    return (
      <div className="device-grid" style={{ placeItems:"center", minHeight:180 }}>
        <p style={{ color:"var(--text-muted)", fontSize:12 }}>Waiting for API…</p>
      </div>
    );
  }
  return (
    <div className="device-grid">
      {devices.map((d) => (
        <DeviceCard key={d.id} device={d} />
      ))}
    </div>
  );
}
