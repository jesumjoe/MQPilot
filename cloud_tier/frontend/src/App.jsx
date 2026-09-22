import { useState, useEffect, useRef } from "react";
import TopBar from "./components/TopBar";
import StatsBar from "./components/StatsBar";
import DeviceGrid from "./components/DeviceGrid";
import StateMachineDiagram from "./components/StateMachineDiagram";
import AlertFeed from "./components/AlertFeed";

const POLL_MS = 5000;

export default function App() {
  const [devices, setDevices]         = useState([]);
  const [alerts, setAlerts]           = useState([]);
  const [connected, setConnected]     = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const historyRef = useRef({});

  const fetchData = async () => {
    try {
      const [dRes, aRes] = await Promise.all([
        fetch("/api/devices"),
        fetch("/api/alerts"),
      ]);
      const devData   = await dRes.json();
      const alertData = await aRes.json();

      // Accumulate per-device packet-rate history for sparklines
      devData.forEach((d) => {
        const h = historyRef.current;
        if (!h[d.id]) h[d.id] = Array(20).fill(d.metrics.packet_rate);
        else {
          h[d.id] = [...h[d.id].slice(-19), d.metrics.packet_rate];
        }
      });

      setDevices(devData);
      setAlerts(alertData);
      setConnected(true);
      setLastUpdated(new Date());
    } catch {
      setConnected(false);
    }
  };

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, POLL_MS);
    return () => clearInterval(id);
  }, []);

  const devicesWithHistory = devices.map((d) => ({
    ...d,
    packetHistory: historyRef.current[d.id] || [],
  }));

  return (
    <div className="app">
      <TopBar connected={connected} lastUpdated={lastUpdated} />
      <div className="main-content">
        <StatsBar devices={devices} />
        <DeviceGrid devices={devicesWithHistory} />
        <div className="bottom-panel">
          <StateMachineDiagram devices={devices} />
          <AlertFeed alerts={alerts} />
        </div>
      </div>
    </div>
  );
}
