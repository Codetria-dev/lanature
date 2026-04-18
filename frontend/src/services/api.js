import axios from 'axios';

// In development, use the Vite proxy (all /api requests proxied to http://localhost:8000)
// In production, use the environment variable or absolute URL
const baseURL = import.meta.env.VITE_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: baseURL,
  withCredentials: true,
});

// Interceptor para adicionar token em todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para tratar erros de autenticação/autorização
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 Unauthorized - Token inválido ou expirado
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
      // Redireciona para login apenas se não estiver já na página de login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    // 403 Forbidden - Usuário não tem permissão (ex: não é admin)
    // Não redireciona automaticamente, deixa o componente tratar
    return Promise.reject(error)
  }
);
