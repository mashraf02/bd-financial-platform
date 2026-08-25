import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getRemittance } from '../api/client';

function safeYear(fullDate) {
  if (!fullDate || typeof fullDate !== 'string') return null;
  return fullDate.slice(0, 4);
}

function Remittance() {
  const [remittance, setRemittance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRemittance()
      .then((data) => {
        const sorted = [...data]
          .reverse()
          .map((d) => ({ year: safeYear(d.full_date), value: d.remittance_usd / 1_000_000_000 }))
          .filter((d) => d.year !== null);
        setRemittance(sorted);
      })
      .catch((err) => console.error('Failed to load remittance data:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Workers' Remittance Inflow (Billion USD)</h1>
      <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
        <div style={{ width: '100%', height: 400 }}>
          <ResponsiveContainer>
            <LineChart data={remittance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="year" stroke="#94a3b8" interval={4} />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              />
              <Line type="monotone" dataKey="value" stroke="#a78bfa" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Remittance;
