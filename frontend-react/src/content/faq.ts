export interface FAQItem {
  id: string
  question: string
  answer: string
}

export const faqs: FAQItem[] = [
  {
    id: 'how-it-works',
    question: 'How does AI email rewriting work?',
    answer:
      'ReCompose uses OpenAI GPT-4o to analyze your email content and rewrite it according to your selected tone. The AI understands context, maintains your message intent, and ensures the rewritten version is clear, professional, and effective.',
  },
  {
    id: 'data-privacy',
    question: 'Is my email content secure and private?',
    answer:
      'Yes, absolutely. All emails are encrypted in transit and at rest. We never store your email content longer than necessary to provide the service, and we comply with GDPR and SOC 2 standards. Your privacy is our top priority.',
  },
  {
    id: 'usage-limits',
    question: 'What are the usage limits for each plan?',
    answer:
      'The Standard plan includes 50 rewrites per day, while the Pro plan offers unlimited rewrites. Both plans include all tone options and email history. Pro plan also includes cold outreach campaigns and AI email generation.',
  },
  {
    id: 'tone-options',
    question: 'What tone options are available?',
    answer:
      'ReCompose offers three tone options: Professional (for business communications), Friendly (for casual interactions), and Persuasive (for sales and outreach). You can set a default tone in your settings.',
  },
  {
    id: 'campaigns',
    question: 'How do cold outreach campaigns work?',
    answer:
      'Campaigns allow you to create multi-step email sequences with automated follow-ups. You can set delays between emails, track opens and clicks, and manage all your outreach in one place. This feature is available on the Pro plan.',
  },
  {
    id: 'billing',
    question: 'Can I change or cancel my plan anytime?',
    answer:
      'Yes, you can upgrade, downgrade, or cancel your subscription at any time. Changes take effect at the start of your next billing cycle.',
  },
]

