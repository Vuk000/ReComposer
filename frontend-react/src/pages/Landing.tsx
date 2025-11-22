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
            <Card className="group text-center transition-all duration-300 hover:scale-105 hover:border-primary/50 hover:shadow-2xl hover:shadow-primary/20 cursor-pointer">
              <CardHeader>
                <div className="mb-4 text-5xl transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">⏱️</div>
                <CardTitle className="text-2xl transition-colors group-hover:text-primary">Maximize Productivity</CardTitle>
                <CardDescription className="mt-2 text-base">
                  Eliminate time-intensive email drafting. Deploy enterprise-quality communications in seconds with AI-powered optimization.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="group text-center transition-all duration-300 hover:scale-105 hover:border-primary/50 hover:shadow-2xl hover:shadow-primary/20 cursor-pointer">
              <CardHeader>
                <div className="mb-4 text-5xl transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">📈</div>
                <CardTitle className="text-2xl transition-colors group-hover:text-primary">Drive Engagement</CardTitle>
                <CardDescription className="mt-2 text-base">
                  Optimized messaging delivers measurable improvements in response rates and stakeholder engagement across all channels.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="group text-center transition-all duration-300 hover:scale-105 hover:border-primary/50 hover:shadow-2xl hover:shadow-primary/20 cursor-pointer">
              <CardHeader>
                <div className="mb-4 text-5xl transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">✨</div>
                <CardTitle className="text-2xl transition-colors group-hover:text-primary">Ensure Consistency</CardTitle>
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
            <div className="group rounded-lg border border-border/50 bg-card/50 p-6 text-center transition-all duration-300 hover:scale-105 hover:border-primary/50 hover:bg-primary/5 hover:shadow-lg hover:shadow-primary/20 cursor-pointer">
              <div className="mb-2 text-3xl transition-transform duration-300 group-hover:scale-125">👨‍💼</div>
              <p className="font-semibold transition-colors group-hover:text-primary">Executive Leadership</p>
            </div>
            <div className="group rounded-lg border border-border/50 bg-card/50 p-6 text-center transition-all duration-300 hover:scale-105 hover:border-primary/50 hover:bg-primary/5 hover:shadow-lg hover:shadow-primary/20 cursor-pointer">
              <div className="mb-2 text-3xl transition-transform duration-300 group-hover:scale-125">🏢</div>
              <p className="font-semibold transition-colors group-hover:text-primary">Enterprise Organizations</p>
            </div>
            <div className="group rounded-lg border border-border/50 bg-card/50 p-6 text-center transition-all duration-300 hover:scale-105 hover:border-primary/50 hover:bg-primary/5 hover:shadow-lg hover:shadow-primary/20 cursor-pointer">
              <div className="mb-2 text-3xl transition-transform duration-300 group-hover:scale-125">📊</div>
              <p className="font-semibold transition-colors group-hover:text-primary">Marketing Teams</p>
            </div>
            <div className="group rounded-lg border border-border/50 bg-card/50 p-6 text-center transition-all duration-300 hover:scale-105 hover:border-primary/50 hover:bg-primary/5 hover:shadow-lg hover:shadow-primary/20 cursor-pointer">
              <div className="mb-2 text-3xl transition-transform duration-300 group-hover:scale-125">💼</div>
              <p className="font-semibold transition-colors group-hover:text-primary">Sales Organizations</p>
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
            <div className="group relative rounded-2xl border border-transparent p-6 transition-all duration-300 hover:border-primary/30 hover:bg-primary/5 hover:shadow-xl hover:shadow-primary/10 cursor-pointer">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-2xl font-bold text-primary transition-all duration-300 group-hover:scale-110 group-hover:bg-primary group-hover:text-white group-hover:shadow-lg">
                1
              </div>
              <h3 className="mb-3 text-2xl font-bold transition-colors group-hover:text-primary">Input Content</h3>
              <p className="text-muted-foreground">
                Import your email content directly into the platform. The system accepts all standard formats without preprocessing requirements.
              </p>
            </div>
            <div className="group relative rounded-2xl border border-transparent p-6 transition-all duration-300 hover:border-primary/30 hover:bg-primary/5 hover:shadow-xl hover:shadow-primary/10 cursor-pointer">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-2xl font-bold text-primary transition-all duration-300 group-hover:scale-110 group-hover:bg-primary group-hover:text-white group-hover:shadow-lg">
                2
              </div>
              <h3 className="mb-3 text-2xl font-bold transition-colors group-hover:text-primary">Configure Parameters</h3>
              <p className="text-muted-foreground">
                Select communication style: Executive Professional, Relationship-Building, or Sales-Optimized. Configure custom tone parameters as needed.
              </p>
            </div>
            <div className="group relative rounded-2xl border border-transparent p-6 transition-all duration-300 hover:border-primary/30 hover:bg-primary/5 hover:shadow-xl hover:shadow-primary/10 cursor-pointer">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-2xl font-bold text-primary transition-all duration-300 group-hover:scale-110 group-hover:bg-primary group-hover:text-white group-hover:shadow-lg">
                3
              </div>
              <h3 className="mb-3 text-2xl font-bold transition-colors group-hover:text-primary">Deploy Optimized Content</h3>
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
                className="group relative overflow-hidden rounded-2xl border border-border/50 bg-card/30 p-8 transition-all duration-300 hover:scale-[1.02] hover:border-primary/50 hover:bg-card/50 hover:shadow-2xl hover:shadow-primary/20 cursor-pointer"
              >
                {/* Icon and badge */}
                <div className="mb-6 flex items-center justify-between">
                  <span className="text-4xl transition-transform duration-300 group-hover:scale-125 group-hover:rotate-12">{slide.icon}</span>
                  <span className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary transition-all duration-300 group-hover:bg-primary group-hover:text-white">
                    Feature {index + 1}
                  </span>
                </div>
                
                {/* Title */}
                <h3 className="mb-4 text-2xl font-bold transition-colors group-hover:text-primary">{slide.title}</h3>
                
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
          <Card className="transition-all duration-300 hover:shadow-2xl hover:shadow-primary/20 hover:border-primary/30">
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
                  className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm transition-all duration-200 focus:border-primary focus:ring-2 focus:ring-primary/20"
                  rows={4}
                  placeholder="Need this completed urgently. Can you deliver by EOD tomorrow?"
                  defaultValue="Need this completed urgently. Can you deliver by EOD tomorrow?"
                />
              </div>
              <div className="flex gap-2">
                {['Executive Professional', 'Relationship-Building', 'Sales-Optimized'].map((tone) => (
                  <button
                    key={tone}
                    className="rounded-lg border border-border bg-secondary px-4 py-2 text-sm font-medium transition-all duration-300 hover:scale-105 hover:border-primary hover:bg-primary/10 hover:text-primary hover:shadow-lg"
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
      <section id="pricing" className="relative container mx-auto px-6 py-24">
        {/* Background decorative elements */}
        <div className="absolute left-0 top-0 h-[500px] w-[500px] rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute right-0 bottom-0 h-[500px] w-[500px] rounded-full bg-purple-500/5 blur-3xl" />
        
        <div className="relative mx-auto max-w-7xl">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
              Simple, Transparent Pricing
            </h2>
            <p className="mx-auto mb-10 max-w-2xl text-lg text-muted-foreground">
              Choose the plan that fits your needs. Upgrade, downgrade, or cancel anytime.
            </p>
            
            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-4">
              <span className={`text-sm font-semibold transition-colors ${!isYearly ? 'text-foreground' : 'text-muted-foreground'}`}>
                Monthly
              </span>
              <button
                onClick={() => setIsYearly(!isYearly)}
                className="relative inline-flex h-8 w-16 items-center rounded-full bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background"
                role="switch"
                aria-checked={isYearly}
              >
                <span
                  className={`inline-block h-6 w-6 transform rounded-full bg-primary shadow-lg transition-transform ${
                    isYearly ? 'translate-x-9' : 'translate-x-1'
                  }`}
                />
              </button>
              <div className="flex items-center gap-2">
                <span className={`text-sm font-semibold transition-colors ${isYearly ? 'text-foreground' : 'text-muted-foreground'}`}>
                  Yearly
                </span>
                {isYearly && (
                  <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-bold text-primary">
                    Save 20%
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="mx-auto grid max-w-5xl gap-8 lg:grid-cols-2">
            {/* Standard Plan */}
            <div className="group relative flex flex-col">
              <div className="relative flex h-full flex-col rounded-3xl border border-border bg-card p-8 shadow-sm transition-all duration-300 hover:shadow-xl hover:border-primary/40">
                <div className="mb-8">
                  <h3 className="mb-2 text-2xl font-bold">Standard</h3>
                  <p className="text-muted-foreground">Perfect for professionals getting started</p>
                </div>
                
                <div className="mb-8">
                  <div className="mb-1 flex items-baseline gap-2">
                    <span className="text-5xl font-bold tracking-tight">${standardPrice.toFixed(2)}</span>
                    <span className="text-lg text-muted-foreground">/{billingPeriod}</span>
                  </div>
                  {isYearly && (
                    <p className="text-sm text-muted-foreground">
                      ${(standardPrice / 12).toFixed(2)} per month, billed annually
                    </p>
                  )}
                </div>
                
                <div className="mb-8 flex-grow">
                  <ul className="space-y-4">
                    <li className="flex items-start gap-3">
                      <svg className="mt-0.5 h-5 w-5 shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-foreground"><strong>50 email rewrites</strong> per day</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <svg className="mt-0.5 h-5 w-5 shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-foreground">All tone options (Professional, Friendly, Persuasive, etc.)</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <svg className="mt-0.5 h-5 w-5 shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-foreground">Email history</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <svg className="mt-0.5 h-5 w-5 shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-foreground">Basic analytics (opens, clicks, usage overview)</span>
                    </li>
                  </ul>
                </div>
                
                <Link to={`/signup?plan=standard&billing=${isYearly ? 'yearly' : 'monthly'}`} className="mt-auto">
                  <Button 
                    variant="outline" 
                    size="lg"
                    className="w-full border-2 font-semibold transition-all hover:scale-[1.02] hover:border-primary hover:bg-primary/5"
                  >
                    Get Started
                  </Button>
                </Link>
              </div>
            </div>

            {/* Pro Plan - Featured */}
            <div className="group relative flex flex-col">
              {/* Gradient border effect */}
              <div className="absolute -inset-[1px] rounded-3xl bg-gradient-to-br from-primary via-purple-500 to-primary opacity-75 blur-sm transition-opacity group-hover:opacity-100" />
              
              <div className="relative flex h-full flex-col rounded-3xl border-2 border-primary/50 bg-gradient-to-br from-primary/5 via-card to-card p-8 shadow-xl transition-all duration-300 hover:shadow-2xl">
                {/* Popular Badge */}
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="rounded-full bg-gradient-to-r from-primary to-purple-600 px-4 py-1.5 text-xs font-bold text-white shadow-lg">
                    MOST POPULAR
                  </div>
                </div>
                
                <div className="mb-8 pt-4">
                  <h3 className="mb-2 text-2xl font-bold">Professional</h3>
                  <p className="text-muted-foreground">For teams and power users</p>
                </div>
                
                <div className="mb-8">
                  <div className="mb-1 flex items-baseline gap-2">
                    <span className="text-5xl font-bold tracking-tight">${proPrice.toFixed(2)}</span>
                    <span className="text-lg text-muted-foreground">/{billingPeriod}</span>
                  </div>
                  {isYearly && (
                    <p className="text-sm text-muted-foreground">
                      ${(proPrice / 12).toFixed(2)} per month, billed annually
                    </p>
                  )}
                </div>
                
                <div className="mb-8 flex-grow">
                  <ul className="space-y-4">
                    <li className="flex items-start gap-3">
                      <svg className="mt-0.5 h-5 w-5 shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-foreground"><strong>Unlimited email rewrites</strong> (fair use)</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <svg className="mt-0.5 h-5 w-5 shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-foreground">Cold outreach campaigns (multi-step sequences + follow-ups)</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <svg className="mt-0.5 h-5 w-5 shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-foreground">AI email generation from scratch</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <svg className="mt-0.5 h-5 w-5 shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-foreground">Advanced campaign analytics and insights</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <svg className="mt-0.5 h-5 w-5 shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-foreground">Usage and team reporting</span>
                    </li>
                  </ul>
                </div>
                
                <Link to={`/signup?plan=pro&billing=${isYearly ? 'yearly' : 'monthly'}`} className="mt-auto">
                  <Button 
                    size="lg"
                    className="w-full bg-gradient-to-r from-primary to-purple-600 font-semibold shadow-lg transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-primary/50"
                  >
                    Get Started
                  </Button>
                </Link>
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
