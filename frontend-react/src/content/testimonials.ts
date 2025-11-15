export interface Testimonial {
  id: string
  quote: string
  author: string
  role: string
  company?: string
}

export const testimonials: Testimonial[] = [
  {
    id: 'sofia-davis',
    quote:
      'This library has saved me countless hours of work and helped me deliver stunning designs to my clients faster than ever before.',
    author: 'Sofia Davis',
    role: 'Product Designer',
    company: 'Design Studio',
  },
  {
    id: 'michael-chen',
    quote:
      'ReCompose transformed how I handle client communications. The AI rewriting is incredibly accurate and saves me hours every week.',
    author: 'Michael Chen',
    role: 'Sales Director',
    company: 'Tech Corp',
  },
  {
    id: 'emily-rodriguez',
    quote:
      'The cold outreach campaigns feature is a game-changer. My response rates increased by 40% after switching to ReCompose.',
    author: 'Emily Rodriguez',
    role: 'Marketing Manager',
    company: 'Startup Inc',
  },
  {
    id: 'david-kim',
    quote:
      'Best investment I made this year. The Pro plan pays for itself with the time saved on email communications.',
    author: 'David Kim',
    role: 'Founder',
    company: 'Innovation Labs',
  },
]

