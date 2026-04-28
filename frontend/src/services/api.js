import axios from 'axios';

const API_BASE_URL = import.meta.env.DEV
  ? 'http://localhost:8000/api/v1'  // development
  : 'https://lanature-production.up.railway.app/api/v1'; // production

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
