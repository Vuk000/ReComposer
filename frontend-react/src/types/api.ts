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
  word_count: number
  token_used: number
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
  status: 'draft' | 'active' | 'paused' | 'completed' | 'cancelled'
  created_at: string
  launched_at?: string
  paused_at?: string
}

export interface CampaignCreate {
  name: string
  description?: string
}

export interface CampaignUpdate {
  name?: string
  description?: string
}

export interface Settings {
  default_tone: 'professional' | 'friendly' | 'persuasive'
  style_learning: boolean
}

export interface BillingStatus {
  plan: 'standard' | 'pro'
  status: 'active' | 'cancelled' | 'past_due'
  stripe_customer_id?: string
  stripe_subscription_id?: string
}

