import { useEffect, useRef, useState } from 'react';
import { WS_URL } from '../api/client';

function LiveTicker() {
  const [rates, setRates] = useState([]);
  const [status, setStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setStatus('connected');
    ws.onclose = () => setStatus('disconnected');
    ws.onerror = () => setStatus('error');

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'rate_update') {
        setRates(message.data);
        setLastUpdate(new Date(message.server_time));
      }
    };

    return () => ws.close();
  }, []);

  const statusColor = {
    connecting: 'bg-yellow-500',
    connected: 'bg-emerald-500',
    disconnected: 'bg-slate-500',
    error: 'bg-red-500',
  }[status];

  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Live Exchange Rates</h2>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className={`w-2 h-2 rounded-full ${statusColor} ${status === 'connected' ? 'animate-pulse' : ''}`} />
          {status}
          {lastUpdate && <span>· updated {lastUpdate.toLocaleTimeString()}</span>}
        </div>
      </div>

      {rates.length === 0 ? (
        <p className="text-slate-400 text-sm">
          Waiting for live data... (make sure the Kafka producer and consumer are running)
        </p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {rates.map((r) => (
            <div key={r.currency_code} className="bg-slate-900 rounded-lg px-3 py-2">
              <div className="text-xs text-slate-400">{r.currency_code}</div>
              <div className="font-mono font-semibold">{r.rate_to_usd.toFixed(4)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default LiveTicker;
