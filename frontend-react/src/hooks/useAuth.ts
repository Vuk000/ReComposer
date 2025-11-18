import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { User, AuthResponse } from '@/types/api'

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const fetchUser = useCallback(async () => {
    try {
      const response = await api.get<User>('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [fetchUser])


  const signup = async (email: string, password: string) => {
    await api.post('/api/auth/signup', { email, password })
    return login(email, password)
  }

  const login = async (email: string, password: string) => {
    const response = await api.post<AuthResponse>('/api/auth/login', { email, password })
    localStorage.setItem('token', response.data.access_token)
    await fetchUser()
    navigate('/app/dashboard')
  }

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setUser(null)
    navigate('/login')
  }, [navigate])

  return { user, loading, signup, login, logout, fetchUser }
}

