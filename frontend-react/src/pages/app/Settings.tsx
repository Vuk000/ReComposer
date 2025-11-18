import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Input from '@/components/ui/Input'
import { useSettings } from '@/hooks/useSettings'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/contexts/ToastContext'
import api from '@/lib/api'
import { AxiosErrorResponse } from '@/types/errors'

const Settings = () => {
  const { user } = useAuth()
  const { settings, billing, updateSettings } = useSettings()
  const { showToast } = useToast()
  const [defaultTone, setDefaultTone] = useState(settings?.default_tone || 'professional')
  const [styleLearning, setStyleLearning] = useState(settings?.style_learning_enabled || false)

  const handleSave = async () => {
    const success = await updateSettings({
      default_tone: defaultTone as 'professional' | 'friendly' | 'persuasive',
      style_learning_enabled: styleLearning,
    })
    if (success) {
      showToast('Settings saved successfully!', 'success')
    } else {
      showToast('Failed to save settings', 'error')
    }
  }

  const handleChangePlan = async () => {
    try {
      const response = await api.post<{ checkout_url: string }>('/api/billing/create-checkout', {
        plan: billing?.plan === 'pro' ? 'standard' : 'pro',
        interval: 'month',
      })
      window.location.href = response.data.checkout_url
    } catch (err) {
      const error = err as AxiosErrorResponse
      showToast(error.response?.data?.detail || 'Failed to create checkout session', 'error')
    }
  }

  const handleManageBilling = async () => {
    try {
      const response = await api.post<{ portal_url: string }>('/api/billing/customer-portal')
      window.location.href = response.data.portal_url
    } catch (err) {
      const error = err as AxiosErrorResponse
      showToast(error.response?.data?.detail || 'Failed to open billing portal', 'error')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account settings and preferences</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>Your account information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium">Email</label>
            <Input value={user?.email || ''} disabled />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">Plan</label>
            <div className="flex items-center gap-2">
              <Badge variant={user?.subscription_plan === 'pro' ? 'default' : 'secondary'}>
                {user?.subscription_plan === 'pro' ? 'Pro Plan' : 'Standard Plan'}
              </Badge>
              <span className="text-sm text-muted-foreground">
                {user?.subscription_plan === 'pro' ? '$49.99/month' : '$14.99/month'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Billing</CardTitle>
          <CardDescription>Manage your subscription and billing</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Button variant="outline" onClick={handleChangePlan}>
              Change Plan
            </Button>
            <Button variant="outline" onClick={handleManageBilling}>
              Manage Billing
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            {user?.subscription_status === 'active'
              ? 'Your subscription is active'
              : user?.subscription_status === 'cancelled'
              ? 'Your subscription has been cancelled'
              : user?.subscription_status === 'past_due'
              ? 'Your subscription is past due'
              : 'Subscription status unknown'}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
          <CardDescription>Customize your experience</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium">Default Tone</label>
            <div className="flex gap-2">
              {(['professional', 'friendly', 'persuasive'] as const).map((tone) => (
                <button
                  key={tone}
                  onClick={() => setDefaultTone(tone)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    defaultTone === tone
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                  }`}
                >
                  {tone.charAt(0).toUpperCase() + tone.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Style Learning</label>
              <p className="text-xs text-muted-foreground">Let AI learn from your writing style</p>
            </div>
            <button
              onClick={() => setStyleLearning(!styleLearning)}
              className={`relative h-6 w-11 rounded-full transition-colors ${
                styleLearning ? 'bg-primary' : 'bg-secondary'
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                  styleLearning ? 'translate-x-5' : ''
                }`}
              />
            </button>
          </div>
          <Button onClick={handleSave}>Save Preferences</Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default Settings

