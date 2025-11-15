import { useState, useEffect } from 'react'
import api from '@/lib/api'
import { Settings, BillingStatus } from '@/types/api'

export const useSettings = () => {
  const [settings, setSettings] = useState<Settings | null>(null)
  const [billing, setBilling] = useState<BillingStatus | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchSettings = async () => {
    setLoading(true)
    try {
      // Placeholder - implement when endpoint exists
      // const response = await api.get<Settings>('/api/user/settings')
      // setSettings(response.data)
      setSettings({ default_tone: 'professional', style_learning: false })
    } catch (err) {
      // Fallback to defaults
      setSettings({ default_tone: 'professional', style_learning: false })
    } finally {
      setLoading(false)
    }
  }

  const fetchBilling = async () => {
    try {
      const response = await api.get<BillingStatus>('/billing/status')
      setBilling(response.data)
    } catch (err) {
      // Fallback
      setBilling({ plan: 'standard', status: 'active' })
    }
  }

  useEffect(() => {
    fetchSettings()
    fetchBilling()
  }, [])

  const updateSettings = async (data: Partial<Settings>): Promise<boolean> => {
    setLoading(true)
    try {
      // Placeholder - implement when endpoint exists
      // await api.put('/api/user/settings', data)
      setSettings((prev) => (prev ? { ...prev, ...data } : null))
      return true
    } catch (err) {
      return false
    } finally {
      setLoading(false)
    }
  }

  return { settings, billing, loading, updateSettings, fetchBilling }
}

