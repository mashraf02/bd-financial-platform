import { useEffect, useState } from 'react';
import { getExchangeRates } from '../api/client';

function ExchangeRates() {
  const [rates, setRates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getExchangeRates('live')
      .then((data) => {
        // Keep only the most recent date's rates, one row per currency
        const seen = new Set();
        const latest = [];
        for (const row of data) {
          if (!seen.has(row.currency_code)) {
            seen.add(row.currency_code);
            latest.push(row);
          }
        }
        latest.sort((a, b) => a.currency_code.localeCompare(b.currency_code));
        setRates(latest);
      })
      .catch((err) => console.error('Failed to load exchange rates:', err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Exchange Rates (per 1 USD)</h1>

      {loading ? (
        <p className="text-slate-400">Loading...</p>
      ) : (
        <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-slate-700/50 text-slate-300 text-sm">
              <tr>
                <th className="px-4 py-3">Currency</th>
                <th className="px-4 py-3">Code</th>
                <th className="px-4 py-3 text-right">Rate to USD</th>
                <th className="px-4 py-3 text-right">As of</th>
              </tr>
            </thead>
            <tbody>
              {rates.map((rate) => (
                <tr key={rate.currency_code} className="border-t border-slate-700 hover:bg-slate-700/30">
                  <td className="px-4 py-3">{rate.currency_name}</td>
                  <td className="px-4 py-3 text-emerald-400 font-mono">{rate.currency_code}</td>
                  <td className="px-4 py-3 text-right font-mono">{rate.rate_to_usd.toFixed(4)}</td>
                  <td className="px-4 py-3 text-right text-slate-400 text-sm">{rate.full_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ExchangeRates;
