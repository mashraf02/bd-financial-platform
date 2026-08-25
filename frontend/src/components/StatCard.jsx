function StatCard({ label, value, suffix = '', loading = false }) {
  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div className="text-sm text-slate-400 mb-1">{label}</div>
      <div className="text-2xl font-bold text-white">
        {loading ? (
          <span className="text-slate-500 text-base">Loading...</span>
        ) : (
          <>{value}{suffix}</>
        )}
      </div>
    </div>
  );
}

export default StatCard;
