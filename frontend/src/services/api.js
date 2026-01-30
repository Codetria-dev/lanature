import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

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
