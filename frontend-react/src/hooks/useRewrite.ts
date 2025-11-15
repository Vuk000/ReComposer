import { useState } from 'react'
import api from '@/lib/api'
import { RewriteRequest, RewriteResponse, UsageStats } from '@/types/api'

export const useRewrite = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const rewriteEmail = async (request: RewriteRequest): Promise<RewriteResponse | null> => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.post<RewriteResponse>('/api/rewrite', request)
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to rewrite email')
      return null
    } finally {
      setLoading(false)
    }
  }

  const getUsage = async (): Promise<UsageStats | null> => {
    try {
      const response = await api.get<UsageStats>('/api/rewrite/usage')
      return response.data
    } catch (err) {
      return null
    }
  }

  return { rewriteEmail, getUsage, loading, error }
}

