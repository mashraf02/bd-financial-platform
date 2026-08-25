import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ExchangeRates from './pages/ExchangeRates';
import Economy from './pages/Economy';
import Remittance from './pages/Remittance';
import Trade from './pages/Trade';
import AboutData from './pages/AboutData';

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/exchange-rates', label: 'Exchange Rates' },
  { to: '/economy', label: 'Economy' },
  { to: '/remittance', label: 'Remittance' },
  { to: '/trade', label: 'Trade' },
  { to: '/about', label: 'About Data' },
];

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-900 text-slate-100">
        <nav className="border-b border-slate-700 px-6 py-4 flex items-center gap-6">
          <span className="text-xl font-bold text-emerald-400">🇧🇩 BD Financial Platform</span>
          <div className="flex gap-4 ml-auto">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-300 hover:text-white'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </nav>
        <main className="px-6 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/exchange-rates" element={<ExchangeRates />} />
            <Route path="/economy" element={<Economy />} />
            <Route path="/remittance" element={<Remittance />} />
            <Route path="/trade" element={<Trade />} />
            <Route path="/about" element={<AboutData />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
