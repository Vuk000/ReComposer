export interface FeatureSlide {
  id: string
  title: string
  description: string
  icon: string
  details: string[]
}

export const featureSlides: FeatureSlide[] = [
  {
    id: 'ai-rewriting',
    title: 'AI-Powered Email Rewriting',
    description:
      'Transform your emails instantly with advanced language-model technology. Our AI understands context, tone, and intent to rewrite your messages flawlessly.',
    icon: '✨',
    details: [
      'Built on advanced AI rewriting technology',
      'Understands context and preserves intent',
      'Rewrites in seconds',
      'Supports multiple styles and formats',
    ],
  },
  {
    id: 'tone-customization',
    title: 'Choose Your Perfect Tone',
    description:
      'Whether you need to sound professional for a client, friendly for a colleague, or persuasive for outreach, we have the tone for you.',
    icon: '🎯',
    details: [
      'Business-professional',
      'Warm & friendly',
      'Sales-persuasive',
      'Custom tone control',
    ],
  },
  {
    id: 'cold-outreach',
    title: 'Automated Multi-Step Cold Outreach',
    description:
      'Launch and manage intelligent email sequences with smart follow-ups. Track opens, clicks, and replies — all in one dashboard.',
    icon: '📧',
    details: [
      'Multi-step sequences',
      'Smart AI-generated follow-ups',
      'Open/click/reply tracking',
      'Unlimited campaigns on Pro',
    ],
  },
  {
    id: 'analytics',
    title: 'Usage Analytics & Insights',
    description:
      'Track your email rewriting activity, monitor usage limits, and analyze performance. See how ReCompose helps you communicate better.',
    icon: '📊',
    details: [
      'Daily usage tracking and limits',
      'Rewrite history and analytics',
      'Performance insights and trends',
      'Export data for reporting',
    ],
  },
  {
    id: 'security',
    title: 'Enterprise-Grade Security',
    description:
      'Your emails are encrypted in transit and at rest. We never store your content longer than necessary.',
    icon: '🔒',
    details: [
      'End-to-end encryption',
      'No long-term storage',
      'Private by design',
      'Secure AI processing',
    ],
  },
  {
    id: 'pro-features',
    title: 'Advanced Pro Features',
    description:
      'Unlock unlimited rewrites, AI email generation, advanced analytics, and priority support with our Pro plan.',
    icon: '🚀',
    details: [
      'Unlimited email rewrites per day',
      'AI-powered email generation from scratch',
      'Advanced campaign analytics and insights',
      'Priority customer support',
    ],
  },
]

