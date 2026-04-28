import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else if (localStorage.getItem('refresh_token')) {
      // No access token but refresh token exists — try silent session restore
      restoreSession()
    } else {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const restoreSession = async () => {
    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: localStorage.getItem('refresh_token')
      })
      const { access_token, refresh_token: newRefreshToken } = response.data
      localStorage.setItem('token', access_token)
      if (newRefreshToken) {
        localStorage.setItem('refresh_token', newRefreshToken)
      }
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      await fetchUser()
    } catch (e) {
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      setLoading(false)
    }
  }

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      // 401/403 — the api.js interceptor will try to refresh automatically.
      // If the retry after refresh also fails, clean up local state.
      if (!localStorage.getItem('token')) {
        localStorage.removeItem('refresh_token')
        delete api.defaults.headers.common['Authorization']
        setUser(null)
      }
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    const response = await api.post('/auth/login', {
      email,
      password
    })
    const { access_token, refresh_token } = response.data

    localStorage.setItem('token', access_token)
    if (refresh_token) {
      localStorage.setItem('refresh_token', refresh_token)
    }
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

    await fetchUser()
    return response.data
  }

  // Helper to check if user is superuser
  const isSuperuser = () => {
    return user?.is_superuser === true
  }

  const register = async (name, email, password) => {
    const response = await api.post('/auth/register', {
      name,
      email,
      password
    })

    // After registration, automatically log in
    await login(email, password)
    return response.data
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } catch (e) {
      // Ignore server errors (e.g. token already expired) — still clear local state
    }
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isSuperuser }}>
      {children}
    </AuthContext.Provider>
  )
}
