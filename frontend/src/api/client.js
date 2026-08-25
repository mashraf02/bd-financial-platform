import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getDashboard = () => api.get('/api/dashboard').then(res => res.data);
export const getExchangeRates = (rateType = 'live') =>
  api.get('/api/exchange-rates', { params: { rate_type: rateType } }).then(res => res.data);
export const getExchangeRateHistory = (code) =>
  api.get(`/api/exchange-rates/${code}`).then(res => res.data);
export const getInflation = () => api.get('/api/inflation').then(res => res.data);
export const getReserves = () => api.get('/api/reserves').then(res => res.data);
export const getTrade = () => api.get('/api/trade').then(res => res.data);
export const getRemittance = () => api.get('/api/remittance').then(res => res.data);

export const WS_URL = 'ws://localhost:8000/ws/exchange-rates';
