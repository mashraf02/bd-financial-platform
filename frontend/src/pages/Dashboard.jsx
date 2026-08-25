import { useEffect, useState } from 'react';
import { getDashboard } from '../api/client';
import StatCard from '../components/StatCard';
import LiveTicker from '../components/LiveTicker';

function formatUSD(value) {
  if (value == null) return '—';
  return `$${(value / 1_000_000_000).toFixed(2)}B`;
}

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch((err) => console.error('Failed to load dashboard:', err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Bangladesh Financial Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="USD / BDT"
          value={data?.latest_usd_bdt_rate?.toFixed(2)}
          loading={loading}
        />
        <StatCard
          label="Inflation Rate"
          value={data?.latest_inflation_rate?.toFixed(2)}
          suffix="%"
          loading={loading}
        />
        <StatCard
          label="Foreign Reserves"
          value={formatUSD(data?.latest_reserves_usd)}
          loading={loading}
        />
        <StatCard
          label="Remittance Inflow"
          value={formatUSD(data?.latest_remittance_usd)}
          loading={loading}
        />
      </div>

      <div className="mt-6">
        <LiveTicker />
      </div>
    </div>
  );
}

export default Dashboard;
