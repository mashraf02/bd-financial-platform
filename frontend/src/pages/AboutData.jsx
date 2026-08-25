function AboutData() {
  const sources = [
    { name: 'Exchange Rates (live)', source: 'open.er-api.com', notes: 'Free, no-key API. Refreshed continuously via Kafka streaming and daily via Airflow batch.' },
    { name: 'Inflation, Reserves, Remittance (historical)', source: 'World Bank Indicators API', notes: 'Annual data, calendar-year based.' },
    { name: 'Trade (exports/imports)', source: 'Bangladesh Bank — Historical Time Series (1972–2024)', notes: 'Fiscal-year based (July–June). Some years have gaps where BB did not publish USD figures.' },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">About This Data</h1>
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden mb-6">
        <table className="w-full text-left">
          <thead className="bg-slate-700/50 text-slate-300 text-sm">
            <tr>
              <th className="px-4 py-3">Dataset</th>
              <th className="px-4 py-3">Source</th>
              <th className="px-4 py-3">Notes</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((s) => (
              <tr key={s.name} className="border-t border-slate-700">
                <td className="px-4 py-3 font-medium">{s.name}</td>
                <td className="px-4 py-3 text-emerald-400">{s.source}</td>
                <td className="px-4 py-3 text-slate-400 text-sm">{s.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 text-sm text-slate-400">
        <p className="mb-2">
          <span className="text-slate-200 font-medium">Data honesty note:</span> where source data had genuine
          gaps (e.g. Bangladesh Bank did not publish USD trade figures for 1973–1987), those years are simply
          absent rather than filled in with estimates. No values in this dashboard are interpolated or fabricated.
        </p>
      </div>
    </div>
  );
}

export default AboutData;
