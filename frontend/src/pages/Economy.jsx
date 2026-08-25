import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getInflation, getReserves } from '../api/client';

function ChartCard({ title, children }) {
  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <h2 className="text-lg font-semibold mb-4">{title}</h2>
      <div style={{ width: '100%', height: 300 }}>{children}</div>
    </div>
  );
}

function safeYear(fullDate) {
  if (!fullDate || typeof fullDate !== 'string') return null;
  return fullDate.slice(0, 4);
}

function Economy() {
  const [inflation, setInflation] = useState([]);
  const [reserves, setReserves] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getInflation(), getReserves()])
      .then(([inflationData, reservesData]) => {
        console.log('RAW reserves data:', reservesData);

        setInflation(
          [...inflationData]
            .reverse()
            .map((d) => ({ year: safeYear(d.full_date), value: d.inflation_rate }))
            .filter((d) => d.year !== null)
        );
        setReserves(
          [...reservesData]
            .reverse()
            .map((d) => ({ year: safeYear(d.full_date), value: d.reserves_usd / 1_000_000_000 }))
            .filter((d) => d.year !== null)
        );
      })
      .catch((err) => console.error('Failed to load economy data:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Economy</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Inflation Rate (%)">
          <ResponsiveContainer>
            <LineChart data={inflation}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="year" stroke="#94a3b8" interval={4} />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              />
              <Line type="monotone" dataKey="value" stroke="#34d399" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Foreign Reserves (Billion USD)">
          <ResponsiveContainer>
            <LineChart data={reserves}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="year" stroke="#94a3b8" interval={6} />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              />
              <Line type="monotone" dataKey="value" stroke="#60a5fa" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}

export default Economy;
