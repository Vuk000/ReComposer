import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import Chart from '@/components/ui/Chart'
import Calendar from '@/components/ui/Calendar'
import Tooltip from '@/components/ui/Tooltip'
import Progress from '@/components/ui/Progress'
import { TrendingUp, TrendingDown, Users, DollarSign, HelpCircle, BarChart3 } from 'lucide-react'

const Dashboard = () => {
  const revenueData = [
    { value: 1200 },
    { value: 1900 },
    { value: 1500 },
    { value: 2100 },
    { value: 1800 },
    { value: 2500 },
    { value: 2200 },
  ]

  const activityData = [
    { value: 45 },
    { value: 52 },
    { value: 48 },
    { value: 61 },
    { value: 55 },
    { value: 58 },
    { value: 62 },
  ]

  const stats = [
    {
      title: 'Total Revenue',
      value: '$1,250.00',
      change: '+12.5%',
      trend: 'up',
      description: 'Visitors for the last 6 months',
      icon: DollarSign,
      tooltip: 'Total revenue generated from all sources',
    },
    {
      title: 'New Customers',
      value: '1,234',
      change: '-20%',
      trend: 'down',
      description: 'Acquisition needs attention',
      icon: Users,
      tooltip: 'New customers acquired this period',
    },
    {
      title: 'Active Accounts',
      value: '45,678',
      change: '+12.5%',
      trend: 'up',
      description: 'Engagement exceed targets',
      icon: Users,
      tooltip: 'Currently active user accounts',
    },
    {
      title: 'Growth Rate',
      value: '4.5%',
      change: '+4.5%',
      trend: 'up',
      description: 'Meets growth projections',
      icon: TrendingUp,
      tooltip: 'Overall growth rate percentage',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here's what's happening with your account.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title} className="transition-all hover:border-primary/50">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                  <Tooltip content={stat.tooltip}>
                    <HelpCircle className="h-4 w-4 text-muted-foreground cursor-help" />
                  </Tooltip>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="flex items-center gap-2 text-xs">
                  {stat.trend === 'up' ? (
                    <TrendingUp className="h-3 w-3 text-chart-1" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-destructive" />
                  )}
                  <span className={stat.trend === 'up' ? 'text-chart-1' : 'text-destructive'}>
                    {stat.change}
                  </span>
                  <span className="text-muted-foreground">this period</span>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{stat.description}</p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Charts and Calendar Row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Revenue Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Total Revenue</CardTitle>
                <CardDescription>Revenue trends over the last 7 days</CardDescription>
              </div>
              <select className="rounded-lg border border-border bg-background px-3 py-2 text-sm">
                <option>Last 7 days</option>
                <option>Last 30 days</option>
                <option>Last 3 months</option>
              </select>
            </div>
          </CardHeader>
          <CardContent>
            <Chart data={revenueData} type="line" height={200} />
          </CardContent>
        </Card>

        {/* Calendar Widget */}
        <Card>
          <CardHeader>
            <CardTitle>Calendar</CardTitle>
            <CardDescription>Select a date to view activity</CardDescription>
          </CardHeader>
          <CardContent>
            <Calendar />
          </CardContent>
        </Card>
      </div>

      {/* Activity and Progress Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Activity Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Daily Activity</CardTitle>
            <CardDescription>Your activity levels over the past week</CardDescription>
          </CardHeader>
          <CardContent>
            <Chart data={activityData} type="bar" height={200} />
          </CardContent>
        </Card>

        {/* Progress Goals */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Goals</CardTitle>
            <CardDescription>Track your progress towards monthly targets</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span>Email Rewrites</span>
                <span className="font-medium">850 / 1,000</span>
              </div>
              <Progress value={85} showLabel />
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span>Campaigns Sent</span>
                <span className="font-medium">12 / 20</span>
              </div>
              <Progress value={60} showLabel />
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span>Response Rate</span>
                <span className="font-medium">8.5%</span>
              </div>
              <Progress value={85} showLabel />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Total Visitors Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Total Visitors</CardTitle>
              <CardDescription>Total for the last 3 months</CardDescription>
            </div>
            <select className="rounded-lg border border-border bg-background px-3 py-2 text-sm">
              <option>Last 3 months</option>
              <option>Last 6 months</option>
              <option>Last year</option>
            </select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex h-[300px] items-center justify-center text-muted-foreground">
            <div className="text-center">
              <BarChart3 className="mx-auto mb-2 h-12 w-12 text-muted-foreground/50" />
              <p>Detailed analytics coming soon</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard
