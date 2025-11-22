import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Progress from '@/components/ui/Progress'
import Badge from '@/components/ui/Badge'
import { useToast } from '@/contexts/ToastContext'
import { useAuth } from '@/hooks/useAuth'
import { useRewrite } from '@/hooks/useRewrite'
import { useStatus } from '@/hooks/useStatus'
import api from '@/lib/api'
import { Mail, Zap, Send, Clock, ArrowRight, Sparkles, FileText, AlertCircle } from 'lucide-react'
import { RewriteLog } from '@/types/api'

const Dashboard = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const { showToast } = useToast()
  const { user } = useAuth()
  const { getUsage } = useRewrite()
  const { status } = useStatus()
  const [rewritesUsed, setRewritesUsed] = useState(0)
  const [rewriteLimit, setRewriteLimit] = useState(50)
  const [recentRewrites, setRecentRewrites] = useState<RewriteLog[]>([])
  const [loadingUsage, setLoadingUsage] = useState(true)

  useEffect(() => {
    // Handle checkout success redirect
    if (searchParams.get('checkout') === 'success') {
      showToast('Subscription activated successfully! Welcome to ReCompose.', 'success')
      // Clean up URL parameter
      setSearchParams((params) => {
        params.delete('checkout')
        return params
      })
    }
  }, [searchParams, setSearchParams, showToast])

  useEffect(() => {
    // Fetch usage stats
    const fetchUsage = async () => {
      setLoadingUsage(true)
      try {
        const usage = await getUsage()
        if (usage) {
          setRewritesUsed(usage.used)
          setRewriteLimit(usage.limit)
        } else {
          // Fallback based on plan
          if (user?.subscription_plan === 'pro') {
            setRewriteLimit(999999) // Unlimited for pro
          } else {
            setRewriteLimit(50) // Standard limit
          }
        }
      } catch (error) {
        console.error('Failed to fetch usage:', error)
        // Fallback based on plan
        if (user?.subscription_plan === 'pro') {
          setRewriteLimit(999999)
        } else {
          setRewriteLimit(50)
        }
      } finally {
        setLoadingUsage(false)
      }
    }

    // Fetch recent rewrites
    const fetchRecentRewrites = async () => {
      try {
        const response = await api.get<{ logs: RewriteLog[]; total: number; limit: number; offset: number }>('/api/rewrite/logs?limit=5')
        if (response.data.logs) {
          setRecentRewrites(response.data.logs)
        }
      } catch (error) {
        console.error('Failed to fetch recent rewrites:', error)
        // Silently fail - not critical
      }
    }

    if (user) {
      fetchUsage()
      fetchRecentRewrites()
    }
  }, [user, getUsage])
  const isPro = user?.subscription_plan === 'pro'
  const usagePercentage = isPro ? 0 : (rewritesUsed / rewriteLimit) * 100

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}!</h1>
        <p className="text-muted-foreground">Start optimizing your emails with AI-powered rewriting</p>
      </div>

      {/* Status Alerts */}
      {status && !status.rewrite_available && (
        <Card className="border-orange-500/50 bg-orange-500/10">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-orange-500 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-orange-600 dark:text-orange-400">AI Provider Not Configured</p>
                <p className="text-sm text-orange-600/80 dark:text-orange-400/80 mt-1">
                  Email rewriting is currently unavailable. Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY in the backend environment.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Rewrite Email */}
        <Link to="/app/rewrite">
          <Card className="group cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:border-primary hover:shadow-xl hover:shadow-primary/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple-600 transition-transform group-hover:scale-110">
                  <Sparkles className="h-6 w-6 text-white" />
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
              </div>
            </CardHeader>
            <CardContent>
              <h3 className="text-xl font-bold">Rewrite Email</h3>
              <p className="text-sm text-muted-foreground">Transform your emails with AI</p>
            </CardContent>
          </Card>
        </Link>

        {/* Campaigns */}
        <Link to="/app/campaigns">
          <Card className="group cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:border-primary hover:shadow-xl hover:shadow-primary/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 transition-transform group-hover:scale-110">
                  <Send className="h-6 w-6 text-white" />
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
              </div>
            </CardHeader>
            <CardContent>
              <h3 className="text-xl font-bold">Campaigns</h3>
              <p className="text-sm text-muted-foreground">
                {isPro ? 'Manage email campaigns' : 'Pro feature - Upgrade to access'}
              </p>
            </CardContent>
          </Card>
        </Link>

        {/* Settings */}
        <Link to="/app/settings">
          <Card className="group cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:border-primary hover:shadow-xl hover:shadow-primary/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 transition-transform group-hover:scale-110">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
              </div>
            </CardHeader>
            <CardContent>
              <h3 className="text-xl font-bold">Settings</h3>
              <p className="text-sm text-muted-foreground">Manage your account</p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Usage Stats */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Usage Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Monthly Usage</CardTitle>
                <CardDescription>
                  {isPro ? 'Unlimited rewrites' : `${rewritesUsed} of ${rewriteLimit} rewrites used`}
                </CardDescription>
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                <Zap className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {loadingUsage ? (
              <div className="text-center py-4 text-sm text-muted-foreground">Loading usage...</div>
            ) : !isPro ? (
              <>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Used today</span>
                  <span className="font-semibold">{rewritesUsed} / {rewriteLimit}</span>
                </div>
                <Progress value={usagePercentage} showLabel />
                {usagePercentage > 80 && (
                  <div className="rounded-lg bg-orange-500/10 p-3 text-sm text-orange-600 dark:text-orange-400">
                    You're running low on rewrites. Consider upgrading to Pro for unlimited access.
                  </div>
                )}
              </>
            ) : (
              <div className="rounded-lg bg-primary/10 p-4 text-center">
                <p className="text-sm font-medium text-primary">Unlimited rewrites available</p>
                <p className="mt-1 text-xs text-muted-foreground">Professional plan active</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Plan Info */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Current Plan</CardTitle>
                <CardDescription>
                  {isPro ? 'Professional' : 'Standard'} Plan
                </CardDescription>
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10">
                <Mail className="h-6 w-6 text-purple-500" />
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Email Rewrites</span>
                <span className="font-medium">{isPro ? 'Unlimited' : '50/day'}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Tone Options</span>
                <span className="font-medium">All Available</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Email Campaigns</span>
                <span className="font-medium">{isPro ? 'Included' : 'Not Available'}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">AI Generation</span>
                <span className="font-medium">{isPro ? 'Included' : 'Not Available'}</span>
              </div>
            </div>
            {!isPro && (
              <Link to="/app/settings">
                <Button className="w-full" variant="outline">
                  Upgrade to Pro
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Your latest email rewrites</CardDescription>
            </div>
            <Clock className="h-5 w-5 text-muted-foreground" />
          </div>
        </CardHeader>
        <CardContent>
          {recentRewrites.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
              <Mail className="mb-4 h-12 w-12 text-muted-foreground/50" />
              <p className="text-lg font-medium">No activity yet</p>
              <p className="mt-1 text-sm">Start by rewriting your first email!</p>
              <Link to="/app/rewrite">
                <Button className="mt-4">
                  <Sparkles className="mr-2 h-4 w-4" />
                  Rewrite Email
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {recentRewrites.map((rewrite) => (
                <div key={rewrite.id} className="rounded-lg border border-border/50 bg-card/30 p-4 transition-all hover:border-primary/30 hover:bg-card/50">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className="text-xs">
                          {rewrite.tone.charAt(0).toUpperCase() + rewrite.tone.slice(1)}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(rewrite.created_at).toLocaleDateString()} at {new Date(rewrite.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        <span className="font-medium">Original:</span> {rewrite.original_email.substring(0, 100)}
                        {rewrite.original_email.length > 100 && '...'}
                      </p>
                      <p className="text-sm mt-2 line-clamp-2">
                        <span className="font-medium text-primary">Rewritten:</span> {rewrite.rewritten_email.substring(0, 100)}
                        {rewrite.rewritten_email.length > 100 && '...'}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              <Link to="/app/rewrite">
                <Button variant="outline" className="w-full mt-4">
                  <Sparkles className="mr-2 h-4 w-4" />
                  Rewrite Another Email
                </Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard
