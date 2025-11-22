import { useState, useEffect } from 'react'
import api from '@/lib/api'

export interface StatusResponse {
  ai_provider: 'openai' | 'anthropic' | 'none'
  billing_enabled: boolean
  stripe_configured: boolean
  rewrite_available: boolean
  billing_available: boolean
}

export function useStatus() {
  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchStatus() {
      try {
        setLoading(true)
        const response = await api.get<StatusResponse>('/api/status')
        setStatus(response.data)
        setError(null)
      } catch (err: any) {
        console.error('Failed to fetch status:', err)
        setError(err.response?.data?.detail || 'Failed to fetch status')
        // Set default status if API fails
        setStatus({
          ai_provider: 'none',
          billing_enabled: false,
          stripe_configured: false,
          rewrite_available: false,
          billing_available: false,
        })
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
  }, [])

  return { status, loading, error }
}

