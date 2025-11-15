import { useState, useEffect } from 'react'
import api from '@/lib/api'
import { Campaign, CampaignCreate, CampaignUpdate } from '@/types/api'

export const useCampaigns = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchCampaigns = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get<Campaign[]>('/api/campaigns')
      setCampaigns(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch campaigns')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCampaigns()
  }, [])

  const createCampaign = async (data: CampaignCreate): Promise<Campaign | null> => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.post<Campaign>('/api/campaigns', data)
      setCampaigns((prev) => [...prev, response.data])
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create campaign')
      return null
    } finally {
      setLoading(false)
    }
  }

  const updateCampaign = async (id: number, data: CampaignUpdate): Promise<Campaign | null> => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.put<Campaign>(`/api/campaigns/${id}`, data)
      setCampaigns((prev) => prev.map((c) => (c.id === id ? response.data : c)))
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update campaign')
      return null
    } finally {
      setLoading(false)
    }
  }

  const deleteCampaign = async (id: number): Promise<boolean> => {
    setLoading(true)
    setError(null)
    try {
      await api.delete(`/api/campaigns/${id}`)
      setCampaigns((prev) => prev.filter((c) => c.id !== id))
      return true
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete campaign')
      return false
    } finally {
      setLoading(false)
    }
  }

  return { campaigns, loading, error, fetchCampaigns, createCampaign, updateCampaign, deleteCampaign }
}

