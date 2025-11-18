// API Types

export interface User {
  id: number
  email: string
  subscription_plan: 'standard' | 'pro'
  subscription_status: 'active' | 'cancelled' | 'past_due'
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface RewriteRequest {
  email_text: string
  tone: 'professional' | 'friendly' | 'persuasive'
}

export interface RewriteResponse {
  rewritten_email: string
}

export interface UsageStats {
  used: number
  limit: number
  remaining: number
  plan: string
}

export interface Campaign {
  id: number
  name: string
  description?: string
  status: 'draft' | 'running' | 'paused' | 'completed' | 'cancelled'
  created_at: string
  launched_at?: string
  paused_at?: string
  email_steps?: CampaignEmail[]
  stats?: CampaignStats
}

export interface CampaignEmail {
  id: number
  step_number: number
  subject: string
  body_template: string
  delay_days: number
  delay_hours: number
  created_at: string
}

export interface CampaignStats {
  total_recipients: number
  pending: number
  sent: number
  replied: number
  bounced: number
  failed: number
  skipped: number
  total_opens: number
}

export interface CampaignCreate {
  name: string
  description?: string
  contact_ids?: number[]
  email_steps?: EmailStepCreate[]
}

export interface EmailStepCreate {
  step_number: number
  subject: string
  body_template: string
  delay_days?: number
  delay_hours?: number
}

export interface CampaignUpdate {
  name?: string
  description?: string
}

export interface Settings {
  default_tone: 'professional' | 'friendly' | 'persuasive' | null
  style_learning_enabled: boolean
  email_notifications?: boolean
  marketing_emails?: boolean
}

export interface BillingStatus {
  plan: 'standard' | 'pro'
  status: 'active' | 'cancelled' | 'past_due'
  stripe_customer_id?: string
  stripe_subscription_id?: string
}

