export interface FAQItem {
  id: string
  question: string
  answer: string
}

export const faqs: FAQItem[] = [
  {
    id: 'how-it-works',
    question: 'How does the AI email optimization technology work?',
    answer:
      'ReCompose leverages OpenAI\'s GPT-4 language model to analyze and enhance email communications. The platform processes your content through advanced natural language algorithms that understand context, preserve core messaging, and optimize for clarity, professionalism, and business impact according to your selected communication style.',
  },
  {
    id: 'data-privacy',
    question: 'What security measures protect our business communications?',
    answer:
      'All communications are protected with AES-256 encryption both in transit and at rest. We implement minimal data retention policies, automatically purging content after processing. Our infrastructure is SOC 2 Type II certified and fully GDPR compliant. Data privacy and security are fundamental to our platform architecture.',
  },
  {
    id: 'usage-limits',
    question: 'What are the plan limits and capabilities?',
    answer:
      'The Standard plan provides 50 email optimizations daily, suitable for individual professionals. The Professional plan offers unlimited processing capacity. Both tiers include all tone configurations and complete revision history. The Professional plan additionally includes automated campaign management and AI content generation capabilities.',
  },
  {
    id: 'tone-options',
    question: 'What communication styles are available?',
    answer:
      'The platform offers three optimized communication styles: Executive Professional (for formal business correspondence), Relationship-Building (for stakeholder engagement), and Sales-Optimized (for conversion-focused outreach). Default preferences can be configured in account settings for consistent brand voice.',
  },
  {
    id: 'campaigns',
    question: 'How does the automated campaign management function?',
    answer:
      'Campaign management enables deployment of sophisticated multi-touch email sequences with configurable timing intervals. The system provides real-time engagement analytics including open rates, click-through rates, and response tracking. All outreach activities are managed through a centralized dashboard. This capability is included in the Professional tier.',
  },
  {
    id: 'billing',
    question: 'What is the subscription modification policy?',
    answer:
      'Subscriptions can be upgraded, downgraded, or cancelled at any time through account settings. Plan modifications take effect at the beginning of the next billing cycle. No long-term contracts or cancellation fees apply.',
  },
]

