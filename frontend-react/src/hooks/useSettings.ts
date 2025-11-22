import { useState, useEffect } from 'react'
import api from '@/lib/api'
import { Settings, BillingStatus } from '@/types/api'
import { AxiosErrorResponse } from '@/types/errors'

export const useSettings = () => {
  const [settings, setSettings] = useState<Settings | null>(null)
  const [billing, setBilling] = useState<BillingStatus | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchSettings = async () => {
    setLoading(true)
    try {
      const response = await api.get<Settings>('/api/user/settings')
      setSettings(response.data)
    } catch (err) {
      // Fallback to defaults
      setSettings({ 
        default_tone: 'professional', 
        style_learning_enabled: false,
        email_notifications: true,
        marketing_emails: false
      })
    } finally {
      setLoading(false)
    }
  }

  const fetchBilling = async () => {
    try {
      const response = await api.get<BillingStatus>('/api/billing/status')
      setBilling(response.data)
    } catch (err) {
      // Handle billing disabled or other errors gracefully
      const error = err as AxiosErrorResponse
      if (error.response?.status === 503 || error.response?.data?.detail?.includes('disabled')) {
        // Billing is disabled - use user's plan from user object as fallback
        console.warn('Billing endpoints disabled, using fallback plan')
        setBilling(null) // Will be handled by Settings component
      } else {
        console.error('Failed to fetch billing status:', error.response?.data?.detail || error.message)
        // Use fallback for other errors
        setBilling({ plan: 'standard', status: 'active' })
      }
    }
  }

  useEffect(() => {
    let isMounted = true
    
    const loadData = async () => {
      if (isMounted) {
        await fetchSettings()
        await fetchBilling()
      }
    }
    
    loadData()
    
    return () => {
      isMounted = false
    }
  }, [])

  const updateSettings = async (data: Partial<Settings>): Promise<boolean> => {
    setLoading(true)
    try {
      const response = await api.put<Settings>('/api/user/settings', data)
      setSettings(response.data)
      return true
    } catch (err) {
      return false
    } finally {
      setLoading(false)
    }
  }

  return { settings, billing, loading, updateSettings, fetchBilling }
}

