import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getTrade } from '../api/client';

function Trade() {
  const [trade, setTrade] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTrade()
      .then((data) => {
        const sorted = [...data]
          .reverse()
          .map((d) => ({
            year: d.fiscal_year_label,
            Exports: d.exports_usd / 1_000_000_000,
            Imports: d.imports_usd / 1_000_000_000,
          }));
        setTrade(sorted);
      })
      .catch((err) => console.error('Failed to load trade data:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Foreign Trade (Billion USD)</h1>
      <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
        <div style={{ width: '100%', height: 420 }}>
          <ResponsiveContainer>
            <BarChart data={trade}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="year" stroke="#94a3b8" interval={2} angle={-45} textAnchor="end" height={60} />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
              />
              <Legend />
              <Bar dataKey="Exports" fill="#34d399" />
              <Bar dataKey="Imports" fill="#f87171" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Trade;
