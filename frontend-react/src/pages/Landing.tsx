import { useState } from 'react'
import { Link } from 'react-router-dom'
import MarketingLayout from '@/components/layout/MarketingLayout'
import Button from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import Accordion from '@/components/ui/Accordion'
import { featureSlides } from '@/content/features'
import { faqs } from '@/content/faq'

const Landing = () => {
  const [isYearly, setIsYearly] = useState(false)

  // Pricing data
  const pricing = {
    standard: {
      monthly: 14.99,
      yearly: 143.9, // 20% discount: 14.99 * 12 * 0.8 = 143.904
    },
    pro: {
      monthly: 49.99,
      yearly: 479.9, // 20% discount: 49.99 * 12 * 0.8 = 479.904
    },
  }

  const standardPrice = isYearly ? pricing.standard.yearly : pricing.standard.monthly
  const proPrice = isYearly ? pricing.pro.yearly : pricing.pro.monthly
  const billingPeriod = isYearly ? 'year' : 'month'
  return (
    <MarketingLayout>
      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="mb-6 text-5xl font-bold tracking-tight md:text-6xl">
            Enterprise Email Intelligence
            <span className="bg-gradient-to-r from-primary to-[#a78bfa] bg-clip-text text-transparent">
              {' '}
              Powered by AI
            </span>
          </h1>
          <p className="mb-8 text-xl text-muted-foreground">
            Optimize business communications with AI-driven email enhancement and automated campaign management.
            Deliver consistent, professional messaging that drives results.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Link to="/signup">
              <Button size="lg" className="transition-all hover:scale-105">
                Get Started
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="transition-all hover:scale-105">
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Why ReCompose Section */}
      <section id="features" className="container mx-auto px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">Why ReCompose?</h2>
            <p className="text-lg text-muted-foreground">
              The enterprise-grade email intelligence platform for modern organizations
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            <Card className="text-center transition-all hover:scale-105 hover:border-primary/50">
              <CardHeader>
                <div className="mb-4 text-5xl">⏱️</div>
                <CardTitle className="text-2xl">Maximize Productivity</CardTitle>
                <CardDescription className="mt-2 text-base">
                  Eliminate time-intensive email drafting. Deploy enterprise-quality communications in seconds with AI-powered optimization.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="text-center transition-all hover:scale-105 hover:border-primary/50">
              <CardHeader>
                <div className="mb-4 text-5xl">📈</div>
                <CardTitle className="text-2xl">Drive Engagement</CardTitle>
                <CardDescription className="mt-2 text-base">
                  Optimized messaging delivers measurable improvements in response rates and stakeholder engagement across all channels.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="text-center transition-all hover:scale-105 hover:border-primary/50">
              <CardHeader>
                <div className="mb-4 text-5xl">✨</div>
                <CardTitle className="text-2xl">Ensure Consistency</CardTitle>
                <CardDescription className="mt-2 text-base">
                  Maintain professional brand voice across all communications. Deliver consistent, high-quality messaging at scale.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Social Proof Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold">Trusted by Organizations Worldwide</h2>
            <p className="text-muted-foreground">
              Join enterprise clients and professionals optimizing business communications globally
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-4">
            <div className="rounded-lg border border-border/50 bg-card/50 p-6 text-center transition-all hover:border-primary/30">
              <div className="mb-2 text-3xl">👨‍💼</div>
              <p className="font-semibold">Executive Leadership</p>
            </div>
            <div className="rounded-lg border border-border/50 bg-card/50 p-6 text-center transition-all hover:border-primary/30">
              <div className="mb-2 text-3xl">🏢</div>
              <p className="font-semibold">Enterprise Organizations</p>
            </div>
            <div className="rounded-lg border border-border/50 bg-card/50 p-6 text-center transition-all hover:border-primary/30">
              <div className="mb-2 text-3xl">📊</div>
              <p className="font-semibold">Marketing Teams</p>
            </div>
            <div className="rounded-lg border border-border/50 bg-card/50 p-6 text-center transition-all hover:border-primary/30">
              <div className="mb-2 text-3xl">💼</div>
              <p className="font-semibold">Sales Organizations</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="container mx-auto px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">Implementation Process</h2>
            <p className="text-lg text-muted-foreground">
              Deploy in three streamlined steps
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            <div className="relative">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-2xl font-bold text-primary">
                1
              </div>
              <h3 className="mb-3 text-2xl font-bold">Input Content</h3>
              <p className="text-muted-foreground">
                Import your email content directly into the platform. The system accepts all standard formats without preprocessing requirements.
              </p>
            </div>
            <div className="relative">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-2xl font-bold text-primary">
                2
              </div>
              <h3 className="mb-3 text-2xl font-bold">Configure Parameters</h3>
              <p className="text-muted-foreground">
                Select communication style: Executive Professional, Relationship-Building, or Sales-Optimized. Configure custom tone parameters as needed.
              </p>
            </div>
            <div className="relative">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-2xl font-bold text-primary">
                3
              </div>
              <h3 className="mb-3 text-2xl font-bold">Deploy Optimized Content</h3>
              <p className="text-muted-foreground">
                Receive AI-optimized communications in real-time. Deploy immediately and monitor engagement performance metrics.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section - Grid Layout */}
      <section className="container mx-auto px-6 py-20">
        <div className="mx-auto max-w-7xl">
          <h2 className="mb-4 text-center text-4xl font-bold">Everything you need to succeed</h2>
          <p className="mb-16 text-center text-lg text-muted-foreground">
            Discover how ReCompose can transform your email communication
          </p>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {featureSlides.map((slide, index) => (
              <div
                key={slide.id}
                className="group relative overflow-hidden rounded-2xl border border-border/50 bg-card/30 p-8 transition-all hover:border-primary/50 hover:bg-card/50"
              >
                {/* Icon and badge */}
                <div className="mb-6 flex items-center justify-between">
                  <span className="text-4xl">{slide.icon}</span>
                  <span className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                    Feature {index + 1}
                  </span>
                </div>
                
                {/* Title */}
                <h3 className="mb-4 text-2xl font-bold">{slide.title}</h3>
                
                {/* Description */}
                <p className="mb-6 text-muted-foreground leading-relaxed">
                  {slide.description}
                </p>
                
                {/* Details List */}
                <ul className="space-y-3">
                  {slide.details.map((detail, detailIndex) => (
                    <li key={detailIndex} className="flex items-start gap-3">
                      <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary">
                        <span className="text-xs">✓</span>
                      </span>
                      <span className="text-sm leading-relaxed text-foreground/90">{detail}</span>
                    </li>
                  ))}
                </ul>
                
                {/* Hover gradient effect */}
                <div className="absolute -right-8 -bottom-8 h-32 w-32 rounded-full bg-primary/5 blur-2xl opacity-0 transition-opacity group-hover:opacity-100" />
              </div>
            ))}
          </div>
          
          {/* CTA Button */}
          <div className="mt-12 text-center">
            <Link to="/signup">
              <Button size="lg" className="transition-all hover:scale-105">
                Get Started Today
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Interactive Demo Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-4 text-center text-3xl font-bold">Platform Demonstration</h2>
          <p className="mb-8 text-center text-muted-foreground">
            Experience real-time AI optimization of business communications
          </p>
          <Card>
            <CardHeader>
              <CardTitle>Email Optimization Demo</CardTitle>
              <CardDescription>
                View sample transformation demonstrating AI-powered content enhancement
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium">Original Communication</label>
                <textarea
                  className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                  rows={4}
                  placeholder="Need this completed urgently. Can you deliver by EOD tomorrow?"
                  defaultValue="Need this completed urgently. Can you deliver by EOD tomorrow?"
                />
              </div>
              <div className="flex gap-2">
                {['Executive Professional', 'Relationship-Building', 'Sales-Optimized'].map((tone) => (
                  <button
                    key={tone}
                    className="rounded-lg border border-border bg-secondary px-4 py-2 text-sm font-medium transition-colors hover:bg-secondary/80"
                  >
                    {tone}
                  </button>
                ))}
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium">Optimized Communication</label>
                <div className="rounded-lg border border-border bg-muted/50 p-4 text-sm">
                  <p className="text-muted-foreground">
                    Good afternoon. I'm reaching out regarding a time-sensitive deliverable. Would it be possible to complete this item by end of business tomorrow? Please confirm if this timeline aligns with your current capacity. I appreciate your prompt attention to this matter.
                  </p>
                </div>
              </div>
              <Link to="/signup">
                <Button className="w-full">Access Full Platform Capabilities</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="relative container mx-auto px-6 py-20">
        {/* Background decorative elements */}
        <div className="absolute left-1/4 top-0 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute right-1/4 bottom-0 h-96 w-96 rounded-full bg-[#a78bfa]/5 blur-3xl" />
        
        <div className="relative mx-auto max-w-6xl">
          <div className="mb-16 text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-2">
              <span className="text-sm font-medium text-primary">Pricing</span>
            </div>
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">Transparent Enterprise Pricing</h2>
            <p className="mb-8 text-lg text-muted-foreground">
              Select the tier aligned with your organizational requirements
            </p>
            
            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-4">
              <span className={`text-sm font-medium transition-colors ${!isYearly ? 'text-foreground' : 'text-muted-foreground'}`}>
                Monthly
              </span>
              <button
                onClick={() => setIsYearly(!isYearly)}
                className="relative inline-flex h-7 w-14 items-center rounded-full bg-primary/20 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background"
                role="switch"
                aria-checked={isYearly}
              >
                <span
                  className={`inline-block h-5 w-5 transform rounded-full bg-primary transition-transform ${
                    isYearly ? 'translate-x-8' : 'translate-x-1'
                  }`}
                />
              </button>
              <div className="flex items-center gap-2">
                <span className={`text-sm font-medium transition-colors ${isYearly ? 'text-foreground' : 'text-muted-foreground'}`}>
                  Yearly
                </span>
                {isYearly && (
                  <span className="rounded-full border border-primary/30 bg-primary/20 px-2 py-0.5 text-xs font-semibold text-primary">
                    Save 20%
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="grid gap-8 md:grid-cols-2">
            {/* Standard Plan */}
            <div className="group relative">
              <div className="relative h-full overflow-hidden rounded-2xl border border-border/50 bg-gradient-to-br from-card/50 to-card/30 p-8 transition-all duration-300 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/10">
                <div className="relative z-10">
                  <div className="mb-6">
                    <h3 className="mb-2 text-2xl font-bold">Standard</h3>
                    <p className="text-sm text-muted-foreground">For individual professionals</p>
                  </div>
                  
                  <div className="mb-8">
                    <div className="flex items-baseline gap-2">
                      <span className="text-5xl font-bold">${standardPrice.toFixed(2)}</span>
                      <span className="text-muted-foreground">/{billingPeriod}</span>
                    </div>
                    {isYearly && (
                      <p className="mt-2 text-sm text-muted-foreground">
                        ${(standardPrice / 12).toFixed(2)} per month
                      </p>
                    )}
                  </div>
                  
                  <ul className="mb-8 space-y-4">
                    <li className="flex items-start gap-3">
                      <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/20">
                        <span className="text-xs font-bold text-primary">✓</span>
                      </div>
                      <span className="text-sm leading-relaxed">50 daily optimizations</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/20">
                        <span className="text-xs font-bold text-primary">✓</span>
                      </div>
                      <span className="text-sm leading-relaxed">All communication styles</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/20">
                        <span className="text-xs font-bold text-primary">✓</span>
                      </div>
                      <span className="text-sm leading-relaxed">Complete revision history</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/20">
                        <span className="text-xs font-bold text-primary">✓</span>
                      </div>
                      <span className="text-sm leading-relaxed">Core analytics dashboard</span>
                    </li>
                  </ul>
                  
                  <Link to={`/signup?plan=standard&billing=${isYearly ? 'yearly' : 'monthly'}`}>
                    <Button variant="outline" className="w-full transition-all hover:scale-105">
                      Deploy Standard Tier
                    </Button>
                  </Link>
                </div>
                
                {/* Decorative gradient */}
                <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-primary/5 blur-2xl" />
              </div>
            </div>

            {/* Pro Plan - Featured */}
            <div className="group relative">
              <div className="absolute -inset-0.5 rounded-2xl bg-gradient-to-r from-primary via-[#a78bfa] to-primary opacity-20 blur transition-opacity group-hover:opacity-30" />
              <div className="relative h-full overflow-hidden rounded-2xl border-2 border-primary/50 bg-gradient-to-br from-primary/10 via-primary/5 to-card/30 p-8 shadow-lg shadow-primary/20 transition-all duration-300">
                {/* Popular Badge */}
                <div className="absolute right-6 top-6">
                  <div className="rounded-full border border-primary/30 bg-primary/20 px-3 py-1 text-xs font-semibold text-primary">
                    Popular
                  </div>
                </div>
                
                <div className="relative z-10">
                  <div className="mb-6">
                    <h3 className="mb-2 text-2xl font-bold">Professional</h3>
                    <p className="text-sm text-muted-foreground">For organizations and teams</p>
                  </div>
                  
                  <div className="mb-8">
                    <div className="flex items-baseline gap-2">
                      <span className="text-5xl font-bold">${proPrice.toFixed(2)}</span>
                      <span className="text-muted-foreground">/{billingPeriod}</span>
                    </div>
                    {isYearly && (
                      <p className="mt-2 text-sm text-muted-foreground">
                        ${(proPrice / 12).toFixed(2)} per month
                      </p>
                    )}
                  </div>
                  
                  <ul className="mb-8 space-y-4">
                    <li className="flex items-start gap-3">
                      <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary">
                        <span className="text-xs font-bold text-primary-foreground">✓</span>
                      </div>
                      <span className="text-sm leading-relaxed">Unlimited email optimization</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary">
                        <span className="text-xs font-bold text-primary-foreground">✓</span>
                      </div>
                      <span className="text-sm leading-relaxed">Automated campaign management</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary">
                        <span className="text-xs font-bold text-primary-foreground">✓</span>
                      </div>
                      <span className="text-sm leading-relaxed">AI content generation</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary">
                        <span className="text-xs font-bold text-primary-foreground">✓</span>
                      </div>
                      <span className="text-sm leading-relaxed">Enterprise analytics suite</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary">
                        <span className="text-xs font-bold text-primary-foreground">✓</span>
                      </div>
                      <span className="text-sm leading-relaxed">Dedicated account support</span>
                    </li>
                  </ul>
                  
                  <Link to={`/signup?plan=pro&billing=${isYearly ? 'yearly' : 'monthly'}`}>
                    <Button className="w-full bg-gradient-to-r from-primary to-[#a78bfa] transition-all hover:scale-105 hover:shadow-lg hover:shadow-primary/50">
                      Deploy Professional Tier
                    </Button>
                  </Link>
                </div>
                
                {/* Decorative gradients */}
                <div className="absolute -right-8 -top-8 h-40 w-40 rounded-full bg-primary/20 blur-3xl" />
                <div className="absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-[#a78bfa]/20 blur-3xl" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="relative container mx-auto px-6 py-20">
        {/* Background decorative elements */}
        <div className="absolute left-0 top-0 h-64 w-64 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute bottom-0 right-0 h-64 w-64 rounded-full bg-[#a78bfa]/5 blur-3xl" />
        
        <div className="relative mx-auto max-w-4xl">
          <div className="mb-12 text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-2">
              <span className="text-sm font-medium text-primary">FAQ</span>
            </div>
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">Frequently Asked Questions</h2>
            <p className="text-lg text-muted-foreground">
              Everything you need to know about ReCompose
            </p>
          </div>
          
          <div className="relative">
            <Accordion
              items={faqs.map((faq) => ({
                id: faq.id,
                title: faq.question,
                content: <p className="leading-relaxed">{faq.answer}</p>,
              }))}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold">Ready to Deploy Enterprise Email Intelligence?</h2>
          <p className="mb-8 text-muted-foreground">
            Join leading organizations leveraging ReCompose for optimized business communications.
          </p>
          <Link to="/signup">
            <Button size="lg" className="transition-all hover:scale-105">
              Start Implementation
            </Button>
          </Link>
        </div>
      </section>
    </MarketingLayout>
  )
}

export default Landing
