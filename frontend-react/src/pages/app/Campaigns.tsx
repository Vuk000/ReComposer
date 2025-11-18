import { useState } from 'react'
import { Plus } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Modal from '@/components/shared/Modal'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'
import { useCampaigns } from '@/hooks/useCampaigns'
import { useToast } from '@/contexts/ToastContext'
import { Campaign } from '@/types/api'

const Campaigns = () => {
  const { campaigns, loading, createCampaign, deleteCampaign } = useCampaigns()
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({ name: '', description: '', subject: '', template: '', delay_days: 0, delay_hours: 0 })
  const { showToast } = useToast()

  const getStatusBadge = (status: Campaign['status']) => {
    const variants: Record<Campaign['status'], 'default' | 'secondary' | 'outline'> = {
      draft: 'outline',
      active: 'default',
      paused: 'secondary',
      completed: 'secondary',
      cancelled: 'outline',
    }
    return <Badge variant={variants[status]}>{status.charAt(0).toUpperCase() + status.slice(1)}</Badge>
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    // Only send name and description for now (email steps can be added later)
    const result = await createCampaign({
      name: formData.name,
      description: formData.description,
      // contact_ids and email_steps can be added in a future update
    })
    if (result) {
      setShowModal(false)
      setFormData({ name: '', description: '', subject: '', template: '', delay_days: 0, delay_hours: 0 })
      showToast('Campaign created successfully!', 'success')
    } else {
      showToast('Failed to create campaign', 'error')
    }
  }

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this campaign?')) {
      const success = await deleteCampaign(id)
      if (success) {
        showToast('Campaign deleted successfully', 'success')
      } else {
        showToast('Failed to delete campaign', 'error')
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Campaigns</h1>
          <p className="text-muted-foreground">Manage your cold outreach campaigns</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Campaign
        </Button>
      </div>

      {loading && campaigns.length === 0 ? (
        <div className="text-center text-muted-foreground">Loading campaigns...</div>
      ) : campaigns.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">No campaigns yet. Create your first campaign to get started.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((campaign) => (
            <Card key={campaign.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle>{campaign.name}</CardTitle>
                    {campaign.description && <CardDescription className="mt-1">{campaign.description}</CardDescription>}
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(campaign.status)}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Created {new Date(campaign.created_at).toLocaleDateString()}</span>
                  <button
                    onClick={() => handleDelete(campaign.id)}
                    className="text-destructive hover:text-destructive/80"
                  >
                    Delete
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Create New Campaign">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium">Campaign Name</label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="My Campaign"
              required
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">Description</label>
            <Textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Campaign description..."
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">Subject Line</label>
            <Input
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              placeholder="Email subject"
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">Email Template</label>
            <Textarea
              value={formData.template}
              onChange={(e) => setFormData({ ...formData, template: e.target.value })}
              placeholder="Email template..."
              className="min-h-[150px]"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-2 block text-sm font-medium">Delay (Days)</label>
              <Input
                type="number"
                value={formData.delay_days}
                onChange={(e) => setFormData({ ...formData, delay_days: parseInt(e.target.value) || 0 })}
                min="0"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium">Delay (Hours)</label>
              <Input
                type="number"
                value={formData.delay_hours}
                onChange={(e) => setFormData({ ...formData, delay_hours: parseInt(e.target.value) || 0 })}
                min="0"
                max="23"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button type="submit" className="flex-1">
              Create Campaign
            </Button>
            <Button type="button" variant="outline" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default Campaigns

