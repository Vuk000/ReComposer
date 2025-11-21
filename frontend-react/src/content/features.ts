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
    title: 'Enterprise-Grade AI Email Optimization',
    description:
      'Leverage state-of-the-art language models to enhance email communications instantly. Our AI maintains your message intent while optimizing clarity, professionalism, and impact across all business contexts.',
    icon: '✨',
    details: [
      'Powered by advanced GPT-4 language technology',
      'Context-aware content preservation and enhancement',
      'Real-time processing with sub-second response times',
      'Support for multiple communication styles and formats',
    ],
  },
  {
    id: 'tone-customization',
    title: 'Intelligent Tone Adaptation',
    description:
      'Align your communication style with business objectives through precision tone control. Ensure every message resonates with the intended audience while maintaining brand consistency.',
    icon: '🎯',
    details: [
      'Executive-level business communications',
      'Relationship-building conversational tone',
      'Sales-optimized persuasive messaging',
      'Customizable tone parameters for brand alignment',
    ],
  },
  {
    id: 'cold-outreach',
    title: 'Automated Email Campaign Management',
    description:
      'Deploy sophisticated multi-touch email sequences with intelligent automation. Monitor engagement metrics and optimize outreach performance through comprehensive analytics and tracking.',
    icon: '📧',
    details: [
      'Configurable multi-step email sequences',
      'AI-generated contextual follow-up messages',
      'Real-time engagement tracking (opens, clicks, replies)',
      'Unlimited campaign capacity on Professional tier',
    ],
  },
  {
    id: 'analytics',
    title: 'Comprehensive Performance Analytics',
    description:
      'Gain actionable insights into communication patterns and platform usage. Track key performance indicators and optimize email effectiveness with detailed analytics dashboards.',
    icon: '📊',
    details: [
      'Real-time usage monitoring and quota management',
      'Complete audit trail and revision history',
      'Performance trend analysis and forecasting',
      'Full data export capabilities for enterprise reporting',
    ],
  },
  {
    id: 'security',
    title: 'Enterprise Security & Compliance',
    description:
      'Protect sensitive business communications with industry-leading security protocols. All data is encrypted end-to-end with minimal retention policies and full compliance certification.',
    icon: '🔒',
    details: [
      'AES-256 encryption for data in transit and at rest',
      'Minimal data retention with automatic purging',
      'Privacy-first architecture and design principles',
      'SOC 2 and GDPR compliant AI processing',
    ],
  },
  {
    id: 'pro-features',
    title: 'Professional Tier Capabilities',
    description:
      'Maximize productivity with unlimited access to all platform features. Professional tier includes advanced AI generation, comprehensive analytics, and dedicated support resources.',
    icon: '🚀',
    details: [
      'Unlimited daily email optimization and rewrites',
      'AI-powered content generation from templates',
      'Advanced campaign analytics with custom reporting',
      'Dedicated account support with priority response',
    ],
  },
]

